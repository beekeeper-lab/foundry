# Task 04: Full Test Suite & Lint Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 03 |
| **Status** | Done |
| **Started** | 2026-02-16 00:07 |
| **Completed** | 2026-02-16 00:09 |
| **Duration** | 2m |

## Goal

Run the complete test suite and lint checks to ensure nothing is broken by the safety writer rewrite.

## Inputs

- Full test suite (`uv run pytest`)
- Lint check (`uv run ruff check foundry_app/`)

## Approach

1. Run `uv run pytest` — all tests must pass
2. Run `uv run ruff check foundry_app/` — zero violations
3. Fix any failures or lint issues found

## Acceptance Criteria

- [ ] All tests pass (`uv run pytest`)
- [ ] Zero lint violations (`uv run ruff check foundry_app/`)
- [ ] No regressions in other test files

## Definition of Done

Full green test suite and clean lint.
