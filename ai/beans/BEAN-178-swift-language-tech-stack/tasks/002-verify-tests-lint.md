# Task 002: Verify Tests and Lint Pass

| Field | Value |
|-------|-------|
| **Task ID** | 002 |
| **Bean** | BEAN-178 |
| **Owner** | Tech-QA |
| **Status** | Pending |
| **Depends On** | 001 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Description

Run the full test suite and lint checks to verify the new Swift stack file doesn't break anything.

## Acceptance Criteria

- [ ] `uv run pytest` passes with all tests green
- [ ] `uv run ruff check foundry_app/` passes with no errors
- [ ] New stack discovered by stack-loading tests

## Inputs

- Test suite output
- Lint output