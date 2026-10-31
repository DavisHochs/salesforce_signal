"""AUTO: the Jev adapter against a fake HTTP transport (no live calls)."""

import json

import httpx
import pytest
from pydantic import ValidationError

from triage.providers import JevError, JevProvider, get_provider

LABELS = ("genuine_shopper", "bot")


def make_provider(handler):
    client = httpx.Client(base_url="https://jev.test", transport=httpx.MockTransport(handler))
    return JevProvider("test-key", client=client)


def ok_response(probabilities, choice="genuine_shopper"):
    return httpx.Response(
        200,
        json={
            "model": "jev-1.14.0",
            "answers": {
                "q": {
                    "type": "choice",
                    "choice": choice,
                    "confidence": 0.8,
                    "probabilities": probabilities,
                }
            },
            "usage": {"input_tokens": 120, "output_tokens": 0},
        },
    )


def test_sends_typesafe_request_shape_and_parses_choice():
    seen = {}

    def handler(request):
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return ok_response({"genuine_shopper": 0.9, "bot": 0.1})

    choice = make_provider(handler).choice("What kind?", LABELS, {"session_id": "s1"})

    assert seen["path"] == "/v1/systemone"
    q = seen["body"]["questions"]["q"]
    assert q["type"] == "choice"
    assert set(q["criteria"]) == set(LABELS)
    assert seen["body"]["model"] == "jev-1.14.0"
    assert choice.label == "genuine_shopper"
    assert choice.provider == "jev"


def test_undeclared_label_in_response_fails_contract():
    def handler(request):
        return ok_response({"genuine_shopper": 0.5, "bot": 0.3, "other": 0.2})

    with pytest.raises(ValidationError):
        make_provider(handler).choice("What kind?", LABELS, {})


def test_http_error_raises_jev_error():
    def handler(request):
        return httpx.Response(429, json={"detail": "rate limited"})

    with pytest.raises(JevError, match="429"):
        make_provider(handler).choice("What kind?", LABELS, {})


def test_missing_key_is_reported(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(JevError, match="TYPESAFE_API_KEY"):
        get_provider("jev")
