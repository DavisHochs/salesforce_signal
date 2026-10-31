"""T0.2 (AUTO-LIVE): a canned session returns a typed Choice with only declared labels
and probabilities summing to 1 (±0.001).

Uses DECISION_PROVIDER from .env. Until ADR-001 is accepted only `mock` is wired up,
which proves the harness; the gate only passes when run with DECISION_PROVIDER=jev.
"""

from __future__ import annotations

import json
import sys

from pydantic import ValidationError

from scripts.smoke._common import REPO_ROOT, env, load_env, write_report
from triage.providers import get_provider
from triage.providers.base import PROBABILITY_TOLERANCE

QUESTION = "What kind of session is this?"
LABELS = ("genuine_shopper", "bot", "internal_test", "accidental")


def main() -> int:
    load_env()
    provider_name = env("DECISION_PROVIDER", "mock")
    seed = int(env("RANDOM_SEED", "42"))
    session = json.loads(
        (REPO_ROOT / "scripts/smoke/fixtures/canned_session.json").read_text(encoding="utf-8")
    )

    try:
        provider = get_provider(provider_name, seed=seed)
        choice = provider.choice(QUESTION, LABELS, session)
    except (ValidationError, ValueError, RuntimeError) as exc:
        write_report("T0.2-smoke-jev", False, {"provider": provider_name, "error": str(exc)})
        return 1

    total = sum(choice.probabilities.values())
    passed = abs(total - 1.0) <= PROBABILITY_TOLERANCE and set(choice.probabilities) == set(LABELS)
    details = {
        "provider": choice.provider,
        "counts_for_gate": choice.provider == "jev",
        "choice": choice.model_dump(),
        "probability_sum": total,
    }
    write_report("T0.2-smoke-jev", passed, details)
    if choice.provider != "jev":
        print(
            "Note: ran against the mock provider. "
            "T0.2 is only satisfied with DECISION_PROVIDER=jev."
        )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
