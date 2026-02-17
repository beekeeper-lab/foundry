# BEAN-144: Bottleneck Check

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-144 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 04:01 |
| **Completed** | 2026-02-17 04:05 |
| **Duration** | 4m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The AI team workflow lacks a systematic check for bottlenecks before and during bean execution. Without identifying constraints early, workers may stall on dependencies, resource contention, or sequential steps that could be parallelized.

## Goal

Add a bottleneck identification and mitigation step to the bean workflow that flags potential serialization points, dependency chains, and resource contention before execution begins.

## Scope

### In Scope
- Add bottleneck analysis to bean decomposition or pre-execution phase
- Identify sequential dependencies that could be parallelized
- Flag resource contention risks (shared files, branches, indexes)

### Out of Scope
- Changes to the application code
- Automated performance profiling

## Acceptance Criteria

- [x] Bean workflow includes a bottleneck check step
- [x] Sequential dependencies are identified and flagged
- [x] Mitigation strategies are documented for identified bottlenecks
- [x] Documentation is clear and actionable

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add bottleneck check step | developer | — | Done |
| 2 | Verify bottleneck check docs | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

(Trello card had no description.)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993da9b03e364a47bdbeb6e |
| **Card Name** | Bottleneck Check |
| **Card URL** | https://trello.com/c/0NmpDZHn/17-bottleneck-check |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add bottleneck check step | developer | 2m | — | — | — |
| 2 | Verify bottleneck check docs | tech-qa | 2m | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |