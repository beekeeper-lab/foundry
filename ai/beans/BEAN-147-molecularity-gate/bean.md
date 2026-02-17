# BEAN-147: Molecularity Gate

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-147 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:01 |
| **Completed** | 2026-02-17 04:03 |
| **Duration** | 2m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Beans sometimes grow too large in scope, combining multiple independent changes into a single unit of work. This makes review harder, increases merge conflict risk, and reduces parallelization potential. There is no systematic check to ensure beans are appropriately sized ("molecular").

## Goal

Add a molecularity gate to the bean creation or refinement process that ensures each bean represents a single, atomic unit of change. Beans that are too broad should be decomposed into smaller beans.

## Scope

### In Scope
- Define molecularity criteria (what makes a bean appropriately sized)
- Add a gate/check to backlog-refinement or bean creation
- Provide guidance on decomposing oversized beans

### Out of Scope
- Changes to the application code
- Automated bean splitting tools

## Acceptance Criteria

- [x] Molecularity criteria are defined and documented
- [x] Gate/check is added to the bean creation or refinement process
- [x] Guidance for decomposing oversized beans is provided
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add molecularity gate to workflow docs | Developer | — | Done |
| 2 | Verify documentation quality and completeness | Tech-QA | 1 | Done |

> Skipped: BA (default — no ambiguous requirements), Architect (default — no new subsystems or APIs)

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993e0093c4a2e1a687248cc |
| **Card Name** | Molecularity Gate |
| **Card URL** | https://trello.com/c/oqEmJZuw/26-molecularity-gate |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add molecularity gate to workflow docs | Developer | < 1m | 42 | 2,934 | $0.22 |
| 2 | Verify documentation quality and completeness | Tech-QA | < 1m | 56 | 3,756 | $0.28 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 98 |
| **Total Tokens Out** | 6,690 |
| **Total Cost** | $0.50 |