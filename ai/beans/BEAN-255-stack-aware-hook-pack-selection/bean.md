# BEAN-255: Stack-Aware Hook Pack Selection

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-255 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
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

- [ ] A documented mapping in `ai/context/hook-selection.md` (or in the library README) defines which hooks default-on for which expertise / cloud selections.
- [ ] `safety_writer.py` (or equivalent) consults that mapping when building the default hook set.
- [ ] Regenerating `examples/small-python-team.yml` yields Python-appropriate hooks and no Azure hooks.
- [ ] Regenerating a React/TS composition yields ESLint/Prettier/tsc hooks and no ruff hook.
- [ ] If a new ESLint/Prettier hook pack is needed in the library, it is added.
- [ ] Tests cover at least two stacks end-to-end.
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

**Architect warranted.** Hook selection mapping is a cross-cutting API surface. ADR-worthy.

**Pairs with BEAN-256.** Both address "generation is not stack-aware enough" — hooks are one half, commands the other.

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
