# BEAN-152: Blast Radius Budget

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-152 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

Beans sometimes touch more files or systems than expected, creating a large "blast radius" that increases review burden and merge conflict risk. There is no upfront budget or constraint on how many files/systems a bean should touch.

## Goal

Define a blast radius budget concept for beans that sets expectations for the number of files changed, systems touched, and scope of impact. Beans exceeding the budget should be flagged for decomposition.

## Scope

### In Scope
- Define blast radius metrics (files changed, systems touched, lines modified)
- Set guideline thresholds for bean sizes
- Add a check to backlog-refinement or bean decomposition

### Out of Scope
- Changes to the application code
- Automated blast radius calculation tools

## Acceptance Criteria

- [ ] Blast radius budget concept is documented
- [ ] Metrics and guideline thresholds are defined
- [ ] Check is added to backlog-refinement or decomposition process
- [ ] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993dabe0c5e7d7422d4ab61 |
| **Card Name** | Blast Radius Budget |
| **Card URL** | https://trello.com/c/mvwflkkh/18-blast-radius-budget |

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
