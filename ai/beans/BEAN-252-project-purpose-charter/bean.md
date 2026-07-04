# BEAN-252: Project Purpose Statement / Charter

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-252 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:16 |
| **Completed** | 2026-04-17 18:20 |
| **Duration** | 4m (corrected 2026-07) |
| **Owner** | worker-bean-252 |
| **Category** | App |

## Problem Statement

External audit (2026-04-17): a freshly generated project's README says only `"AI-team-backed project for <Name>"` when `spec.project.description` is empty. The audit called this out as the #1 day-1 blocker: *"Nine personas, zero product. A team with no goal will invent one, inconsistently."* `project.description` is an optional field on `ProjectIdentity`, and the Wizard doesn't require it. BEAN-244's README falls back to a generic blurb that contains no purpose information.

The generated team needs a one-page source of truth answering: **what is this, who is it for, what does "done" look like.**

## Goal

A generated project contains a visible, hard-to-skip purpose statement. A persona opening the project at day 1 can understand the what/who/done without reading code or asking the user.

Two plausible implementations (decide during Architect/BA participation):

1. **Scaffold `ai/context/project-charter.md`** — a templated one-pager with clearly marked `TODO` sections for purpose, audience, success criteria, constraints. The generator emits it empty-but-structured.
2. **Promote description to required** — make `project.description` a required field (with validation minimum length, e.g., 40 chars) and have the scaffold refuse to proceed without it. Charter derived from description.

Both are valid. The bean picks one after design.

## Scope

### In Scope
- Decide between charter-file approach and required-description approach (BA + Architect both land on the wave).
- Implement the chosen approach in `foundry_app/services/scaffold.py` (or the wizard layer for the validation path).
- Update the wizard's project-identity page to reflect the new requirement if chosen.
- If a charter file is scaffolded, populate it with a clear TODO-oriented template.
- Tests: asserting the charter / required description is present and meets the contract.

### Out of Scope
- Designing a full project-requirements workflow (BA persona already covers that).
- Changing the generated CLAUDE.md — that already reflects the description once present.
- Forcing existing projects to add charters retroactively.

## Acceptance Criteria

- [x] Decision recorded in `ai/context/decisions.md` (ADR-003) — charter-file approach chosen over required-description.
- [x] Chosen approach implemented: `ai/context/project-charter.md` is scaffolded with a structured TODO template via `_render_project_charter()` in `foundry_app/services/scaffold.py`.
- [x] Charter file contains labeled sections for **Purpose**, **Audience**, **Success Criteria**, **Non-Goals**, and **Constraints**.
- [x] Tests cover the happy path and the missing-description path (`test_charter_echoes_description_when_present` + `test_charter_shows_todo_when_description_absent`).
- [x] All tests pass: `uv run pytest` → 1819 passed.
- [x] Lint clean: `uv run ruff check foundry_app/` → All checks passed.

> The required-description criteria were not exercised because Option 2 was not chosen (see ADR-003).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Record decision (charter-file approach) + draft template structure | Architect | — | Done |
| 2 | Define charter section content guidance | BA | 1 | Done |
| 3 | Implement scaffold_project charter generation | Developer | 1, 2 | Done |
| 4 | Tests + verification | Tech-QA | 3 | Done |

> Bottleneck check: tasks are sequential; charter content (BA) blocks dev implementation. No shared-resource contention.

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/scaffold.py` | +90 (new `_render_project_charter()` + emission block in `scaffold_project()`) |
| `tests/test_scaffold.py` | +102 / −2 (new `TestProjectCharter` 8-test class + dir-count update) |
| `ai/context/decisions.md` | +44 (ADR-003) |

## Notes

**Origin.** External audit, 2026-04-17: "Project has no purpose statement. README says 'project for Test2'; nothing tells the team what Test2 is, who it's for, or what 'done' looks like."

**Pairing.** BA + Architect both plausible on the wave — BA for the charter template, Architect for the validation approach.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Record decision (charter-file approach) + draft template structure | Architect | < 1m | N/A (suspect) | N/A (suspect) | — |
| 2 | Define charter section content guidance | BA | < 1m | 845,992 | 10,302 | $2.43 |
| 3 | Implement scaffold_project charter generation | Developer | < 1m | 373,830 | 21,229 | $4.40 |
| 4 | Tests + verification | Tech-QA | < 1m | N/A (suspect) | N/A (suspect) | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 2m |
| **Total Tokens In** | 1,219,822 |
| **Total Tokens Out** | 31,531 |
| **Total Cost** | $6.83 |