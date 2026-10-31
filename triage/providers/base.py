"""Decision provider contract.

Every decision model (Jev, alternatives, rules, mock) sits behind this interface so
AUTO tests never call a live service. Phase 0 defines only `choice()`, which the
T0.2 smoke test needs; `score()` and the probability call are added in Phase 3.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, model_validator

PROBABILITY_TOLERANCE = 0.001


class Choice(BaseModel):
    """A typed decision over a fixed, declared label set."""

    model_config = ConfigDict(frozen=True)

    question: str
    declared_labels: tuple[str, ...]
    label: str
    probabilities: dict[str, float]
    provider: str

    @model_validator(mode="after")
    def _check_contract(self) -> Choice:
        declared = set(self.declared_labels)
        if len(declared) != len(self.declared_labels):
            raise ValueError("declared_labels contains duplicates")
        if self.label not in declared:
            raise ValueError(f"label {self.label!r} is not a declared label")
        extra = set(self.probabilities) - declared
        if extra:
            raise ValueError(f"probabilities include undeclared labels: {sorted(extra)}")
        missing = declared - set(self.probabilities)
        if missing:
            raise ValueError(f"probabilities missing declared labels: {sorted(missing)}")
        for name, p in self.probabilities.items():
            if not 0.0 <= p <= 1.0:
                raise ValueError(f"probability for {name!r} out of range: {p}")
        total = sum(self.probabilities.values())
        if abs(total - 1.0) > PROBABILITY_TOLERANCE:
            raise ValueError(f"probabilities sum to {total}, expected 1 ± {PROBABILITY_TOLERANCE}")
        return self


@runtime_checkable
class DecisionProvider(Protocol):
    name: str

    def choice(
        self, question: str, labels: Sequence[str], context: Mapping[str, Any]
    ) -> Choice: ...
