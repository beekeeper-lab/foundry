# Task 02: Rewrite `generate-image` (Multi-Provider, Plan-Driven)

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-29 19:55 |
| **Completed** | 2026-04-29 20:06 |
| **Duration** | 11m |

## Goal

Rewrite `.claude/shared/skills/generate-image/generate_image.py` per
ADR-010 (from Task 01). Take
`Course_Material/Git_Fundamentals/scripts/generate_images.py` (495
lines) as the basis — it carries the rate limiter constant, retry-on-429
logic, and frontmatter parser already proven in production. Adapt for
Foundry conventions: import from `_media_lib` for `.env` discovery, add
plan-driven mode, add OpenAI provider with gpt-image-2 default and 1.5
fallback, add unified `--quality low|medium|high` flag, expand sidecar
schema, print end-of-run cost summary.

Single-shot mode (`--prompt "..."`) is preserved so `generate-screen`
keeps working without modification. Plan-driven mode (`--plan IMAGE-PLAN.md`)
is the new primary mode.

The user has explicitly waived backwards compatibility for the existing
single-shot CLI's argument shape — feel free to redesign the flags as
long as `generate-screen`'s caller can be updated in lockstep.

## Inputs

- `ai/beans/BEAN-282-generate-image-plan-driven/bean.md` — full scope
- `ai/context/decisions.md` — ADR-010 (multi-provider routing) and ADR-009 (kit distribution)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/Git_Fundamentals/scripts/generate_images.py` — canonical implementation (basis; copy and adapt with attribution in header)
- `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` — reference design (cost table, sidecar fields, frontmatter keys)
- `.claude/shared/skills/generate-image/generate_image.py` — current single-shot implementation (will be replaced)
- `.claude/shared/skills/generate-image/SKILL.md` — current skill doc (will be rewritten)
- `.claude/shared/skills/_media_lib/` — shared library for `.env` discovery (`load_env`)
- `.claude/shared/skills/generate-screen/` — verify the `generate-screen` caller still works after the rewrite (smoke test only; don't modify generate-screen unless the caller breaks)
- `tests/` — directory for new tests
- `pyproject.toml` — for adding `openai` as an optional dependency if needed (ideally use `uv run --with openai` so it's not a hard runtime dep of foundry_app)

CONTEXT DIET: stay within these inputs. Do not browse the rest of foundry_app.

## Changes Required

1. **Rewrite `.claude/shared/skills/generate-image/generate_image.py`** as a single CLI entry point supporting both modes:
   - **Plan-driven mode**: `python generate_image.py --plan path/to/IMAGE-PLAN.md [--filter <substring>] [--force] [--dry-run]`
   - **Single-shot mode**: `python generate_image.py --prompt "..." [--quality high] [--output path] [--reference-image path]` etc. (preserve everything `generate-screen` needs).
   - Header comment crediting the Stonewaters reference (`Course_Material/Git_Fundamentals/scripts/generate_images.py`) as the basis.
2. **Frontmatter parser** for `IMAGE-PLAN.md` — recognize: `Style`, `Branding`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`, `Philosophy`, `Generator`, `Quality`, `Size`. Same bold-key markdown format the Stonewaters scripts use.
3. **Plan entry parser** — read `### Image N: <slug>` blocks; required `**File**` and `**Description**`; optional `**Page**` (ignored) and structured `**Prompt**` block (overrides description+defaults assembly when present).
4. **Provider dispatch** — `Generator:` value containing `openai` OR `gpt-image` routes to OpenAI (model name via `gpt-image-[\d.]+`); everything else → Gemini. Default (omitted) → Gemini `gemini-3-pro-image-preview`.
5. **OpenAI provider** — implement with `openai` Python SDK (`uv run --with openai`). Default model `gpt-image-2`. On org-verification error, automatically retry with `gpt-image-1.5` and set `fallback_used: true` in the sidecar. Print a one-line warning. Fail fast on `billing hard limit`.
6. **Unified quality flag** — `--quality low|medium|high`, default `high`. Plan frontmatter `Quality:` overrides CLI default. Mapping per ADR-010.
7. **Skip-on-disk** — for each plan entry, if the destination PNG exists and `--force` is not set, skip. `--filter <substring>` restricts to entries whose `**File**` path contains the substring. `--dry-run` walks the plan and prints what would be generated; no API calls.
8. **Rate limiter** — Gemini: `MIN_INTERVAL_SECONDS = 60.0/18` (matches Stonewaters). Retry on 429 honoring the `retryDelay` from the error body. OpenAI: respect 429 retry-after; fail fast on billing-hard-limit.
9. **Sidecar JSON** — write next to each PNG with the same stem. Required fields: timestamp (ISO 8601), provider, model, quality (OpenAI), size (OpenAI), assembled_prompt, output_file basename, generation_time_ms, usage tokens (Gemini), fallback_used, negative_constraints, aspect_ratio, background, text_in_image. Match the Stonewaters reference's expanded schema (see `AGENTIC-MEDIA-SKILLS.md`).
10. **Cost table** — bake current rates into the script (a `_COST_TABLE` dict at module top, with comment pointing to the source data in `AGENTIC-MEDIA-SKILLS.md`). End-of-run summary prints provider, count, and estimated total cost.
11. **`.env` discovery** — import and call `load_env()` from `_media_lib.env` at startup. Does not overwrite existing process env.
12. **Rewrite `.claude/shared/skills/generate-image/SKILL.md`** to document plan-driven mode, frontmatter keys, quality flag, provider routing, sidecar schema, env vars (`GEMINI_API_KEY`, `OPENAI_API_KEY`), and the cost-table-in-code rule. Single-shot mode docs stay (with any flag-shape updates).
13. **Tests** at `tests/test_generate_image.py`:
    - Frontmatter parser: every documented key, including `Generator:` dispatch.
    - Plan parser: image entries with/without optional `**Prompt**` blocks.
    - Provider dispatch (mocked): `gemini-...` vs `openai-...` vs `gpt-image-...` routing; tolerant containment check.
    - Skip-on-disk: existing files skipped; `--force` overrides.
    - `--filter` matches substring of `**File**` path.
    - `--dry-run` makes no API calls (mock the providers; assert never called).
    - Quality flag → provider arg mapping (all 6 cells of the table).
    - OpenAI org-verification fallback path (mocked: simulate the error, assert fallback to gpt-image-1.5 with `fallback_used: true` in sidecar).
    - Rate limiter: `MIN_INTERVAL_SECONDS` enforced (mocked clock).
    - Cost summary: end-of-run prints provider + count + total estimated cost.
14. **Smoke-test `generate-screen`** — run a representative `generate-screen` invocation that uses the single-shot path. If it breaks, update the caller in `generate-screen`'s SKILL.md / code in lockstep with the new flag shape.

## Acceptance Criteria

- [ ] `--plan IMAGE-PLAN.md` mode generates only missing images, skipping existing ones.
- [ ] `--prompt "..."` mode generates one image (single-shot path preserved or updated; `generate-screen` still works).
- [ ] `Generator:` frontmatter routes Gemini vs OpenAI correctly; tolerant dispatch tested.
- [ ] OpenAI default is `gpt-image-2`; falls back to `gpt-image-1.5` on org-verification error with a warning.
- [ ] `--quality` flag behaves per the mapping table; default is `high`.
- [ ] Sidecar JSON contains every required field for each successful generation.
- [ ] Gemini rate limiter caps at ~18 req/min; honors `retryDelay` on 429.
- [ ] `--filter`, `--force`, `--dry-run` behave as documented.
- [ ] End-of-run summary prints provider, count, and estimated cost.
- [ ] `.env` discovery via `_media_lib.env.load_env`.
- [ ] `generate-screen` smoke test still works.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- Code changes committed on the feature branch.
- Tests pass; lint clean.
- `generate-screen` verified working.
- SKILL.md rewritten.
- Commit message: `BEAN-282 task 02: generate-image plan-driven rewrite (multi-provider)`.
