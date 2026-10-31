# ADR-003: Email delivery, and where open and click events come from

- **Gate:** R0.3
- **Status:** Proposed
- **Author:** build agent
- **Date drafted:** 2026-10-31
- **Blocks:** D0.4 (email account), T0.4 (`make smoke-mail`), the Phase 4 sender bridge,
  Phase 6 engagement (R6.1)

## Question

Which email paths do we use: Mailpit, a free email service tier, or Salesforce native email?
And, stated explicitly: **where do open and click events come from?**

## Context

- Most sends are test traffic (T4.4 sends up to 200 messages per run). Only a handful need to
  reach a real inbox to prove the message renders.
- No real people get email. Recipients are seed inboxes Davis owns.
- Phase 6 needs engagement (open, click, bounce, unsubscribe) feeding `Engagement__c` and
  suppression.

## Alternatives

### A. Mailpit only (local SMTP catcher)

- **How it works:** the bridge sends SMTP to `localhost:1025`. Messages show in a web UI, and the
  REST API can be queried (already used by `smoke-mail`).
- **Pros:** free, unlimited, instant, and works offline. Ideal for AUTO-LIVE reconciliation
  (T4.4 counts Mailpit messages).
- **Cons:** no real delivery and no real engagement events.

### B. Resend free tier (recommended for real seed-inbox sends)

- **Limits:** 3,000 emails a month, capped at 100 a day, 3 custom domains and 30 days of data
  retention.
- **Webhooks:** 1 endpoint, with events `email.sent`, `email.delivered`, `email.opened`,
  `email.clicked`, `email.bounced`, `email.complained` and `email.suppressed`.
- **Tracking:** open and click tracking is a per-domain setting available on every plan,
  including Free.
- **Pros:** simple HTTP API, and real webhooks for every engagement type the plan needs.
- **Cons:**
  - Sending to arbitrary addresses needs a verified domain (DNS records).
  - The 100-a-day cap means Resend can't take a full replay; Mailpit has to carry the bulk.
- **Cost:** $0 (vendor-reported).

### C. Postmark free developer plan

- **How it works:** 100 emails a month with no overage.
- **Pros:** strong deliverability reputation.
- **Cons:** the free tier is tiny, and we couldn't confirm it includes open/click tracking.
- **Cost:** $0.

### D. Salesforce native email (`Messaging.SingleEmailMessage` or Flow "Send Email")

- **How it works:** the org sends directly.
- **Pros:** no external service; the plan's Adobe-like "MTA inside the platform" story.
- **Cons:**
  - Developer Edition caps single email at **50 recipients a day** (older docs say 15).
  - It skips the sender bridge the plan is built around.
  - It gives no outbound webhook stream of opens and clicks that we control.
  - It's hard to reconcile automatically.

## Where do open and click events come from?

| Source | Pros | Cons |
| --- | --- | --- |
| **Real webhooks** from Resend seed sends | Proves the wiring end to end with real events | Few events (≤100 sends a day). Open tracking is unreliable: privacy proxies like Apple Mail Privacy Protection pre-fetch images and inflate opens. |
| **Simulated engagement** from the generator | Volume, known propensities per camp, reproducible with a seed, measurable against ground truth | Not real behavior, so it must be labeled "simulated" everywhere |

## Recommendation

1. **Delivery:** use **Mailpit for all test and replay traffic**, and **Resend (free tier) for a
   small set of real seed-inbox sends** (5–20 per demo), both behind one `EmailSender` interface
   chosen by config. Salesforce native email is not used.
2. **Engagement:** use **both, labeled separately.**
   - Simulated engagement from the generator is the primary data for the funnel and results
     (marked `source = "simulated"`).
   - Real Resend webhooks for the seed-inbox sends prove the integration (marked
     `source = "webhook"`).
   - The dashboard and write-up never mix the two in one number.
   - Opens are reported as an indicative metric only; clicks and bounces are the reliable ones.
3. **T0.4:** passes when Mailpit receives the message and Resend's send API returns success
   (2xx with an email ID).

## Open questions

1. Does Davis own a domain that can be verified in Resend (SPF/DKIM DNS records)? If not, the
   Resend sandbox sender may only reach the account owner's own address. That's enough for T0.4
   and seed sends to one inbox, but not for several seed inboxes.
2. Which seed inbox addresses should we use? (Davis-owned only.)
3. The webhook endpoint needs a public URL. That's covered by ADR-004.

## Sources

- [Resend pricing](https://resend.com/pricing) (accessed 2026-10-31; free tier limits, webhooks and tracking on Free)
- [Resend docs: webhook event types](https://resend.com/docs/dashboard/webhooks/event-types) (accessed 2026-10-31)
- [Postmark pricing](https://postmarkapp.com/pricing.txt) (accessed 2026-10-31)
- [Salesforce: SingleEmailMessage limits, API v232](https://developer.salesforce.com/docs/atlas.en-us.232.0.api_action.meta/api_action/actions_obj_email_simple.htm) (accessed 2026-10-31; 50 recipients a day in Developer Edition)
- [Mailpit](https://github.com/axllent/mailpit) (accessed 2026-10-31)

## Decision

<!-- Filled in by Davis. -->
- Decision:
- Accepted by Davis on:
- Notes:
