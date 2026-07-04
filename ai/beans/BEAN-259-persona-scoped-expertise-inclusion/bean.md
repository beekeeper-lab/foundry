# BEAN-259: Persona-Scoped Expertise Inclusion

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-259 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-30 09:17 |
| **Completed** | 2026-04-30 09:38 |
| **Duration** | 21m (corrected 2026-07) |
| **Owner** | team-lead |
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

- [x] ADR recorded in `ai/context/decisions.md` with the chosen mechanism (A or B) and rationale.
- [x] Library metadata updated to support the filter (either on expertise or on personas).
- [x] Compiler and agent-writer respect the filter.
- [x] Regenerating `small-python-team.yml`: Developer member prompt contains Python/clean-code expertise; DevOps-Release member prompt (if present in the team) contains deploy-relevant expertise only.
- [x] Regenerating a React/TS composition: DevOps-Release and UX-UI-Designer member prompts do NOT contain `tsconfig` or language-specific lint config detail.
- [x] Token-count measurement: verify the filter reduces per-persona prompt size by a meaningful amount (target: ≥20% reduction for non-Developer personas).
- [x] Tests cover the filter end-to-end for at least two personas.
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Mechanism choice ADR | architect | — | Done |
| 2 | Implement persona-scoped expertise filter | developer | 1 | Done |
| 3 | Verify filter | tech-qa | 2 | Done |

> Skipped: BA (default) — requirements are clear, two candidate mechanisms documented in the bean. Architect engaged per bean's "Architect required" note.

## Changes

| File | Lines |
|------|-------|
| ai-team-library/expertise/accessibility-compliance/accessibility-audits.md | 8 |
| ai-team-library/expertise/python/conventions.md | 8 |
| ai-team-library/expertise/react/conventions.md | 8 |
| ai-team-library/expertise/typescript/conventions.md | 7 |
| ai/beans/BEAN-259-persona-scoped-expertise-inclusion/bean.md | 48 |
| ai/beans/BEAN-259-persona-scoped-expertise-inclusion/tasks/01-architect-mechanism-adr.md | 57 |
| ai/beans/BEAN-259-persona-scoped-expertise-inclusion/tasks/02-developer-implement-filter.md | 70 |
| ai/beans/BEAN-259-persona-scoped-expertise-inclusion/tasks/03-tech-qa-verify.md | 45 |
| ai/beans/_index.md | 2 |
| ai/context/decisions.md | 85 |
| ai/outputs/tech-qa/bean-259-verification.md | 88 |
| foundry_app/core/models.py | 8 |
| foundry_app/services/agent_writer.py | 30 |
| foundry_app/services/compiler.py | 40 |
| foundry_app/services/library_indexer.py | 92 |
| scripts/measure_bean_259_savings.py | 137 |
| tests/test_agent_writer.py | 357 |
| tests/test_compiler.py | 166 |
| tests/test_library_indexer.py | 174 |
| **Total** | **19 files: +1404 / -26** |

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
| 1 | Mechanism choice ADR | architect | 3m | 665,012 | 4,736 | $1.40 |
| 2 | Implement persona-scoped expertise filter | developer | 11m | 1,247,966 | 5,733 | $2.63 |
| 3 | Verify filter | tech-qa | 5m | 746,248 | 6,416 | $1.63 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 19m |
| **Total Tokens In** | 2,659,226 |
| **Total Tokens Out** | 16,885 |
| **Total Cost** | $5.66 |