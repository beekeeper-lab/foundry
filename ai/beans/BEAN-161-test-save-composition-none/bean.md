# BEAN-161: Test save_composition Excludes None Fields from YAML Output

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-161 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:16 |
| **Completed** | 2026-02-20 20:19 |
| **Duration** | 3m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

`save_composition` uses `exclude_none=True`, but no test verifies `None` fields are actually absent from the raw YAML on disk — they only check the round-tripped model. A `safety: null` entry could break downstream tools expecting clean YAML.

## Goal

Add a test that saves a spec with `safety=None`, reads the raw YAML, and asserts `"safety"` is not a key. Prevents `safety: null` noise in generated YAML files.

## Scope

### In Scope
- Add a test that saves a composition with `safety=None`
- Read back the raw YAML file (not the round-tripped model)
- Assert the `"safety"` key is absent from the YAML

### Out of Scope
- Modifying `save_composition` logic
- Testing other None-able fields beyond what's needed to verify the pattern

## Acceptance Criteria

- [x] Test saves a composition spec with `safety=None`
- [x] Test reads raw YAML from disk and asserts `"safety"` key is absent
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add test for None field exclusion in save_composition YAML output | Developer | — | Done |
| 2 | Verify None exclusion test and acceptance criteria | Tech-QA | Task 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — 2 sequential tasks, single file modified

## Notes

Ensures clean YAML output without null noise for downstream tool compatibility.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997cb01c3f59005c645e31f |
| **Card Name** | Test save_composition excludes None fields from YAML output |
| **Card URL** | https://trello.com/c/N3fWsD1p/34-test-savecomposition-excludes-none-fields-from-yaml-output |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add test for None field exclusion in save_composition YAML output | Developer | < 1m | 1,088,298 | 909 | $3.16 |
| 2 | Verify None exclusion test and acceptance criteria | Tech-QA | < 1m | 2,098,409 | 1,751 | $4.94 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 3,186,707 |
| **Total Tokens Out** | 2,660 |
| **Total Cost** | $8.10 |