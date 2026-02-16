# Task 02: Update Telemetry Report Skill with Cost Computation

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-16 01:02 |
| **Completed** | 2026-02-16 01:02 |
| **Duration** | < 1m |

## Goal

Update the `/telemetry-report` skill to read pricing from the config file and compute/display costs.

## Work Items

1. Update `.claude/skills/telemetry-report/SKILL.md` process section to:
   - Read rates from `ai/context/token-pricing.md` before computing
   - Compute cost per task: `(tokens_in * input_rate) + (tokens_out * output_rate)`
   - Add Cost column to per-task display
   - Add Total Cost to bean summary
   - Add Cost column to category and owner breakdown tables
   - Display format: `$X.XX` (two decimal places), `< $0.01` for tiny amounts

## Acceptance Criteria

- [ ] Skill references `ai/context/token-pricing.md` as an input
- [ ] Process describes reading rates from config (not hardcoded)
- [ ] Per-task, per-bean, and aggregate cost display is specified
- [ ] Report format examples include Cost columns
