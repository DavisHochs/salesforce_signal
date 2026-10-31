"""T0.3 (AUTO-LIVE): authenticate to the org and return the org limits payload.

Relies on the Salesforce CLI session created in runbook D0.1 (`sf org login web`),
so this script never sees credentials.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

from scripts.smoke._common import env, load_env, write_report

# Limits recorded in docs/limits-worksheet.md (T0.6)
WATCHED_LIMITS = (
    "DailyApiRequests",
    "HourlyPublishedPlatformEvents",
    "DailyDeliveredPlatformEvents",
    "MonthlyPlatformEventsUsageEntitlement",
    "DailyAsyncApexExecutions",
    "SingleEmail",
    "MassEmail",
    "DataStorageMB",
)


def main() -> int:
    load_env()
    org = env("SF_TARGET_ORG", "signal-dev")
    sf = shutil.which("sf")
    if not sf:
        write_report("T0.3-smoke-sf", False, {"error": "Salesforce CLI `sf` not found on PATH"})
        return 1

    proc = subprocess.run(
        [sf, "org", "list", "limits", "--target-org", org, "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        write_report(
            "T0.3-smoke-sf", False, {"org": org, "error": proc.stderr.strip() or proc.stdout[:500]}
        )
        return 1

    limits = payload.get("result") or []
    passed = payload.get("status") == 0 and isinstance(limits, list) and len(limits) > 0
    watched = {row["name"]: row for row in limits if row.get("name") in WATCHED_LIMITS}
    write_report(
        "T0.3-smoke-sf",
        passed,
        {
            "org": org,
            "limit_count": len(limits),
            "watched_limits": watched,
            "error": None if passed else payload.get("message"),
        },
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
