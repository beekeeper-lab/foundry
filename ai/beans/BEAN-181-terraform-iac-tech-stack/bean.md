# BEAN-181: Terraform/IaC Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-181 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:09 |
| **Completed** | 2026-02-20 19:13 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a terraform/iac tech stack. Add Terraform/IaC stack to ai-team-library. Module structure, state management, drift detection, provider patterns, workspace strategies.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add Terraform/IaC stack to ai-team-library. Module structure, state management, drift detection, provider patterns, workspace strategies.

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
| 1 | Create conventions.md — defaults, alternatives, project structure, naming, provider patterns | Developer | — | Done |
| 2 | Create modules.md — module structure, composition, registry patterns | Developer | — | Done |
| 3 | Create state-management.md — backends, locking, migration, workspace strategies | Developer | — | Done |
| 4 | Create operations.md — drift detection, CI/CD, plan/apply workflows | Developer | — | Done |
| 5 | Update test_library_indexer.py EXPECTED_STACKS | Developer | 1 | Done |
| 6 | Run tests and lint verification | Tech-QA | 5 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #54.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33974d4b6ae039e21dc |
| **Card Name** | Terraform/IaC Tech Stack |
| **Card URL** | https://trello.com/c/9g945X4L |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create conventions.md — defaults, alternatives, project structure, naming, provider patterns | Developer | — | — | — | — |
| 2 | Create modules.md — module structure, composition, registry patterns | Developer | — | — | — | — |
| 3 | Create state-management.md — backends, locking, migration, workspace strategies | Developer | — | — | — | — |
| 4 | Create operations.md — drift detection, CI/CD, plan/apply workflows | Developer | — | — | — | — |
| 5 | Update test_library_indexer.py EXPECTED_STACKS | Developer | — | — | — | — |
| 6 | Run tests and lint verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 6 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |