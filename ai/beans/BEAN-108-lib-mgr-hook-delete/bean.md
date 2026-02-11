# BEAN-108: Library Manager — Hook Delete

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-108 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 |
| **Duration** | — |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot delete hooks. The existing code in library_manager.py has delete logic for hooks, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can select an existing hook and delete it via the 'Delete' button with a confirmation dialog. The tree refreshes to reflect the removal.

## Scope

### In Scope
- Selecting a hook enables the 'Delete' button
- Clicking 'Delete' shows a confirmation dialog with the hook name
- Confirming deletion removes the hook from disk
- Tree auto-refreshes and the deleted hook is no longer visible
- Cancelling the confirmation dialog leaves the hook intact

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] The 'Delete' button is enabled when a hook is selected
- [x] Clicking 'Delete' shows a confirmation dialog naming the hook
- [x] Confirming deletes the hook file/directory from disk
- [x] Tree auto-refreshes and the deleted hook is gone
- [x] Cancelling the dialog preserves the hook unchanged
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Verify hook delete logic and add comprehensive tests | Developer | — | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-107 (Hook Update) — need full CRUD chain verified.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 57s).
