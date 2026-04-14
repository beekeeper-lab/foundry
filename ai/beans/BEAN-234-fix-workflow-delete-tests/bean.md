# BEAN-234: Fix Workflow Delete Tests

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-234 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-03-08 |
| **Started** | 2026-03-27 15:07 |
| **Completed** | 2026-03-27 15:09 |
| **Duration** | 2m |
| **Owner** | team-lead |
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
| 1 | Fix Test Construction | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| ai/beans/BEAN-234-.../bean.md | +29 -21 |
| ai/beans/BEAN-234-.../tasks/01-developer-fix-tests.md | +32 |
| ai/beans/BEAN-234-.../tasks/02-tech-qa-verification.md | +27 |
| ai/beans/_index.md | +1 -1 |
| tests/test_workflow_delete.py | +5 -5 |

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
| 1 | Fix Test Construction | Developer | 1m | 1,814,991 | 846 | $2.85 |
| 2 | Tech-QA Verification | Tech-QA | < 1m | 333,214 | 201 | $0.54 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 2,148,205 |
| **Total Tokens Out** | 1,047 |
| **Total Cost** | $3.39 |