# BEAN-149: Hard Reset Protocol

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-149 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:07 |
| **Completed** | 2026-02-17 04:09 |
| **Duration** | <5m |
| **Owner** | team-lead |
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

- [x] Hard reset protocol is documented
- [x] Covers common failure states (stalled worker, merge conflict, corrupted worktree)
- [x] Step-by-step recovery procedures are provided
- [x] Pre/post reset verification checklist is included
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Write hard reset protocol document | Developer | — | Done |
| 2 | Review hard reset protocol | Tech-QA | Task 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: sequential dependency is correct — Tech-QA reviews Developer output

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
| 1 | Write hard reset protocol document | Developer | 1m | 11 | 2,914 | $0.22 |
| 2 | Review hard reset protocol | Tech-QA | < 1m | 5 | 30 | < $0.01 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 16 |
| **Total Tokens Out** | 2,944 |
| **Total Cost** | $0.23 |