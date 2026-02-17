# BEAN-152: Blast Radius Budget

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-152 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:07 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | 2m |
| **Owner** | team-lead |
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

- [x] Blast radius budget concept is documented
- [x] Metrics and guideline thresholds are defined
- [x] Check is added to backlog-refinement or decomposition process
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Document Blast Radius Budget | Developer | — | Done |
| 2 | Verify Blast Radius Budget Documentation | Tech-QA | Task 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential Developer → Tech-QA wave, no shared writes.

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
| 1 | Document Blast Radius Budget | Developer | < 1m | 7 | 725 | $0.05 |
| 2 | Verify Blast Radius Budget Documentation | Tech-QA | < 1m | 9 | 1,196 | $0.09 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 16 |
| **Total Tokens Out** | 1,921 |
| **Total Cost** | $0.14 |