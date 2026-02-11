# BEAN-107: Library Manager — Hook Update

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-107 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 |
| **Duration** | 1 session |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot edit and save hooks. The existing code in library_manager.py has update logic for hooks, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can select an existing hook, edit its markdown content in the editor, save changes, and confirm the file on disk is updated.

## Scope

### In Scope
- Selecting a hook loads its current content into the editor
- Editing the content marks the editor as dirty (shows modified indicator)
- Clicking 'Save' writes the changes to disk
- Clicking 'Revert' discards unsaved changes and reloads the file
- Live preview updates as the user types

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Selecting a hook loads its content into the editor
- [x] Editing text triggers the dirty/modified state indicator
- [x] Clicking 'Save' persists changes to disk and clears the dirty state
- [x] Clicking 'Revert' restores the original content and clears the dirty state
- [x] The live preview updates in real-time during editing
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-106 (Hook Create) — need items to exist to test editing.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 81s).
