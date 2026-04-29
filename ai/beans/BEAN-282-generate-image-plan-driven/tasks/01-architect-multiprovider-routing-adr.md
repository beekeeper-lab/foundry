# Task 01: ADR — Multi-Provider Image Generation Routing

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-29 19:51 |
| **Completed** | 2026-04-29 19:54 |
| **Duration** | 3m |

## Goal

Record an ADR (next consecutive number after ADR-009) in
`ai/context/decisions.md` capturing the multi-provider image generation
routing design. The ADR locks the contract that the Developer task (02)
implements: how the `Generator:` frontmatter line dispatches between
Gemini and OpenAI, the unified `--quality low|medium|high` flag's
per-provider mapping, the OpenAI version fallback rule, and the
single-shot-vs-plan-driven duality of the rewritten skill.

## Inputs

- `ai/beans/BEAN-282-generate-image-plan-driven/bean.md` — full scope and acceptance criteria
- `ai/context/decisions.md` — ADR home (next number after ADR-009)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` — reference design (Image-generation skill section)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_images.py` — canonical implementation (provider dispatch lives here)
- `.claude/shared/skills/generate-image/SKILL.md` — current skill doc (single-shot only); the rewrite preserves single-shot mode and adds plan mode

CONTEXT DIET: stay within these inputs.

## Required ADR sections

1. **Context** — single-shot mode is sufficient for ad-hoc work but plan-driven generation is required for any portfolio-style project (Foundry-generated and Stonewaters reference both need it). Mixing providers within a single project visibly breaks style — frontmatter-locked routing prevents that.
2. **Decision** — six concrete commitments:
   1. **Plan-driven mode** (`--plan path/to/IMAGE-PLAN.md`) is the primary mode. Single-shot mode (`--prompt "..."`) is preserved for `generate-screen` and ad-hoc use.
   2. **`Generator:` frontmatter line is the per-project provider lock.** Default (omitted) → Gemini `gemini-3-pro-image-preview` (Nanobanana Pro). Tolerant dispatch: any value containing `openai` or `gpt-image` routes to OpenAI; OpenAI model name extracted via `gpt-image-[\d.]+`.
   3. **OpenAI default model: `gpt-image-2`** with automatic fallback to `gpt-image-1.5` when the org-verification error is detected. Print a one-line warning so the user knows to verify their org if they want gpt-image-2.
   4. **Unified `--quality low|medium|high` flag**, default `high`. Plan frontmatter `Quality:` overrides CLI default. Mapping table:

      | `--quality` | OpenAI gpt-image-2 / 1.5 | Gemini |
      |---|---|---|
      | `low` | `low` | `nanobanana2` |
      | `medium` | `medium` | `nanobanana2` |
      | `high` | `high` | `nanobanana-pro` (default) |

   5. **Rate limiter**: Gemini hard-paced at ~18 req/min via `MIN_INTERVAL_SECONDS = 60.0/18`. Retry on 429 honoring `retryDelay` from the Gemini error body. OpenAI: respect 429 retry-after header; on `billing hard limit` error, fail fast with a clear message (don't retry — quota is hard).
   6. **Sidecar JSON next to each PNG** captures: timestamp, provider, model, quality (OpenAI), size (OpenAI), assembled prompt, output basename, generation_time_ms, usage tokens (Gemini), fallback_used flag, negative_constraints. Schema lives in code (`generate_image.py`); ADR documents the *required* fields, not the exact JSON structure.
3. **Cost table location** — restate the rule from `AGENTIC-MEDIA-SKILLS.md`: cost rates live in the script, not in docs. End-of-run summary prints estimated cost using the in-script table. When rates change, update the script, not the ADR.
4. **One-provider-per-project rule** — call out explicitly that switching `Generator:` mid-project commits to regenerating *all* images for that project (style drift at the seam is the most visible quality bug).
5. **Failover use case** — Gemini and OpenAI quotas are independent. Documenting this here makes the failover (when one provider hits quota, advance projects routed to the other) a deliberate strategy rather than ad-hoc.
6. **Consequences** — what becomes easier (multi-provider portfolios; clean dispatch via frontmatter; cost predictability), what becomes harder (must keep regex tolerance honest as new OpenAI models land; cost table needs maintenance).
7. **Alternatives considered** — at minimum:
   - **Per-image provider override** (rejected: invites style drift within a project).
   - **Auto-pick provider based on quality flag** (rejected: removes the project-level lock, defeats the purpose).
   - **Ship with OpenAI off until org verification is complete** (rejected: gpt-image-1.5 works without verification and the fallback handles 2 → 1.5 gracefully; users get value immediately).

## Acceptance Criteria

- [ ] ADR exists in `ai/context/decisions.md` with the structure above.
- [ ] ADR is numbered consecutively (likely ADR-010 since ADR-009 is the most recent).
- [ ] All six "Decision" commitments are stated unambiguously, with the quality mapping table verbatim.
- [ ] Provider dispatch regex is named (`gpt-image-[\d.]+`) and the tolerant containment check (`openai` or `gpt-image`) is documented.
- [ ] OpenAI fallback behavior (gpt-image-2 → gpt-image-1.5 on org-verification error) is named explicitly.
- [ ] Cost-table-in-code rule is stated.
- [ ] One-provider-per-project rule is stated as a hard rule, not a recommendation.
- [ ] At least 3 alternatives rejected, each with a one-line reason.
- [ ] No code changes — design only.

## Definition of Done

- ADR appended to `ai/context/decisions.md`.
- Developer task (02) can read this ADR and implement without further design discussion.
- Commit message: `BEAN-282 task 01: ADR for multi-provider image generation routing`.
