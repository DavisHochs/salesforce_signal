# Phase 0 exit gate (E0) — Research and environment

- **Status:** Open
- **Prerequisite ADRs:** ADR-001 to ADR-005, all "Accepted by Davis"

## Progress

### Research gates (agent drafts, Davis decides)

| Gate | ADR | Status |
| --- | --- | --- |
| R0.1 Jev access | [ADR-001](../decisions/ADR-001-jev-access.md) | Proposed: Vercel AI Gateway now, join TypeSafe waitlist in parallel |
| R0.2 Event ingestion into Salesforce | [ADR-002](../decisions/ADR-002-salesforce-ingestion.md) | Proposed: Platform Events over REST; Data 360 Ingestion for Phase 5 only |
| R0.3 Email and engagement | [ADR-003](../decisions/ADR-003-email-and-engagement.md) | Proposed: Mailpit + Resend free tier; simulated and webhook engagement, labeled separately |
| R0.4 Hosting | [ADR-004](../decisions/ADR-004-hosting.md) | Proposed: ngrok free plan, bridge only |
| R0.5 Dashboard | [ADR-005](../decisions/ADR-005-dashboard.md) | Proposed: static page on GitHub Pages |

### DevOps (Davis)

| Step | Runbook | Status |
| --- | --- | --- |
| D0.0 Local tooling (make, sf, Docker, venv) | [D0.0](../runbooks/D0.0-local-tooling.md) | ☐ |
| D0.1 Salesforce Developer Edition + `sf` auth | [D0.1](../runbooks/D0.1-salesforce-org.md) | ☐ |
| D0.2 GitHub branch protection + secrets | [D0.2](../runbooks/D0.2-github.md) | ☐ |
| D0.3 Jev access + spend cap | [D0.3](../runbooks/D0.3-jev-access.md) (waits on ADR-001) | ☐ |
| D0.4 Email accounts + hosting/tunnel | [D0.4](../runbooks/D0.4-email-and-hosting.md) (waits on ADR-003/004) | ☐ |

### Build (agent)

| Item | Status |
| --- | --- |
| Repo scaffold per plan layout | Done |
| Makefile (`test`, `lint`, `smoke-*`) | Done |
| ruff, pytest, pre-commit (with gitleaks) | Done |
| CI workflow with gitleaks secret scan | Done (runs on first push) |
| `.env.example` | Done |
| ADR and gate-file templates | Done |
| Smoke scripts | `smoke-sf` ready; `smoke-mail` Mailpit half ready, service half waits on ADR-003; `smoke-jev` harness ready on mock, Jev adapter waits on ADR-001 |

## Tests

| ID | Label | Test | Pass condition | Result | Evidence |
| --- | --- | --- | --- | --- | --- |
| T0.1 | AUTO | CI on a fresh push | Lint, test suite and secret scan all green | ☐ pass ☐ fail | |
| T0.2 | AUTO-LIVE | `make smoke-jev` with `DECISION_PROVIDER=jev` | A canned session returns a typed Choice with only declared labels and probabilities summing to 1 (±0.001) | ☐ pass ☐ fail | |
| T0.3 | AUTO-LIVE | `make smoke-sf` | Authenticates to the org and returns the org limits payload | ☐ pass ☐ fail | |
| T0.4 | AUTO-LIVE | `make smoke-mail` | A test message arrives in Mailpit, and the chosen service returns a success response | ☐ pass ☐ fail | |
| T0.5 | HITL | ADR review | Davis marks ADR-001 to ADR-005 "Accepted" | ☐ pass ☐ fail | |
| T0.6 | HITL | Limits worksheet | Davis confirms the recorded Developer Edition limits match what the org's Setup shows | ☐ pass ☐ fail | [limits worksheet](../limits-worksheet.md) |

## HITL checklists

### T0.5 — ADR review

- [ ] ADR-001 read; decision recorded
- [ ] ADR-002 read; decision recorded
- [ ] ADR-003 read; decision recorded (including where open/click events come from)
- [ ] ADR-004 read; decision recorded
- [ ] ADR-005 read; decision recorded
- **Expected:** each ADR's Status reads "Accepted by Davis (date)".

### T0.6 — Limits worksheet

- [ ] Run `make smoke-sf`; open the newest `reports/T0.3-smoke-sf-*.json`
- [ ] In the org, open Setup → Company Information (and Data 360 / Einstein setup pages) and compare
- [ ] Fill the "Org shows" column in `docs/limits-worksheet.md`
- **Expected:** every row matches, or differences are noted and the affected ADR updated.

## Open decisions from the plan (before Phase 0 closes)

- [ ] Keep "Ridgeline Outfitters" as the fictional brand?
- [ ] Monthly spend cap for paid API calls: $____
- [ ] Agent tool for the build and how it reports at gates (proposed: Claude Code, reporting through this gate file plus a summary in chat)

## Sign-off

- Signed by Davis on:
- Phase 1 may start: ☐ yes
