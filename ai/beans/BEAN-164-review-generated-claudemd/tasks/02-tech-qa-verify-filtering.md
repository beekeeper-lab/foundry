# Task 02: Verify Persona Filtering in Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-20 20:21 |
| **Completed** | 2026-02-20 20:21 |
| **Duration** | < 1m |

## Goal

Verify that the compiler changes from Task 01 correctly filter non-selected persona references, and that all acceptance criteria are met.

## Inputs

- `foundry_app/services/compiler.py` — modified compiler service
- `tests/test_compiler.py` — existing and new tests
- `ai/beans/BEAN-164-review-generated-claudemd/bean.md` — acceptance criteria

## Verification Checklist

- [ ] Run full test suite: `uv run pytest` — all pass
- [ ] Run lint: `uv run ruff check foundry_app/` — clean
- [ ] AC1: Generated CLAUDE.md only references team members that were selected
- [ ] AC2: No extraneous persona/agent references appear for non-selected team members
- [ ] AC3: Generated CLAUDE.md is concise — no verbose boilerplate for unused features
- [ ] AC4: Tests exist covering the filtering logic
- [ ] Edge cases tested: empty team, single persona, all personas selected, persona with no collaboration table

## Example Output

A verification report confirming each acceptance criterion with evidence.

## Definition of Done

- [ ] All acceptance criteria verified with concrete evidence
- [ ] Full test suite passes
- [ ] Lint is clean
- [ ] No regressions identified
