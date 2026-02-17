# BEAN-153: Long-Run Continuous Assignment Loop

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-153 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The `/long-run --fast N` orchestrator spawns ~5 beans into tmux windows and then stops. The dashboard loop reads status files and renders progress, but never actually detects worker completion or spawns replacement workers. This is because the replacement logic is described in a separate narrative sub-section ("Worker completion — orchestrator merge") outside the numbered dashboard loop steps (1-8) in `/spawn-bean`. The Claude agent follows the numbered steps literally, rendering the dashboard and sleeping, but never executes the replacement code path.

## Goal

After this bean is complete, `/long-run --fast N` continuously processes the entire approved backlog: when a worker finishes, the orchestrator merges the completed bean, re-reads the backlog to find the next approved bean, spawns a replacement worker, and repeats until no approved beans remain.

## Scope

### In Scope
- Rewrite the dashboard loop in `.claude/commands/internal/spawn-bean.md` Step 4 to integrate worker-done detection, worktree cleanup, merge, backlog re-read, and replacement spawning directly into the numbered loop steps
- Add a concrete bash `while true` polling snippet as a reference implementation alongside the numbered prose steps
- Update `.claude/commands/long-run.md` parallel mode sections ("Bean assignment rules" and "Progress monitoring — dashboard loop") to be consistent with the improved spawn-bean loop
- Ensure the orchestrator re-reads `_index.md` fresh each time a worker finishes (not a pre-computed queue) to pick up newly-approved beans or dependency changes
- No maximum bean limit — the loop runs until no approved beans remain (user can Ctrl-C)

### Out of Scope
- Changes to sequential mode (already works via step 14 "Loop")
- Changes to the worker prompt or status file protocol (these work correctly)
- Adding new CLI flags (no `--max N`)
- Changes to `/merge-bean` command itself
- Changes to how worktrees are created (current pattern works)

## Acceptance Criteria

- [ ] `spawn-bean.md` Step 4 dashboard loop has numbered steps that explicitly include: (a) check each status file for `status: done`, (b) for done workers: remove worktree, run `/internal:merge-bean`, update `_index.md`, (c) re-read backlog for next approved bean, (d) spawn replacement worker with new worktree
- [ ] `spawn-bean.md` includes a concrete bash `while true; do ... sleep 30; done` reference snippet that implements the polling loop
- [ ] `long-run.md` parallel mode "Bean assignment rules" section references the integrated dashboard loop and does not describe replacement logic in a separate disconnected section
- [ ] `long-run.md` "Progress monitoring — dashboard loop" section is consistent with spawn-bean Step 4
- [ ] The loop exit condition is explicit: "exit when all status files show `done` AND no approved beans remain in `_index.md`"
- [ ] The re-read-backlog-each-cycle behavior is explicitly stated (not pre-computed queue)
- [ ] No regressions to sequential mode, `--wide` mode, or single-worker `/spawn-bean` behavior

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Root cause: the numbered dashboard loop steps (1-8) in spawn-bean Step 4 handle rendering and sleep, but replacement spawning is in a separate "Worker completion — orchestrator merge" sub-section that the agent skips.
- Fix approach: merge the "Worker completion" logic directly into the numbered loop steps so the agent cannot miss it.
- The concrete bash snippet serves as a fallback — if the agent struggles with the prose loop, it can execute the bash directly.
- Files changed: `.claude/commands/long-run.md`, `.claude/commands/internal/spawn-bean.md` (2 files)

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
