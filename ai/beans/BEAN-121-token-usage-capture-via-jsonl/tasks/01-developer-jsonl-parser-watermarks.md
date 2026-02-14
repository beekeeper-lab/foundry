# Task 1: Add JSONL token parser and watermark system

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-02-14 14:19 |
| **Completed** | 2026-02-14 14:21 |
| **Duration** | 2m |

## Goal

Add functions to `telemetry-stamp.py` that:
1. Find and parse the current Claude Code conversation JSONL file
2. Sum cumulative token usage (input_tokens, output_tokens) from assistant messages
3. Store/load watermarks in a `.telemetry.json` file in the bean directory
4. Compute per-task token deltas (current cumulative - watermark)
5. Update Telemetry table rows with token data
6. Sum Total Tokens In / Total Tokens Out from per-task values

## Inputs

- `.claude/hooks/telemetry-stamp.py` — existing telemetry hook
- `~/.claude/projects/<project-hash>/*.jsonl` — JSONL conversation files

## Acceptance Criteria

- [ ] `find_session_jsonl()` finds the current session's JSONL file
- [ ] `sum_session_tokens()` computes cumulative input/output tokens
- [ ] `save_watermark()` / `load_watermark()` persist token snapshots
- [ ] `compute_task_tokens()` computes delta from watermark
- [ ] `update_telemetry_row_tokens()` fills token columns in a telemetry row
- [ ] `sum_telemetry_tokens()` computes totals from per-task values

## Definition of Done

All helper functions implemented and tested via lint check.
