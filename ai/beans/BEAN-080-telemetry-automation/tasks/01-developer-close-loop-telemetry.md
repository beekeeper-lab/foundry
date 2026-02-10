# Task 01: Enhance close-loop with telemetry recording

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Tokens** | — |

## Goal

Expand step 8 of `/close-loop` SKILL.md with specific telemetry recording instructions: prompt for token self-report, record timestamps, compute duration, and update the bean's per-task telemetry table row.

## Acceptance Criteria

- [ ] Step 8 specifies timestamp format `YYYY-MM-DD HH:MM`
- [ ] Step 8 specifies token format `X,XXX in / Y,YYY out`
- [ ] Step 8 specifies duration format `Xm` or `Xh Ym`
- [ ] Step 8 includes updating the bean's Telemetry per-task table row
- [ ] Step 8 includes fallback: if Started is not set, record it now
