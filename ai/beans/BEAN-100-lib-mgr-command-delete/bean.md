# BEAN-100: Library Manager — Command Delete

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-100 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot delete commands. The existing code in library_manager.py has delete logic for commands, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can select an existing command and delete it via the 'Delete' button with a confirmation dialog. The tree refreshes to reflect the removal.

## Scope

### In Scope
- Selecting a command enables the 'Delete' button
- Clicking 'Delete' shows a confirmation dialog with the command name
- Confirming deletion removes the command from disk
- Tree auto-refreshes and the deleted command is no longer visible
- Cancelling the confirmation dialog leaves the command intact

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [ ] The 'Delete' button is enabled when a command is selected
- [ ] Clicking 'Delete' shows a confirmation dialog naming the command
- [ ] Confirming deletes the command file/directory from disk
- [ ] Tree auto-refreshes and the deleted command is gone
- [ ] Cancelling the dialog preserves the command unchanged
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-099 (Command Update) — need full CRUD chain verified.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
