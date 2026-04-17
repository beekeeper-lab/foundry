# BEAN-255: Stack-Aware Hook Pack Selection

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-255 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:16 |
| **Completed** | 2026-04-17 18:21 |
| **Duration** | 1269h 14m |
| **Owner** | Claude Code (worker) |
| **Category** | App |

## Problem Statement

External audit (2026-04-17): "Hook/stack mismatch. `pre-commit-lint` runs `ruff` (Python) on a React/TS project. Should be ESLint/Prettier/`tsc --noEmit`. Also two Azure hooks enabled for a project with no Azure footprint."

Hook pack selection today is either static (posture-driven: baseline = a fixed set) or user-composed. It doesn't respond to the selected expertise / stack. Result: a React/TS project gets Python lint hooks, an AWS project gets Azure hooks. The hooks look like governance theater because they don't match the tech.

## Goal

Hook pack selection responds to the selected expertise, personas, and cloud providers. When a user picks `react` + `typescript` as expertise, `pre-commit-lint` binds to ESLint/Prettier/tsc, not ruff. When no Azure providers are selected, Azure hooks are not enabled by default.

## Scope

### In Scope
- Map expertise → default hook-pack choices (e.g., `python` → `ruff` lint hook; `react`/`typescript`/`node` → `eslint` + `prettier` + `tsc` hooks).
- Map cloud providers → cloud-specific hooks (e.g., `azure` → Azure Secret/Policy hooks; `aws` → AWS equivalents; none → neither).
- Update `safety_writer.py` (or the relevant library composition logic) to assemble the hook-pack list from posture + stack signals rather than a fixed list.
- Library additions: if ESLint/Prettier hook packs don't exist yet in `ai-team-library/claude/hooks/`, add them. If they do, wire them through.
- Tests asserting the hook set for a React/TS composition does not include Python lint hooks, and vice versa.
- Warn (don't fail) when a composition explicitly requests a hook pack that doesn't match its stack — keeps backward compatibility.

### Out of Scope
- Dynamic hook authoring (users write custom hook code).
- Per-persona hook gating.
- Changing posture semantics (that's BEAN-250).
- Implementing dev-loop commands (that's BEAN-256).

## Acceptance Criteria

- [x] A documented mapping in `ai/context/hook-selection.md` (or in the library README) defines which hooks default-on for which expertise / cloud selections.
- [x] `safety_writer.py` (or equivalent) consults that mapping when building the default hook set.
- [x] Regenerating `examples/small-python-team.yml` yields Python-appropriate hooks and no Azure hooks.
- [x] Regenerating a React/TS composition yields ESLint/Prettier/tsc hooks and no ruff hook.
- [x] If a new ESLint/Prettier hook pack is needed in the library, it is added.
- [x] Tests cover at least two stacks end-to-end.
- [x] All tests pass (`uv run pytest`) — 1830 passed.
- [x] Lint clean (`uv run ruff check foundry_app/`) — All checks passed.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design stack→hook mapping, create hook-selection.md | Architect | — | Done |
| 2 | Add new hook pack library docs (lint-js, aws-*) | Developer | 1 | Done |
| 3 | Implement stack-aware resolution in safety_writer | Developer | 1,2 | Done |
| 4 | Add tests for stack-aware hook selection | Tech-QA | 3 | Done |
| 5 | Run pytest and ruff, verify acceptance criteria | Tech-QA | 4 | Done |

> Skipped: BA (default — scope is well-defined by external audit)

## Changes

| File | Lines |
|------|-------|
| ai/context/hook-selection.md | +117 |
| ai-team-library/claude/hooks/pre-commit-lint-js.md | +36 |
| ai-team-library/claude/hooks/aws-read-only.md | +35 |
| ai-team-library/claude/hooks/aws-limited-ops.md | +36 |
| foundry_app/services/safety_writer.py | +182/-26 |
| tests/test_safety_writer.py | +251 |
| tests/test_library_indexer.py | +3 |

## Notes

**Architect warranted.** Hook selection mapping is a cross-cutting API surface. ADR-worthy.

**Pairs with BEAN-256.** Both address "generation is not stack-aware enough" — hooks are one half, commands the other.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Design stack→hook mapping, create hook-selection.md | Architect | — | — | — | — |
| 2 | Add new hook pack library docs (lint-js, aws-*) | Developer | — | — | — | — |
| 3 | Implement stack-aware resolution in safety_writer | Developer | — | — | — | — |
| 4 | Add tests for stack-aware hook selection | Tech-QA | — | — | — | — |
| 5 | Run pytest and ruff, verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 5 |
| **Total Duration** | 1269h 14m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |