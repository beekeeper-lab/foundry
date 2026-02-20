# BEAN-162: Bean Change Summary Section

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-162 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:18 |
| **Completed** | 2026-02-20 20:23 |
| **Duration** | 5m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

When a team finishes a bean, there is no record of exactly what files and code changed. The user wants to track the implementation diff for each bean to understand the concrete impact of the work.

## Goal

After a bean is completed, generate a git diff summary and add it as a new `## Changes` section in the bean's `bean.md`. This should list files changed and a concise description of what changed in each.

## Scope

### In Scope
- Add a `## Changes` section to the bean template
- Update the merge-bean or long-run workflow to populate the Changes section from `git diff` when a bean is completed
- Include: files changed (with +/- line counts), brief description of changes per file

### Out of Scope
- Retroactively populating Changes for already-completed beans
- Full inline diffs (just summaries)

## Acceptance Criteria

- [x] Bean template includes a `## Changes` section placeholder
- [x] When a bean is completed and merged, the Changes section is populated with a git diff summary
- [x] Changes section lists files modified with line count deltas
- [x] The workflow update is documented (which step populates the section)
- [x] All tests pass (`uv run pytest`) — pre-existing PySide6/libGL UI test failures only
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add Changes section to template and merge workflow | Developer | — | Done |
| 2 | Verify Changes section implementation | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention — tasks are sequential (Developer → Tech-QA)

## Notes

The git diff should be computed from the merge commit or feature branch diff against the base branch. Keep the summary concise — file list with +/- counts, not full diffs.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6997ceab59e7a373079d88d3 |
| **Card Name** | Summary of changes added to the bean. |
| **Card URL** | https://trello.com/c/10AK7iyi/35-summary-of-changes-added-to-the-bean |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add Changes section to template and merge workflow | Developer | 1m | 833,635 | 1,150 | $1.63 |
| 2 | Verify Changes section implementation | Tech-QA | 3m | 1,542,088 | 596 | $2.77 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 4m |
| **Total Tokens In** | 2,375,723 |
| **Total Tokens Out** | 1,746 |
| **Total Cost** | $4.40 |