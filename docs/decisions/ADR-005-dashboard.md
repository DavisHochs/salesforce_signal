# ADR-005: Dashboard tool

- **Gate:** R0.5
- **Status:** Accepted by Davis (2026-10-31)
- **Author:** build agent
- **Date drafted:** 2026-10-31
- **Blocks:** Phase 6 dashboard, R6.2 portfolio format

## Question

Should the dashboard be built in Streamlit, as a static page, or with Salesforce reports?
The criterion: **easy to show on a portfolio site.**

## Context

- **Contents (Phase 6):** the funnel (events → triaged → routes → sent → engaged), the provider
  comparison (macro-F1, ECE, latency, cost), the reliability diagram and suppression reasons.
- **Data sources:** every number comes from files the pipeline already writes: the DuckDB
  decision log, delivery-log exports and `reports/*.json`.
- **T6.3:** dashboard totals must equal the log counts.
- **Audience:** portfolio visitors won't have a Salesforce login, and live services (Jev,
  Salesforce, tunnel) won't be running when they visit.

## Alternatives

### A. Static page (recommended)

- **How it works:** a Python build step reads the logs and reports and writes one HTML page with
  embedded charts (Plotly or Vega-Lite JSON). It's published with GitHub Pages from the repo.
- **Pros:**
  - Always up, with no cold start, no secrets and no running services.
  - Loads instantly on a portfolio link.
  - Each build is a frozen, versioned snapshot of a run, so T6.3 can check the same numbers the
    page shows.
  - `make demo` can rebuild and open it locally.
- **Cons:**
  - Not interactive beyond chart hovers and filters.
  - Rebuilt per run, not live.
- **Cost:** $0.
- **Setup effort:** low to medium.

### B. Streamlit

- **How it works:** a Python app reads the same files. It can be hosted free on Streamlit
  Community Cloud.
- **Pros:** fastest way to build interactive views in Python.
- **Cons:**
  - Community Cloud apps sleep after about 12 hours without traffic and show a wake-up screen.
    That's a poor first impression from a portfolio link.
  - About 1 GB of memory and no custom domain (third-party reports).
  - The data must be committed or fetched anyway.
- **Cost:** $0.
- **Setup effort:** low.

### C. Salesforce reports and dashboards

- **How it works:** native reports on `Delivery_Log__c` and `Engagement__c`.
- **Pros:** shows Salesforce skill directly, and is real-time inside the org.
- **Cons:**
  - Visitors can't open it, so only screenshots work.
  - It can't show provider metrics (ECE, latency) that live outside the org.
- **Cost:** $0.
- **Setup effort:** low.

## Trade-offs

| Criterion | A. Static page | B. Streamlit | C. Salesforce reports |
| --- | --- | --- | --- |
| Visitor opens a link and sees it instantly | Yes | Not after idle (wake-up screen) | No (login needed) |
| Shows provider metrics and the reliability diagram | Yes | Yes | No |
| Reconciles to logs (T6.3) | Yes, built from them | Yes | Partly |
| Interactivity | Basic | Rich | Rich, in the org |
| Running cost and services | None | None (sleeps) | None |

## Recommendation

- **A. A static page** built from the run outputs and published with GitHub Pages. It's the
  portfolio link.
- **C.** Add **a few Salesforce report screenshots** in the write-up to show the org side.
- **B (Streamlit)** stays an optional local exploration tool if it's useful during development.
  It isn't a deliverable.

## Open questions

1. Is GitHub Pages on this repo acceptable for the portfolio, or does the portfolio site host the
   page itself? (Decided at R6.2.)
2. Which chart library: Plotly (heavier, familiar) or Vega-Lite (lighter)? This can wait for
   Phase 6.

## Sources

- [Streamlit forum: Community Cloud sleep threshold (12 hours)](https://discuss.streamlit.io/t/web-apps-keeps-on-sleeping-after-30-minutes-or-a-day-of-inactivity/97350) (accessed 2026-10-31)
- [livemy.app: Deploying Streamlit in 2026](https://livemy.app/blog/deploy-streamlit-app) (accessed 2026-10-31; resource limits, third-party)
- [GitHub Pages documentation](https://docs.github.com/en/pages) (accessed 2026-10-31)

## Decision

<!-- Filled in by Davis. -->
- Decision: Option A and B
- Accepted by Davis on: 10/31/2026
- Notes: Github pages is fine, streamlit is good too, less worried about it needing to be always live again. I want the core to be usable I can always just record a demo video of what is happening for the portfolio if needed
