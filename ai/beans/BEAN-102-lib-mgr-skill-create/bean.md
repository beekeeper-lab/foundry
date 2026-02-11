# BEAN-102: Library Manager — Skill Create

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-102 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-09 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 |
| **Duration** | — |
| **Owner** | Developer |
| **Category** | App |

## Problem Statement

In the Library Manager, users cannot create new skills. The existing code in library_manager.py has create logic for skills, but it does not work correctly end-to-end — items may not appear in the tree, operations may not persist, or the UI may not refresh properly.

## Goal

A user can create a new skill via the 'New...' button, providing a name, and the new skill appears immediately in the tree with proper starter content.

## Scope

### In Scope
- Clicking 'New...' when the Skill category is selected prompts for a name
- Valid name creates the skill with proper starter content (claude/skills/{name}/SKILL.md Claude Code skill directories)
- The tree refreshes to show the newly created skill
- The new skill is automatically selected and its content shown in the editor
- Invalid names (spaces, uppercase, duplicates) show validation errors

### Out of Scope
- Other library types (handled by separate beans)
- Library indexer service changes
- Composition editor integration

## Acceptance Criteria

- [x] Clicking 'New...' on Skill category opens a name input dialog
- [x] Entering a valid name creates the skill with starter content on disk
- [x] Tree auto-refreshes and the new skill is visible
- [x] Selecting the new skill shows its starter content in the editor
- [x] Duplicate name detection prevents overwriting existing skills
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-101 (Skill Read) — need to see items in the tree to verify creation.

Key files:
- `foundry_app/ui/screens/library_manager.py` — main Library Manager screen
- `tests/test_library_manager.py` — existing test suite

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 2m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 2m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 165s).
