# BEAN-086: Library Manager — Stack Create

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-086 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot create new stacks. The existing code in library_manager.py has create logic for stacks, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can create a new stack via the 'New...' button, providing a name, and the new stack appears immediately in the tree with proper starter content.

## Scope

### In Scope
- Clicking 'New...' when the Stack category is selected prompts for a name
- Valid name creates the stack with proper starter content (stacks/{name}/ directory with conventions.md and other stack docs)
- The tree refreshes to show the newly created stack
- The new stack is automatically selected and its content shown in the editor
- Invalid names (spaces, uppercase, duplicates) show validation errors

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [ ] Clicking 'New...' on Stack category opens a name input dialog
- [ ] Entering a valid name creates the stack with starter content on disk
- [ ] Tree auto-refreshes and the new stack is visible
- [ ] Selecting the new stack shows its starter content in the editor
- [ ] Duplicate name detection prevents overwriting existing stacks
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-085 (Stack Read) — need to see items in the tree to verify creation.

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
