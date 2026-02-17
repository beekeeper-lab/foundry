# BEAN-143: Downstream Gate

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-143 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

Before making changes, the team does not systematically identify downstream systems that could be impacted (tests, CI, build, deployment, docs, migrations, monitoring). This leads to regressions that are caught late. This effects /backlog-refinement.

## Goal

Add a "Downstream Gate" step to the bean workflow or backlog-refinement process that requires listing downstream systems likely impacted by a change and stating how each will be verified (exact commands). If any verification is missing, it must be added to the plan before work begins. Keep scope small.

## Scope

### In Scope
- Add downstream impact analysis step to the backlog-refinement skill or bean workflow
- Require explicit verification commands for each impacted system
- Enforce that missing verification steps are added before proceeding

### Out of Scope
- Automated CI/CD pipeline changes
- Changes to the application code itself

## Acceptance Criteria

- [ ] Backlog-refinement or bean workflow includes a downstream impact analysis step
- [ ] The step requires listing impacted systems (tests, CI, build, deployment, docs, migrations, monitoring)
- [ ] Each impacted system has an explicit verification command
- [ ] Missing verifications are flagged and must be added before proceeding
- [ ] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Source Trello card description: "This effects /backlog-refinement. Before making changes, list the downstream systems likely impacted (tests, CI, build, deployment, docs, migrations, monitoring). For each, state how we will verify no regression (exact commands). If any verification is missing, add it to the plan. Keep scope small."

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993da5ebdfaa21deb36c403 |
| **Card Name** | Downstream Gate |
| **Card URL** | https://trello.com/c/hRDQovMX/16-downstream-gate |

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
