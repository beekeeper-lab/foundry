# BEAN-283: `generate-audio` Skill (ElevenLabs Narration)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-283 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 20:11 |
| **Completed** | 2026-04-29 20:58 |
| **Duration** | 47m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-280, BEAN-281 |

## Problem Statement

Foundry has no audio-generation skill today. The reference design (`AGENTIC-MEDIA-SKILLS.md` — "Audio-generation skill" section) defines the shape:

- Narration text lives **inline** in source markdown as `> 🎙️ ...` blockquotes (the contract).
- A `NARRATION-PLAN.md` enumerates blocks per source file with char counts and DONE/MISSING flags (the review surface).
- A generator script reads the inline blocks, strips markdown markers before sending to ElevenLabs (so "star star" isn't pronounced), writes one MP3 per block plus a `manifest.json` per source file.
- Manifests record the **stripped** text — required for content-hash dedup across pages.
- ElevenLabs is 1 credit per character; cost is fully predictable from char counts in the plan.

This is a portable, plan-first, sidecar-driven skill that mirrors the image skill's architecture. It belongs in ClaudeKit so every consumer gets it.

## Goal

A new `generate-audio` skill in ClaudeKit that scans source markdown for `> 🎙️` blocks, generates ElevenLabs MP3s, writes manifests, supports skip-on-disk and content-aware regeneration, and prints char/credit costs. Available in subtree-mode and library-copy-mode generated projects via BEAN-280's distribution.

## Scope

### In Scope

- **New `.claude/shared/skills/generate-audio/`** containing:
  - `generate_audio.py` — adapted from `Course_Material/Git_Fundamentals/scripts/generate_narration.py` (274 lines). Attribution in header comment.
  - `SKILL.md` — usage doc.
- **Inline `> 🎙️` block scanner**: walks source markdown files, captures contiguous blockquoted lines starting with the microphone emoji. Configurable source-file glob (default `module-*.md`).
- **Pre-send markdown stripping** via `_media_lib.text.normalize_narration_text` (BEAN-281). This is what's sent to ElevenLabs and what's stored in the manifest's `text` field.
- **Per-source-file manifest** at `audio/<source-stem>/manifest.json`: array of `{index, module, audio_file, text, size_bytes}`. Index is 1-based and matches the `NN_` prefix on the MP3 filename.
- **Voice routing**:
  - Default voice `rachel` (`21m00Tcm4TlvDq8ikWAM`). Voice map covers a few well-known names; unknown values pass through as raw IDs.
  - `--voice <name-or-id>` CLI override.
  - **No cloned voice IDs in the source** (per user direction — Gregg's cloned voice ID stays in his project plans, not in the kit).
- **`NARRATION-PLAN.md` parser** for `Voice:` and `Model:` frontmatter (informational; CLI flags override).
- **ElevenLabs default model**: `eleven_multilingual_v2`. Override via `--model` and frontmatter.
- **Skip-on-disk semantics**:
  - Missing MP3 → generate.
  - `--regenerate-changed` → regenerate when current stripped text differs from the manifest's `text` field.
  - `--force` → regenerate everything for the run.
  - `--dry-run` → walk plan, print plan, no API calls.
  - `--all` → include auxiliary source files (default is `module-*.md` only).
- **Orphan cleanup**: when rewriting a manifest, remove MP3s whose blocks no longer exist in source.
- **Cost reporting**: end-of-run summary prints total chars sent = total credits spent. Plan-aware: when invoked with a `NARRATION-PLAN.md` it can print "this run: X credits; remaining in plan: Y credits."
- **`.env` discovery via `_media_lib.env.load_env`** (BEAN-281). Requires `ELEVENLABS_API_KEY`.
- **Add `generate-audio` to `_KIT_DISTRIBUTED_SKILLS`** (BEAN-280).
- **Tests** (`tests/skills/test_generate_audio.py`):
  - Block scanner: finds `> 🎙️` blocks, ignores other blockquotes, handles multi-line blocks.
  - Stripping: matches `_media_lib.text.normalize_narration_text` output (delegated, not re-tested).
  - Manifest writer: shape and stripped-text invariant.
  - Skip-on-disk modes: missing/regenerate-changed/force/dry-run all behave correctly.
  - Orphan cleanup: removes MP3s whose blocks no longer exist.
  - Voice map: rachel resolves to ID; unknown name → passthrough; `--voice` overrides frontmatter.
  - Char-count cost report.

### Out of Scope

- Plan-template scaffolding (BEAN-284 ships `NARRATION-PLAN.md` skeleton).
- Build pipeline / content-hash audio reuse across pages — this is a build-time concern. The reference doc points to `build_course.py` as the consumer; Foundry-generated projects don't have a fixed build target. The library function exists in `_media_lib.text.hash_text` (BEAN-281) and a usage example will live in BEAN-285's docs.
- HTML rendering or data-URI embedding — out of scope; build-pipeline concerns.
- Cloned voice ID in source — explicitly excluded (per user). Lives in user's project plans only.

## Acceptance Criteria

- [x] Skill at `.claude/shared/skills/generate-audio/` with generator + SKILL.md.
- [x] Walks source markdown, finds `> 🎙️` blocks, generates MP3 per block.
- [x] Strips markdown markers before sending to ElevenLabs (delegated to `_media_lib`).
- [x] Writes per-source manifest with stripped text.
- [x] Default voice `rachel`; `--voice` overrides; voice map handles names + raw IDs.
- [x] Default model `eleven_multilingual_v2`; `--model` overrides.
- [x] Skip-on-disk: missing → generate; `--force`, `--regenerate-changed`, `--dry-run`, `--all` all behave per spec.
- [x] Orphan MP3s removed on manifest rewrite.
- [x] End-of-run summary prints char-count = credits.
- [x] `.env` discovery resolves `ELEVENLABS_API_KEY`.
- [x] No cloned voice IDs in committed code.
- [x] All tests pass (`uv run pytest`) — 2150 passed (+69 from baseline).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | ADR — audio skill design | Architect | — | Done |
| 02 | generate-audio implementation | Developer | 01 | Done |
| 03 | Verify acceptance criteria | Tech-QA | 01, 02 | Done |

> Activated: Architect (new external dependency: ElevenLabs SDK; manifest format is a cross-system contract via content-hash), Developer, Tech-QA.
> Skipped: BA (requirements concrete from `AGENTIC-MEDIA-SKILLS.md`).

## Changes

| File | Lines |
|------|-------|
| `.claude/shared` (submodule pointer — generate-audio skill + ADR) | +1 −1 |
| `ai/beans/BEAN-283-generate-audio-skill/bean.md` | +35 −16 |
| `ai/beans/BEAN-283-generate-audio-skill/tasks/01-architect-audio-skill-adr.md` | +74 −0 |
| `ai/beans/BEAN-283-generate-audio-skill/tasks/02-developer-generate-audio-implementation.md` | +106 −0 |
| `ai/beans/BEAN-283-generate-audio-skill/tasks/03-tech-qa-verify-generate-audio.md` | +157 −0 |
| `ai/context/decisions.md` (ADR-011) | +387 −9 |
| `foundry_app/services/asset_copier.py` (`generate-audio` registered) | +1 −0 |
| `tests/test_generate_audio.py` | +856 −0 |
| **Total** | **+1,617 −26** |

## Notes

**Depends on BEAN-280, BEAN-281.** Asset distribution + `_media_lib` text normalization.

**`ELEVENLABS_API_KEY` must be added to root `.env`.** Document in BEAN-285.

**Cost discipline.** ElevenLabs Pro is 500K credits/month at $100. A 200-block course of ~600 chars/block burns ~24% of the monthly cap. The cost summary on every run is essential for the user to pace work — not an optional nicety.

**Reference script:** `Course_Material/Git_Fundamentals/scripts/generate_narration.py` (274 lines) is the canonical implementation. Adapt with attribution. The stripping regex order, blockquote scanner, and orphan cleanup all carry production knowledge.

**Manifest contract is portable.** The manifest's `text` field must be the stripped text. Any downstream pipeline that hashes text to dedupe MP3s (`_media_lib.text.hash_text`) depends on this.

**Voice IDs.** ElevenLabs accepts names registered in your voice library OR raw voice IDs. The voice map covers `rachel` and a few stock names. Unknown values are passed through to ElevenLabs as-is — works for raw IDs and for names the user has registered.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | ADR — audio skill design | Architect | 3m | — | — | — |
| 02 | generate-audio implementation | Developer | 27m | — | — | — |
| 03 | Verify acceptance criteria | Tech-QA | 2m | — | — | — |
| **Total** | 3 tasks | — | **32m** | — | — | — |