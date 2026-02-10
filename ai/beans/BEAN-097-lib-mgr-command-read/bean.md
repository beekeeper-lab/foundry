# BEAN-097: Library Manager — Command Read

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-097 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 01:53 |
| **Completed** | 2026-02-10 01:53 |
| **Duration** | 0m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot list and view commands. The existing code in library_manager.py has read logic for commands, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

When a user clicks on the command category in the Library Manager tree, all existing commands from the library are listed in the navigation tree. Selecting one displays its content in the markdown editor.

## Scope

### In Scope
- Navigating to Command category populates the tree with all existing commands from the library
- Selecting a command in the tree loads its content into the markdown editor
- The file path label shows the correct path for the selected command
- The live preview renders the markdown content correctly
- Tree correctly shows nested files/directories for commands

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Tree shows all existing commands when the Command category is selected
- [x] Clicking a command file displays its content in the editor pane
- [x] File path label updates to show the selected file path
- [x] Live preview renders the command markdown correctly
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Verify command read logic and add tests | Developer | — | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

This is the foundational bean — Read must work before Create, Update, or Delete can be verified.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 0m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
