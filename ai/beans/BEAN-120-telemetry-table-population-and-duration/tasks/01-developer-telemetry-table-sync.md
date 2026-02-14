# Task 1: Add telemetry table sync to telemetry-stamp.py

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-02-14 14:06 |
| **Completed** | 2026-02-14 14:30 |
| **Duration** | — |

## Goal

Add functions to `telemetry-stamp.py` that sync the Telemetry per-task table
with the Tasks table in bean.md. When the Tasks table is filled during
decomposition, the Telemetry table should auto-populate with matching rows.

## Inputs

- `.claude/hooks/telemetry-stamp.py` — existing telemetry hook

## Acceptance Criteria

- [ ] `sync_telemetry_table()` reads Tasks table and creates matching Telemetry rows
- [ ] `update_telemetry_row_duration()` fills Duration column for a specific task
- [ ] `sum_telemetry_durations()` computes total from per-task durations
- [ ] `handle_bean_file()` calls sync on every bean.md edit
- [ ] `handle_task_file()` propagates per-task duration to bean.md when task Done
- [ ] Total Duration prefers sum of per-task durations over git-based duration

## Definition of Done

All helper functions implemented and integrated into the main handlers.
