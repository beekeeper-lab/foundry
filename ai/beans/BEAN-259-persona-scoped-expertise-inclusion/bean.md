# BEAN-259: Persona-Scoped Expertise Inclusion

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-259 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

External audit (2026-04-17): "All 9 personas receive identical React/TS expertise. DevOps-Release, Integrator-Merge-Captain, and UX/UI Designer don't need strict-mode TS configs in their prompt. Inflates context, dilutes role focus."

Today the compiler injects every selected expertise into every persona's member prompt. The result: the DevOps-Release agent's prompt includes `tsconfig.json` strict-mode details, and the UX designer's prompt includes `ruff` formatter defaults. This inflates token usage, dilutes role focus, and makes every prompt longer than it needs to be.

## Goal

Each persona's compiled member prompt contains only the expertise it actually uses. The Developer sees the full stack. DevOps-Release sees infra/deploy expertise and omits language-specific config noise. UX/UI Designer sees a11y/design-system expertise and omits back-end detail.

## Scope

### In Scope
- **Design first.** Decide on a mechanism — two candidates:
  - **(A) Per-expertise persona relevance.** Each expertise YAML (or convention file front-matter) lists the personas it applies to. The compiler filters expertise per persona based on that list.
  - **(B) Per-persona expertise filter.** Each persona file declares which expertise *categories* it wants (e.g., `design`, `deploy`, `language`). The compiler filters by category.
- Architect wave contribution with ADR in `ai/context/decisions.md`.
- Implement the chosen approach in `foundry_app/services/compiler.py` and `foundry_app/services/agent_writer.py`.
- Library content additions: whichever approach is chosen requires metadata on either expertise files or persona files.
- Tests: a React/TS composition's DevOps-Release member prompt contains no `tsconfig` detail; its UX member prompt contains no `ruff` detail. Its Developer member prompt still contains both.

### Out of Scope
- Dynamic expertise tailoring based on task content (that's runtime, not compile-time).
- Reducing expertise library size.
- Changing the expertise extraction heuristics (that's orthogonal).

## Acceptance Criteria

- [ ] ADR recorded in `ai/context/decisions.md` with the chosen mechanism (A or B) and rationale.
- [ ] Library metadata updated to support the filter (either on expertise or on personas).
- [ ] Compiler and agent-writer respect the filter.
- [ ] Regenerating `small-python-team.yml`: Developer member prompt contains Python/clean-code expertise; DevOps-Release member prompt (if present in the team) contains deploy-relevant expertise only.
- [ ] Regenerating a React/TS composition: DevOps-Release and UX-UI-Designer member prompts do NOT contain `tsconfig` or language-specific lint config detail.
- [ ] Token-count measurement: verify the filter reduces per-persona prompt size by a meaningful amount (target: ≥20% reduction for non-Developer personas).
- [ ] Tests cover the filter end-to-end for at least two personas.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Architect required — design-first bean.** The mechanism choice drives significant library metadata and compiler changes. ADR before implementation.

**Backward compatibility.** Existing compositions without metadata should default to today's behavior (all expertise to all personas). Don't break existing generated projects.

**Interaction with BEAN-240.** Agent Context Budget Optimization — this bean advances the same goal (smaller, more focused per-persona context) with a complementary mechanism.

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
