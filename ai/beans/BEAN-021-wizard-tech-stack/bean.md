# BEAN-021: Wizard — Technology Stack Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-021 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs a page where users select which technology stack packs to include in their generated project. The library contains 11 stacks (python, node, react, typescript, java, dotnet, devops, security, clean-code, sql-dba, python-qt-pyside6), each with convention documents. Users need an intuitive way to browse and select one or more stacks, with ordering support since stack order affects compiled prompt priority.

## Goal

Build the technology stack selection wizard page (page 3 of 6) where users can browse all available stacks from the library and select one or more for their project. Each stack shows its name, file count, and convention documents. Selected stacks can be reordered to control compilation priority.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/stack_page.py`
- List all stacks from LibraryIndex (via BEAN-018)
- Multi-select with checkboxes (card-based UI consistent with persona page)
- Per-stack info: name, description, file count, convention file list
- Ordering support: move up/down buttons for selected stacks
- Data binding to CompositionSpec.stacks (list[StackSelection])
- Validation: at least one stack must be selected to proceed
- Consistent Catppuccin visual theme matching existing wizard pages

### Out of Scope
- Editing stack content (library browser feature, deferred)
- Creating new stacks
- Per-stack overrides (StackOverrides model — future extensibility)
- Stack previews (full markdown rendering)

## Acceptance Criteria

- [x] All library stacks appear in the selection list
- [x] User can select/deselect stacks with checkboxes
- [x] Each stack shows name, description, and file count
- [x] Selected stacks can be reordered (order field in StackSelection)
- [x] At least one stack must be selected to proceed (validation)
- [x] Selections populate list[StackSelection] correctly
- [x] All tests pass (`uv run pytest`) — 296 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement technology stack page | developer | — | Done |
| 2 | Write comprehensive tests (56 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (StackSelection model), BEAN-017 (app shell/wizard framework), BEAN-018 (library indexer). This is wizard page 3 of 6. Follow the same card-based UI pattern established by BEAN-020 (persona page).
