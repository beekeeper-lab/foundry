# BEAN-158: Test Generator Runtime Path-Traversal Containment

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-158 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:12 |
| **Completed** | 2026-02-20 20:16 |
| **Duration** | 4m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generator has a runtime containment check (defense-in-depth) that raises `ValueError("Refusing to generate")` when the output path escapes its root. Existing tests only cover the Pydantic model-level validator. There is no test verifying the runtime ValueError fires when a path-traversal attack bypasses model validation.

## Goal

Add a test that passes an output_root like `tmp / "safe" / ".." / ".." / "escape"` and asserts the runtime ValueError fires. Demonstrates defense-in-depth beyond model validation.

## Scope

### In Scope
- Add a test for the runtime path-traversal containment check in the generator
- Verify the ValueError message contains "Refusing to generate"

### Out of Scope
- Modifying the generator's containment logic
- Changing existing tests

## Acceptance Criteria

- [x] Test passes an output_root with `..` path traversal and asserts `ValueError("Refusing to generate")` is raised
- [x] Test demonstrates the runtime check fires independently of model validation
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add runtime containment traversal test | Developer | — | Done |
| 2 | Verify test and acceptance criteria | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — sequential 2-task wave, no shared files

## Notes

Defense-in-depth test — complements existing Pydantic model-level validation tests.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997cafdba819efa9117a956 |
| **Card Name** | Test generator runtime path-traversal containment |
| **Card URL** | https://trello.com/c/OYbuz834/31-test-generator-runtime-path-traversal-containment |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add runtime containment traversal test | Developer | 1m | 667,441 | 1,149 | $1.28 |
| 2 | Verify test and acceptance criteria | Tech-QA | 2m | 848,830 | 369 | $1.44 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3m |
| **Total Tokens In** | 1,516,271 |
| **Total Tokens Out** | 1,518 |
| **Total Cost** | $2.72 |