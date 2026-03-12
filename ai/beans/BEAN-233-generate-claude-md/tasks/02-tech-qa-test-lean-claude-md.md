# Task 02: Test lean CLAUDE.md generation

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-03-12 03:16 |
| **Completed** | 2026-03-12 03:16 |
| **Duration** | < 1m |

## Goal

Update the existing test suite to validate the new lean CLAUDE.md generation, separate persona/expertise file writing, and the new `description` field on `ProjectIdentity`.

## Inputs

- `tests/test_compiler.py` — existing compiler tests (update for new behavior)
- `tests/test_scaffold.py` — existing scaffold tests (update for new dirs)
- `tests/test_models.py` — existing model tests (add description field test)
- Developer's changes from Task 01

## Definition of Done

- [ ] Existing tests updated to match new compiler output structure
- [ ] Tests verify CLAUDE.md contains project name, description, tech stack, directory overview, pointers
- [ ] Tests verify CLAUDE.md is under 100 lines
- [ ] Tests verify persona content written to `ai/generated/members/<id>.md`
- [ ] Tests verify expertise content written to `ai/generated/expertise/<id>.md`
- [ ] Tests verify persona-specific content NOT in CLAUDE.md
- [ ] All tests pass (`uv run pytest`)
