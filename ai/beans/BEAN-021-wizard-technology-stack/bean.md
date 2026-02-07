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

Users need to select which technology stack convention packs to include in their generated Claude Code project. The library provides 11 stacks (Python, React, TypeScript, etc.), each containing convention documents for coding standards, testing, security, and performance. The wizard needs a page where users can browse, understand, and select the right stacks.

## Goal

Build the technology stack selection wizard page where users can browse all available stacks from the library and select one or more for their project. Each stack should show its name, description, and file count. Selected stacks should have a configurable compilation order.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/stack_page.py`
- List all stacks from LibraryIndex (via BEAN-018)
- Multi-select with checkboxes
- Per-stack info: name, description, file count badge
- Per-stack config: compilation order (spinbox)
- Data binding to CompositionSpec.stacks (list[StackSelection])
- Comprehensive test suite

### Out of Scope
- Editing stack content (library browser feature, deferred)
- Creating new stacks
- Stack file previews (full markdown rendering)
- Drag-and-drop reordering (spinbox is sufficient)

## Acceptance Criteria

- [x] All 11 library stacks appear in the selection list
- [x] User can select/deselect stacks with checkboxes
- [x] Each stack shows name and description
- [x] Per-stack config (compilation order) is accessible
- [x] Stacks are selectable with no minimum requirement (0 stacks is valid)
- [x] Selections populate list[StackSelection] model correctly
- [x] All tests pass (`uv run pytest`) — 286 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement stack selection page | developer | — | Done |
| 2 | Write UI and integration tests (46 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (StackSelection model), BEAN-017 (app shell), BEAN-018 (library indexer). This is wizard page 3 of 6.
