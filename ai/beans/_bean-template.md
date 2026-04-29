# BEAN-NNN: Title

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-NNN |
| **Status** | Unapproved |
| **Priority** | Medium |
| **Created** | YYYY-MM-DD |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | (App \| Process \| Infra) |
| **Depends On** | — (or comma-separated BEAN-NNN list) |

## Problem Statement

What problem does this bean solve? Why does it matter?

## Goal

What is the desired outcome when this bean is complete?

## Scope

### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory. **Every task file must have a
> non-empty `## Inputs` section** — the validate-task-inputs hook blocks
> a task from moving to `In Progress` without one. Example:
>
> ```
> ## Inputs
> - foundry_app/services/generator.py — `generate_project()` entry point
> - ai/beans/BEAN-NNN-x/bean.md — full scope
> ```
>
> Escape hatch (rare, repo-wide scans only):
> `Inputs: NONE (justified: <reason of at least 10 characters>)`

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

(Any additional context, links, or discussion.)

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
