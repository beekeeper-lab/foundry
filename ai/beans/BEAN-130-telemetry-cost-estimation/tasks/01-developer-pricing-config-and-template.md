# Task 01: Create Pricing Config and Update Bean Template

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-16 01:01 |
| **Completed** | 2026-02-16 01:01 |
| **Duration** | < 1m |

## Goal

Create the token pricing config file and update the bean template to include Cost columns.

## Work Items

1. Create `ai/context/token-pricing.md` with Claude Opus 4 rates ($15/MTok input, $75/MTok output)
2. Update `ai/beans/_bean-template.md`:
   - Add `Cost` column to the per-task telemetry table
   - Add `**Total Cost**` row to the summary table

## Acceptance Criteria

- [ ] `ai/context/token-pricing.md` exists with input rate, output rate, model name, and last-updated date
- [ ] Bean template per-task table has 7 columns: #, Task, Owner, Duration, Tokens In, Tokens Out, Cost
- [ ] Bean template summary table has a Total Cost row
