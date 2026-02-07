# TASK-004: Integration verification and lint check

| Field | Value |
|-------|-------|
| **Task ID** | TASK-004 |
| **Bean** | BEAN-028 |
| **Owner** | tech-qa |
| **Priority** | 4 |
| **Status** | Pending |
| **Depends On** | TASK-003 |

## Description

Run the full test suite and linter to verify everything passes. Ensure no regressions in existing tests.

## Acceptance Criteria

- [ ] `uv run pytest` passes all tests (including new and existing)
- [ ] `uv run ruff check foundry_app/` reports no issues
- [ ] No regressions in existing test suite
