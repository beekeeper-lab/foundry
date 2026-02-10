# Task 03: Add telemetry rollup to merge-bean

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Tokens** | — |

## Goal

Update `/merge-bean` SKILL.md to aggregate task telemetry into the bean's summary totals when marking a bean Done (before the merge).

## Acceptance Criteria

- [ ] merge-bean reads all task telemetry rows from bean.md
- [ ] merge-bean computes Total Tasks, Total Duration, Total Tokens In, Total Tokens Out
- [ ] Summary totals are written to the bean's Telemetry summary table
