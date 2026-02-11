# BEAN-106: Library Manager — Hook Create

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-106 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 |
| **Duration** | — |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot create new hooks. The existing code in library_manager.py has create logic for hooks, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can create a new hook via the 'New...' button, providing a name, and the new hook appears immediately in the tree with proper starter content.

## Scope

### In Scope
- Clicking 'New...' when the Hook category is selected prompts for a name
- Valid name creates the hook with proper starter content (claude/hooks/{name}.md hook pack files)
- The tree refreshes to show the newly created hook
- The new hook is automatically selected and its content shown in the editor
- Invalid names (spaces, uppercase, duplicates) show validation errors

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Clicking 'New...' on Hook category opens a name input dialog
- [x] Entering a valid name creates the hook with starter content on disk
- [x] Tree auto-refreshes and the new hook is visible
- [x] Selecting the new hook shows its starter content in the editor
- [x] Duplicate name detection prevents overwriting existing hooks
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-105 (Hook Read) — need to see items in the tree to verify creation.

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

> Duration backfilled from git timestamps (commit→merge, 14s).
