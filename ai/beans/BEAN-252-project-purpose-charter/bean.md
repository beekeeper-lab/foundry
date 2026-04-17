# BEAN-252: Project Purpose Statement / Charter

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-252 |
| **Status** | Unapproved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
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

- [ ] Decision recorded in `ai/context/decisions.md` or in this bean's Notes before implementation begins.
- [ ] Chosen approach implemented: either `ai/context/project-charter.md` is scaffolded with a structured TODO template, OR `spec.project.description` is required with minimum length.
- [ ] If charter-file approach: the generated file contains labeled sections for **Purpose**, **Audience**, **Success Criteria**, **Non-Goals**, and **Constraints**.
- [ ] If required-description approach: the validator rejects compositions with missing/short descriptions; wizard surfaces the error before Generate is clickable.
- [ ] Tests cover both the happy path and the missing/weak-description rejection.
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

**Origin.** External audit, 2026-04-17: "Project has no purpose statement. README says 'project for Test2'; nothing tells the team what Test2 is, who it's for, or what 'done' looks like."

**Pairing.** BA + Architect both plausible on the wave — BA for the charter template, Architect for the validation approach.

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
