# BEAN-101: Library Manager — Skill Read

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-101 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 02:02 |
| **Completed** | 2026-02-10 02:02 |
| **Duration** | 0m |
| **Owner** | developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot list and view skills. The existing code in library_manager.py has read logic for skills, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

When a user clicks on the skill category in the Library Manager tree, all existing skills from the library are listed in the navigation tree. Selecting one displays its content in the markdown editor.

## Scope

### In Scope
- Navigating to Skill category populates the tree with all existing skills from the library
- Selecting a skill in the tree loads its content into the markdown editor
- The file path label shows the correct path for the selected skill
- The live preview renders the markdown content correctly
- Tree correctly shows nested files/directories for skills

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Tree shows all existing skills when the Skill category is selected
- [x] Clicking a skill file displays its content in the editor pane
- [x] File path label updates to show the selected file path
- [x] Live preview renders the skill markdown correctly
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Verify skill read logic in library_manager.py | developer | — | Done |
| 2 | Write skill read tests (tests/test_skill_read.py) | developer | 1 | Done |
| 3 | Run tests and lint | developer | 2 | Done |

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
