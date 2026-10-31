"""AUTO: the Choice contract and the mock provider honour it."""

import pytest
from pydantic import ValidationError

from triage.providers import MockProvider, get_provider
from triage.providers.base import Choice, DecisionProvider

LABELS = ("genuine_shopper", "bot", "internal_test", "accidental")


def make_choice(**overrides):
    base = {
        "question": "q",
        "declared_labels": ("a", "b"),
        "label": "a",
        "probabilities": {"a": 0.7, "b": 0.3},
        "provider": "test",
    }
    base.update(overrides)
    return Choice(**base)


def test_valid_choice():
    assert make_choice().label == "a"


def test_sum_within_tolerance_is_accepted():
    make_choice(probabilities={"a": 0.7005, "b": 0.3})


@pytest.mark.parametrize(
    "overrides",
    [
        {"label": "c"},
        {"probabilities": {"a": 0.7, "b": 0.2, "c": 0.1}},
        {"probabilities": {"a": 1.0}},
        {"probabilities": {"a": 0.7, "b": 0.2}},
        {"probabilities": {"a": 1.2, "b": -0.2}},
        {"declared_labels": ("a", "a", "b")},
    ],
)
def test_invalid_choices_rejected(overrides):
    with pytest.raises(ValidationError):
        make_choice(**overrides)


def test_mock_satisfies_protocol_and_contract():
    provider = MockProvider(seed=42)
    assert isinstance(provider, DecisionProvider)
    choice = provider.choice("What kind of session is this?", LABELS, {"session_id": "s1"})
    assert set(choice.probabilities) == set(LABELS)
    assert abs(sum(choice.probabilities.values()) - 1.0) <= 0.001


def test_mock_is_deterministic():
    a = MockProvider(seed=7).choice("q", LABELS, {"x": 1})
    b = MockProvider(seed=7).choice("q", LABELS, {"x": 1})
    assert a == b


def test_jev_waits_on_adr():
    with pytest.raises(RuntimeError, match="ADR-001"):
        get_provider("jev")
