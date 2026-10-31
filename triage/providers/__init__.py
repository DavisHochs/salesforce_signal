"""Provider registry."""

from __future__ import annotations

import os

from triage.providers.base import Choice, DecisionProvider
from triage.providers.jev import DEFAULT_BASE_URL, DEFAULT_MODEL, JevError, JevProvider
from triage.providers.mock import MockProvider

__all__ = [
    "Choice",
    "DecisionProvider",
    "JevError",
    "JevProvider",
    "MockProvider",
    "get_provider",
]


def get_provider(name: str, seed: int = 42) -> DecisionProvider:
    name = name.strip().lower()
    if name == "mock":
        return MockProvider(seed=seed)
    if name == "jev":
        return JevProvider(
            os.environ.get("TYPESAFE_API_KEY", ""),
            base_url=os.environ.get("TYPESAFE_BASE_URL") or DEFAULT_BASE_URL,
            model=os.environ.get("JEV_MODEL") or DEFAULT_MODEL,
        )
    raise ValueError(f"unknown decision provider: {name!r}")
