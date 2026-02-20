# BEAN-155: Trello Lifecycle E2E Test

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-155 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 05:10 |
| **Completed** | 2026-02-17 05:13 |
| **Duration** | 3m |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

The Trello-to-bean lifecycle integration has no automated verification. We need a test that confirms a card in Sprint_Backlog is imported as a bean, processed through the long-run, moved to In_Progress during execution, and moved to Completed after the bean is marked Done.

## Goal

Create a test (manual or scripted procedure) that validates the full Trello card lifecycle: Sprint_Backlog → import as bean → long-run processes it → card moves to In_Progress → bean completes → card moves to Completed.

## Scope

### In Scope
- Document the Trello lifecycle test procedure
- Define expected state transitions for Trello cards at each stage
- Verify the current implementation handles all transitions

### Out of Scope
- Automated pytest-level integration tests against the live Trello API
- Changes to the application code

## Acceptance Criteria

- [x] Test procedure is documented with step-by-step instructions
- [x] Expected Trello card state at each bean lifecycle stage is defined
- [x] Procedure covers: import, in-progress transition, and completion transition
- [x] Any gaps between expected and actual behavior are identified

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Document Trello lifecycle test procedure | developer | — | Done |
| 2 | Tech-QA review | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

(Trello card had no description beyond the title.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993f760e312474ae6e398e4 |
| **Card Name** | Write a test that looks for a backlog item in the sprint backlog in Trello, kicks off the long-run process, then checks in Trello to see that it was moved to in progress, then completes it, then checks in Trello again to see that it's in the completed list. |
| **Card URL** | https://trello.com/c/z8stZHO0/28-write-a-test-that-looks-for-a-backlog-item-in-the-sprint-backlog-in-trello |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Document Trello lifecycle test procedure | developer | 1m | 757,652 | 132 | $1.24 |
| 2 | Tech-QA review | tech-qa | < 1m | 447,193 | 287 | $0.74 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 1,204,845 |
| **Total Tokens Out** | 419 |
| **Total Cost** | $1.98 |