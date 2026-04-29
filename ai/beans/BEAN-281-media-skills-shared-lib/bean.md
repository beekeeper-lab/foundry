# BEAN-281: Media-Skills Shared Library (`_lib/`)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-281 |
| **Status** | In Progress |
| **Priority** | High |
| **Created** | 2026-04-29 |
| **Started** | 2026-04-29 18:46 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |
| **Depends On** | BEAN-280 |

## Problem Statement

The image and audio generators (BEAN-282, BEAN-283) share two non-trivial concerns:

1. **`.env` discovery.** Foundry's root `.env` holds `GEMINI_API_KEY` today and will hold `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` once media skills land. The Stonewaters reference loads `.env` from the script's directory only. The right behavior for a kit-distributed skill is: walk cwd → parents → `$HOME`, take first found, fall back to existing process env. Same logic in two scripts is duplication waiting to drift.
2. **Content-hash dedup.** The Stonewaters audio pipeline computes `sha256(_normalize_text(text))` to dedupe MP3s across pages. The reference doc is explicit: "if you port this skill, port those functions verbatim into your build pipeline." That means the normalizer + hasher must be a portable library, not an inline function in one script.

Building these once, in one place, with tests, is the right thing.

## Goal

A small `.claude/shared/skills/_media_lib/` (or similar) module that both generators (and any downstream build pipeline) import. Tested in isolation. No provider-specific logic.

## Scope

### In Scope

- New directory `.claude/shared/skills/_media_lib/` containing:
  - `env.py` — `load_env()` walks `Path.cwd()` → parents → `Path.home()` looking for `.env`. First found wins. Loads via `python-dotenv` if available, else parses `KEY=VALUE` lines manually. Existing process env always wins over `.env` values.
  - `text.py` — `normalize_narration_text(text: str) -> str` strips markdown markers (`**bold**`, `*italic*`, `` `code` ``, `[text](url)`), HTML tags, the `🎙️` emoji, leading `> ` blockquote markers, and collapses whitespace. Order of regex application matches the Stonewaters reference verbatim (load-bearing).
  - `text.py` — `hash_text(text: str) -> str` returns sha256 hex of `normalize_narration_text(text)`. Used as the content-hash dedup key.
  - `cost.py` — small helpers for cost-table lookups + per-run cost summaries (used by both image and audio generators with their own cost tables).
  - `__init__.py` exporting the public surface.
- Tests in `tests/skills/test_media_lib.py`:
  - `.env` discovery: walks correctly, picks nearest, respects `$HOME`, doesn't override real env.
  - Text normalization: every Stonewaters regex case (bold, italic, code, link, emoji, blockquote, HTML, whitespace).
  - Hash stability: same input → same hash; trivially-different markdown → same hash; semantically-different text → different hash.

### Out of Scope

- Provider-specific code (HTTP clients, retry logic, plan parsing).
- Cost tables themselves (those live in the generators that own them).
- Any modification to existing Foundry services.

## Acceptance Criteria

- [ ] `_media_lib/` module exists in `.claude/shared/skills/` with `env.py`, `text.py`, `cost.py`, `__init__.py`.
- [ ] `_media_lib` is added to `_KIT_DISTRIBUTED_SKILLS` (BEAN-280) so library-copy-mode projects receive it.
- [ ] `load_env()` resolves `.env` from cwd → parents → `$HOME`, with existing process env taking precedence.
- [ ] `normalize_narration_text()` reproduces the Stonewaters reference behavior bit-for-bit on the test cases ported from `Course_Material/Git_Fundamentals/scripts/generate_narration.py`.
- [ ] `hash_text()` returns `sha256(normalize_narration_text(s))` hex digest.
- [ ] Tests pass (`uv run pytest tests/skills/test_media_lib.py`).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | _media_lib shared library + tests | Developer | — | Pending |
| 02 | Verify acceptance criteria | Tech-QA | 01 | Pending |

> Activated: Developer, Tech-QA.
> Skipped: BA (requirements concrete from spec). Architect (default — small library, portability contract captured inline as docstring + locked-down regex-order test rather than a separate ADR; the architectural decision for kit distribution is already in ADR-009 from BEAN-280).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Depends on BEAN-280.** `_media_lib` only reaches library-copy-mode projects via the asset_copier extension.

**Portability is the load-bearing requirement.** A future build pipeline (Foundry-generated or downstream) must produce the same hash for the same normalized text. Don't change normalization order without updating every consumer.

**Why a `_` prefix?** Signals "internal helpers, not user-invokable as a slash command." Mirrors Foundry's existing `internal:*` convention for non-user skills.

**Reference:** `Course_Material/Git_Fundamentals/scripts/generate_narration.py` `_strip_markdown` (~lines 90–110 in current revision) is the canonical normalization order.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | _media_lib shared library + tests | Developer | — | — | — | — |
| 02 | Verify acceptance criteria | Tech-QA | — | — | — | — |