# BEAN-003: Bean Management Commands

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-003 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

## Problem Statement

Creating beans manually requires copying the template, creating directories, updating the index, and assigning sequential IDs. This is tedious and error-prone. Claude Code commands (`/new-bean`, `/pick-bean`) could automate the boilerplate.

## Goal

Add Claude Code commands and skills to the library that automate bean creation, picking, and status updates.

## Scope

### In Scope
- `/new-bean` command: creates bean directory, copies template, assigns next ID, updates index
- `/pick-bean` command: Team Lead selects bean(s) from backlog, updates status
- `/bean-status` command: shows current bean backlog summary
- Corresponding skills in `.claude/skills/`

### Out of Scope
- Bean decomposition automation (Team Lead does this manually)
- Integration with external issue trackers

## Acceptance Criteria

- [ ] `/new-bean` creates `ai/beans/BEAN-NNN-<slug>/bean.md` with correct ID
- [ ] `/new-bean` updates `ai/beans/_index.md` with the new entry
- [ ] `/pick-bean` updates bean status to `Picked` in both bean.md and index
- [ ] `/bean-status` outputs a readable summary of the backlog
- [ ] Commands are documented in the library's `claude/commands/` directory
- [ ] Skills are documented in the library's `claude/skills/` directory

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

These commands would live in `ai-team-library/claude/commands/` so they're available to any project using the beans workflow, not just Foundry itself.
