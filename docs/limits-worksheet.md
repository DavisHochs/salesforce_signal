# Developer Edition limits worksheet (T0.6)

Limits that shape the design. "Plan / ADR says" comes from research (R0.2 and others) and is
vendor-reported. "Org shows" is filled in by Davis from Setup or `make smoke-sf` and is
measured here.

| Limit | Plan / ADR says (vendor-reported) | Org shows (measured here) | Source in org | Match? |
| --- | --- | --- | --- | --- |
| Daily API requests | | | `DailyApiRequests` | |
| Platform events published per hour | | | `HourlyPublishedPlatformEvents` | |
| Platform events delivered per day | | | `DailyDeliveredPlatformEvents` | |
| Async Apex executions per day | | | `DailyAsyncApexExecutions` | |
| Single email per day | | | `SingleEmail` | |
| Data storage | | | `DataStorageMB` | |
| Data 360 data spaces | 1 | | Data 360 Setup | |
| Data 360 storage | 10 GB | | Data 360 Setup | |
| LLM outputs per hour (Agentforce / Prompt Builder) | 150 | | Einstein / Agentforce Setup | |

Recorded on: ____  by: ____
