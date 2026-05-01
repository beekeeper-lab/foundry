# Task 01 — Developer: Casing Helper + Compiler Display-Name Fix

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 19:29 |
| **Completed** | 2026-04-17 19:29 |
| **Duration** | < 10m |

## Goal

Replace `.replace("-", " ").title()` in `foundry_app/services/compiler.py::_build_lean_claude_md` with a casing helper that preserves acronym capitalization (`Tech QA`, `UX/UI Designer`), driven primarily by each persona's own `# Persona: <Name>` header.

## Inputs

- `foundry_app/services/compiler.py` (target — lines ~414, ~442 use `.title()`)
- `ai-team-library/personas/*/persona.md` (source of `# Persona: <Name>` headers)
- `ai/beans/BEAN-266-fix-claudemd-title-casing/bean.md` (this bean)

## Required Changes

1. **`foundry_app/services/compiler.py`** (modify)
   - Add module-level `_ACRONYMS: frozenset[str]` containing at least: `qa`, `ui`, `ux`, `api`, `sre`, `ml`, `ai`, `ba`, `sql`, `dba`.
   - Add helper `_display_name_from_id(identifier: str) -> str`:
     - Split on `-`; for each part, uppercase if in `_ACRONYMS`, else `.capitalize()`.
     - Consecutive acronym parts join with `/` (so `ux-ui-designer` → `UX/UI Designer`).
     - Non-acronym runs separate with a single space.
   - Add helper `_canonicalize_persona_header(name: str) -> str`:
     - Strip trailing parenthetical annotation `\s*\([^)]+\)\s*`.
     - Split on ` / `. While consecutive segments both start with a short (≤ 3 char) all-upper token, merge with `/`. Otherwise keep only the first segment.
     - `Tech-QA / Test Engineer` → `Tech-QA`; `UX / UI Designer` → `UX/UI Designer`; `Business Analyst (BA)` → `Business Analyst`.
   - Add helper `_persona_display_name(persona_id: str, index: LibraryIndex) -> str`:
     - Look up the persona; read its `persona.md`; extract header via existing `_PERSONA_HEADER_RE`.
     - If found, return `_canonicalize_persona_header(header)`; else fall back to `_display_name_from_id`.
   - In `_build_lean_claude_md`:
     - **Tech Stack table**: replace `eid.replace("-", " ").title()` with `_display_name_from_id(eid)`.
     - **Team table**: replace `pid.replace("-", " ").title()` with a name passed in from `compile_project` (resolved via `_persona_display_name`). Easiest: change the `persona_descriptions` tuple to `(id, display, desc)` or introduce a parallel `persona_display_names` dict parameter. Keep the signature minimally invasive.
   - Keep function bodies small; no broader refactors.

## Acceptance Criteria

- [ ] `_display_name_from_id("tech-qa") == "Tech QA"` and `_display_name_from_id("ux-ui-designer") == "UX/UI Designer"`.
- [ ] Generated CLAUDE.md Team table shows `Tech-QA` (from the persona header) — NOT `Tech Qa` — and `UX/UI Designer` — NOT `Ux Ui Designer`.
- [ ] Tech Stack table entries like `sql-dba` render as `SQL/DBA` (or similar acronym-preserving form), not `Sql Dba`.
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] No other files modified.
