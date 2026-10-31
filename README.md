# Salesforce Signal — Signal to Send

A real-time cart-recovery journey for a fictional outdoor retailer, Ridgeline Outfitters.
A decision model separates real shopping intent from noisy clickstream data before
Salesforce automation fires, and an LLM writes message copy under guardrails.

Full plan: [`Phased Plans/`](Phased%20Plans/). Current phase: **Phase 0 — Research and
environment** ([gate file](docs/gates/phase-0.md)).

## Layout

```
generator/        synthetic events + ground-truth labels
triage/           decision service, providers, routing policy
eval/             evaluation harness and reports
salesforce/       sfdx project (objects, events, flows, apex)
bridge/           sender bridge (Salesforce -> email service)
dashboard/
scripts/smoke/    AUTO-LIVE smoke scripts
tests/            AUTO tests (run in CI, mocks only)
reports/          AUTO-LIVE run outputs
docs/decisions/   ADRs (R gates)
docs/runbooks/    DevOps steps (D gates)
docs/gates/       phase sign-offs (E gates)
```

## Quick start

Requires Python 3.12 and `make` (Windows setup: [D0.0 runbook](docs/runbooks/D0.0-local-tooling.md)).

```bash
make venv
make install
cp .env.example .env
make lint
make test
```

## Test labels

- **AUTO**: runs in CI on every push, mocks only (`make test`)
- **AUTO-LIVE**: hits a live service; run by hand (`make smoke-jev`, `make smoke-sf`, `make smoke-mail`), results go to `reports/`
- **HITL**: human checklist recorded in `docs/gates/`

All data is synthetic. No secrets in the repo: `.env.example` only, with gitleaks in pre-commit and CI.
