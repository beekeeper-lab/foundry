# BEAN-114: Telemetry Backfill from Git History

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-114 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-10 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

Of 109 Done beans, only 4 have any telemetry data (BEAN-075–078, backfilled manually from git reflog). The remaining 105 Done beans have either empty telemetry sections or no telemetry section at all. Without historical data we cannot answer basic questions: how long does an average bean take? How does duration vary by category (App vs Process vs Infra)? What is the total time invested in the project?

## Goal

Every Done bean has a computed duration in its telemetry section, derived from git history (branch creation timestamp → merge commit timestamp). This provides a complete historical dataset for project analytics.

## Scope

### In Scope
- Parse git log to find branch creation and merge timestamps for all Done beans (BEAN-001–113)
- Compute duration for each bean and update the Telemetry section in bean.md
- For beans without a Telemetry section (BEAN-001–071), add the section
- For beans with empty telemetry rows, populate duration from git timestamps
- Handle edge cases: beans done in a single commit (no branch), beans with multiple merge attempts
- Produce a summary of results (how many backfilled, any that couldn't be computed)

### Out of Scope
- Token usage data (not recoverable from git history)
- Backfilling per-task breakdowns (only bean-level duration)
- Modifying the telemetry format or schema

## Acceptance Criteria

- [ ] All 109+ Done beans have a duration value in their Telemetry section
- [ ] Beans that previously lacked a Telemetry section (BEAN-001–071) now have one
- [ ] Duration values are computed from git timestamps (branch create → merge), not estimated
- [ ] Beans where duration cannot be computed are documented with a note explaining why
- [ ] A summary report is produced showing total beans backfilled and aggregate stats
- [ ] No existing telemetry data is overwritten (beans with real data keep their values)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Git timestamps are the most reliable source: `git log --format=%aI` on branch creation commits and merge commits
- For beans worked on `main` directly (early beans before feature-branch workflow), use first and last commit touching the bean's files
- BEAN-075–078 already have real duration data — skip or verify, don't overwrite
- This is a one-time data recovery task, not an ongoing process (that's BEAN-115)

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
