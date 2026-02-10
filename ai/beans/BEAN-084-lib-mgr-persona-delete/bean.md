# BEAN-084: Library Manager — Persona Delete

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-084 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot delete personas. The existing code in library_manager.py has delete logic for personas, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can select an existing persona and delete it via the 'Delete' button with a confirmation dialog. The tree refreshes to reflect the removal.

## Scope

### In Scope
- Selecting a persona enables the 'Delete' button
- Clicking 'Delete' shows a confirmation dialog with the persona name
- Confirming deletion removes the persona from disk
- Tree auto-refreshes and the deleted persona is no longer visible
- Cancelling the confirmation dialog leaves the persona intact

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [ ] The 'Delete' button is enabled when a persona is selected
- [ ] Clicking 'Delete' shows a confirmation dialog naming the persona
- [ ] Confirming deletes the persona file/directory from disk
- [ ] Tree auto-refreshes and the deleted persona is gone
- [ ] Cancelling the dialog preserves the persona unchanged
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-083 (Persona Update) — need full CRUD chain verified.

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
