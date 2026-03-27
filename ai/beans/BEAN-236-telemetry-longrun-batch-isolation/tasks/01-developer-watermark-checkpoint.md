# Task 01: Watermark Checkpoint Mechanism

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 11:29 |
| **Completed** | 2026-03-27 11:36 |
| **Duration** | 7m |

## Goal

Fix the telemetry watermark system so that sequential tasks within a single `/long-run` session have isolated token counts. Add a "session checkpoint" mechanism that records the token position after each task completes, so the next task's delta starts from the correct baseline.

## Inputs

- `.claude/hooks/telemetry-stamp.py` — the hook that manages watermarks and token telemetry

## Problem Analysis

Two bugs in the current watermark flow:

1. **Pending → Done skip**: When a task transitions directly from Pending to Done (skipping In Progress), no watermark is saved. The Done handler falls back to full session tokens, which is wrong for any task after the first.

2. **No inter-task checkpoint**: After task N completes, there's no record of the session token position. When task N+1 starts (or goes directly to Done), it has no baseline to compute a delta from.

## Implementation

In `telemetry-stamp.py`:

1. **Add a `save_checkpoint` function** — After a task is marked Done and its token delta is computed, save a `_checkpoint` entry in the `.telemetry.json` watermark file with the current cumulative session tokens. This acts as the baseline for the next task.

2. **Add a `load_checkpoint` function** — Returns the last checkpoint's token values from `.telemetry.json`.

3. **Fix the Done handler for missing watermarks** — In `handle_task_file`, when a task has status=Done and no task-specific watermark exists:
   - Load the session checkpoint (from the previous task's completion)
   - If a checkpoint exists, use it as the baseline and compute the delta
   - If no checkpoint exists either (first task in the session), fall back to full session tokens (existing behavior, which is correct for the first task)

4. **Save checkpoint after every task completion** — After computing and recording the token delta for a completed task, save the current session token position as the new checkpoint.

## Acceptance Criteria

- [ ] When a task goes from Pending to Done in one edit, token counts are still computed correctly
- [ ] Sequential tasks in one session have isolated token counts (task 2 doesn't include task 1's tokens)
- [ ] The checkpoint mechanism persists across bean boundaries within one session
- [ ] First task in a session (no checkpoint, no watermark) still works correctly
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Definition of Done

- `telemetry-stamp.py` updated with checkpoint mechanism
- Watermark save/load cycle handles the Pending → Done skip case
- Tests pass, lint clean
