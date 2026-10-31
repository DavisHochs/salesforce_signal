"""T0.4 (AUTO-LIVE): a test message arrives in Mailpit, and the chosen email service
returns a success response.

The email-service half waits on ADR-003; until then it is reported as "pending"
and the gate cannot pass.
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
        mailpit_ok = find_in_mailpit(env("MAILPIT_API_URL", "http://localhost:8025"), token)
    except (OSError, httpx.HTTPError) as exc:
        mailpit_ok = False
        details["mailpit_error"] = str(exc)
    details["mailpit"] = "pass" if mailpit_ok else "fail"

    # Service adapter is added once ADR-003 picks a provider; until then this half is pending.
    service_ok = False
    details["email_service"] = env("EMAIL_SERVICE")
    details["email_service_result"] = "pending: waiting on ADR-003"

    # The gate needs both halves. Exit 0 when Mailpit works so the local half can be checked.
    write_report("T0.4-smoke-mail", mailpit_ok and service_ok, details)
    print(f"Mailpit: {details['mailpit']}; email service: {details['email_service_result']}")
    return 0 if mailpit_ok else 1


if __name__ == "__main__":
    sys.exit(main())
