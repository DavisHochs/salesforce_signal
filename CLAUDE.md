# Working notes for the build agent

- The plan lives in `Phased Plans/`. Work phase by phase; stop at every R (research) and E (exit)
  gate for Davis. Gate status is tracked in `docs/gates/phase-<n>.md`.
- **Decision rule (Davis, 2026-10-31):** always recommend the lowest-friction option, even if
  email never really goes out, the dashboard isn't permanently reachable, or throughput is lower.
  The goal is to build this end to end with AI while learning Salesforce architecture. Portfolio
  display can be a diagram and a recorded demo.
- Accepted stack (ADRs 001–005): Jev via TypeSafe direct API; Platform Events over REST;
  Mailpit only, with engagement simulated by the generator; ngrok for the bridge, run on demand;
  static page + Streamlit for the dashboard.
- Every external service sits behind an interface with a mock. AUTO tests never call live services.
- No secrets in the repo; `.env` is local only. Synthetic data only. Fixed seeds.
- Run `make lint` and `make test` (or `.venv/Scripts/python -m ruff ...` / `pytest`) before every push.
