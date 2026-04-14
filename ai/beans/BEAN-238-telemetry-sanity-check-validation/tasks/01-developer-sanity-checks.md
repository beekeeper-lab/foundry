# Task 01: Sanity Check Implementation

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 15:03 |
| **Completed** | 2026-03-27 15:05 |
| **Duration** | 2m |

## Goal

Add plausibility validation to telemetry-stamp.py before writing token data.

## Inputs

- `.claude/hooks/telemetry-stamp.py`
- `.claude/skills/telemetry-report/SKILL.md`

## Implementation

1. Add a `validate_token_delta()` function to telemetry-stamp.py:
   - Floor: delta_in < 5,000 → suspect (return "N/A (suspect)")
   - Zero: delta_in == 0 and delta_out == 0 → suspect
   - Ceiling: delta_in > 5,000,000 → log warning but still write
   - Return validated values or N/A markers

2. Call `validate_token_delta()` before writing to bean telemetry row.

3. Add `--validate` flag to telemetry-report SKILL.md that scans Done beans for suspect rows.

## Acceptance Criteria

- [ ] Values < 5K flagged as suspect
- [ ] Zero deltas flagged
- [ ] Values > 5M logged as warning
- [ ] Stderr explains rejections
- [ ] Tests pass, lint clean

## Definition of Done

- Hook updated, skill updated, tests pass, lint clean
