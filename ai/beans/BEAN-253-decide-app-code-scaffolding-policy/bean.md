# BEAN-253: Decide App-Code Scaffolding Policy

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-253 |
| **Status** | Unapproved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |

## Problem Statement

External audit (2026-04-17): "No code scaffolding despite claiming React/TS. No `package.json`, `tsconfig.json`, `vite.config.ts`, `src/`, `.eslintrc`, no lockfile. A Developer cannot run anything on day 1."

This is a **design question about Foundry's scope**, not an implementation bug. Today, Foundry generates the *AI team scaffold* (`.claude/`, `ai/`, `CLAUDE.md`, agent/member files), not the *app code scaffold* (language-specific project skeleton). The audit is correct that this leaves the generated team with nothing to build on, but *adding app scaffolding* is a substantial scope expansion and deserves a conscious decision rather than a drive-by fix.

## Goal

Foundry's position on app-code scaffolding is documented and consistent. The three viable directions:

- **(A) Foundry scaffolds both.** The generator runs a stack-appropriate initializer (e.g., `npm create vite@latest` for React/TS, `uv init` for Python) as a pipeline stage. Pro: day-1 runnable. Con: significant scope expansion, stack maintenance, interaction with user-chosen directories, dependency management.
- **(B) Foundry scaffolds AI only; docs say so.** Add an explicit "Scope" section to the generated CLAUDE.md and README stating Foundry generates the team context; the user initializes the app themselves. Pair with a `docs/starter-stacks.md` that recommends init commands per stack. Pro: keeps Foundry focused, zero maintenance of stack templates. Con: worse out-of-box experience.
- **(C) Composition-controlled.** Add `spec.generation.scaffold_app_code: bool | null` (default null = prompt user). When true, invoke a per-stack scaffolder plugin. Pro: users who want fast start get it; users who want strict control keep it.

This bean picks one direction and documents it. Implementation may be a follow-up bean if the direction requires substantial work.

## Scope

### In Scope
- Research + decision: write an ADR in `ai/context/decisions.md` covering the three options, trade-offs, and the chosen direction.
- Update the generated project's CLAUDE.md and/or README to state the chosen policy explicitly.
- If direction (A) or (C): file follow-up beans for per-stack scaffolder implementations (at least one proof-of-concept stack).
- If direction (B): the bean is doc-only — update CLAUDE.md template and README template.
- BEAN-251 (permission scope) should agree with this decision; cross-reference.

### Out of Scope
- Implementing every per-stack scaffolder (those become follow-up beans).
- Integrating with external tools like `cookiecutter` or `yeoman` in this bean.
- Retrofitting existing generated projects.

## Acceptance Criteria

- [ ] ADR in `ai/context/decisions.md` records the chosen direction (A, B, or C) with rationale.
- [ ] Generated project's CLAUDE.md contains a clear Scope statement aligning with the decision.
- [ ] If direction (B): no code changes beyond CLAUDE.md/README template updates.
- [ ] If direction (A) or (C): at least one follow-up bean is filed (e.g., "React/TS app scaffolder") with the implementation plan.
- [ ] Cross-referenced with BEAN-251 — the chosen policy matches the permission model.
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

**Architect required.** This is a scope/boundary decision with downstream impact on the pipeline, permissions, and user expectations.

**Dependencies.** BEAN-251 (permission scope) and this bean should be decided together — they answer the same underlying question about Foundry's role.

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
