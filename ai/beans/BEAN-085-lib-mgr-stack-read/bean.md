# BEAN-085: Library Manager — Stack Read

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-085 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 01:52 |
| **Completed** | 2026-02-10 01:52 |
| **Duration** | 0m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot list and view stacks. The existing code in library_manager.py has read logic for stacks, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

When a user clicks on the stack category in the Library Manager tree, all existing stacks from the library are listed in the navigation tree. Selecting one displays its content in the markdown editor.

## Scope

### In Scope
- Navigating to Stack category populates the tree with all existing stacks from the library
- Selecting a stack in the tree loads its content into the markdown editor
- The file path label shows the correct path for the selected stack
- The live preview renders the markdown content correctly
- Tree correctly shows nested files/directories for stacks

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Tree shows all existing stacks when the Stack category is selected
- [x] Clicking a stack file displays its content in the editor pane
- [x] File path label updates to show the selected file path
- [x] Live preview renders the stack markdown correctly
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add stack read tests (pure logic + Qt integration) | Developer | — | Done |
| 2 | Verify existing stack read code works end-to-end | Developer | 1 | Done |

> 15 new tests in `tests/test_stack_read.py` + 11 Qt integration tests in `tests/test_library_manager.py::TestStackRead`.

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
