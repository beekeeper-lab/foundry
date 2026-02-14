# BEAN-120: Telemetry Table Population & Duration Tracking

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-120 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-14 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The Telemetry section at the bottom of every bean.md has a per-task table with columns (#, Task, Owner, Duration, Tokens In, Tokens Out) but it is never populated. Recent completed beans (BEAN-117, BEAN-118, BEAN-119) all show a single empty template row despite having 5-7 completed tasks each. The telemetry hook (`telemetry-stamp.py`) correctly stamps Started/Completed timestamps on individual task files, and computes bean-level Duration — but it never transfers per-task data into the bean's Telemetry table. The `/close-loop` skill is supposed to do this (step 8) but is not effectively invoked during `/long-run`. Without per-task duration data, we cannot compute average task times, compare planning vs building vs validating effort, or identify which personas take the longest.

## Goal

Every completed bean has a fully populated Telemetry table where each row matches a task from the Tasks table, with task name, owner, and duration filled in. Bean-level totals (Total Tasks, Total Duration) are accurately computed from per-task data.

## Scope

### In Scope
- Update the telemetry hook to auto-populate Telemetry table rows when tasks are created during decomposition (pre-fill #, Task name, Owner from the Tasks table)
- Update the telemetry hook to fill in per-task Duration when a task is marked Done (compute from the task file's Started→Completed timestamps)
- Ensure the Telemetry table row count stays in sync with the Tasks table (add rows for new tasks, don't remove existing data)
- Compute Total Duration as the sum of per-task durations (wall-clock, not the git-based bean duration)
- Ensure Total Tasks is accurately counted from per-task rows, not just a generic count
- Handle edge cases: tasks added after initial decomposition, tasks skipped, tasks with no task file

### Out of Scope
- Token tracking (separate bean: BEAN-121)
- Changing the bean template format (the table structure is fine)
- Backfilling telemetry for already-completed beans (not worth the effort)
- Modifying `/long-run` or `/close-loop` skill process (fix the hook, not the caller)

## Acceptance Criteria

- [ ] When tasks are decomposed (Tasks table filled in bean.md), the Telemetry table auto-populates with matching rows (#, Task name, Owner, empty Duration/Tokens)
- [ ] When a task file's status changes to Done, the corresponding Telemetry table row gets its Duration filled in (from Started→Completed in the task file)
- [ ] Total Tasks in the summary table equals the number of per-task rows
- [ ] Total Duration in the summary table equals the sum of per-task durations
- [ ] Running `/long-run` on a test bean produces a fully populated Telemetry table
- [ ] The hook handles tasks added after initial decomposition (new rows appended)
- [ ] The hook does not overwrite already-filled Telemetry rows
- [ ] All existing tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- The telemetry hook fires on every Edit/Write to bean.md and task files — it has access to both file types
- Task files already get Started/Completed timestamps stamped by the hook
- The Tasks table in bean.md has columns: #, Task, Owner, Depends On, Status
- The Telemetry table in bean.md has columns: #, Task, Owner, Duration, Tokens In, Tokens Out
- The hook should read the Tasks table and mirror rows into the Telemetry table
- Duration format should be consistent with existing format: `< 1m`, `Xm`, `Xh Ym`
- The hook currently uses `format_duration()` and `format_seconds()` — reuse these
- Token columns should remain `—` until BEAN-121 (Token Usage Capture) is implemented
- This bean depends on nothing and unblocks BEAN-121

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
