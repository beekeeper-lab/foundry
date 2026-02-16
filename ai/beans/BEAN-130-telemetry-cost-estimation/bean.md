# BEAN-130: Telemetry Cost Estimation

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-130 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-16 |
| **Started** | 2026-02-16 00:35 |
| **Completed** | 2026-02-16 01:05 |
| **Duration** | 30m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The telemetry system tracks token usage (input and output) per task and per bean, but there's no way to see the actual dollar cost of running beans. Token counts alone don't convey cost because input and output tokens have different rates, and those rates change over time as Anthropic updates pricing. Without cost visibility, it's hard to budget, identify expensive patterns, or compare the cost-effectiveness of different approaches.

## Goal

Every telemetry table (in bean.md files and in `/telemetry-report` output) shows a `Cost` column computed from token counts and configurable per-token rates. Rates are stored in a single config file that's easy to update when pricing changes.

## Scope

### In Scope
- Create a token pricing config file at `ai/context/token-pricing.md` with input and output cost-per-token rates
- Update the bean telemetry template (`ai/beans/_bean-template.md`) to include a `Cost` column in the per-task table and a `Total Cost` row in the summary table
- Update the `/telemetry-report` skill (`.claude/skills/telemetry-report/SKILL.md`) to:
  - Read rates from the config file
  - Compute cost per task: `(tokens_in * input_rate) + (tokens_out * output_rate)`
  - Show cost per task, per bean, and in aggregate summaries
  - Add cost columns to category and owner breakdown tables
- Update telemetry-writing skills/hooks (e.g., `/close-loop`, telemetry-stamp) to compute and write the Cost column when recording task telemetry in bean.md

### Out of Scope
- Historical backfill of cost data into existing bean.md files (can be a follow-up bean)
- Multiple model pricing tiers (use a single rate pair for the primary model)
- Currency conversion or localization
- Cost alerts or budgeting features

## Acceptance Criteria

- [x] `ai/context/token-pricing.md` exists with clearly labeled input and output rates ($/token)
- [x] Rates in the config file use current Anthropic pricing for the primary model used (Claude Opus 4)
- [x] Bean template telemetry table has a `Cost` column
- [x] Bean template summary table has a `Total Cost` row
- [x] `/telemetry-report` reads rates from the config file (not hardcoded)
- [x] `/telemetry-report` single-bean view shows cost per task and total cost
- [x] `/telemetry-report` aggregate view shows cost in category and owner breakdowns
- [x] Telemetry-writing automation computes and writes the Cost field when recording task data
- [x] Changing rates in the config file changes the computed costs in `/telemetry-report` output
- [x] All tests pass (`uv run pytest`) — 608 pass, 8 pre-existing SVG icon failures
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create pricing config and update bean template | developer | — | Done |
| 2 | Update telemetry-report skill with cost computation | developer | 1 | Done |
| 3 | Update telemetry-stamp hook to write Cost column | developer | 1 | Done |
| 4 | Verification — tests and lint | tech-qa | 1, 2, 3 | Done |

## Notes

- Suggested config format for `ai/context/token-pricing.md`:
  ```
  # Token Pricing

  | Field | Value |
  |-------|-------|
  | **Model** | Claude Opus 4 |
  | **Input Rate** | $0.000015 per token ($15/MTok) |
  | **Output Rate** | $0.000075 per token ($75/MTok) |
  | **Updated** | 2026-02-16 |
  ```
- Cost formula: `cost = (tokens_in * input_rate) + (tokens_out * output_rate)`
- Display format: `$0.42` (two decimal places for most values, `< $0.01` for very small amounts)
- The config file approach means updating pricing requires editing one file, not multiple skills
- Consider showing cost in the bean metadata table too (next to Duration) for quick reference

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | Create pricing config and update bean template | developer | < 1m | 277 | 12,626 |
| 2 | Update telemetry-report skill with cost computation | developer | < 1m | 285 | 14,431 |
| 3 | Update telemetry-stamp hook to write Cost column | developer | < 1m | 314 | 16,531 | $1.24 |
| 4 | Verification — tests and lint | tech-qa | < 1m | 325 | 17,274 | $1.30 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 2m |
| **Total Tokens In** | 1,201 |
| **Total Tokens Out** | 60,862 |