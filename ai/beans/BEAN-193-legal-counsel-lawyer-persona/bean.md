# BEAN-193: Legal Counsel / Lawyer Persona

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-193 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:31 |
| **Completed** | 2026-02-20 19:36 |
| **Duration** | 5m |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a legal counsel / lawyer persona. Add legal-counsel persona to ai-team-library. Contract review, IP and licensing guidance, regulatory compliance, risk assessment, legal drafting. Works alongside compliance-risk and BA personas.

## Goal

Add the persona to `ai-team-library/personas/` with complete persona definition, outputs, prompts, and templates.

## Scope

### In Scope
- Add legal-counsel persona to ai-team-library. Contract review, IP and licensing guidance, regulatory compliance, risk assessment, legal drafting. Works alongside compliance-risk and BA personas.

### Out of Scope
- Changes to the Foundry application code
- Modifications to existing library content

## Acceptance Criteria

- [x] Persona directory created in `ai-team-library/personas/` with persona.md, outputs.md, prompts.md, templates/
- [x] persona.md follows standardized format with mission, capabilities, boundaries
- [x] outputs.md defines deliverable types and formats
- [x] prompts.md provides reusable prompt templates
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create legal-counsel persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | Done |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | 1 | Done |
| 3 | Run tests and lint to verify | Tech-QA | 2 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #68.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f3d32e70c5b76447f9d6 |
| **Card Name** | Legal Counsel / Lawyer Persona |
| **Card URL** | https://trello.com/c/dWHjhWvc |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create legal-counsel persona directory with persona.md, outputs.md, prompts.md, templates/ | Developer | — | — | — | — |
| 2 | Update test_library_indexer.py EXPECTED_PERSONAS | Developer | — | — | — | — |
| 3 | Run tests and lint to verify | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 5m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |