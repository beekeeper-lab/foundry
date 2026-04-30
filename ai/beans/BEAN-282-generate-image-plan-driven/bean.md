# BEAN-282: `generate-image` Plan-Driven Rewrite (Multi-Provider)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-282 |
| **Status** | In Progress |
| **Priority** | High |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 19:49 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |
| **Depends On** | BEAN-280, BEAN-281 |

## Problem Statement

The current `generate-image` skill in `.claude/shared/skills/generate-image/` is a single-shot CLI wrapper around Gemini's Nano Banana models. Useful for one-off icons or hero images. Unsuitable for the workflow that the Stonewaters Course_Material portfolio (and any future Foundry-generated portfolio project) actually needs:

- Generate hundreds of images per project from a reviewed plan markdown.
- Pin the provider for the life of the project to avoid visible style drift at the seam between Gemini and OpenAI outputs.
- Skip-on-disk so re-running the script is the normal way to add one image.
- Honor a unified quality knob so the user can trade cost for fidelity without learning each provider's vocabulary.
- Record auditable sidecars (timestamp, model, prompt as sent, cost) for every image.
- Cap rate-limit damage on Gemini and budget-hard-limit damage on OpenAI by failing fast with a clear message.

The full design is documented in `/home/gregg/Nextcloud/Stonewaters_consulting/Course_Material/AGENTIC-MEDIA-SKILLS.md` ("Image-generation skill" section). This bean ports it into ClaudeKit.

The user has explicitly said no backwards compatibility is required, so this is a rewrite, not a graft.

## Goal

A single `generate-image` skill in ClaudeKit that supports both **plan-driven batch generation** (`--plan IMAGE-PLAN.md`) and **single-shot generation** (`--prompt "..."`), routes between Gemini and OpenAI via the plan's frontmatter, and exposes a unified `--quality low|medium|high` knob. Library-copy-mode and subtree-mode generated projects both receive the new skill via BEAN-280's distribution mechanism.

## Scope

### In Scope

- **Implementation in `.claude/shared/skills/generate-image/generate_image.py`** (rewrite). Take `Course_Material/Git_Fundamentals/scripts/generate_images.py` as the basis and adapt — it carries hard-won knowledge (rate-limit constant, retry-on-429, frontmatter parser, dispatch regex). Add an attribution header.
- **Plan-driven mode (`--plan path/to/IMAGE-PLAN.md`)**:
  - Parse frontmatter (bold-key markdown): `Style`, `Branding`, `Aspect ratio`, `Background`, `Text in image`, `Avoid`, `Philosophy`, `Generator`, `Quality`, `Size`.
  - Parse `### Image N: <slug>` entries with required `**File**` and `**Description**`, optional `**Prompt**` structured block.
  - Skip-on-disk: skip entries whose `**File**` already exists; only generate missing ones.
  - Flags: `--filter <substring>`, `--force`, `--dry-run`.
- **Single-shot mode (`--prompt "..."`)**: preserved for `generate-screen` consumers and ad-hoc use.
- **Provider routing via frontmatter `Generator:`**:
  - Default (omitted) → Gemini `gemini-3-pro-image-preview` (Nanobanana Pro).
  - Tolerant dispatch: any value containing `openai` or `gpt-image` → OpenAI; model name extracted via `gpt-image-[\d.]+`.
  - **Default OpenAI model: `gpt-image-2`** (per user). Falls back to `gpt-image-1.5` with a warning if `gpt-image-2` returns the org-verification error.
- **Unified quality flag (`--quality low|medium|high`, default `high`)**:

  | `--quality` | OpenAI gpt-image-2 / 1.5 | Gemini |
  |---|---|---|
  | `low` | `low` | `nanobanana2` |
  | `medium` | `medium` | `nanobanana2` |
  | `high` | `high` | `nanobanana-pro` (default) |

  Plan frontmatter `Quality:` overrides the CLI default.
- **Sidecar JSON next to each PNG**: timestamp, provider, model, quality, size (OpenAI), prompt-as-sent, output basename, generation_time_ms, usage tokens (Gemini), fallback_used, negative_constraints. Match the Stonewaters reference schema.
- **Rate limiter**: Gemini ~18 req/min (`MIN_INTERVAL_SECONDS = 60.0/18`), retry on 429 honoring `retryDelay` from the error body. OpenAI: respect 429 retry-after headers; fail clearly on `billing hard limit`.
- **Cost table baked into the script** with the rates documented in `AGENTIC-MEDIA-SKILLS.md`. End-of-run summary prints estimated total cost.
- **`.env` discovery via `_media_lib.env.load_env`** (BEAN-281).
- **Add `generate-image` to `_KIT_DISTRIBUTED_SKILLS`** (BEAN-280) — already there for the existing skill; this just confirms it stays.
- **Tests** (`tests/skills/test_generate_image.py`):
  - Frontmatter parser: every documented key, including `Generator:` dispatch.
  - Plan parser: image entries with/without optional `**Prompt**` blocks.
  - Skip-on-disk: existing files skipped; `--force` overrides.
  - `--filter` matches substring of `**File**` path.
  - `--dry-run` makes no API calls.
  - Quality flag → provider arg mapping.
  - OpenAI org-verification fallback path (mocked).
  - Rate limiter respects min interval (mocked clock).

### Out of Scope

- Audio generation (BEAN-283).
- Plan-template scaffolding (BEAN-284).
- Implementation of `generate-screen` changes — single-shot CLI surface is preserved so `generate-screen` keeps working without modification (smoke-test only).
- Backwards compatibility shims (per user direction).

## Acceptance Criteria

- [ ] `--plan IMAGE-PLAN.md` mode generates only missing images, skipping existing ones.
- [ ] `--prompt "..."` mode generates one image (single-shot path).
- [ ] `Generator:` frontmatter routes Gemini vs OpenAI correctly, including the regex-tolerant dispatch.
- [ ] Default OpenAI model is `gpt-image-2`; falls back to `gpt-image-1.5` on org-verification error with a warning.
- [ ] `--quality` flag behaves per the mapping table; default is `high`.
- [ ] Sidecar JSON contains every documented field for each successful generation.
- [ ] Gemini rate limiter caps at ~18 req/min; honors `retryDelay` on 429.
- [ ] `--filter`, `--force`, `--dry-run` behave as documented.
- [ ] End-of-run summary prints provider, count, and estimated cost.
- [ ] `.env` discovery walks cwd → parents → `$HOME`.
- [ ] `generate-screen` smoke test still works (single-shot mode unbroken).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | ADR — multi-provider routing | Architect | — | Done |
| 02 | generate-image plan-driven rewrite | Developer | 01 | Done |
| 03 | Verify acceptance criteria | Tech-QA | 01, 02 | Pending |

> Activated: Architect (new external dependency: OpenAI SDK; provider-routing format), Developer, Tech-QA.
> Skipped: BA (requirements concrete from `AGENTIC-MEDIA-SKILLS.md`).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Depends on BEAN-280, BEAN-281.** Asset distribution + shared `_media_lib`.

**`OPENAI_API_KEY` must be added to root `.env`.** Currently only `GEMINI_API_KEY` is present. Document this in BEAN-285.

**`gpt-image-2` requires OpenAI org verification.** Detect the verification error and fall back to `gpt-image-1.5` automatically — don't fail the whole batch. Print a one-line warning so the user knows to verify their org if they want gpt-image-2.

**Cost-table source of truth lives in the script**, not in the bean or docs. When provider prices change, update `generate_image.py` and let docs reference it.

**Reference scripts:** `Course_Material/Git_Fundamentals/scripts/generate_images.py` (495 lines) is the canonical implementation. Copy-and-adapt with attribution; don't re-derive the rate-limit constant or the 429 retry pattern from scratch.

**SKILL.md** — update the existing `.claude/shared/skills/generate-image/SKILL.md` to document the plan-driven mode, frontmatter keys, quality flag, and provider routing. Single-shot mode docs stay.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | ADR — multi-provider routing | Architect | — | — | — | — |
| 02 | generate-image plan-driven rewrite | Developer | — | — | — | — |
| 03 | Verify acceptance criteria | Tech-QA | — | — | — | — |