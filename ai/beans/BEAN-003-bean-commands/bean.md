# BEAN-003: Bean Management Commands

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-003 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

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

- [x] `/new-bean` creates `ai/beans/BEAN-NNN-<slug>/bean.md` with correct ID
- [x] `/new-bean` updates `ai/beans/_index.md` with the new entry
- [x] `/pick-bean` updates bean status to `Picked` in both bean.md and index
- [x] `/bean-status` outputs a readable summary of the backlog
- [x] Commands documented in `.claude/commands/` (3 files)
- [x] Skills documented in `.claude/skills/` (3 directories with SKILL.md)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Create Bean Commands & Skills | developer | — | Done |
| 02 | Bean Commands Verification | tech-qa | 01 | Done |

> BA and Architect skipped — no requirements ambiguity or architectural decisions. This bean creates markdown command/skill files, not Python code.

## Notes

These commands would live in `ai-team-library/claude/commands/` so they're available to any project using the beans workflow, not just Foundry itself.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (single commit, no merge).
