"""Jev via TypeSafe's direct System One API (ADR-001).

Phase 0 only needs `choice()` for the T0.2 smoke test. The batched `decide()` contract
from ADR-001 (choice + score + binary in one call) is added in Phase 3.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from triage.providers.base import Choice

DEFAULT_BASE_URL = "https://api.typesafe.ai"
DEFAULT_MODEL = "jev-1.14.0"


class JevError(RuntimeError):
    """A failed or malformed Jev call."""


class JevProvider:
    name = "jev"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_s: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise JevError("TYPESAFE_API_KEY is not set")
        self.model = model
        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout_s,
        )

    def choice(
        self,
        question: str,
        labels: Sequence[str],
        context: Mapping[str, Any],
        descriptions: Mapping[str, str] | None = None,
    ) -> Choice:
        if not labels:
            raise ValueError("labels must not be empty")
        criteria = {label: (descriptions or {}).get(label, label) for label in labels}
        body = {
            "model": self.model,
            "state": dict(context),
            "questions": {"q": {"type": "choice", "instructions": question, "criteria": criteria}},
        }
        try:
            resp = self._client.post("/v1/systemone", json=body)
        except httpx.HTTPError as exc:
            raise JevError(f"request failed: {exc}") from exc
        if resp.status_code != 200:
            raise JevError(f"HTTP {resp.status_code}: {resp.text[:300]}")

        payload = resp.json()
        answer = payload.get("answers", {}).get("q")
        if not answer or answer.get("type") != "choice":
            raise JevError(f"unexpected response shape: {str(payload)[:300]}")
        return Choice(
            question=question,
            declared_labels=tuple(labels),
            label=answer["choice"],
            probabilities={k: float(v) for k, v in answer["probabilities"].items()},
            provider=self.name,
        )
