# Signal to Send — Phased Build Plan

Oct 31, 2026 · @Davis

## Overview

Signal to Send is a real-time cart-recovery journey for a fictional outdoor retailer, Ridgeline Outfitters. A decision model (Jev) separates real shopping intent from noisy clickstream data before Salesforce automation fires, and an LLM writes the message copy under guardrails. The portfolio point is three kinds of reasoning working together: deterministic rules, fast calibrated decisions, and generative content.

The project runs in seven phases (0 to 6). Phases 0 to 4 are a complete portfolio piece on their own; Phases 5 and 6 are upgrades.

&#91;embedded content: system architecture · 11 components\]

Only sessions Jev routes to "trigger" reach Salesforce. There, rules gate every send, and LLM copy must pass a Jev guardrail before the sender bridge delivers it.

| Role | Owns |
| --- | --- |
| Davis (orchestrator) | Every research and tool decision at a gate, accounts and access, secrets, DevOps (repo, CI, hosting, Salesforce org config and deploys), human-in-the-loop validation, phase sign-off |
| Build agent | Research briefs for each gate, scaffolding, code, tests, runbooks, evaluation runs, documentation |

Proposed stack, confirmed or changed at Gate 0:

- **Python 3.12** for the event generator, triage service, sender bridge and evaluation harness (FastAPI, pydantic, pytest, DuckDB)
- **Salesforce Developer Edition** (free) for Platform Events, Flow, Apex, custom objects, Data 360 and Agentforce or Prompt Builder
- **Jev** (TypeSafe AI) as the decision model, reached directly or through Vercel's AI Gateway, behind a provider adapter
- **Mailpit** locally, plus an email service for real seed-inbox sends (chosen at Gate 0)
- **GitHub and GitHub Actions** for source control and CI; **Salesforce CLI** (`sf`) for metadata deploys
- **Dashboard tool** chosen at Gate 0 (Streamlit or a static page are the default candidates)

## Working agreement

The agent never crosses a gate on its own: every phase ends at an exit gate Davis signs, and every tool or approach choice passes a research gate first.

### Gate types

| Gate | Who acts | What it requires |
| --- | --- | --- |
| **R** (research and decision) | Agent researches, Davis decides | A decision brief at `docs/decisions/ADR-<nn>.md`: the question, at least two alternatives, trade-offs, a recommendation, dated sources, open questions. Work that depends on it waits until the ADR reads "Accepted by Davis". |
| **D** (DevOps) | Davis | Accounts, credentials, org setup, deploys, hosting, CI secrets. The agent writes the runbook at `docs/runbooks/` and never handles raw secrets. |
| **E** (exit) | Agent runs, Davis signs | All AUTO tests green in CI, AUTO-LIVE tests run and attached, HITL checklist completed, recorded in `docs/gates/phase-<n>.md`. |

### Test labels

| Label | Meaning |
| --- | --- |
| **AUTO** | Deterministic, runs in CI on every push, uses mocks for external services, costs nothing |
| **AUTO-LIVE** | Scripted and self-checking, but hits a live service (Jev, Salesforce, email) or costs money. Davis triggers it with a `make` target; results saved to `reports/`. |
| **HITL** | Needs human judgment or a manual action. Each has a written checklist and an expected result; Davis records pass or fail in the gate file. |

### Rules for the agent

1. Stop at every R and E gate and say what is needed from Davis. Do not start the next phase until its gate file is signed.
2. If research shows a planned tool is unavailable or unsuitable, stop and raise it in an ADR. Never substitute silently.
3. Put every external service (Jev, LLMs, Salesforce publish, email) behind an interface with a mock, so AUTO tests never call live services.
4. No secrets in the repo: `.env.example` only, plus a secret scan in CI.
5. Synthetic data only. No real personal data, and no employer or client names, schemas or code.
6. Fixed random seeds everywhere, so every run is reproducible.
7. Keep `docs/parallels.md` current: each component's Adobe Campaign Classic equivalent, for interview talking points.
8. Label every vendor figure in docs as "vendor-reported" or "measured here".

### Repo layout

```
generator/        synthetic events + ground-truth labels
triage/           decision service, providers, routing policy
eval/             evaluation harness and reports
salesforce/       sfdx project (objects, events, flows, apex)
bridge/           sender bridge (Salesforce -> email service)
dashboard/
docs/decisions/   ADRs (R gates)
docs/runbooks/    DevOps steps (D gates)
docs/gates/       phase sign-offs (E gates)
```

## Phase 0 — Research and environment

**Goal:** prove every tool is reachable and settle the stack before any feature work.

### Research gates

- [ ] **R0.1 Jev access.** TypeSafe direct early access vs. Vercel AI Gateway. Document the API shape (the Choice, Score and probability primitives), SDKs, rate limits, pricing, latency, and terms. List fallback decision models (rival decision models on the gateway; a general LLM with structured output). Recommend an adapter contract.
- [ ] **R0.2 Event ingestion into Salesforce.** Platform Events over REST vs. Pub/Sub API vs. the Data 360 Ingestion API. Record Developer Edition limits that apply: event publishing and delivery, API calls, Data 360 (1 data space, 10 GB), and 150 LLM outputs per hour.
- [ ] **R0.3 Email and engagement.** Mailpit vs. a free email service tier vs. Salesforce native email. Answer one question explicitly: where do open and click events come from? Options are real webhooks from seed-inbox sends, or simulated engagement from the generator.
- [ ] **R0.4 Hosting.** How Salesforce reaches the sender bridge and triage service: a local tunnel (ngrok, Cloudflare Tunnel) vs. a small host (Render, Fly.io, Vercel functions). Include cost and setup effort.
- [ ] **R0.5 Dashboard.** Streamlit vs. a static page vs. Salesforce reports. Criterion: easy to show on a portfolio site.

### DevOps (Davis)

- [ ] **D0.1** Sign up for a Salesforce Developer Edition org; assign Data 360 and Agentforce permission sets; install `sf` and authorize the org.
- [ ] **D0.2** Create the GitHub repo, branch protection, and Actions secrets.
- [ ] **D0.3** Get Jev access and an API key per ADR from R0.1; set a spend cap and alerts.
- [ ] **D0.4** Create email service accounts per ADR from R0.3; set up hosting or a tunnel per R0.4.

### Build (agent)

Repo scaffold per the layout above; `Makefile` with `test`, `lint`, `smoke-*` targets; ruff, pytest, pre-commit; a CI workflow with a secret scan (gitleaks); `.env.example`; ADR and gate-file templates; smoke scripts for each live service.

### Exit gate E0

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T0.1 | AUTO | CI on a fresh push | Lint, empty test suite and secret scan all green |
| T0.2 | AUTO-LIVE | `make smoke-jev` | A canned session returns a typed Choice with only declared labels and probabilities summing to 1 (±0.001) |
| T0.3 | AUTO-LIVE | `make smoke-sf` | Authenticates to the org and returns the org limits payload |
| T0.4 | AUTO-LIVE | `make smoke-mail` | A test message arrives in Mailpit, and the chosen service returns a success response |
| T0.5 | HITL | ADR review | Davis marks ADR-001 to ADR-005 "Accepted" |
| T0.6 | HITL | Limits worksheet | Davis confirms the recorded Developer Edition limits match what the org's Setup shows |

## Phase 1 — Noisy event generator

**Goal:** a reproducible Ridgeline Outfitters clickstream with known ground truth, noisy enough that simple rules cannot solve it.

### Research gates

- [ ] **R1.1 Event schema.** Compare common analytics specs (Segment, GA4 ecommerce, Snowplow) and recommend one to follow loosely.
- [ ] **R1.2 Noise taxonomy.** Realistic forms and rates of bot traffic, duplicate events, accidental add-to-carts, internal or test traffic, tab-thrashing and clock skew, with sources. Davis sets the final rates in config.

### Build (agent)

- Customer generator: profiles, consent flags, channel preferences, purchase history.
- Session simulator: shopper personas mapped to the intent camps (browser, researcher, price watcher, ready to buy).
- Noise injectors, one per noise type, each toggled and rated in `generator/config.yaml` with a seed.
- Ground-truth labels written to a separate file (session type, camp, recovery-worthy), never inside the events.
- Output to JSONL and Parquet; a replay mode that streams events to an HTTP endpoint at a set rate.
- A data card (`docs/data-card.md`): what is generated, how, and its known limits.

### Exit gate E1

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T1.1 | AUTO | Reproducibility | Same seed and config produce byte-identical output (matching hash) |
| T1.2 | AUTO | Schema validation | 100% of events validate against the pydantic models |
| T1.3 | AUTO | Noise rates | For a 10,000-session run, each injected noise rate is within ±2 points of config |
| T1.4 | AUTO | Label integrity | Labels join 1:1 to sessions; no label field or value appears in any event payload |
| T1.5 | AUTO | Replay rate | Replay to a mock endpoint holds the configured events per second within ±10% |
| T1.6 | HITL | Realism review | Davis reviews 20 sampled sessions rendered as timelines and confirms each noise type looks plausible and genuine shoppers vary |

**Deliverable:** dataset v1, frozen and tagged, plus the data card.

## Phase 2 — Rules baseline and evaluation harness

**Goal:** a measured yardstick before any AI is involved, so every later claim is a comparison.

### Research gates

- [ ] **R2.1 Metrics.** Recommend a metric set for calibrated classifiers: accuracy, macro-F1, Brier score, expected calibration error (ECE), reliability diagrams, plus how to measure p50/p95 latency and cost per 1,000 sessions.
- [ ] **R2.2 Data splits.** Train/dev/test split strategy. The test split is touched only for final reported numbers; thresholds are tuned on dev.

### Build (agent)

- Rules classifier using heuristics a marketing ops team would write: event cadence, user agent, internal domains and IPs, dwell time, cart edits.
- Evaluation harness: takes a predictions file (label, probability per label, latency, cost) and writes a JSON report, a markdown summary and a reliability plot to `reports/`.
- A `make eval PROVIDER=<name> SPLIT=<split>` target used by every later phase.

### Exit gate E2

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T2.1 | AUTO | Metric correctness | Harness output on toy fixtures matches hand-computed F1, Brier and ECE to 1e-6 |
| T2.2 | AUTO | Baseline coverage | Rules baseline scores 100% of test-split sessions and a report is written |
| T2.3 | AUTO | Input validation | Harness rejects unknown labels and probability sets that don't sum to 1 (±0.001) |
| T2.4 | HITL | Targets | Davis reads the baseline report and writes the Phase 3 success targets (e.g. minimum macro-F1 gain, maximum ECE, latency and cost ceilings) into the gate file |
| T2.5 | HITL | Error review | Davis inspects 10 baseline misclassifications and confirms they are genuinely ambiguous, not generator bugs |

## Phase 3 — Jev triage service

**Goal:** every session gets typed decisions with calibrated confidence, and plain code routes it to trigger, nurture or drop.

### Research gates

- [ ] **R3.1 Question design.** Decompose triage into atomic questions per TypeSafe's guidance: session type (Choice), intent camp (Choice), recovery worthiness (Score). Decide what state to send (compact session summary vs. raw events), and per-session vs. batched calls. Give at least two designs with cost and latency estimates.
- [ ] **R3.2 Comparison set.** Pick at most two alternatives to benchmark against Jev (for example a rival decision model on the gateway and a general LLM with structured output). Davis chooses.

### DevOps (Davis)

- [ ] **D3.1** Provision keys for the chosen providers; confirm spend caps before any AUTO-LIVE run.

### Build (agent)

- `DecisionProvider` interface with `choice()`, `score()` and a probability call; implementations for Jev, the chosen alternatives, rules and a mock.
- State builder that turns a session into the compact state agreed in R3.1.
- Triage service (FastAPI): `POST /sessions/triage` returns the decisions plus a route.
- Routing policy as code and config: thresholds tuned on the dev split decide trigger, nurture or drop.
- Decision log in DuckDB: provider, probabilities, route, latency, cost.
- Idempotency on session ID; timeout with fallback to the rules provider, logged with a reason.

### Exit gate E3

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T3.1 | AUTO | Provider contract | Every provider (mocked) returns only declared labels and valid probabilities |
| T3.2 | AUTO | Routing table | Table-driven cases, including exact threshold boundaries, give the expected route |
| T3.3 | AUTO | Fallback | A provider timeout falls back to rules, logs the reason, and the endpoint still answers within the agreed timeout |
| T3.4 | AUTO | Idempotency | Posting the same session twice yields one decision record |
| T3.5 | AUTO-LIVE | Benchmark | `make eval` on the test split for Jev and each alternative; report has macro-F1, ECE, p50/p95 latency, cost per 1,000 sessions. Passes if Jev or the chosen provider meets the T2.4 targets. |
| T3.6 | HITL | Threshold sign-off | Davis reviews the reliability diagram and 15 low-confidence sessions and approves the thresholds |
| T3.7 | HITL | Vendor claims | Davis writes a short note on whether TypeSafe's speed and cost claims held up on this task |

## Phase 4 — Salesforce journey core

**Goal:** a "trigger" decision becomes a delivered, logged message only after consent, suppression, frequency and purchase checks pass.

### Research gates

- [ ] **R4.1 Data model.** Standard consent objects (Individual, Contact Point Consent) vs. custom fields; custom objects for the delivery log, suppression and engagement.
- [ ] **R4.2 Orchestration.** Platform-event-triggered Flow vs. Apex for the gate chain; how to do the wait-then-cancel-if-purchased step; how to test platform-event paths (Flow tests vs. Apex tests that publish events).
- [ ] **R4.3 Callouts.** Named and External Credentials to the sender bridge; bulkification and governor-limit practices.

### DevOps (Davis)

- [ ] **D4.1** Deploy metadata with `sf project deploy`; assign permission sets.
- [ ] **D4.2** Configure Named and External Credentials; run the bridge on the R0.4 host or tunnel.
- [ ] **D4.3** Load seed contacts that match the generator's customers.

### Build (agent)

- Platform Event `Cart_Signal__e`: session ID, contact external ID, cart value, camp, confidence, idempotency key.
- Objects: `Delivery_Log__c` (the broadLog equivalent, with status and reason), `Suppression__c`, `Engagement__c`; consent per R4.1.
- Gate chain: dedupe → consent → suppression → frequency cap → quiet hours → wait → purchase check → send. Cap, wait and quiet hours live in Custom Metadata, not code.
- Apex invocable action that calls the sender bridge; Apex test classes for every path.
- Sender bridge service: send request in, email out via Mailpit or the chosen service, message ID back.
- Publisher in the triage service: routes marked "trigger" publish to Salesforce via the R0.2 method.

### Exit gate E4

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T4.1 | AUTO | Apex tests | `sf apex run test` passes with at least 85% coverage of custom Apex |
| T4.2 | AUTO | Gate paths | One test per gate: each blocked case writes a delivery log with the right reason (e.g. "Suppressed: consent") and sends nothing |
| T4.3 | AUTO | Idempotency | The same event published twice produces one delivery log |
| T4.4 | AUTO-LIVE | End to end | Replay 200 sessions through triage, Salesforce, bridge and Mailpit. A script checks counts reconcile: trigger routes = delivery logs (sent + each suppression reason), and Mailpit messages = sent logs. |
| T4.5 | AUTO-LIVE | Purchase cancel | A purchase inside the wait window cancels the journey; no message sent |
| T4.6 | HITL | Message review | Davis opens 5 delivered emails and confirms rendering and merge fields; checks the matching delivery logs in the org |
| T4.7 | HITL | Limits headroom | Davis records org limit usage after T4.4 and confirms headroom for the demo |

## Phase 5 — Data 360, AI copy and the Jev guardrail

**Goal:** messages are personalized from a unified profile, written by an LLM, and blocked by a Jev guardrail when they break brand or compliance rules.

### Research gates

- [ ] **R5.1 Data 360 in Developer Edition.** Ingestion options, identity resolution rulesets, calculated insights, and how Flow or Apex reads them. Confirm what the free org actually allows.
- [ ] **R5.2 Generation path.** Prompt Builder template vs. an Agentforce action vs. an external LLM; grounding approach; a design that respects the 150 LLM outputs per hour cap (queueing, caching, fallback).
- [ ] **R5.3 Guardrail design.** A scoring rubric for Jev: on-brand tone, no invented prices or discounts, no false urgency, product matches the cart. Legal elements (unsubscribe, address) live in the fixed template, never in generated text. Davis approves the rubric and threshold.

### DevOps (Davis)

- [ ] **D5.1** Complete Data 360 setup: data streams, identity resolution, calculated insights.
- [ ] **D5.2** Enable and configure Prompt Builder or Agentforce per R5.2.

### Build (agent)

- Stream engagement events and triage decisions into Data 360; resolve web sessions to contacts.
- Calculated insights: cart value, days since last purchase, current camp.
- Prompt template grounded on those fields plus the camp.
- Guardrail step: deterministic checks first (links, merge fields), then a Jev Score against the rubric.
- Static fallback template per camp; a queue that respects the hourly cap.
- Delivery log records the content outcome: generated, fallback, or blocked.
- A 40-item guardrail eval set: 20 compliant and 20 violating messages, written by the agent and approved by Davis.

### Exit gate E5

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T5.1 | AUTO | Deterministic checks | Broken links and unresolved merge fields are caught in 100% of eval-set cases |
| T5.2 | AUTO | Quota fallback | With the LLM quota mocked as exhausted, the fallback template sends and the outcome is logged |
| T5.3 | AUTO-LIVE | Guardrail accuracy | Jev guardrail on the 40-item set meets the block rate and false-block ceiling Davis set in R5.3 |
| T5.4 | AUTO-LIVE | Identity resolution | Unified profile count matches the generator's ground truth for the seeded customers |
| T5.5 | AUTO-LIVE | End to end | 100 sessions with generation on: zero messages sent without passing the guardrail; generation calls stay under the cap |
| T5.6 | HITL | Copy review | Davis reads 20 generated messages across camps, scores them on the rubric, and compares them blind against the fallback templates |
| T5.7 | HITL | Profile check | Davis confirms profiles and calculated insights look right in the Data 360 UI |

## Phase 6 — Feedback loop, dashboard and write-up

**Goal:** engagement closes the loop, the dashboard tells the story end to end, and a single command runs the demo from a clean clone.

### Research gates

- [ ] **R6.1 Engagement source.** Confirm the R0.3 choice (real webhooks, simulated engagement, or both) and how each is labeled in the write-up.
- [ ] **R6.2 Portfolio format.** What the portfolio page shows: architecture diagram, results tables, a 3-minute demo video or a live link.

### Build (agent)

- Engagement events (open, click, bounce, unsubscribe) into `Engagement__c` and Data 360; a hard bounce or unsubscribe updates suppression.
- Dead-letter queue for failed publishes and sends, with `make replay-dlq`.
- Dashboard: funnel (events → sessions → triaged → trigger/nurture/drop → sent → engaged), provider comparison (macro-F1, ECE, latency, cost), reliability diagram, suppression reasons.
- `make demo`: reset, generate, replay, and open the dashboard.
- Write-up: architecture, Adobe Campaign Classic parallels from `docs/parallels.md`, results, what held up and what didn't, lessons learned.

### Exit gate E6

| ID | Label | Test | Pass condition |
| --- | --- | --- | --- |
| T6.1 | AUTO | Bounce suppression | A hard bounce suppresses the contact, and that contact's next trigger is blocked with reason logged |
| T6.2 | AUTO | Dead-letter replay | With Salesforce mocked as unavailable, events land in the DLQ; replay delivers each exactly once |
| T6.3 | AUTO | Reconciliation | Dashboard totals equal the decision log and delivery log counts |
| T6.4 | AUTO-LIVE | Clean demo | `make demo` from a fresh clone completes within the time Davis sets |
| T6.5 | HITL | Demo rehearsal | Davis runs the 3-minute demo for someone unfamiliar with the project, who can then explain what the decision layer does |
| T6.6 | HITL | Publish check | Davis confirms the write-up contains no employer or client names, schemas or code, and every vendor figure is labeled vendor-reported or measured |

## Risks and open decisions

| Risk | Mitigation |
| --- | --- |
| Jev access is slow (it launched through an early-access waitlist) | Provider adapter from day one; Phase 3 can run on an alternative and swap in Jev later |
| Developer Edition limits (150 LLM outputs per hour, 1 data space, 10 GB) | Small replay volumes, queueing, caching, fallback templates |
| Salesforce can't reach local services | Settled at R0.4: tunnel or small host |
| No real open or click data from sandbox sends | Simulated engagement with known propensities, stated plainly in the write-up |
| Vendor benchmarks may be biased toward the vendor | Measure on our own labeled data (T3.5, T3.7) |
| Scope creep | Phases 0–4 stand alone as a finished piece; 5 and 6 are upgrades |

**Open decisions for Davis before Phase 0 starts:**

- [ ] Keep "Ridgeline Outfitters" as the fictional brand, or pick another non-hospitality brand
- [ ] Monthly spend cap for paid API calls
- [ ] Which agent tool runs the build (e.g. Claude Code) and how it reports at gates

**Definition of done:** every gate file E0–E6 signed, `make demo` works from a clean clone, and the write-up is live on the portfolio site.

## Sources

- [Introducing the new Salesforce Developer Edition, now with Agentforce and Data Cloud](https://developer.salesforce.com/blogs/2025/03/introducing-the-new-salesforce-developer-edition-now-with-agentforce-and-data-cloud)
- [Developer Edition updates, April 2026 (Data Cloud renamed Data 360)](https://developer.salesforce.com/blogs/2026/04/new-developer-edition-agentforce-vibes-claude-mcp)
- [Apex Hours: free Agentforce and Data Cloud developer org (limits)](https://apexhours.com/free-agentforce-and-data-cloud-developer-org)
- [SiliconANGLE: TypeSafe AI exits stealth with Jev](https://siliconangle.com/2026-09-16/typesafe-ai-exits-stealth-with-40m-to-build-ai-for-use-by-software/)
- [Let's Data Science: TypeSafe AI launches Jev](https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0)
- [Let's Data Science: Jev rivals and Vercel AI Gateway](https://letsdatascience.com/blog/openai-jev-rival-three-weeks-typesafe-raised-870-million)
