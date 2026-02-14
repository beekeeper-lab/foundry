# Task 2: Wire token tracking into task handlers

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | 1 |
| **Started** | 2026-02-14 14:21 |
| **Completed** | 2026-02-14 14:21 |
| **Duration** | < 1m |

## Goal

Integrate the token tracking functions into handle_task_file() and
handle_bean_file():
- On task "In Progress": record watermark
- On task "Done": compute token delta, update bean telemetry row
- On bean "Done": fill Total Tokens In / Total Tokens Out

## Inputs

- `.claude/hooks/telemetry-stamp.py` — with new token functions from Task 1

## Acceptance Criteria

- [ ] handle_task_file() records watermark on In Progress
- [ ] handle_task_file() fills token data on Done
- [ ] handle_bean_file() fills Total Tokens In/Out on Done
- [ ] Graceful fallback when JSONL unavailable

## Definition of Done

Token tracking wired end-to-end.
