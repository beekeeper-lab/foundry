# BEAN-295: Web and backend framework expertise packs

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-295 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-07-03 |
| **Started** | 2026-07-04 02:05 |
| **Completed** | 2026-07-04 02:21 |
| **Duration** | 16m |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

SPEC-021 (2026-07 audit) identified framework gaps in the expertise library: no Vue/Svelte/Next.js pack and no backend framework packs (FastAPI/Django, Spring, Express/Nest). Teams composing projects on these stacks get only generic language packs.

## Goal

The library ships framework packs for the most-requested web and backend stacks, following the SPEC-019 authoring contract (frontmatter, canonical schema, decision-dense Defaults table).

## Scope

### In Scope
- New packs (prioritized): fastapi, nextjs, vue, spring-boot; more per demand
- Each pack: conventions.md entry file per the authoring contract + 2-4 sibling deep-dive files
- dev-loop stack mapping entries where a new runner is implied

### Out of Scope
- Rewriting existing packs
- CSS frameworks and component libraries

## Acceptance Criteria

> Authored by: BA (when activated) | Team-Lead (default).

- [ ] (file:ai-team-library/expertise/fastapi/conventions.md) FastAPI pack exists with frontmatter
- [ ] (file:ai-team-library/expertise/nextjs/conventions.md) Next.js pack exists with frontmatter
- [ ] (test:tests/test_reference_integrity.py) Frontmatter contract holds
- [ ] (test:tests/) All tests pass (`uv run pytest`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Author fastapi pack | developer | — | Done |
| 2 | Author nextjs pack | developer | — | Done |
| 3 | Author vue pack | developer | — | Done |
| 4 | Author spring-boot pack | developer | — | Done |
| 5 | Integration (indexer tests, dev-loop map) | developer | 1,2,3,4 | Done |
| 6 | Verification + VDD report | tech-qa | 5 | Done |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

Origin: SPEC-021 deferred scope (`ai/context/audits/2026-07-agentic-excellence/SPEC-021-new-expertise-packs.md`). Pack authoring parallelizes well across developer subagents (the 2026-07 SPEC-003 curation used four).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | team-lead, developer, tech-qa |
| **Bounces** | 0 |
| **Scope changes** | 1 (category value normalized to existing `Frameworks` taxonomy during integration) |
| **Contract violations** | 0 |
| **Inputs escape-hatch invocations** | 0 |
| **Dispatch mode** | mixed (agent-subagent ×5, in-process ×1 tiny integration task) |
