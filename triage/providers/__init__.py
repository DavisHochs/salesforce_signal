"""Provider registry. Live providers are added only after their ADR is accepted."""

from __future__ import annotations

from triage.providers.base import Choice, DecisionProvider
from triage.providers.mock import MockProvider

__all__ = ["Choice", "DecisionProvider", "MockProvider", "get_provider"]


class ProviderNotReady(RuntimeError):
    """Raised for a provider whose adapter waits on an unaccepted ADR."""


def get_provider(name: str, seed: int = 42) -> DecisionProvider:
    name = name.strip().lower()
    if name == "mock":
        return MockProvider(seed=seed)
    if name == "jev":
        raise ProviderNotReady(
            "The Jev adapter is not built yet: it waits on ADR-001 (R0.1 Jev access) "
            "being accepted by Davis."
        )
    raise ValueError(f"unknown decision provider: {name!r}")
