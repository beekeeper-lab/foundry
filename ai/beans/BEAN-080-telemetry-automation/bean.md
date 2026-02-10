# BEAN-080: Bean & Task Telemetry Automation

| Field         | Value        |
| ------------- | ------------ |
| **Bean ID**   | BEAN-080     |
| **Status**    | Done         |
| **Priority**  | High         |
| **Created**   | 2026-02-09   |
| **Started**   | 2026-02-09   |
| **Completed** | 2026-02-09   |
| **Duration**  | <1 day       |
| **Owner**     | team-lead    |
| **Category**  | Process      |

## Problem Statement

The bean template includes a Telemetry section with per-task duration/token tables and bean-level summary totals, and the Team Lead agent documentation describes populating these fields as part of the workflow. However, no skill, command, or code actually writes to these fields. Every completed bean in the repository (75+ beans) has all telemetry fields set to `—` placeholders. The data structures exist but the population logic is completely unimplemented.

Key gaps:
- `/close-loop` mentions "record task completion telemetry" but doesn't write anything
- `/handoff` doesn't record timing or tokens
- `/merge-bean` doesn't roll up task telemetry into bean totals
- No skill records task `Started`/`Completed` timestamps
- No skill prompts agents for self-reported token usage
- No skill computes duration from timestamps
- No skill aggregates task data into the bean's Telemetry summary

## Goal

When a task is started, its timestamp is recorded. When a task completes, the agent is prompted to self-report token usage, the completion timestamp and computed duration are written, and the bean's Telemetry table is updated with the task's row. When a bean is marked Done, the summary totals (total tasks, total duration, total tokens in/out) are computed and filled in.

## Scope

### In Scope
- **`/close-loop` skill**: Add telemetry recording — prompt agent for token usage (format: `X in / Y out`), record `Completed` timestamp, compute `Duration`, update the bean's Telemetry per-task table row
- **`/pick-bean` or `/seed-tasks` skill**: When a task is claimed/started, record `Started` timestamp in the task file metadata
- **`/merge-bean` skill**: When marking a bean Done, aggregate all task telemetry rows and fill in the bean's Telemetry summary table (Total Tasks, Total Duration, Total Tokens In, Total Tokens Out)
- **`/handoff` skill**: Include telemetry data in handoff notes so the receiving persona can continue tracking
- **Task file metadata**: Ensure task files include `Started`, `Completed`, `Duration`, and `Tokens` fields (the seed-tasks template already documents this but may not create them)
- **Duration computation**: Parse `YYYY-MM-DD HH:MM` timestamps, compute difference, format as `Xm` or `Xh Ym`
- **Token format**: Self-reported as `X in / Y out` (comma-formatted numbers)

### Out of Scope
- Automated token extraction from Claude Code API (not available)
- Retroactively populating telemetry for already-completed beans
- Python application code changes (this is purely process/skill changes)
- Changing the bean template structure (it's already correct)

## Acceptance Criteria

- [x] `/close-loop` prompts the completing agent for token usage (self-report)
- [x] `/close-loop` records `Completed` timestamp in the task file
- [x] `/close-loop` computes `Duration` from `Started`/`Completed` timestamps
- [x] `/close-loop` updates the bean's Telemetry per-task table with the task's row (duration + tokens)
- [x] Task files include `Started` timestamp when a task is picked/claimed
- [x] `/merge-bean` computes and fills the bean's Telemetry summary totals when marking Done
- [x] Token self-report uses format `X,XXX in / Y,YYY out`
- [x] Duration format is `Xm` for under 1 hour, `Xh Ym` for 1+ hours
- [x] A bean completed after this change has fully populated Telemetry section
- [x] Existing skills (`/bean-status`) correctly read the populated telemetry data

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Enhance close-loop with telemetry recording | developer | — | Done |
| 2 | Add task Started recording to long-run execution loop | developer | — | Done |
| 3 | Add telemetry rollup to merge-bean | developer | 1 | Done |
| 4 | Include telemetry data in handoff packets | developer | 1 | Done |
| 5 | Verify all telemetry changes | tech-qa | 1,2,3,4 | Done |

## Notes

- Key files to modify:
  - `.claude/skills/close-loop/SKILL.md` — add telemetry recording steps
  - `.claude/skills/pick-bean/SKILL.md` — add `Started` timestamp recording
  - `.claude/skills/merge-bean/SKILL.md` — add telemetry rollup steps
  - `.claude/skills/handoff/SKILL.md` — include telemetry in handoff
  - `.claude/skills/seed-tasks/SKILL.md` — ensure task template includes telemetry fields
  - `.claude/agents/team-lead.md` — already documents telemetry; may need minor updates
- The bean-status skill already reads telemetry (lines 28, 48) so it should work once data is populated
- Self-report is the pragmatic choice since Claude Code doesn't expose a token usage API

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Enhance close-loop with telemetry | team-lead | 3m | — | — |
| 2 | Add Started recording to long-run | team-lead | (incl. in 1) | — | — |
| 3 | Add telemetry rollup to merge-bean | team-lead | (incl. in 1) | — | — |
| 4 | Include telemetry in handoff | team-lead | (incl. in 1) | — | — |
| 5 | Verify all telemetry changes | team-lead | (incl. in 1) | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 5 |
| **Total Duration** | 3m |
| **Total Tokens In** | — (not tracked) |
| **Total Tokens Out** | — (not tracked) |

> Backfilled from git reflog: branch 19:48:11 → merge 19:51:40 (shared commit with BEAN-079). Token data unavailable — ironic for the telemetry bean itself.
