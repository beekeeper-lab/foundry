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

The wizard needs a page where users select which technology stacks (e.g. Python, React, TypeScript, DevOps) to include in their generated project. The library contains 11 stack packs, each with convention documents. Users must be able to browse, understand, and select one or more stacks, with ordering control since stack order affects prompt compilation.

## Goal

Build the technology stack wizard page where users can browse all available stacks from the library and select one or more for their project. Each stack should display its name, description, and the convention files it includes. Selected stacks should support ordering.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/stack_page.py`
- List all stacks from LibraryIndex (via BEAN-018)
- Multi-select with checkboxes via StackCard components
- Per-stack info: name, description, file count badge
- Per-stack order control (spin box) since StackSelection.order matters
- Visual consistency with persona_page.py (Catppuccin theme, card pattern)
- Data binding to CompositionSpec.stacks (list[StackSelection])

### Out of Scope
- Editing stack content (library browser feature, deferred)
- Creating new stacks
- Stack file previews (full markdown rendering)
- StackOverrides configuration (future extensibility)

## Acceptance Criteria

- [x] All library stacks appear in the selection list
- [x] User can select/deselect stacks with checkboxes
- [x] Each stack shows name, description, and file count
- [x] Per-stack order control is accessible for selected stacks
- [x] At least one stack must be selected to proceed
- [x] Selections populate list[StackSelection] correctly
- [x] All tests pass (`uv run pytest`) — 282 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement technology stack page | developer | — | Done |
| 2 | Write UI and integration tests (42 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (StackSelection model), BEAN-017 (app shell), BEAN-018 (library indexer). This is wizard page 3 of 6.
