# BEAN-142: Test Generator Stage Callback Contract

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-142 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-19 |
| **Started** | 2026-02-19 21:41 |
| **Completed** | 2026-02-19 21:44 |
| **Duration** | 3m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The `generate_project()` pipeline accepts a `stage_callback` parameter that the UI progress dialog relies on for real-time stage reporting, but this callback contract has zero test coverage. Without tests, changes to the orchestrator could silently break the progress UI without any test catching the regression.

## Goal

Add a focused test that exercises the `stage_callback` parameter of `generate_project()`, verifying the callback contract (invocation count, stage keys, and payload shape) so that any future changes to the orchestrator that break the UI progress reporting will be caught by the test suite.

## Scope

### In Scope
- Add a test that passes a mock `stage_callback` to `generate_project()`
- Assert callback fires twice per stage ("running" + "done")
- Assert stage keys match expected stages (scaffold, compile, etc.)
- Assert `file_count` on "done" is a non-negative int
- Validate the contract between the orchestrator and the UI

### Out of Scope
- Changes to the generator pipeline itself
- UI-level integration testing of the progress dialog
- Performance or timing tests on callback latency

## Acceptance Criteria

- [ ] Test passes a mock callback to `generate_project()` and runs the pipeline
- [ ] Test asserts callback fires twice per stage ("running" + "done")
- [ ] Test asserts stage keys match expected stages (scaffold, compile, etc.)
- [ ] Test asserts `file_count` on "done" payloads is a non-negative int
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement stage callback contract test | developer | — | Done |
| 2 | Tech-QA verification | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

This validates the contract between the orchestrator and the UI progress dialog. The test should be placed in the existing generator test module alongside other pipeline tests.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Workspace** | gregg.reed's workspace |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997c57422b73c1bd37b9289 |
| **Card Name** | Test generator stage callback contract |
| **Card URL** | https://trello.com/c/aAHyysTK |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement stage callback contract test | developer | 1m | 25 | 159 | $0.01 |
| 2 | Tech-QA verification | tech-qa | < 1m | 5 | 28 | < $0.01 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 30 |
| **Total Tokens Out** | 187 |
| **Total Cost** | $0.01 |