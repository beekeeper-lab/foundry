# Task 01: Update Worker Prompts and Dashboard Loop for Reliability

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-21 18:07 |
| **Completed** | 2026-02-21 18:10 |
| **Duration** | 3m |

## Goal

Add reliability improvements to parallel worker prompts and orchestrator dashboard loop: incremental commits, error-exit patterns, and automated stale worker recovery.

## Inputs

- `.claude/skills/long-run/SKILL.md` — worker spawn section (lines 168-192) and dashboard loop (lines 200-223)
- `.claude/commands/long-run.md` — worker prompt (lines 121-146) and dashboard loop (lines 156-171)
- `.claude/commands/internal/spawn-bean.md` — worker prompts (lines 169-248) and dashboard loop (lines 240-327)
- Library mirrors in `ai-team-library/claude/`

## Changes Required

### Worker Prompt Improvements (all 6 files)

Add to worker prompt instructions:

1. **Incremental commits** — "Commit after completing each task, not just at the end. If you stall on task 3 of 4, tasks 1-2 should already be committed."
2. **Error-exit pattern** — "On unrecoverable error: (a) commit any completed work, (b) update status file to `status: error` with a clear message, (c) exit immediately. Do NOT retry indefinitely."
3. **Maximum execution guidance** — "If you've been running for more than 30 minutes, commit whatever is done, set status appropriately, and exit."
4. **Status file heartbeat** — "Update the status file `updated` timestamp after every task, even if nothing else changes. This lets the orchestrator detect stalls."

### Dashboard Loop Improvements (3 files + 3 library mirrors)

Enhance stale worker handling in the continuous assignment dashboard loop:

1. **Configurable stale threshold** — Change from "5+ minutes" to a configurable value (default 10 minutes).
2. **Automated recovery** — When a worker is stale:
   a. Kill the tmux window: `tmux kill-window -t "bean-NNN"`
   b. Remove the worktree: `git worktree remove --force /tmp/foundry-worktree-BEAN-NNN`
   c. Write the status file: `status: error`, `message: Killed by orchestrator (stale for N minutes)`
   d. Log the event to the dashboard
3. **Stale counter** — Track consecutive stale detections before taking action (2 consecutive checks = 1 minute apart means the worker hasn't updated for ~2 minutes, but we wait for the threshold).

## Acceptance Criteria

- [ ] Worker prompts include incremental commit instruction
- [ ] Worker prompts include error-exit pattern
- [ ] Worker prompts include execution time guidance
- [ ] Worker prompts include heartbeat instruction
- [ ] Dashboard loop has automated stale recovery
- [ ] Library templates mirror all changes

## Definition of Done

All files updated with reliability improvements. Worker prompts emphasize commit-early/exit-on-error. Dashboard loop can detect and recover from stalled workers.
