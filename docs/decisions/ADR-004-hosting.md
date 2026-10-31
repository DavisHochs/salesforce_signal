# ADR-004: How Salesforce reaches our local services

- **Gate:** R0.4
- **Status:** Accepted by Davis (2026-10-31)
- **Author:** build agent
- **Date drafted:** 2026-10-31
- **Blocks:** D0.4, Phase 4 Named Credential to the bridge, Resend webhooks (ADR-003)

## Question

How do Salesforce (and the email service's webhooks) reach the sender bridge and triage service:
a local tunnel, or a small host?

## Context

What actually needs to be reachable from the internet is narrower than the plan assumed:

- **Triage service: doesn't need to be reachable.** It calls *out* to Salesforce (ADR-002), so it
  can stay local.
- **Sender bridge: needs to be reachable.** Salesforce calls it from Apex through a Named
  Credential, and Resend posts webhooks to it.

Other constraints:

- **Callout timeout:** Apex callouts default to a 10 s timeout (120 s max per transaction), so a
  host that cold-starts slowly will fail callouts.
- **Stable URL:** a Named Credential holds a fixed URL. If the URL changes every restart, Davis
  has to edit the org each time.
- **Demo mode:** `make demo` (Phase 6) has to run from a clean clone, so whatever we pick must be
  scriptable.

## Alternatives

### A. ngrok, free plan (recommended)

- **How it works:** the `ngrok` agent exposes `localhost:<bridge port>` on a dev domain assigned
  to the account. The domain stays the same across restarts.
- **Pros:** stable URL with no domain purchase, a one-command start, and a request inspector
  that's handy for debugging callouts.
- **Cons:**
  - Free-plan caps: 1 GB of transfer a month and 3 endpoints. Third-party sites also report about
    20,000 requests a month, which we couldn't confirm in ngrok's docs.
  - Free plans show an interstitial page to browsers. It doesn't affect API callers like Apex or
    webhooks (third-party report; verify in D0.4).
- **Cost:** $0.
- **Setup effort:** low (an account plus an auth token stored in ngrok's own config, not in the
  repo).

### B. Cloudflare Tunnel

- **Quick tunnel** (`cloudflared tunnel --url`):
  - No account needed.
  - **New random URL every run**, up to 200 in-flight requests, and no uptime guarantee.
  - Fine for a one-off smoke test, not for a Named Credential.
- **Named tunnel:**
  - Stable hostname and free.
  - Needs a Cloudflare account and a domain on Cloudflare DNS for a public hostname.
- **Setup effort:** low (quick) / medium (named).

### C. Render free web service

- **How it works:** deploy the bridge from GitHub.
- **Cons:**
  - Spins down after 15 minutes idle, with about a one-minute cold start. That's longer than the
    10 s callout default, so the first callout after idle fails unless we stretch the timeout to
    near the 120 s cap.
  - The free tier is capped at 750 instance hours a month.
  - The bridge would also need to reach Mailpit, which runs locally.
- **Cost:** $0. $7 a month removes spin-down (vendor-reported).

### D. Fly.io

- **How it works:** always-on small machine.
- **Cost:** about $2.19 a month for shared-cpu-1x / 256 MB after the October 2026 RAM price change
  (third-party figure; Fly's own page still showed $1.94). No free tier is confirmed for new
  accounts.
- **Cons:** costs money and needs a deploy pipeline; same Mailpit problem as C.

### E. Vercel Functions

- **How it works:** serverless Python.
- **Cons:** stateless, so it can't write a local DuckDB or reach local Mailpit. It would need a
  redesign for this project.

## Trade-offs

| Criterion | A. ngrok free | B. CF quick / named | C. Render free | D. Fly.io | E. Vercel |
| --- | --- | --- | --- | --- | --- |
| Stable URL | Yes | No / Yes | Yes | Yes | Yes |
| Works with 10 s callout default | Yes | Yes | No (cold start) | Yes | Usually |
| Reaches local Mailpit | Yes | Yes | No | No | No |
| Cost | $0 | $0 | $0 | ~$2/mo | $0 |
| Needs a domain | No | No / Yes | No | No | No |
| Setup effort | Low | Low / Medium | Medium | Medium | High (redesign) |

## Recommendation

**A. ngrok free plan, on the sender bridge only.**

- The triage service stays local.
- If Davis already has a domain on Cloudflare, **B (named tunnel)** is an equal choice with no
  usage caps.
- A hosted option (C or D) is only worth revisiting in Phase 6, if the portfolio needs an
  always-on live demo. ADR-005 recommends a static dashboard, so it probably won't.

## Open questions

1. Does Davis have a domain on Cloudflare? If yes, consider the named tunnel instead.
2. Confirm in D0.4 that ngrok's free interstitial page doesn't intercept Apex callouts (send a
   test callout from Anonymous Apex).
3. Add the tunnel URL to Remote Site Settings, or use only the Named Credential (decided in
   R4.3).

## Sources

- [ngrok docs: free plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits) and [licensing](https://ngrok.com/docs/guides/licensing/) (accessed 2026-10-31)
- [Cloudflare docs: Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) (accessed 2026-10-31)
- [Render changelog: free web service spin-down](https://render-www.onrender.com/changelog/free-web-services-now-remain-active-while-receiving-websocket-messages) (2026-02-24) and [livemy.app: Render pricing](https://livemy.app/blog/render-pricing) (accessed 2026-10-31)
- [Fly.io resource pricing](https://fly.io/docs/about/pricing/) and [buildmvpfast: Fly.io pricing 2026](https://www.buildmvpfast.com/blog/fly-io-pricing-2026-ram-increase-vs-hetzner) (accessed 2026-10-31)
- [Salesforce: Apex callout limits and timeouts](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_callouts_timeouts.htm) (accessed 2026-10-31)

## Decision

<!-- Filled in by Davis. -->
- Decision: Option A
- Accepted by Davis on: 10/31/2026
- Notes: ngrok is fine for the MVP and likely will not need any always on live demo capabilities, Id rather this remain more local often and something I can spin up to show as a demo use case rather than some hyper complex always on endeavor
