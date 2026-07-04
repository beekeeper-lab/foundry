# BEAN-266: Fix CLAUDE.md Title-Casing for Acronyms and Slashed Names

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-266 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:28 |
| **Completed** | 2026-04-17 19:31 |
| **Duration** | 3m (corrected 2026-07) |
| **Owner** | Team Lead |
| **Category** | App |

## Problem Statement

External review (2026-04-17): "Title-casing bugs in CLAUDE.md:
'Ux Ui Designer', 'Tech Qa'."

Confirmed in a fresh `small-python-team` generation: the Team table
contains `| Tech Qa | Software Development | ... |`. The compiler
converts persona IDs to display names via `.replace("-", " ").title()`,
which lowercases acronym characters after the first.

## Goal

Persona display names render acronyms in uppercase (`Tech QA`,
`UX/UI Designer`) and preserve intentional slashes.

## Scope

### In Scope
- Fix the display-name rendering in `foundry_app/services/compiler.py`
  (`_build_lean_claude_md` — the Team and Tech Stack tables use
  `.replace("-", " ").title()`).
- Add an acronym/phrase dictionary (e.g. `{"qa": "QA", "ui": "UI",
  "ux": "UX", "api": "API", "ml": "ML"}`) applied post-title-case, or
  derive display names from the persona's own `persona.md` `#` header.
- Tests: a persona with ID `tech-qa` renders as `Tech QA`, and
  `ux-ui-designer` renders as `UX/UI Designer` (or similar canonical
  form).

### Out of Scope
- Renaming persona IDs themselves.
- Localizing display names.

## Acceptance Criteria

- [x] Generated CLAUDE.md displays `Tech-QA`, `UX/UI Designer`, and
      similar names with correct casing.
- [x] Acronyms are uppercased consistently.
- [x] Unit tests cover the casing helper.
- [x] All tests pass (`uv run pytest` — 1923 passed).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

> Skipped: BA (default), Architect (default).

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Casing helper + compiler display-name fix | Developer | — | Done |
| 2 | Tests for casing helper and generated CLAUDE.md tables | Tech-QA | 1 | Done |

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/compiler.py` | +~95 / -7 |
| `tests/test_compiler.py` | +~155 / -1 |
| `ai/beans/BEAN-266-fix-claudemd-title-casing/bean.md` | +~10 / -5 |
| `ai/beans/BEAN-266-fix-claudemd-title-casing/tasks/01-developer-casing-helper.md` | +60 |
| `ai/beans/BEAN-266-fix-claudemd-title-casing/tasks/02-tech-qa-casing-tests.md` | +40 |

## Notes

**Source.** External review (2026-04-17). Confirmed in a fresh
`small-python-team` generation.

**Preferred approach.** Reading the display name from each persona's
own `persona.md` `# Persona: <Name>` header (which is already parsed for
the name-to-id map) is more robust than a hard-coded acronym list.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Casing helper + compiler display-name fix | Developer | < 10m | 889,500 | 33,781 | $6.04 |
| 2 | Tests for casing helper and generated CLAUDE.md tables | Tech-QA | < 10m | 87,086 | 113 | $0.15 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1270h 23m |
| **Total Tokens In** | 976,586 |
| **Total Tokens Out** | 33,894 |
| **Total Cost** | $6.19 |