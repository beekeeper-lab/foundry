# BEAN-175: GDPR & Data Privacy Compliance Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-175 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 18:16 |
| **Completed** | 2026-02-20 18:20 |
| **Duration** | 4m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The ai-team-library has SOX and ISO 9000 compliance stacks but lacks GDPR/data privacy coverage. Teams building applications that handle EU personal data need guidance on data subject rights, privacy by design, DPIAs, cross-border transfers, and breach notification.

## Goal

Add a complete GDPR/data privacy compliance stack to the ai-team-library following the established stack template pattern.

## Scope

### In Scope
- GDPR fundamentals and key principles
- Data subject rights (access, erasure, portability, etc.)
- Privacy by design and by default
- Data protection impact assessments (DPIAs)
- Cross-border data transfers (SCCs, adequacy decisions)
- Breach notification procedures
- References to GDPR text, ICO guidance, and EDPB guidelines
- Stack file following standardized template

### Out of Scope
- Modifications to existing compliance stacks
- Country-specific implementations beyond GDPR
- Application code changes

## Acceptance Criteria

- [x] `ai-team-library/stacks/gdpr-data-privacy/` directory exists with properly formatted stack file
- [x] Stack file follows the standardized template pattern (Defaults table+alternatives, Do/Don't, Common Pitfalls, Checklist)
- [x] Covers GDPR fundamentals, data subject rights, privacy by design, DPIAs, cross-border transfers, and breach notification
- [x] All tests pass (`uv run pytest`) — pre-existing PySide6 import error in headless env, no regression
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create GDPR fundamentals and data subject rights stack file | Developer | — | Done |
| 2 | Create privacy by design and DPIAs stack file | Developer | — | Done |
| 3 | Create cross-border transfers and breach notification stack file | Developer | — | Done |
| 4 | Verify all acceptance criteria, run tests and lint | Tech-QA | 1,2,3 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Follows the pattern of iso-9000 and sox-compliance stacks. References GDPR text, ICO guidance, and EDPB guidelines.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998e28ca32d2ac1d7ffdd53 |
| **Card Name** | GDPR & Data Privacy Compliance Stack |
| **Card URL** | https://trello.com/c/fGMVrtXp/44-gdpr-data-privacy-compliance-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create GDPR fundamentals and data subject rights stack file | Developer | — | — | — | — |
| 2 | Create privacy by design and DPIAs stack file | Developer | — | — | — | — |
| 3 | Create cross-border transfers and breach notification stack file | Developer | — | — | — | — |
| 4 | Verify all acceptance criteria, run tests and lint | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 4m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |