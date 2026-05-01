# Task 01: Drop Missing Expertise References from Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-17 17:42 |
| **Completed** | 2026-04-17 17:43 |
| **Duration** | 1m |

## Goal

Update `foundry_app/services/compiler.py` so a generated `CLAUDE.md` never
lists an expertise whose source file was not emitted. The existing warning
for missing `conventions.md` must still be emitted via `StageResult.warnings`.

## Inputs

- `foundry_app/services/compiler.py` — `compile_project()` and `_build_lean_claude_md()`
- `tests/test_compiler.py` — existing compiler unit tests

## Changes Required

1. In `compile_project()`, track only the expertise IDs for which
   `_compile_expertise_section` returned a non-None section (i.e. the file
   was actually written to `ai/generated/expertise/<id>.md`).
2. Pass that filtered, order-preserving list to `_build_lean_claude_md()`
   instead of the full `expertise_ids` from the spec.
3. Do not change the warning behavior — the
   `Expertise '<id>' missing conventions.md` warning stays.

## Acceptance Criteria

- [ ] When an expertise source is missing, the generated `CLAUDE.md` has no
      `ai/generated/expertise/<id>.md` reference in the Tech Stack table
      for that expertise.
- [ ] The "missing conventions.md" warning is still emitted.
- [ ] A new unit test in `tests/test_compiler.py` asserts that a missing
      expertise does not appear as a `ai/generated/expertise/<id>.md`
      reference in the generated `CLAUDE.md`.
- [ ] `uv run pytest tests/test_compiler.py` passes.
- [ ] `uv run ruff check foundry_app/` passes.

## Definition of Done

- Compiler change lands.
- New unit test verifies the behavior.
- Full test suite (`uv run pytest`) passes.
- Lint clean (`uv run ruff check foundry_app/`).
