# BEAN-082: Library Manager — Persona Create

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-082 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 |
| **Duration** | — |
| **Owner** | developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot create new personas. The existing code in library_manager.py has create logic for personas, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can create a new persona via the 'New...' button, providing a name, and the new persona appears immediately in the tree with proper starter content.

## Scope

### In Scope
- Clicking 'New...' when the Persona category is selected prompts for a name
- Valid name creates the persona with proper starter content (personas/{name}/ directory with persona.md, outputs.md, prompts.md, templates/)
- The tree refreshes to show the newly created persona
- The new persona is automatically selected and its content shown in the editor
- Invalid names (spaces, uppercase, duplicates) show validation errors

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Clicking 'New...' on Persona category opens a name input dialog
- [x] Entering a valid name creates the persona with starter content on disk
- [x] Tree auto-refreshes and the new persona is visible
- [x] Selecting the new persona shows its starter content in the editor
- [x] Duplicate name detection prevents overwriting existing personas
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add auto-select after persona creation | developer | — | Done |
| 2 | Add test for auto-select behavior | developer | 1 | Done |
| 3 | Run tests, lint, finalize | developer | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-081 (Persona Read) — need to see items in the tree to verify creation.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 3m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 3m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 209s).
