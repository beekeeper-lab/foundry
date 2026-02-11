# BEAN-116: Telemetry Summary Report Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-116 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 20:59 |
| **Completed** | 2026-02-10 21:00 |
| **Duration** | 1m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Even after BEAN-114 (backfill) and BEAN-115 (live capture) populate telemetry data in individual bean files, there is no way to see aggregate project metrics. To answer "how long does an average bean take?" or "what's the total time invested?" you'd have to manually parse 100+ bean.md files. The team needs a single command that produces a rollup report.

## Goal

A `/telemetry-report` skill that parses all bean telemetry sections and produces a concise summary with aggregate statistics, breakdowns by category and persona, and optionally a cost estimate based on token usage.

## Scope

### In Scope
- New skill at `.claude/skills/telemetry-report/SKILL.md`
- Parse all bean.md files for Telemetry sections
- Compute and display:
  - Total beans, total duration, average duration per bean
  - Duration breakdown by Category (App, Process, Infra)
  - Duration breakdown by Owner/persona
  - Longest and shortest beans
  - Token usage totals and averages (if data available)
  - Estimated cost based on token pricing (if token data available)
- Output as a formatted markdown table to the console
- Support optional filters: `--category`, `--status`, `--since YYYY-MM-DD`

### Out of Scope
- Persistent storage of aggregated data (computed on the fly each time)
- Graphical charts or visualizations
- Exporting to CSV/JSON (can be added later)
- Modifying the telemetry format in bean.md files

## Acceptance Criteria

- [ ] `/telemetry-report` skill exists and is invocable
- [ ] Produces a summary table with total beans, total duration, average duration
- [ ] Shows breakdown by Category (App, Process, Infra) with counts and averages
- [ ] Shows breakdown by Owner with counts and averages
- [ ] Identifies top 5 longest and top 5 shortest beans
- [ ] Handles beans with missing telemetry gracefully (reports count of "no data" beans)
- [ ] Token/cost summary is shown when data is available, omitted when not
- [ ] `--category` filter works (e.g., `/telemetry-report --category App`)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-114 (backfill) for historical data and BEAN-115 (live capture) for ongoing data
- Can be built incrementally: start with duration-only report, add token/cost later
- Consider making the output format match what /status-report produces for consistency
- The skill parses bean.md markdown directly — no database or structured data store needed

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
