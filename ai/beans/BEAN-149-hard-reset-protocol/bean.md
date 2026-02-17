# BEAN-149: Hard Reset Protocol

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-149 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

When a bean or task gets stuck in a bad state (corrupted worktree, merge conflicts, stalled worker, broken branch), there is no documented protocol for cleanly resetting and restarting. Ad-hoc recovery attempts can make things worse.

## Goal

Define a hard reset protocol that provides step-by-step instructions for cleanly recovering from various failure states during bean execution, including worktree cleanup, branch reset, status file cleanup, and re-spawning.

## Scope

### In Scope
- Document recovery procedures for common failure states
- Cover worktree cleanup, branch management, status file reset
- Provide checklist for pre/post reset verification

### Out of Scope
- Automated recovery tooling
- Changes to the application code

## Acceptance Criteria

- [ ] Hard reset protocol is documented
- [ ] Covers common failure states (stalled worker, merge conflict, corrupted worktree)
- [ ] Step-by-step recovery procedures are provided
- [ ] Pre/post reset verification checklist is included
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
| **Card ID** | 6993dfd4d1d856cd74b50af7 |
| **Card Name** | Hard Reset Protocol |
| **Card URL** | https://trello.com/c/ZuB3zJXx/24-hard-reset-protocol |

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
