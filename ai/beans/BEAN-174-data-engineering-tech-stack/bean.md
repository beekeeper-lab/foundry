# BEAN-174: Data Engineering Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-174 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 18:11 |
| **Completed** | 2026-02-20 18:15 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

No current stack addresses data pipelines or analytics engineering. Teams building ETL/ELT pipelines, data warehouses, and analytics platforms lack domain-specific guidance in the library.

## Goal

Add a complete data engineering tech stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- ETL/ELT pipeline patterns
- Data modeling (dimensional modeling, data vault)
- Pipeline orchestration (Airflow, dbt)
- Data quality frameworks
- Warehouse design best practices
- Stack file following standardized template

### Out of Scope
- ML/AI-specific data pipelines
- Modifications to existing stacks
- Application code changes

## Acceptance Criteria

- [x] `ai-team-library/stacks/data-engineering/` directory exists with properly formatted stack file
- [x] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [x] Covers ETL/ELT, data modeling, orchestration, data quality, and warehouse design
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create ETL/ELT pipelines stack file | Developer | — | Done |
| 2 | Create data modeling stack file | Developer | — | Done |
| 3 | Create orchestration stack file | Developer | — | Done |
| 4 | Create data quality stack file | Developer | — | Done |
| 5 | Create warehouse design stack file | Developer | — | Done |
| 6 | Verify all files follow template, run tests & lint | Tech-QA | 1–5 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Fills a major domain gap — data pipelines and analytics engineering are common project types with no current stack coverage.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e28e7951e468ec11746d |
| **Card Name** | Data Engineering Tech Stack |
| **Card URL** | https://trello.com/c/D25pheq0/45-data-engineering-tech-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create ETL/ELT pipelines stack file | Developer | — | — | — | — |
| 2 | Create data modeling stack file | Developer | — | — | — | — |
| 3 | Create orchestration stack file | Developer | — | — | — | — |
| 4 | Create data quality stack file | Developer | — | — | — | — |
| 5 | Create warehouse design stack file | Developer | — | — | — | — |
| 6 | Verify all files follow template, run tests & lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |