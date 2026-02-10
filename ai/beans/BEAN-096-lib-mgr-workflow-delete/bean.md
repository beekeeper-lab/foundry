# BEAN-096: Library Manager — Workflow Delete

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-096 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot delete workflows. The existing code in library_manager.py has delete logic for workflows, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can select an existing workflow and delete it via the 'Delete' button with a confirmation dialog. The tree refreshes to reflect the removal.

## Scope

### In Scope
- Selecting a workflow enables the 'Delete' button
- Clicking 'Delete' shows a confirmation dialog with the workflow name
- Confirming deletion removes the workflow from disk
- Tree auto-refreshes and the deleted workflow is no longer visible
- Cancelling the confirmation dialog leaves the workflow intact

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [ ] The 'Delete' button is enabled when a workflow is selected
- [ ] Clicking 'Delete' shows a confirmation dialog naming the workflow
- [ ] Confirming deletes the workflow file/directory from disk
- [ ] Tree auto-refreshes and the deleted workflow is gone
- [ ] Cancelling the dialog preserves the workflow unchanged
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-095 (Workflow Update) — need full CRUD chain verified.

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
