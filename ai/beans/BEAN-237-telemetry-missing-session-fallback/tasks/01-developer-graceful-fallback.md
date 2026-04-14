# Task 01: Graceful Fallback Implementation

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 14:59 |
| **Completed** | 2026-03-27 15:01 |
| **Duration** | 2m |

## Goal

When no JSONL session is found, write `N/A` to telemetry fields instead of leaving sentinels. Ensure summary computations skip N/A rows.

## Inputs

- `.claude/hooks/telemetry-stamp.py` — the telemetry hook

## Implementation

1. In `handle_task_file`, when `find_session_jsonl()` returns None: set `tok_in_str = "N/A"` and `tok_out_str = "N/A"`.
2. Enhance the stderr log to include cwd, candidate dirs searched.
3. In `update_telemetry_row_tokens`, ensure `N/A` values are written (not skipped).
4. Verify `sum_telemetry_tokens` and `sum_telemetry_costs` skip `N/A` rows — they already do via try/except and regex.
5. Add a test for the N/A fallback behavior.

## Acceptance Criteria

- [ ] When no JSONL, telemetry shows N/A not sentinels
- [ ] Summary computation skips N/A rows
- [ ] Stderr log includes cwd and candidates
- [ ] All tests pass
- [ ] Lint clean

## Definition of Done

- Hook updated, tests pass, lint clean
