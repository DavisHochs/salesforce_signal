"""Deterministic mock provider: same seed + inputs always give the same Choice."""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections.abc import Mapping, Sequence
from typing import Any

from triage.providers.base import Choice


class MockProvider:
    name = "mock"

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def _rng(
        self, question: str, labels: Sequence[str], context: Mapping[str, Any]
    ) -> random.Random:
        payload = json.dumps(
            {"q": question, "labels": list(labels), "ctx": context}, sort_keys=True, default=str
        )
        digest = hashlib.sha256(f"{self.seed}:{payload}".encode()).hexdigest()
        return random.Random(int(digest[:16], 16))

    def choice(self, question: str, labels: Sequence[str], context: Mapping[str, Any]) -> Choice:
        if not labels:
            raise ValueError("labels must not be empty")
        rng = self._rng(question, labels, context)
        logits = [rng.gauss(0.0, 1.5) for _ in labels]
        peak = max(logits)
        weights = [math.exp(x - peak) for x in logits]
        total = sum(weights)
        probs = {label: w / total for label, w in zip(labels, weights, strict=True)}
        best = max(probs, key=probs.__getitem__)
        return Choice(
            question=question,
            declared_labels=tuple(labels),
            label=best,
            probabilities=probs,
            provider=self.name,
        )
