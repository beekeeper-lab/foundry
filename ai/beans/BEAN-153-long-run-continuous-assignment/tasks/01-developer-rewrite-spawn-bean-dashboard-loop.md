# Task 01: Rewrite spawn-bean Dashboard Loop with Integrated Replacement

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-17 04:35 |
| **Completed** | 2026-02-17 04:36 |
| **Duration** | 1m |

## Goal

Rewrite the dashboard loop in `.claude/commands/internal/spawn-bean.md` Step 4 so that worker-done detection, worktree cleanup, merge, backlog re-read, and replacement spawning are integrated directly into the numbered loop steps — not in a separate disconnected sub-section.

## Inputs

- `.claude/commands/internal/spawn-bean.md` — current spawn-bean spec (Step 4: Dashboard)
- `ai/beans/BEAN-153-long-run-continuous-assignment/bean.md` — acceptance criteria

## Work

1. Rewrite Step 4 "Dashboard — monitor workers from the main window" to replace the current numbered steps (1-8) with an integrated loop that includes:
   - Step: Read all status files
   - Step: For each status file showing `status: done` that hasn't been processed yet — remove worktree, run `/internal:merge-bean`, update `_index.md` on `test`
   - Step: Re-read `_index.md` fresh for next approved bean (not pre-computed queue)
   - Step: If an unblocked approved bean exists, create worktree + spawn replacement worker
   - Step: Render dashboard table
   - Step: Alert on blocked/stale workers
   - Step: Check exit condition: all done AND no approved beans remain
   - Step: Sleep ~30 seconds, repeat

2. Add a concrete bash `while true; do ... sleep 30; done` reference snippet alongside the prose steps.

3. Remove the separate "Worker completion — orchestrator merge" sub-section (its content is now in the numbered steps).

4. Preserve all existing behavior: `--wide` mode, status file protocol, alerting, cleanup.

## Acceptance Criteria

- [ ] Dashboard loop has numbered steps that explicitly include done-detection, merge, re-read, and replacement spawning
- [ ] Concrete bash `while true` reference snippet is present
- [ ] No separate disconnected "Worker completion" sub-section remains
- [ ] `--wide` mode, status file protocol, alerting, and cleanup are preserved
- [ ] Exit condition is explicit: all done AND no approved beans in backlog

## Definition of Done

All acceptance criteria checked, spawn-bean.md updated.
