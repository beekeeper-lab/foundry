# BEAN-186: Microservices Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-186 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:18 |
| **Completed** | 2026-02-20 19:27 |
| **Duration** | 9m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a microservices tech stack. Add microservices stack to ai-team-library. Service boundaries, inter-service communication, distributed tracing, circuit breakers, service mesh.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add microservices stack to ai-team-library. Service boundaries, inter-service communication, distributed tracing, circuit breakers, service mesh.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Stack file created in `ai-team-library/stacks/` following standardized template
- [x] Includes: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist, code examples
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create microservices conventions.md | Developer | — | Done |
| 2 | Create communication.md | Developer | — | Done |
| 3 | Create resilience.md | Developer | — | Done |
| 4 | Create observability.md | Developer | — | Done |
| 5 | Create service-mesh.md | Developer | — | Done |
| 6 | Verify acceptance criteria | Tech-QA | 1-5 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #59.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f34051b5bab7fa6936e8 |
| **Card Name** | Microservices Tech Stack |
| **Card URL** | https://trello.com/c/yHHT056Z |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create microservices conventions.md | Developer | — | — | — | — |
| 2 | Create communication.md | Developer | — | — | — | — |
| 3 | Create resilience.md | Developer | — | — | — | — |
| 4 | Create observability.md | Developer | — | — | — | — |
| 5 | Create service-mesh.md | Developer | — | — | — | — |
| 6 | Verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 9m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |