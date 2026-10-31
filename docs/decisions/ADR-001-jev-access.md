# ADR-001: How to reach Jev, and the decision-provider adapter contract

- **Gate:** R0.1
- **Status:** Accepted by Davis (2026-10-31)
- **Author:** build agent
- **Date drafted:** 2026-10-31
- **Blocks:** D0.3 (Jev key and spend cap), T0.2 (`make smoke-jev`), the Jev adapter, Phase 3

## Question

Do we reach Jev through TypeSafe's direct API (early access) or through Vercel AI Gateway?
What adapter contract should every decision provider implement?

## Context

- The plan assumes three primitives: "Choice, Score and probability". The real API calls the
  probability primitive **`noul`** (TypeSafe) or **`boolean`** (Vercel's own Decision API).
- Spend must sit under a monthly cap (open decision in the plan), and AUTO tests must never call
  a live service.
- Phase 3 benchmarks Jev against up to two alternatives (R3.2), so one account that reaches
  several decision models is worth something.

## What the API looks like (TypeSafe System One API)

`POST https://api.typesafe.ai/v1/systemone`, `Authorization: Bearer <key>`.

Request:

```json
{
  "model": "jev-1.14.0",
  "state": { "...": "string, object or array" },
  "questions": {
    "session_type": {
      "type": "choice",
      "instructions": "What kind of session is this?",
      "criteria": { "genuine_shopper": "...", "bot": "...", "internal_test": "...", "accidental": "..." }
    },
    "recovery_worthy": {
      "type": "score",
      "instructions": "How worth recovering is this cart?",
      "criteria": ["not worth it", "low", "medium", "high"]
    },
    "is_bot": { "type": "noul", "instructions": "Is this automated traffic?" }
  }
}
```

Response: `model`, `answers` keyed by question name, `usage.input_tokens` / `usage.output_tokens`.

| Type | Answer fields | Limits |
| --- | --- | --- |
| `choice` | `choice`, `confidence` (0–1), `probabilities` per option (sum ≈ 1) | 1–255 options |
| `score` | `score` (probability-weighted average), `confidence`, `legend`, `probabilities` per level | 1–10 levels |
| `noul` | `noul` = P(true), 0–1 | — |
| `box` | image bounding box (not used here) | needs images header |

- **Errors:** 400 (bad request), 422 (validation, with `detail[]`), 429 (rate limit, with retry-after).
- **Models:** `jev-1.14.0` (released 2026-10-14) and `jev-1.13.0`. Aliases `jev-latest` and
  `jev-preview` move, so pin a version.
- **Context:** 64k tokens per request and 32k per question by default.
- **Rate limits:** set per organization (tokens and requests per second) and shown only in the
  console. They aren't published.
- **Price:** $0.042 per million input tokens; output tokens free (vendor-reported).
- **Data:** TypeSafe says customer requests aren't used for training; zero data retention is enterprise-only.
- **Latency:** 70–500 ms end to end (vendor-reported, from TypeSafe's own comparisons).
- **Speed and cost claims:** Vercel's changelog repeats TypeSafe's "up to 193.6x faster and
  444.6x cheaper than LLMs" (vendor-reported). T3.7 tests these claims.

## Alternatives

### A. TypeSafe direct (early access)

- **How it works:** join the waitlist at typesafe.ai, wait for a console invite, then create a
  key at console.typesafe.ai.
- **Pros:** no middleman; rate limits come straight from TypeSafe; Python SDK `typesafe-sdk`
  (third-party report: v0.7.2, Python ≥3.10).
- **Cons:** still waitlist-gated, with no published timeline for invites. No free tier or credits
  are documented. This only reaches Jev, so R3.2 alternatives need separate accounts.
- **Cost:** $0.042 per million input tokens (vendor-reported).
- **Setup effort:** low once invited, but the wait is unknown.

### B. Vercel AI Gateway, TypeSafe-compatible endpoint (recommended)

- **How it works:** `POST https://ai-gateway.vercel.sh/typesafe/v1/systemone` with an AI Gateway
  API key and model `typesafe-ai/jev`. The request and response bodies are TypeSafe's own, so
  moving to option A later changes only the base URL and key.
- **Pros:**
  - No waitlist.
  - Budgets give a per-key or per-project spend cap: requests past the budget get HTTP 402.
  - The same key reaches the rival decision models for R3.2: OpenAI Decisions, Liquid d1,
    Microsoft Decision-1 and Perplexity Decider. It also reaches general LLMs through the
    gateway's `/v1/evaluate` structured-output path.
  - Each response carries cost metadata, which feeds the decision log.
  - $5 of free gateway credit every 30 days (vendor-reported).
- **Cons:**
  - One more hop adds some latency, which we measure in T3.5.
  - It isn't clear whether the free credit covers Jev; the free tier covers only "a subset of
    models".
  - It isn't clear whether a pinned version (`jev-1.14.0`) can be requested through the gateway.
  - The budget may let the one request that crosses the limit through (docs and third parties
    disagree on hard vs. soft cap).
- **Cost:** model price at zero markup; the sample response shows `surchargeCost: "0"`
  (vendor-reported).
- **Setup effort:** low. Needs a Vercel account, an AI Gateway key and a budget.

### C. Other third-party gateways (OpenRouter, Portkey, Zuplo, LiteLLM)

- **How it works:** same TypeSafe body, routed through their own gateway.
- **Pros:** also no waitlist.
- **Cons:** another account. Some policies block Jev bodies (Zuplo's DLP rules return
  `guardrail_uninspectable`), and they reach fewer native decision models than Vercel.
- **Recommendation:** not recommended. Listed for completeness.

## Trade-offs

| Criterion | A. Direct | B. Vercel gateway | C. Other gateways |
| --- | --- | --- | --- |
| Available today | No (waitlist) | Yes | Yes |
| Spend cap | Console (details unknown) | Budgets, HTTP 402 | Varies |
| Reaches R3.2 alternatives | No | Yes, same key | Partly |
| Body matches Jev docs | Yes | Yes | Mostly |
| Latency | Lowest | +1 hop (to measure) | +1 hop |
| Lock-in | TypeSafe | Base-URL swap away from A | Same |

## Fallback decision models (for the adapter and R3.2)

1. **Rival decision models on the gateway:** OpenAI Decisions (GPT-6 Luna, $0.10 per million
   input tokens), Liquid d1 / d1-ultra, Microsoft Decision-1, Perplexity Decider v1.2, and
   Cloudflare Clef / Clef-flash on Workers AI ($0.24 / $0.09 per million input tokens). Prices
   vendor-reported. All of these return typed answers with probabilities.
2. **A general LLM with structured output** through the gateway's `/v1/evaluate`. **Caveat:**
   when an LLM answers a Choice or Score, the gateway returns `confidence: 0` and
   `probabilities: {}`, which means "not available". That breaks calibration metrics, so the
   adapter has to ask the LLM for probabilities explicitly or mark them missing.
3. **Rules provider** (Phase 2 baseline). This is the offline fallback on timeout (T3.3).
4. **Strands Decider 2B** (open weights, runs locally). An option only if we want a zero-cost
   local rival.

**Don't use the gateway's built-in "decision fallbacks"** (`providerOptions.gateway.models`) in
benchmarks. They rerun uncertain answers on another model inside the same call, which mixes two
providers in one result. Fallback stays in our own code, where it's logged with a reason.

## Recommended adapter contract

The plan's `choice()` / `score()` / probability calls become thin helpers over one batched call.
Jev answers several questions against one `state` in a single request, so the state's input
tokens are billed once, not once per question.

```python
class ChoiceQ(BaseModel):  type: Literal["choice"]; instructions: str; criteria: dict[str, str]
class ScoreQ(BaseModel):   type: Literal["score"];  instructions: str; criteria: list[str]
class BinaryQ(BaseModel):  type: Literal["binary"]; instructions: str; criteria: dict[bool, str] | None

class Decision(BaseModel):
    answers: dict[str, Choice | Score | Binary]   # validated: declared labels only, probs sum to 1 ± 0.001
    provider: str; model: str                     # model = the version that actually answered
    input_tokens: int; cost_usd: float | None     # cost from gateway metadata when present
    latency_ms: float; request_id: str | None

class DecisionProvider(Protocol):
    name: str
    def decide(self, state: dict | str, questions: dict[str, ChoiceQ | ScoreQ | BinaryQ],
               *, timeout_s: float) -> Decision: ...
    # helpers built on decide(): choice(), score(), probability()
```

- **Naming:** we use neutral names (`binary`); each adapter maps them to `noul` (TypeSafe),
  `boolean` (Vercel `/v1/evaluate`) or `predicate` (OpenAI).
- **HTTP client:** the Jev adapter calls the HTTP endpoint with `httpx`, without the
  `typesafe-sdk` dependency. That keeps one HTTP client for every gateway provider and makes the
  mock easy.
- **Answers missing probabilities** (the LLM path) fail the contract, unless the provider is
  marked `calibrated=False` and kept out of ECE.
- **Retries:** 429 is retried with backoff up to the timeout. After that, the caller falls back
  to rules.
- **Changes to the Phase 0 code:** `Choice` stays as is. `Score`, `Binary` and `decide()` are
  added in Phase 3, after this ADR is accepted.

## Recommendation

Use **option B (Vercel AI Gateway, TypeSafe-compatible endpoint)** now, with model
`typesafe-ai/jev`, and **join the TypeSafe waitlist in parallel**. If an invite arrives, moving
to direct access is a base-URL and key change, and T3.5 can measure the latency difference.
Adopt the `decide()`-based adapter contract above.

## Open questions

1. Does Vercel's $5 monthly free credit cover `typesafe-ai/jev`? If not, a small credit purchase
   is needed, and buying credits ends the free credit.
2. Can a pinned version (`typesafe-ai/jev-1.14.0` or similar) be requested through the gateway?
   Check `GET /typesafe/v1/models` once the key exists. If not, record the `model` the response
   reports on every call.
3. What monthly spend cap should we use? (This is an open decision in the plan.) Expected spend
   is tiny: 10,000 sessions × ~1,500 input tokens ≈ 15M tokens ≈ $0.63 at Jev's price (estimate,
   not measured).
4. Is a soft cap acceptable (one request may cross the budget)?

## Sources

- [TypeSafe docs: System One API](https://docs.typesafe.ai/api) (accessed 2026-10-31)
- [TypeSafe docs: Models (pricing, limits, rate limits)](https://docs.typesafe.ai/models) (accessed 2026-10-31)
- [Vercel docs: TypeSafe API with AI Gateway](https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe) (updated 2026-10-05, accessed 2026-10-31)
- [Vercel docs: Decision modality](https://vercel.com/docs/ai-gateway/modalities/decision) (updated 2026-10-07, accessed 2026-10-31)
- [Vercel changelog: TypeSafe clients and HTTP API for Jev](https://vercel.com/changelog/ai-gateway-now-supports-typesafe-clients-and-http-api-for-jev) (2026-09-21)
- [Vercel changelog: Jev now available on AI Gateway](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway) (2026-09-16)
- [Vercel docs: AI Gateway pricing](https://vercel.com/docs/ai-gateway/pricing) and [budgets](https://vercel.com/docs/ai-gateway/budgets.md) (accessed 2026-10-31)
- [Let's Data Science: TypeSafe AI launches Jev](https://letsdatascience.com/news/typesafe-ai-launches-jev-decision-model-889a38c0) (2026-09-19)
- [Let's Data Science: Jev rivals and Vercel AI Gateway](https://letsdatascience.com/blog/openai-jev-rival-three-weeks-typesafe-raised-870-million) (2026-10-09)
- [Apidog: How to get a Jev API key](https://apidog.com/blog/jev-api-key/) (2026-09-18; waitlist status)
- [Zuplo docs: Jev through AI Gateway](https://zuplo.com/docs/ai-gateway/jev) (accessed 2026-10-31)

## Decision

<!-- Filled in by Davis. -->
- Decision: Option A
- Accepted by Davis on: 10/31/2026
- Notes: I have a TypeSafe account and API key already setup
