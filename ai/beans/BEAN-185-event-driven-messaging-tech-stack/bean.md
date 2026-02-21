# BEAN-185: Event-Driven / Messaging Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-185 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:18 |
| **Completed** | 2026-02-20 19:24 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a event-driven / messaging tech stack. Add event-driven stack to ai-team-library. Kafka, RabbitMQ, event sourcing, CQRS, saga patterns, dead letter queues, idempotency.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add event-driven stack to ai-team-library. Kafka, RabbitMQ, event sourcing, CQRS, saga patterns, dead letter queues, idempotency.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Stack file created in `ai-team-library/stacks/` following standardized template
- [x] Includes: Defaults table with alternatives, Do/Don't lists, Common Pitfalls, Checklist, code examples
- [x] All tests pass (`uv run pytest`) — pre-existing Qt import error unrelated to changes
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create conventions.md — core defaults, broker selection, message design | Developer | — | Done |
| 2 | Create event-sourcing.md — event sourcing, CQRS, event stores | Developer | — | Done |
| 3 | Create patterns.md — sagas, DLQ, idempotency, retry | Developer | — | Done |
| 4 | Create operations.md — production ops, monitoring, scaling | Developer | — | Done |
| 5 | Verify stack: tests pass, lint clean, acceptance criteria | Tech-QA | 1,2,3,4 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #58.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33fc240d6710e73ef1b |
| **Card Name** | Event-Driven / Messaging Tech Stack |
| **Card URL** | https://trello.com/c/Ez5ueUIW |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create conventions.md — core defaults, broker selection, message design | Developer | — | — | — | — |
| 2 | Create event-sourcing.md — event sourcing, CQRS, event stores | Developer | — | — | — | — |
| 3 | Create patterns.md — sagas, DLQ, idempotency, retry | Developer | — | — | — | — |
| 4 | Create operations.md — production ops, monitoring, scaling | Developer | — | — | — | — |
| 5 | Verify stack: tests pass, lint clean, acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 5 |
| **Total Duration** | 6m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |