# BEAN-093: Library Manager — Workflow Read

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-093 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot list and view workflows. The existing code in library_manager.py has read logic for workflows, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

When a user clicks on the workflow category in the Library Manager tree, all existing workflows from the library are listed in the navigation tree. Selecting one displays its content in the markdown editor.

## Scope

### In Scope
- Navigating to Workflow category populates the tree with all existing workflows from the library
- Selecting a workflow in the tree loads its content into the markdown editor
- The file path label shows the correct path for the selected workflow
- The live preview renders the markdown content correctly
- Tree correctly shows nested files/directories for workflows

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [ ] Tree shows all existing workflows when the Workflow category is selected
- [ ] Clicking a workflow file displays its content in the editor pane
- [ ] File path label updates to show the selected file path
- [ ] Live preview renders the workflow markdown correctly
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

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
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
