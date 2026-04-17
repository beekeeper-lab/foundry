# BEAN-266: Fix CLAUDE.md Title-Casing for Acronyms and Slashed Names

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-266 |
| **Status** | Approved |
| **Priority** | Low |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
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

- [ ] Generated CLAUDE.md displays `Tech QA`, `UX/UI Designer`, and
      similar names with correct casing.
- [ ] Acronyms are uppercased consistently.
- [ ] Unit tests cover the casing helper.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

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
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
