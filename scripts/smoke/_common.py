"""Shared helpers for AUTO-LIVE smoke scripts: env loading and report writing."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = REPO_ROOT / "reports"


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env")


def env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    return value if value not in ("", None) else default


def write_report(test_id: str, passed: bool, details: dict[str, Any]) -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = REPORTS_DIR / f"{test_id}-{stamp}.json"
    report = {"test_id": test_id, "passed": passed, "run_at_utc": stamp, **details}
    path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"[{test_id}] {'PASS' if passed else 'FAIL'} -> {path.relative_to(REPO_ROOT)}")
    return path
