# BEAN-142: Verification-Driven Development (VDD) Policy

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-142 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-17 |
| **Started** | 2026-02-17 03:40 |
| **Completed** | 2026-02-17 03:44 |
| **Duration** | 4m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The AI team currently lacks a formal policy enforcing verification-driven development. Without a structured VDD approach, beans may be marked as complete without adequate proof that acceptance criteria are truly met. This leads to regressions, incomplete features, and inconsistent quality across the codebase.

## Goal

Establish a Verification-Driven Development (VDD) policy that mandates every bean's acceptance criteria be verified through concrete, reproducible evidence (tests, lint checks, manual verification steps) before a bean can be marked Done. Codify this policy in team documentation so all personas follow it consistently.

## Scope

### In Scope
- Define the VDD policy document in `ai/context/`
- Specify verification requirements per bean category (App, Process, Infra)
- Update the bean workflow documentation to reference VDD gates
- Update the Tech-QA agent instructions to enforce VDD verification
- Update the Team Lead agent to check VDD compliance before closing beans

### Out of Scope
- Automated CI/CD enforcement (future bean)
- Changes to the Python application code
- Changes to test infrastructure

## Acceptance Criteria

- [ ] VDD policy document exists in `ai/context/` with clear verification requirements
- [ ] Bean workflow (`ai/context/bean-workflow.md`) references VDD verification gates
- [ ] Tech-QA agent (`.claude/agents/tech-qa.md`) includes VDD verification checklist
- [ ] Team Lead agent (`.claude/agents/team-lead.md`) includes VDD compliance check before bean closure
- [ ] Policy covers all three bean categories (App, Process, Infra) with category-specific verification steps

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create VDD Policy Doc & Update Team Docs | developer | — | Done |
| 2 | Verify VDD Policy Implementation | tech-qa | 1 | Done |

> Skipped: BA (default), Architect (default)

## Notes

Sourced from Trello Sprint_Backlog card. Card had no description — scope inferred from title.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6993d3ecb8d0f595f30d4455 |
| **Card Name** | Verification-Driven Development (VDD) Policy |
| **Card URL** | https://trello.com/c/iuPdEsP2/15-verification-driven-development-vdd-policy |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create VDD Policy Doc & Update Team Docs | developer | 2m | 15 | 2,036 | $0.15 |
| 2 | Verify VDD Policy Implementation | tech-qa | < 1m | 11 | 727 | $0.05 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 2m |
| **Total Tokens In** | 26 |
| **Total Tokens Out** | 2,763 |
| **Total Cost** | $0.20 |