# BEAN-233: Generate Optimized CLAUDE.md for Projects

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-233 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-03-12 |
| **Started** | 2026-03-12 03:06 |
| **Completed** | 2026-03-12 03:17 |
| **Duration** | 344h 40m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Generated projects need a well-structured CLAUDE.md file that serves as a context budget — concise, universal instructions that apply to every Claude Code conversation. Currently, generated CLAUDE.md files may be bloated or missing key information. CLAUDE.md should be a table of contents with context (~50-100 lines), not an encyclopedia.

## Goal

Generate lean, optimized CLAUDE.md files for new projects that include only universally relevant information: project name, tech stack summary, key conventions, directory structure, and pointers to detailed docs. Persona-specific, stack-specific, and workflow-specific content should be in separate files loaded on demand.

## Scope

### In Scope
- Generate CLAUDE.md with: project name/description, tech stack summary, key universal conventions, directory structure overview, pointers to detailed docs
- Keep generated CLAUDE.md under ~100 lines
- Move persona-specific content to separate files referenced by pointers
- Move stack-specific conventions to separate files

### Out of Scope
- Modifying the Foundry project's own CLAUDE.md
- Changing the generation pipeline architecture

## Acceptance Criteria

- [x] Generated CLAUDE.md contains project name and one-line description
- [x] Generated CLAUDE.md contains tech stack summary
- [x] Generated CLAUDE.md contains key universal conventions
- [x] Generated CLAUDE.md contains directory structure overview
- [x] Generated CLAUDE.md contains pointers to detailed docs (not the docs themselves)
- [x] Generated CLAUDE.md is under 100 lines
- [x] Persona-specific content is in separate files, not in CLAUDE.md
- [x] All tests pass (`uv run pytest`) — 530 non-UI tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add description field to ProjectIdentity and refactor compiler for lean CLAUDE.md | Developer | — | Done |
| 2 | Test lean CLAUDE.md generation | Tech-QA | 1 | Done |

> Skipped: BA (no user-facing behavior change — internal generation output), Architect (no new subsystem — refactoring within existing compiler service)
> Bottleneck check: no contention — task 1 modifies source, task 2 modifies tests

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Trello card #103. Key principle from card description: "CLAUDE.md is a context budget, not a documentation dump. Every line costs tokens on every conversation. Treat it like a hot path."

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 69b22a343bc5c7a588078f8c |
| **Card Name** | Generating new Claude.md files for generated projects. |
| **Card URL** | https://trello.com/c/goVm1LMF |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Add description field to ProjectIdentity and refactor compiler for lean CLAUDE.md | Developer | < 1m | 3,553,258 | 13,130 | $10.55 |
| 2 | Test lean CLAUDE.md generation | Tech-QA | < 1m | 14,701,692 | 39,460 | $30.44 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 18,254,950 |
| **Total Tokens Out** | 52,590 |
| **Total Cost** | $40.99 |