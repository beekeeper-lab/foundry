# BEAN-143: Downstream Gate

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-143 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:01 |
| **Completed** | 2026-02-17 04:03 |
| **Duration** | 2m |
| **Owner** | team-lead |
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

- [x] Backlog-refinement or bean workflow includes a downstream impact analysis step
- [x] The step requires listing impacted systems (tests, CI, build, deployment, docs, migrations, monitoring)
- [x] Each impacted system has an explicit verification command
- [x] Missing verifications are flagged and must be added before proceeding
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add Downstream Gate step to backlog-refinement skill | Developer | — | Done |
| 2 | Verify documentation is clear, complete, and actionable | Tech-QA | Task 1 | Done |

> Skipped: BA (default), Architect (default)

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
| 1 | Add Downstream Gate step to backlog-refinement skill | Developer | < 1m | 44 | 1,832 | $0.14 |
| 2 | Verify documentation is clear, complete, and actionable | Tech-QA | < 1m | 63 | 3,013 | $0.23 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 107 |
| **Total Tokens Out** | 4,845 |
| **Total Cost** | $0.37 |