# BEAN-151: Context Diet

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-151 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

AI team workers consume large amounts of context (reading many files, lengthy agent instructions, full backlog indexes) which wastes tokens, slows execution, and can cause context window overflow. There is no systematic approach to minimizing context consumption.

## Goal

Define a "context diet" policy that establishes guidelines for minimizing unnecessary context consumption during bean execution — reading only what's needed, avoiding redundant file reads, and keeping agent prompts focused.

## Scope

### In Scope
- Define context consumption guidelines for workers
- Specify what context is essential vs. optional per task type
- Add guidance to agent instructions or spawn-bean prompts

### Out of Scope
- Changes to the application code
- Automated context trimming tools

## Acceptance Criteria

- [ ] Context diet policy is documented
- [ ] Guidelines distinguish essential vs. optional context
- [ ] Agent instructions or worker prompts reference the policy
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
| **Card ID** | 6993dd932358c5a127c6f73b |
| **Card Name** | Context Diet |
| **Card URL** | https://trello.com/c/I9ioJXOb/20-context-diet |

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
