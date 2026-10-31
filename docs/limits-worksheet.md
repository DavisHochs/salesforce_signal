# Developer Edition limits worksheet (T0.6)

Limits that shape the design. "ADR says" comes from research
([ADR-002](decisions/ADR-002-salesforce-ingestion.md)) and is vendor-reported. "Org shows" is
filled in by Davis from Setup or `make smoke-sf`, and is measured here.

| Limit | ADR says (vendor-reported) | Org shows (measured here) | Source in org | Match? |
| --- | --- | --- | --- | --- |
| Daily API requests | 15,000 / rolling 24 h | | `DailyApiRequests` | |
| Platform events published per hour | 50,000 / rolling hour (all methods) | | `HourlyPublishedPlatformEvents` | |
| Platform events delivered per day (API subscribers only) | 10,000 / rolling 24 h | | `DailyDeliveredPlatformEvents` | |
| Concurrent long-running API requests | 5 | | n/a (docs only) | |
| Single email per day | 50 recipients (older docs: 15) | | `SingleEmail` | |
| Async Apex executions per day | not researched | | `DailyAsyncApexExecutions` | |
| Data storage | not researched | | `DataStorageMB` | |
| Data 360 data spaces | 1 | | Data 360 Setup | |
| Data 360 storage | 10 GB | | Data 360 Setup | |
| LLM outputs per hour (Agentforce / Prompt Builder) | 150 | | Einstein / Agentforce Setup | |

Recorded on: ____  by: ____
