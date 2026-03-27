# BEAN-234: Fix Workflow Delete Tests

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-234 |
| **Status** | Approved |
| **Priority** | Low |
| **Created** | 2026-03-08 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

`test_workflow_delete.py` has 10 failing tests. The tests use `object.__new__(LibraryManagerScreen)` to construct instances without calling `__init__`, but PySide6's metaclass rejects this with:

```
TypeError: object.__new__(LibraryManagerScreen) is not safe, use LibraryManagerScreen.__new__()
```

This is a PySide6 compatibility issue — Qt widget classes use a custom `__new__` that enforces construction through their own metaclass. The tests need to be updated to construct `LibraryManagerScreen` properly or mock at a different level.

## Goal

All 10 `test_workflow_delete.py` tests pass in both isolation and full suite.

## Scope

### In Scope
- Fix `test_workflow_delete.py` to work with PySide6's metaclass
- Ensure tests still verify delete button state, confirmation dialog, filesystem removal, and tree refresh

### Out of Scope
- Changes to `LibraryManagerScreen` itself
- Other test files

## Acceptance Criteria

- [ ] All 10 `test_workflow_delete.py` tests pass
- [ ] Tests pass in isolation (`uv run pytest tests/test_workflow_delete.py`)
- [ ] Tests pass in full suite (`uv run pytest`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

The 10 failing tests are in `TestWorkflowDeleteButtonState` (3 tests) and `TestWorkflowDeleteFile` (7 tests). The 7 passing tests in other classes (`TestBuildFileTreeWorkflows`, `TestStarterContentForWorkflows`, etc.) use pure functions and don't construct `LibraryManagerScreen`.

> Skipped: BA (default), Architect (default)

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
