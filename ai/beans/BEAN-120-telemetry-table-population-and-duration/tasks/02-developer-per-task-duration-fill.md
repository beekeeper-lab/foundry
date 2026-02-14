# Task 2: Add per-task duration fill on task Done

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | 1 |
| **Started** | 2026-02-14 14:14 |
| **Completed** | 2026-02-14 14:14 |
| **Duration** | < 1m |

## Goal

Verify that when a task file's status changes to Done, the corresponding
Telemetry table row in bean.md gets its Duration filled in from the task
file's Started→Completed timestamps.

## Inputs

- `.claude/hooks/telemetry-stamp.py` — updated hook from Task 1

## Acceptance Criteria

- [ ] Task file Done → Duration computed from Started/Completed
- [ ] Bean telemetry row updated with the task's duration
- [ ] Already-filled rows are not overwritten
- [ ] Edge cases handled: missing bean.md, no task number in filename

## Definition of Done

Per-task duration propagation working end-to-end.
