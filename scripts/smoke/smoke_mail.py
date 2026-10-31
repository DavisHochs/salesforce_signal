"""T0.4 (AUTO-LIVE): a test message sent over SMTP arrives in Mailpit.

Per ADR-003 the project uses Mailpit only, so there is no external email service to check.
"""

from __future__ import annotations

import smtplib
import sys
import time
import uuid
from email.message import EmailMessage

import httpx

from scripts.smoke._common import env, load_env, write_report


def send_to_mailpit(host: str, port: int, sender: str, to: str, token: str) -> None:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = f"Signal smoke test {token}"
    msg.set_content(f"Smoke test message. Token: {token}")
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.send_message(msg)


def find_in_mailpit(api_url: str, token: str, attempts: int = 10) -> bool:
    for _ in range(attempts):
        resp = httpx.get(f"{api_url}/api/v1/search", params={"query": token}, timeout=5)
        resp.raise_for_status()
        if resp.json().get("messages_count", 0) > 0:
            return True
        time.sleep(0.5)
    return False


def main() -> int:
    load_env()
    token = uuid.uuid4().hex[:12]
    details: dict[str, object] = {"token": token}

    try:
        send_to_mailpit(
            env("MAILPIT_SMTP_HOST", "localhost"),
            int(env("MAILPIT_SMTP_PORT", "1025")),
            env("MAIL_FROM", "journeys@ridgeline-outfitters.test"),
            env("MAIL_TEST_TO", "seed-inbox@ridgeline-outfitters.test"),
            token,
        )
        passed = find_in_mailpit(env("MAILPIT_API_URL", "http://localhost:8025"), token)
    except (OSError, httpx.HTTPError) as exc:
        passed = False
        details["error"] = str(exc)

    write_report("T0.4-smoke-mail", passed, details)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
