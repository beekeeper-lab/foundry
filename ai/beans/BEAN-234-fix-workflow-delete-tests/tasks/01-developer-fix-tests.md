# Task 01: Fix Test Construction

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 15:08 |
| **Completed** | 2026-03-27 15:09 |
| **Duration** | 1m |

## Goal

Fix `object.__new__(LibraryManagerScreen)` calls to work with PySide6's metaclass.

## Inputs

- `tests/test_workflow_delete.py`

## Implementation

Replace `object.__new__(LibraryManagerScreen)` with `LibraryManagerScreen.__new__(LibraryManagerScreen)` in `_make_screen()` and in any test class that calls it directly.

## Acceptance Criteria

- [ ] All 10 previously failing tests pass
- [ ] Full test suite passes
- [ ] Lint clean

## Definition of Done

- Tests fixed, all pass, lint clean
