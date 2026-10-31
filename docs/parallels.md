# Adobe Campaign Classic parallels

Each component's closest Adobe Campaign Classic (ACC) equivalent, for interview
talking points. Updated as components are built.

| Component (this project) | Phase | ACC equivalent | Notes |
| --- | --- | --- | --- |
| Event generator + replay | 1 | External signal / incoming event (Message Center real-time events) | |
| Triage service (decision model) | 3 | Typology rules + targeting workflow filters, but with calibrated confidence | |
| Routing policy (trigger / nurture / drop) | 3 | Workflow split activity | |
| `Cart_Signal__e` platform event | 4 | Message Center event (`nms:rtEvent`) | |
| `Delivery_Log__c` | 4 | broadLog (`nms:broadLogRcp`) | Status and reason per send |
| `Suppression__c` | 4 | Quarantine + denylist (`nms:address`) | |
| Gate chain in Flow/Apex | 4 | Typology rules (pressure, control, filtering) | |
| Frequency cap (Custom Metadata) | 4 | Pressure rules | |
| Sender bridge | 4 | MTA / delivery instance | |
| `Engagement__c` | 6 | trackingLog | |
| Data 360 unified profile | 5 | Recipient schema + reconciliation | |
| LLM copy + guardrail | 5 | Content templates + approval / proofs | |
| Dashboard | 6 | Delivery and workflow reports | |
