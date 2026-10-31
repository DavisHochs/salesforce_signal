# ADR-002: How events get into Salesforce, and the Developer Edition limits that apply

- **Gate:** R0.2
- **Status:** Proposed
- **Author:** build agent
- **Date drafted:** 2026-10-31
- **Blocks:** Phase 4 publisher, `Cart_Signal__e` design, T0.6 limits worksheet

## Question

How does the triage service send a "trigger" decision into Salesforce: Platform Events over REST,
Platform Events over the Pub/Sub API, or the Data 360 Ingestion API? Which Developer Edition
limits shape the design?

## Context

- Only sessions routed to "trigger" reach Salesforce. A replay of 10,000 sessions might produce a
  few hundred to a few thousand triggers. T4.4 replays 200 sessions.
- The journey (gate chain) runs in a platform-event-triggered Flow or Apex trigger (R4.2), so the
  event has to land on the event bus within seconds.
- Data 360 is needed in Phase 5 for profiles and engagement, not for the trigger itself.

## Developer Edition limits (vendor-reported, from Salesforce docs)

| Limit | Developer Edition | Notes |
| --- | --- | --- |
| Platform event publishing | **50,000 per hour** | Counts every method: Apex, Pub/Sub, REST, SOAP, Bulk, Flow. Rolling hour. Over the limit, publish fails with `LIMIT_EXCEEDED` and the event is not queued. |
| Platform event delivery | **10,000 per 24 hours** | Counts only API subscribers (Pub/Sub, CometD, empApi, event relays). **Flows and Apex triggers don't count.** |
| API requests | **15,000 per 24 hours** | Rolling 24 hours. REST, SOAP and Bulk **publishes use this**. Pub/Sub API, Apex and Flow publishes don't. |
| Concurrent long-running API requests (≥20 s) | 5 | — |
| Apex callout timeout | 10 s default, 120 s max per transaction | Matters for the bridge (ADR-004). |
| Data 360 data spaces | 1 | Developer Edition launch post (March 2025) |
| Data 360 storage | 10 GB | Same |
| LLM outputs (Agentforce / Prompt Builder) | 150 per hour | Same |
| Data 360 Ingestion API (streaming) | 200 KB per request; 250 requests per second across endpoints; processed asynchronously (one docs version says about every 3 minutes); about 30 s before data can be queried | — |
| Org lifetime | Doesn't expire if you log in regularly (one third-party source says at least every 45 days) | — |

T0.6 checks these figures against the real org. `make smoke-sf` already captures
`HourlyPublishedPlatformEvents`, `DailyDeliveredPlatformEvents` and `DailyApiRequests`.

## Alternatives

### A. Platform Events over REST (recommended for Phase 4)

- **How it works:** `POST /services/data/vXX.X/sobjects/Cart_Signal__e/` with JSON. One HTTP
  call publishes one event.
- **Pros:**
  - Plain HTTPS and JSON from Python with `httpx`; no extra libraries.
  - Easy to mock in AUTO tests.
  - The response returns the event's ID (or errors) right away.
  - Fires the Flow or Apex trigger within seconds.
- **Cons:** each publish uses one of the 15,000 daily API requests.
- **Budget:** at the planned volumes (hundreds to low thousands of triggers a day) that's under
  20% of the allowance. A 10,000-trigger stress test would use most of it.
- **Setup effort:** low.
  - **Local runs:** reuse the `sf` CLI session (`sf org display --json` returns an access token
    and instance URL), so there's no new credential.
  - **Hosted runs:** need an OAuth client credentials flow on an External Client App (a DevOps
    step in Phase 4).

### B. Platform Events over the Pub/Sub API

- **How it works:** gRPC `Publish` / `PublishStream` with Avro-encoded payloads. The official
  repo has Python examples.
- **Pros:**
  - **Doesn't use daily API requests.**
  - Handles high volume, and up to 200 events per publish call is recommended.
  - The same API lets us subscribe later (for example, in a Phase 6 dead-letter or monitoring
    view).
- **Cons:**
  - gRPC plus Avro schema handling adds `grpcio` and `avro` dependencies and generated stubs.
  - Harder to mock.
  - More moving parts for a portfolio reader to follow.
- **Setup effort:** medium.

### C. Data 360 Ingestion API

- **How it works:** a streaming endpoint takes JSON records into a Data 360 data stream.
  Processing is asynchronous and batched.
- **Pros:** this is the right path for profile and engagement data in Phase 5 (unified profile,
  calculated insights).
- **Cons:**
  - Asynchronous, with minutes of latency, so it can't drive a real-time trigger.
  - Firing a journey would need Data 360 data actions on top.
  - Counts against Data 360 limits in a single-data-space org.
- **Setup effort:** high (data streams, schema upload, connected app).

## Trade-offs

| Criterion | A. REST events | B. Pub/Sub API | C. Data 360 Ingestion |
| --- | --- | --- | --- |
| Time to Flow/Apex trigger | Seconds | Seconds | Minutes (async) |
| Uses daily API requests | Yes (1 per event) | No | Own limits |
| Python effort | Low (`httpx`) | Medium (gRPC + Avro) | Medium |
| Easy to mock for AUTO tests | Yes | Harder | Yes |
| Fit with plan | Phase 4 trigger | Phase 4 upgrade | Phase 5 profile data |

## Recommendation

- **Phase 4 trigger path:** use **A (REST)**, behind a `SignalPublisher` interface with a mock,
  so **B (Pub/Sub API)** can be swapped in if API requests ever get tight. Log the
  `Sforce-Limit-Info` response header on each publish so usage is visible.
- **Phase 5:** use **C (Data 360 Ingestion API)** for profile, engagement and decision data only,
  never for the trigger.
- **Volumes:** keep replays at 1,000 sessions or fewer per run.

## Open questions

1. When we go hosted, is a client-credentials External Client App acceptable for
   server-to-server auth? This is Davis's DevOps call (D4.x).
2. Confirm that the org shows 50,000 / 10,000 / 15,000 in Setup (T0.6). Some older docs versions
   list 25,000 per hour for publishing.

## Sources

- [Salesforce: Default Platform Event Allocations for Event Publishing and Delivery](https://developer.salesforce.com/docs/platform/platform-events/guide/platform-events-limits-default.html) (accessed 2026-10-31)
- [Salesforce: API Request Limits and Allocations](https://developer.salesforce.com/docs/platform/salesforce-app-limits-cheatsheet/guide/salesforce-app-limits-platform-api.html) (accessed 2026-10-31)
- [Salesforce: Publish events with Pub/Sub API](https://developer.salesforce.com/docs/atlas.en-us.264.0.platform_events.meta/platform_events/platform_events_publish_pubsub_api.htm) and [Pub/Sub API GitHub repo](https://github.com/forcedotcom/pub-sub-api) (accessed 2026-10-31)
- [Salesforce: Get Started with Ingestion API (Data 360)](https://developer.salesforce.com/docs/data/data-cloud-int/references/data-cloud-ingestionapi-ref/c360-a-api-get-started.html) and [v248 version, ~3-minute processing](https://developer.salesforce.com/docs/atlas.en-us.248.0.c360a_api.meta/c360a_api/c360a_api_get_started.htm) (accessed 2026-10-31)
- [Salesforce: Apex callout limits and timeouts](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_callouts_timeouts.htm) (accessed 2026-10-31)
- [Salesforce blog: New Developer Edition with Agentforce and Data Cloud](https://developer.salesforce.com/blogs/2025/03/introducing-the-new-salesforce-developer-edition-now-with-agentforce-and-data-cloud) (March 2025)
- [Salesforce blog: Developer Edition updates, April 2026](https://developer.salesforce.com/blogs/2026/04/new-developer-edition-agentforce-vibes-claude-mcp) (April 2026)
- [Apex Hours: Free Agentforce and Data Cloud developer org](https://apexhours.com/free-agentforce-and-data-cloud-developer-org) (2025-03-05; 150 LLM outputs per hour, 1 data space, 10 GB)

## Decision

<!-- Filled in by Davis. -->
- Decision:
- Accepted by Davis on:
- Notes:
