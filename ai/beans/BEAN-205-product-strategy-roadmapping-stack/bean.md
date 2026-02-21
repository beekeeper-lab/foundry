# BEAN-205: Product Strategy & Roadmapping Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-205 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 19:52 |
| **Completed** | 2026-02-20 19:59 |
| **Duration** | <10m |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

The ai-team-library lacks a product strategy & roadmapping stack. Add product-strategy stack to ai-team-library. OKRs, prioritization frameworks (RICE, MoSCoW), user story mapping, competitive analysis templates, go-to-market planning, feature lifecycle management.

## Goal

Add the stack to `ai-team-library/stacks/` with comprehensive, production-ready guidance.

## Scope

### In Scope
- Add product-strategy stack to ai-team-library. OKRs, prioritization frameworks (RICE, MoSCoW), user story mapping, competitive analysis templates, go-to-market planning, feature lifecycle management.

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
| 1 | Create product-strategy stack files | Developer | — | Done |
| 2 | Verify product-strategy stack | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)
> Bottleneck check: no contention found — sequential Developer → Tech-QA wave.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

Sourced from Trello card #80.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998f4b8dceb93c15c345b07 |
| **Card Name** | Product Strategy & Roadmapping Stack |
| **Card URL** | https://trello.com/c/humxdX2B |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create product-strategy stack files | Developer | < 1m | 2,135,521 | 607 | $5.68 |
| 2 | Verify product-strategy stack | Tech-QA | < 1m | 3,081,767 | 643 | $7.31 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 5,217,288 |
| **Total Tokens Out** | 1,250 |
| **Total Cost** | $12.99 |