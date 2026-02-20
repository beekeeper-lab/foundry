# BEAN-164: Review and Prune Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-164 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 20:11 |
| **Completed** | 2026-02-20 20:21 |
| **Duration** | 10m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

When Foundry generates a new application, the CLAUDE.md file in the generated project includes references to sub-agents and personas that are not part of the selected team. For example, a project with team members [compliance-risk, integrator-merge-captain, research-librarian, team-lead, technical-writer] still has other agent types listed in the CLAUDE.md. The generated CLAUDE.md is too verbose and contains irrelevant content.

## Goal

Investigate how CLAUDE.md is generated, identify why non-selected personas appear, and fix the generation logic to only include team members that were actually selected. Prune the template/generation to produce a cleaner, more focused CLAUDE.md.

## Scope

### In Scope
- Investigate the CLAUDE.md generation pipeline (compiler service, templates)
- Identify why non-selected personas/agents appear in the output
- Fix the generation logic to filter CLAUDE.md content to only selected team members
- Ensure the generated CLAUDE.md is concise and relevant

### Out of Scope
- Redesigning the CLAUDE.md format entirely
- Modifying the Foundry project's own CLAUDE.md

## Acceptance Criteria

- [x] Generated CLAUDE.md only references team members that were selected in the composition
- [x] No extraneous persona/agent references appear for non-selected team members
- [x] Generated CLAUDE.md is concise — no verbose boilerplate for unused features
- [x] Existing test for CLAUDE.md generation is updated or new test added
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Filter non-selected persona references in generated CLAUDE.md | Developer | — | Done |
| 2 | Verify persona filtering | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention found — sequential Developer → Tech-QA wave

## Notes

Look at the generated project in `generated-projects/my-new-app-idea/` for a concrete example. The team was [compliance-risk, integrator-merge-captain, research-librarian, team-lead, technical-writer] but CLAUDE.md had other agent types listed.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69984597908c4c734466f8be |
| **Card Name** | Review Claude.md |
| **Card URL** | https://trello.com/c/zLLmGx8X/38-review-claudemd |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Filter non-selected persona references in generated CLAUDE.md | Developer | 5m | 3,349,453 | 1,222 | $6.85 |
| 2 | Verify persona filtering | Tech-QA | < 1m | 1,101,754 | 304 | $1.81 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 5m |
| **Total Tokens In** | 4,451,207 |
| **Total Tokens Out** | 1,526 |
| **Total Cost** | $8.66 |