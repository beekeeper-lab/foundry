# BEAN-180: Kubernetes Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-180 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:09 |
| **Completed** | 2026-02-20 19:14 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a kubernetes tech stack. Add K8s stack to ai-team-library. Manifests, Helm charts, operators, RBAC, network policies, resource limits, pod security. Cloud-agnostic.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add K8s stack to ai-team-library. Manifests, Helm charts, operators, RBAC, network policies, resource limits, pod security. Cloud-agnostic.

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
| 1 | Create conventions.md — core K8s conventions, manifests, resource mgmt | Developer | — | Done |
| 2 | Create helm-charts.md — Helm charts, templating, releases | Developer | — | Done |
| 3 | Create security.md — RBAC, pod security, network policies | Developer | — | Done |
| 4 | Create networking.md — Services, ingress, DNS, service mesh | Developer | — | Done |
| 5 | Create operations.md — Operators, scaling, monitoring, upgrades | Developer | — | Done |
| 6 | Update test expectations for kubernetes stack | Developer | 1 | Done |
| 7 | Run tests and lint verification | Tech-QA | 1-6 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #53.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f33821f5afb7d095df3c |
| **Card Name** | Kubernetes Tech Stack |
| **Card URL** | https://trello.com/c/dAhQ2OMT |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create conventions.md — core K8s conventions, manifests, resource mgmt | Developer | — | — | — | — |
| 2 | Create helm-charts.md — Helm charts, templating, releases | Developer | — | — | — | — |
| 3 | Create security.md — RBAC, pod security, network policies | Developer | — | — | — | — |
| 4 | Create networking.md — Services, ingress, DNS, service mesh | Developer | — | — | — | — |
| 5 | Create operations.md — Operators, scaling, monitoring, upgrades | Developer | — | — | — | — |
| 6 | Update test expectations for kubernetes stack | Developer | — | — | — | — |
| 7 | Run tests and lint verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 7 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |