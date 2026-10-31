# Phase 0 exit gate (E0) — Research and environment

- **Status:** Open
- **Prerequisite ADRs:** ADR-001 to ADR-005, all "Accepted by Davis"

## Progress

### Research gates (agent drafts, Davis decides)

| Gate | ADR | Status |
| --- | --- | --- |
| R0.1 Jev access | [ADR-001](../decisions/ADR-001-jev-access.md) | Accepted: TypeSafe direct API (Davis already has a key) |
| R0.2 Event ingestion into Salesforce | [ADR-002](../decisions/ADR-002-salesforce-ingestion.md) | Accepted: Platform Events over REST |
| R0.3 Email and engagement | [ADR-003](../decisions/ADR-003-email-and-engagement.md) | Accepted: Mailpit only; engagement simulated by the generator |
| R0.4 Hosting | [ADR-004](../decisions/ADR-004-hosting.md) | Accepted: ngrok free plan, bridge only, run locally on demand |
| R0.5 Dashboard | [ADR-005](../decisions/ADR-005-dashboard.md) | Accepted: static page (GitHub Pages) and Streamlit, neither needs to be always live |

### DevOps (Davis)

| Step | Runbook | Status |
| --- | --- | --- |
| D0.0 Local tooling (make, sf, Docker, venv) | [D0.0](../runbooks/D0.0-local-tooling.md) | ☐ |
| D0.1 Salesforce Developer Edition + `sf` auth | [D0.1](../runbooks/D0.1-salesforce-org.md) | ☐ |
| D0.2 GitHub branch protection + secrets | [D0.2](../runbooks/D0.2-github.md) | ☐ |
| D0.3 Jev key in `.env` + spend cap | [D0.3](../runbooks/D0.3-jev-access.md) | ☐ (key exists; spend cap to set) |
| D0.4 Mailpit running + ngrok account | [D0.4](../runbooks/D0.4-email-and-hosting.md) | ☐ |

### Build (agent)

| Item | Status |
| --- | --- |
| Repo scaffold per plan layout | Done |
| Makefile (`test`, `lint`, `smoke-*`) | Done |
| ruff, pytest, pre-commit (with gitleaks) | Done |
| CI workflow with gitleaks secret scan | Done (green on `main`) |
| `.env.example` | Done |
| ADR and gate-file templates | Done |
| Smoke scripts | All three ready: `smoke-jev` (TypeSafe direct), `smoke-sf`, `smoke-mail` (Mailpit only) |

## Tests

| ID | Label | Test | Pass condition | Result | Evidence |
| --- | --- | --- | --- | --- | --- |
| T0.1 | AUTO | CI on a fresh push | Lint, test suite and secret scan all green | ☑ pass ☐ fail | [CI run](https://github.com/DavisHochs/salesforce_signal/actions/runs/41220621569) |
| T0.2 | AUTO-LIVE | `make smoke-jev` with `DECISION_PROVIDER=jev` | A canned session returns a typed Choice with only declared labels and probabilities summing to 1 (±0.001) | ☐ pass ☐ fail | |
| T0.3 | AUTO-LIVE | `make smoke-sf` | Authenticates to the org and returns the org limits payload | ☐ pass ☐ fail | |
| T0.4 | AUTO-LIVE | `make smoke-mail` | A test message arrives in Mailpit (email-service half dropped per ADR-003: Mailpit only) | ☐ pass ☐ fail | |
| T0.5 | HITL | ADR review | Davis marks ADR-001 to ADR-005 "Accepted" | ☑ pass ☐ fail | Decisions recorded 2026-10-31 |
| T0.6 | HITL | Limits worksheet | Davis confirms the recorded Developer Edition limits match what the org's Setup shows | ☐ pass ☐ fail | [limits worksheet](../limits-worksheet.md) |

## HITL checklists

### T0.5 — ADR review

- [x] ADR-001 read; decision recorded (Option A, TypeSafe direct)
- [x] ADR-002 read; decision recorded (Option A, REST)
- [x] ADR-003 read; decision recorded (Option A only; engagement is simulated)
- [x] ADR-004 read; decision recorded (Option A, ngrok)
- [x] ADR-005 read; decision recorded (Options A and B)
- **Expected:** each ADR's Status reads "Accepted by Davis (date)".

### T0.6 — Limits worksheet

- [ ] Run `make smoke-sf`; open the newest `reports/T0.3-smoke-sf-*.json`
- [ ] In the org, open Setup → Company Information (and Data 360 / Einstein setup pages) and compare
- [ ] Fill the "Org shows" column in `docs/limits-worksheet.md`
- **Expected:** every row matches, or differences are noted and the affected ADR updated.

## Standing guidance from Davis (2026-10-31)

At every decision point, pick the lowest-friction option, even if email never really goes out,
the dashboard isn't permanently reachable, or throughput is lower. The goal is to build this end
to end with AI while learning Salesforce architecture. Portfolio display can be a diagram and a
recorded demo.

## Open decisions from the plan (before Phase 0 closes)

- [ ] Keep "Ridgeline Outfitters" as the fictional brand?
- [ ] Monthly spend cap for paid API calls: $____
- [ ] Agent tool for the build and how it reports at gates (proposed: Claude Code, reporting through this gate file plus a summary in chat)

## Sign-off

- Signed by Davis on:
- Phase 1 may start: ☐ yes
