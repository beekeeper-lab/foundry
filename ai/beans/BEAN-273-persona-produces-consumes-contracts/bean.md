# BEAN-273: Persona `produces:` / `consumes:` Contracts

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-273 |
| **Status** | Deferred |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |
| **Depends On** | — |

## Problem Statement

Today persona files describe outputs in prose ("Implementation notes and decision records," "User stories with acceptance criteria"). There is no machine-readable contract: what artifact types a persona *produces*, and what types it *consumes* from upstream personas.

The architectural review identified this as the weakest of the three principles ("narrow specialist boundaries with strict contracts"). Without typed contracts:

- The compose-time validator can't tell if a team is internally coherent (e.g., Tech-QA needs `traceability-input` but no producer is on the team).
- Handoffs are generic prose templates regardless of sender/receiver pair.
- Role overlap (the BA/Team-Lead/Developer/Tech-QA acceptance-criteria tangle) cannot be detected automatically.

## Goal

Every persona file declares a frontmatter (or sibling YAML) block listing the artifact types it produces and consumes. A small registry names each artifact type. The compiler reads these and emits a compiled contract graph the validator (BEAN-274) and handoff schemas (BEAN-276) can use.

## Scope

### In Scope

- New file `ai-team-library/contracts/artifact-types.yml` — registry of all artifact types with: `name`, `description`, `format` (markdown/yaml/json), `required-fields`, `template-path`.
- Initial registry covers ~12-15 types: `bean-spec`, `task-spec`, `user-story`, `acceptance-criteria`, `scope-definition`, `risk-register`, `adr`, `design-spec`, `dev-decision`, `code-change`, `test-suite`, `traceability-matrix`, `vdd-report`, `handoff-packet`, `merge-summary`.
- Add YAML frontmatter (or a `contracts:` block in the existing markdown) to every core persona file in `ai-team-library/personas/core/*/persona.md`:
  - `produces:` list of artifact-type names
  - `consumes:` list of artifact-type names
- Same edits propagated into Foundry's `.claude/agents/*.md` via the kit/regen.
- New helper in `foundry_app/services/library_indexer.py` (or new `contracts_loader.py`) that loads and validates the registry + persona contracts.
- Compiler emits a `contracts:` block into generated `ai/team/composition.yml` showing the team's compiled produces/consumes graph (informational; BEAN-274 will use this for validation).
- Tests: registry loads; every type referenced by a persona exists; round-trip through compiler.

### Out of Scope

- Validating the graph (BEAN-274).
- Schema enforcement on the artifacts themselves (e.g., "user-story must have Given/When/Then") — registry names the format and required fields, but enforcing them on output content is a follow-up bean.
- Updating extended personas (limit to core 5 in this bean to keep scope small).
- Changing artifact templates (use existing `ai-team-library/personas/*/templates/`).

## Acceptance Criteria

- [ ] `ai-team-library/contracts/artifact-types.yml` exists with the initial registry.
- [ ] All 5 core persona files declare `produces:` and `consumes:` lists.
- [ ] Every type referenced by a persona exists in the registry (validated by tests).
- [ ] Compiled `composition.yml` in generated projects contains a `contracts:` block summarizing the team's graph.
- [ ] At least one core persona pair has matching `produces` → `consumes` (e.g., BA produces `user-story`, Developer consumes `user-story`).
- [ ] No core persona has `produces:` or `consumes:` empty (every role connects to at least one other).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: BA (define the artifact-type registry — this is requirements work), Architect (ADR for the contract format and where it lives), Developer (registry file + persona edits + indexer changes), Tech-QA (verification).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**BA + Architect required.** The artifact-type registry is essentially a domain glossary — BA territory. The contract location and indexer integration is design work — Architect territory.

**Foundation for BEAN-274 and BEAN-276.** Both depend on this bean's contracts being in place. Land this first.

**Resolves part of role overlap.** The acceptance-criteria ownership question (5 roles touching one artifact) gets a structural answer here: whichever persona declares `produces: acceptance-criteria` owns it. BEAN-275 codifies the policy decision.

**Frontmatter format.** Recommend YAML frontmatter at the top of `persona.md`, fenced with `---`. Keeps the contract human-readable and lets `ai-team-library/personas/*/persona.md` stay markdown-readable. Architect ADR can revisit if there's a better location.

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
