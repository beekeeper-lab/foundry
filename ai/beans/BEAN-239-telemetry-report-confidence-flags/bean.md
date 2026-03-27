# BEAN-239: Telemetry Report Confidence Indicators

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-239 |
| **Status** | Approved |
| **Priority** | Low |
| **Created** | 2026-03-27 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The `/telemetry-report` skill presents all bean telemetry data as equally trustworthy. Beans with 15 input tokens sit alongside beans with 3M input tokens in the same table with no indication that the former is clearly wrong. Users reviewing the report have no way to quickly distinguish reliable data from suspect data without manually inspecting each bean.

## Goal

The telemetry report visually flags beans with suspect or missing data, and includes a data quality summary so users know how much of the report to trust.

## Scope

### In Scope
- Add confidence markers to the telemetry report output:
  - Flag beans with `N/A`, `N/A (suspect)`, or sentinel (`—`) token values
  - Flag beans with <5,000 total input tokens (impossibly low)
  - Flag beans with `< 1m` duration but >2M input tokens (suspicious cost/time ratio)
- Add a "Data Quality" section to the report header:
  - Count of beans with complete telemetry data
  - Count of beans with partial/missing data
  - Count of beans with suspect data
  - Overall confidence percentage: `(complete / total_with_data) * 100`
- Exclude suspect data from aggregate statistics (averages, medians) with a note

### Out of Scope
- Fixing the underlying data capture issues (BEAN-235, 236, 237, 232)
- Auto-correcting suspect data
- Historical backfill

## Acceptance Criteria

- [ ] Beans with <5K input tokens show a warning marker in the report
- [ ] Beans with `N/A` or sentinel token values are flagged
- [ ] Report header includes a "Data Quality" section with completeness stats
- [ ] Aggregate statistics exclude flagged beans with a footnote
- [ ] Report is still readable and not cluttered with warnings for clean data
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

This is a reporting improvement, not a data fix. It depends on BEAN-238 for the `N/A (suspect)` markers but can be implemented independently by detecting implausible values during report generation.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
