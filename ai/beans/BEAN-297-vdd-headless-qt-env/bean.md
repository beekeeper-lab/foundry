# BEAN-297: /vdd test runner fails on headless machines (Qt env)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-297 |
| **Status** | Unapproved |
| **Priority** | Medium |
| **Created** | 2026-07-04 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

`foundry_app/services/vdd.py` dispatches `test:` criteria via `uv run pytest`
without setting `QT_QPA_PLATFORM=offscreen`. On headless machines the PySide6
UI tests abort (pytest exit 134), so the VDD gate spuriously FAILs beans whose
code is green. Found by Tech-QA during BEAN-295 verification (retro pipeline).

## Goal

`/vdd` produces the same verdict on headless and desktop machines.

## Scope

### In Scope
- vdd.py test-runner env: inherit os.environ + set QT_QPA_PLATFORM=offscreen when unset
- Regression test

### Out of Scope
- Changing which tests the gate runs

## Acceptance Criteria

> Authored by: Team-Lead (default).

- [ ] (file-contains:foundry_app/services/vdd.py::QT_QPA_PLATFORM) Runner sets the offscreen platform when unset
- [ ] (test:tests/test_vdd.py) VDD runner tests pass
- [ ] (test:tests/) All tests pass (`uv run pytest`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

Origin: Tech-QA finding in `ai/outputs/tech-qa/BEAN-295-vdd.md` (2026-07-04).

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

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | — (comma-separated, actual not planned) |
| **Bounces** | — (Tech-QA → Developer kicks) |
| **Scope changes** | — (in-flight scope edits) |
| **Contract violations** | — (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | — (BEAN-272's NONE-justified) |
| **Dispatch mode** | — (agent-subagent / agent-worktree / in-process / mixed) |
