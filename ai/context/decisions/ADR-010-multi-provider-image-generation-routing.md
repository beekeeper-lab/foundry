# ADR-010: Multi-Provider Image Generation Routing

| Field | Value |
|-------|-------|
| **Date** | 2026-04-29 |
| **Status** | Accepted |
| **Bean** | BEAN-282 |
| **Deciders** | Architect |

## Context

The current `generate-image` skill (`.claude/shared/skills/generate-image/`)
is a single-shot CLI wrapper around Google's Gemini Nano Banana models.
It is sufficient for ad-hoc one-off assets — an icon for a screen, a
hero image for a marketing page — and the existing `generate-screen`
skill consumes it in exactly that mode.

It is **not** sufficient for any portfolio-style project. Both the
Stonewaters `Course_Material` reference (18 illustrated, narrated HTML
courses) and any future Foundry-generated portfolio project need to
generate hundreds of images per project from a reviewed plan markdown,
re-runnable, idempotent against on-disk state, with auditable
sidecars. The plan-driven workflow is documented in
`/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md`
under "Image-generation skill"; the canonical implementation lives in
`Course_Material/Git_Fundamentals/scripts/generate_images.py` and
carries hard-won knowledge (rate-limit constant, 429 retry-with-
`retryDelay`, frontmatter parser, dispatch regex).

Two further forces shape this ADR:

1. **Visible style drift at the seam.** Gemini and OpenAI image
   models produce recognizably different illustrations even at
   matched prompts and quality. Mixing providers within a single
   project is the most visible quality bug — readers see the seam.
   The provider choice must therefore be locked **per project**,
   not per image.
2. **Independent provider quotas.** Gemini's free tier enforces a
   per-minute and per-24-hour cap; OpenAI's image generation can hit
   a dashboard "billing hard limit" mid-batch. When one provider is
   throttled, work routed to the other keeps moving — but only if
   the routing is documented in a per-project frontmatter line that
   the generator script honors deterministically.

The rewrite preserves single-shot mode (`--prompt "..."`) so
`generate-screen` and any ad-hoc consumer keeps working without
modification, and adds plan-driven mode (`--plan IMAGE-PLAN.md`) as
the primary surface. The single-shot/plan-driven duality is the
shape of the rewrite; multi-provider routing is the contract this
ADR locks down.

## Decision

Six concrete commitments. The Developer task (BEAN-282 task 02)
implements directly against this list.

**1. Plan-driven mode is the primary mode; single-shot mode is
preserved.** The rewritten skill exposes two CLI surfaces:

- `--plan path/to/IMAGE-PLAN.md` — primary mode. Reads frontmatter
  + image entries, skips on disk, supports `--filter <substring>`,
  `--force`, `--dry-run`. This is the mode every portfolio-style
  project uses.
- `--prompt "..."` — preserved single-shot mode for `generate-screen`
  consumers and ad-hoc one-off use. No frontmatter; provider/quality
  come from CLI flags or default.

The two modes share the provider-dispatch and rate-limiter code paths
but differ in input shape (plan vs. one prompt) and looping (many vs.
one). The duality is intentional: single-shot is exactly right for
small dispatches, plan-driven is exactly right for portfolios.

**2. The `Generator:` frontmatter line is the per-project provider
lock.** Tolerant containment dispatch:

- Default (line omitted entirely) → **Gemini**
  `gemini-3-pro-image-preview` (Nanobanana Pro). This preserves the
  current skill's behavior for every plan that does not opt into
  OpenAI.
- Any value containing the substring `openai` **OR** `gpt-image`
  (case-insensitive) → **OpenAI**.
- The OpenAI model name is extracted from the same string with the
  regex `gpt-image-[\d.]+`. If no match, fall back to the OpenAI
  default model (commitment 3).

The containment check is deliberately tolerant so all of
`openai-gpt-image-1.5`, `openai-gpt-image-2`, `gpt-image-1.5`,
`gpt-image-2`, and a leading marketing-name prefix (e.g.
`OpenAI gpt-image-2`) route correctly. Anything not matching
`openai`/`gpt-image` routes to Gemini — no auto-pick, no
heuristic, no implicit OpenAI selection.

**3. OpenAI default is `gpt-image-2` with automatic fallback to
`gpt-image-1.5` on the org-verification error.** When the resolved
OpenAI model is `gpt-image-2` and the API returns the
org-verification error (the OpenAI dashboard requires verifying the
org before `gpt-image-2` is callable), the script:

- Prints a one-line warning to stderr — single line, mentions both
  the verification requirement and the fallback that just happened
  (e.g. `WARNING: gpt-image-2 requires OpenAI org verification; falling back to gpt-image-1.5 for this run. Verify your org at platform.openai.com to use gpt-image-2.`).
- Retries the same request against `gpt-image-1.5`.
- Records `fallback_used: true` in the sidecar JSON.

On the OpenAI `billing hard limit` error the script **fails fast**
with a clear message and does not retry. The hard limit is exactly
that — quota is gone for the period; retrying just burns time and
prints the same error N times. The user's correct response is to
raise the dashboard cap or wait for the next billing period; the
script's job is to surface that decision quickly.

The `gpt-image-2` default tracks user direction: ship the newest
model on by default, fall back gracefully when verification has not
yet been completed, surface the verification requirement so the user
can fix it. Shipping with `gpt-image-1.5` as the default would hide
the upgrade path; the fallback handles unverified orgs cleanly.

**4. Unified `--quality low|medium|high` flag, default `high`.** A
single user-facing knob across both providers. Plan frontmatter
`Quality:` overrides the CLI default; CLI flag overrides nothing
about the plan (the plan is the contract).

Mapping table — verbatim:

| `--quality` | OpenAI gpt-image-2 / 1.5 | Gemini |
|---|---|---|
| `low` | `low` | `nanobanana2` |
| `medium` | `medium` | `nanobanana2` |
| `high` | `high` | `nanobanana-pro` (default) |

Two notes on the table:

- OpenAI's quality tokens (`low` / `medium` / `high`) pass through
  unchanged to the OpenAI Images API.
- Gemini exposes two model slots — the faster, cheaper `nanobanana2`
  and the higher-fidelity `nanobanana-pro`. `low` and `medium`
  collapse onto `nanobanana2` because Gemini's lower-quality models
  do not have the same tier granularity as OpenAI; only `high` walks
  up to `nanobanana-pro`.

The unified flag is the *user-facing* knob. The
provider-specific arg names (`quality=high` for OpenAI, model
selection for Gemini) live behind the dispatcher; no caller of the
skill needs to know the difference.

**5. Rate limiter — provider-specific.**

- **Gemini:** hard-paced at ~18 req/min via the in-script constant
  `MIN_INTERVAL_SECONDS = 60.0 / 18`. Gemini's per-minute ceiling is
  20; the 18 target leaves headroom. On 429, the script reads
  `retryDelay` from the Gemini error body and sleeps that long
  before retrying (default `MAX_RETRIES_ON_429 = 3` per request,
  matching the canonical implementation). The constant is not
  configurable — it is a property of the Gemini quota, not a tunable.
- **OpenAI:** the script respects the 429 `retry-after` header when
  present and retries within the same per-request retry budget. On
  the `billing hard limit` error, **fail fast** — do not retry, do
  not enter a retry loop, do not pace. Print the error and exit the
  current run with a clear message so the user knows why work
  stopped. The hard limit is hard; further attempts only delay the
  inevitable failure.

**6. Sidecar JSON next to each PNG — required fields.** Every
successful generation writes a JSON sidecar with the same basename as
the PNG (`<slug>.png` ↔ `<slug>.json`). The sidecar **must** include:

- `timestamp` (ISO 8601, UTC)
- `provider` (`gemini` or `openai`)
- `model` (resolved model name, e.g. `gemini-3-pro-image-preview` or
  `gpt-image-1.5`)
- `quality` (OpenAI only — `low` / `medium` / `high`)
- `size` (OpenAI only — e.g. `1536x1024`)
- `prompt` (the **assembled prompt as sent**, not the raw plan
  description — this is what reproduces the image)
- `output_file` (basename of the PNG)
- `generation_time_ms` (wall-clock time from request to response)
- `usage` (Gemini only — `prompt_tokens` / `candidates_tokens` /
  `total_tokens`; OpenAI's image API does not return token usage)
- `fallback_used` (boolean — true when `gpt-image-2` was requested
  and the script fell back to `gpt-image-1.5`; false otherwise)
- `negative_constraints` (the parsed `Avoid:` list, possibly empty)

The exact JSON shape (key order, optional helper fields, additional
provenance like `assembled_prompt` vs. `prompt`) lives in code
(`generate_image.py`); this ADR documents the *required* fields, not
the exact serialized structure. Adding fields is non-breaking;
removing or renaming any of the listed required fields requires a
follow-up ADR.

## Cost table location

The cost-per-image rates documented in
`AGENTIC-MEDIA-SKILLS.md` (Gemini per-token pricing, OpenAI per
quality+size combo) are baked into a constant table inside
`generate_image.py`. The end-of-run summary prints provider, image
count, and estimated cost computed from that table. **Provider
prices change. The cost table in `generate_image.py` is the
load-bearing version.** When rates change, update the script, not
this ADR and not the bean. Docs that reference cost rates link to
the script's table rather than restating the numbers.

This rule mirrors what `AGENTIC-MEDIA-SKILLS.md` already says about
its reference implementation. We restate it here so the rule is part
of the architecture record, not a footnote.

## One-provider-per-project rule

**Hard rule, not a recommendation: a project commits to one provider
for the life of the project.** The `Generator:` frontmatter line is
the lock. Switching providers mid-project means committing to
**regenerating every image** in that project — half-converted plans
are not supported and will produce visible style drift at the seam.

This is non-negotiable. Style drift between Gemini and OpenAI within
one project is the most visible quality bug in any portfolio-style
output. The skill enforces the rule by reading `Generator:` once per
plan and applying it uniformly; it does not support per-image
provider override (commitment 2 above forbids it). When a user
changes `Generator:` in a plan, the correct response is `--force`
and a re-run, not a partial regeneration.

## Failover use case

Gemini and OpenAI quotas are independent: Gemini has its own
per-minute and per-24-hour limits; OpenAI has its own dashboard-set
billing hard limit. When one provider is throttled or capped,
projects routed to the other keep working.

Documenting the routing in plan frontmatter (commitment 2) makes
this failover **deliberate strategy**, not ad-hoc. When planning a
portfolio of projects, intentionally split the routing so a
quota event on one provider does not block all work. "Today is a
Gemini day, advance Gemini-routed projects; OpenAI is blocked
until next billing period" is a coherent operating mode only when
each project's provider is recorded in writing. This ADR makes
that recording the contract.

## Consequences

**Positive:**

- **Multi-provider portfolios are tractable.** A user can run 18
  projects with some routed to Gemini, some to OpenAI, and pace
  them independently against each provider's quota.
- **Dispatch is one regex and one containment check.** No new
  configuration surface, no per-call provider negotiation.
  Frontmatter line in, provider out.
- **Cost is predictable per project.** End-of-run summary plus the
  one-provider-per-project rule means a project's spend is bounded
  by its image count times the in-script rate for the resolved
  provider/model/quality combo.
- **The single-shot path stays simple.** `generate-screen` and
  ad-hoc callers do not learn anything about plans, frontmatter, or
  failover; the new shape is strictly additive.
- **Sidecars are auditable.** Six months later a regeneration can
  read the sidecar's `prompt` and `model` and reproduce the exact
  request, even if the plan has been edited.

**Negative:**

- **Regex tolerance must stay honest.** As OpenAI ships new image
  models (`gpt-image-3`, `gpt-image-2.1`, etc.), the regex
  `gpt-image-[\d.]+` and the containment check must continue to
  match. Adding a regex test for each new model when it lands is the
  Tech-QA expectation; failing to do so means the new model name
  routes to the OpenAI default fallback silently.
- **Cost table needs maintenance.** Provider prices change; the
  in-script table must be updated when they do. The ADR
  intentionally does not embed numbers — but the maintenance burden
  is real and falls on whoever ships the rate change.
- **The fallback warning is one line.** A user running a 200-image
  batch will see one fallback line and may scroll past it. We
  accept this — louder warnings are noisier and the sidecar's
  `fallback_used` field is the durable record.
- **OpenAI org verification is a manual step.** Until the user
  verifies their OpenAI org, every `gpt-image-2` request falls back
  to `gpt-image-1.5`. The fallback ships value immediately; the
  one-line warning surfaces the unlock path.

## Alternatives Considered

1. **Per-image provider override (e.g. an `Image N:`-level
   `Generator:` field).** Rejected. Invites style drift within a
   single project — the exact failure mode the one-provider-per-
   project rule prevents. The visible-seam quality bug is the
   reason this ADR exists; per-image overrides would re-introduce
   it.
2. **Auto-pick provider from the `--quality` flag (e.g. `low`
   always means OpenAI low, `high` always means Gemini Pro).**
   Rejected. Removes the per-project lock and defeats the purpose
   of the `Generator:` frontmatter line. Quality is a user-facing
   knob *within* a chosen provider; it must not double as a
   provider selector. Coupling quality and provider also makes the
   failover use case incoherent — a user "running OpenAI today"
   could no longer ask for `high` without flipping the project's
   provider.
3. **Ship with OpenAI off until org verification is complete.**
   Rejected. `gpt-image-1.5` works today without verification;
   keeping OpenAI off entirely would deny that value. The
   `gpt-image-2` → `gpt-image-1.5` fallback handles the unverified
   case gracefully and prints the unlock path, so users get value
   immediately and can verify their org when convenient.
4. **Configure provider in CLI flags rather than plan frontmatter.**
   Rejected. CLI flags travel with the invocation, not the
   project. A plan re-run six months later with a different flag
   accidentally produces a different-style image — the seam bug
   again. Frontmatter travels with the project markdown and is
   reviewable in version control; the CLI default just supplies a
   value when the plan does not.
5. **Use a config file (`.image-generator-config.toml`) instead of
   plan frontmatter.** Rejected. Adds a second file to keep in
   sync with the plan, and the plan markdown is already the
   single source of truth for "what should exist." Embedding the
   provider in the plan keeps every project self-describing in one
   reviewable file.

## Reversibility

The dispatch contract is the load-bearing piece. Adding a new
recognized substring (e.g. a third provider's namespace) is
additive and backwards-compatible — existing plans keep routing
correctly. Changing the meaning of an existing substring (e.g.
having `gpt-image` route somewhere other than OpenAI) would
invalidate every project's frontmatter and is the only edit that
requires a follow-up ADR.

The required-fields list for sidecars is similarly load-bearing:
adding a field is non-breaking; removing or renaming a field
requires the follow-up. The exact JSON shape lives in code and
can churn freely without a new ADR, as long as the required
fields keep their current semantics.
