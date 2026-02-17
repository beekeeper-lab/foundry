# BEAN-145: Micro-Iteration Loop

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-145 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

The current bean workflow executes tasks in a single pass without structured feedback loops. When a task produces output that doesn't meet acceptance criteria on the first attempt, there's no defined process for quick iteration cycles within a task.

## Goal

Define a micro-iteration loop pattern for task execution that enables rapid test-fix-verify cycles within a single task, reducing the chance of tasks being marked "done" with incomplete work.

## Scope

### In Scope
- Define micro-iteration loop pattern for task execution
- Specify when and how to apply iteration cycles within tasks
- Add guidance to agent instructions or bean workflow documentation

### Out of Scope
- Changes to the application code
- Automated retry mechanisms

## Acceptance Criteria

- [ ] Micro-iteration loop pattern is documented
- [ ] Pattern specifies entry/exit conditions for iteration cycles
- [ ] Agent instructions or workflow docs reference the pattern
- [ ] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993daef96590e32288b9f19 |
| **Card Name** | Micro-Iteration Loop |
| **Card URL** | https://trello.com/c/sxEytxow/19-micro-iteration-loop |

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
