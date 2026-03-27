# BEAN-240: Agent Context Budget Optimization

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-240 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-03-27 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

Some beans show 5M+ input tokens for simple file-writing tasks (e.g., BEAN-205 at $12.99 to create one expertise markdown file, BEAN-206 at $11.88). Each API turn sends the full conversation context, so a session with 20 turns at ~250K tokens/turn accumulates 5M total billed input tokens. The agent is loading far more context than needed for the task at hand — reading large files, indexing the full library, or accumulating tool results that bloat the context window.

This is not a telemetry bug — the billing is correct. The problem is agent behavior: skills and agent instructions don't enforce context discipline, and there's no mechanism to track or limit context growth during a session.

## Goal

Agent instructions and key skills include explicit context budgeting guidance that reduces unnecessary context loading for common task patterns, measurably reducing per-bean token costs for simple tasks.

## Scope

### In Scope
- Audit agent files (`.claude/agents/*.md`) for instructions that cause unnecessary context loading (e.g., "read all personas", "index the full library")
- Add "context budget" guidance to agent instructions: for simple tasks (single file create/edit), agents should avoid reading unrelated files
- Update the `/long-run` skill to pass context hints to workers: "this is a simple library content bean, minimize reads"
- Add a "Context Budget" section to `ai/context/bean-workflow.md` with guidelines per bean category:
  - Library content beans: read template + target file only
  - Process beans: read affected doc files only, not entire codebase
  - App beans: read affected modules + test files, not entire service layer
- Review CLAUDE.md size — if it's >500 lines, it contributes significant base context to every turn

### Out of Scope
- Changes to Claude Code itself (can't control context window management)
- Changes to the telemetry system
- Automatic context limiting (can only guide through instructions)
- Reducing CLAUDE.md size (may need a separate bean if it's too large)

## Acceptance Criteria

- [ ] Agent instruction files include context budget guidance
- [ ] `ai/context/bean-workflow.md` has a "Context Budget" section with per-category guidelines
- [ ] `/long-run` skill passes task complexity hints to spawned workers
- [ ] CLAUDE.md size is documented; if >500 lines, a follow-up bean is recommended
- [ ] After implementation, test beans (simple library content) should show <2M total input tokens (down from 5M+)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Evidence from telemetry analysis:
- BEAN-205 (Product Strategy Stack): 5,217,288 tokens in, 1 min, $12.99 — writes one .md file
- BEAN-206 (BI Analytics Stack): 5,308,132 tokens in, 1 min, $11.88 — writes one .md file
- BEAN-166 (Foundry Kit): 5,429,369 tokens in, 1h 39m, $11.43 — complex multi-file work, but similar token count

The first two beans cost as much as a complex 1.5-hour bean for trivially simple work. The context budget should target a 50-75% reduction for simple beans.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
