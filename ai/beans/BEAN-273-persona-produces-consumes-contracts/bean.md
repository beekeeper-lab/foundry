# BEAN-273: Persona `produces:` / `consumes:` Contracts

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-273 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-04-30 10:40 |
| **Completed** | 2026-04-30 11:04 |
| **Duration** | 1573h 57m |
| **Owner** | team-lead |
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
| 1 | Define artifact-type registry content | BA | — | Done |
| 2 | ADR — contract format, location, loader integration | Architect | 01 | Done |
| 3 | Implement registry, persona contracts, loader, compiler emission | Developer | 02 | Done |
| 4 | Verify contracts — tests, lint, AC sweep | Tech-QA | 03 | Done |

> Wave: BA → Architect → Developer → Tech-QA. BA + Architect engaged per bean Notes ("BA + Architect required") and engagement rules (BA #4 spec/doc work; Architect #1 new module/dir, #5 schema/format, #7 foundation for BEAN-274/276). Tech-QA mandatory.

## Changes

| File | Lines |
|------|-------|
| ai-team-library/contracts/artifact-types.yml | +229 |
| ai-team-library/personas/architect/contracts.yml | +14 |
| ai-team-library/personas/ba/contracts.yml | +13 |
| ai-team-library/personas/developer/contracts.yml | +14 |
| ai-team-library/personas/team-lead/contracts.yml | +17 |
| ai-team-library/personas/tech-qa/contracts.yml | +14 |
| ai/beans/BEAN-273-…/bean.md | +28 −4 |
| ai/beans/BEAN-273-…/tasks/01-ba-…md | +79 |
| ai/beans/BEAN-273-…/tasks/02-architect-…md | +77 |
| ai/beans/BEAN-273-…/tasks/03-developer-…md | +99 |
| ai/beans/BEAN-273-…/tasks/04-tech-qa-…md | +80 |
| ai/beans/_index.md | +1 −1 |
| ai/context/decisions.md | +84 |
| ai/outputs/architect/BEAN-273-design.md | +441 |
| ai/outputs/ba/BEAN-273-artifact-types.md | +460 |
| ai/outputs/tech-qa/BEAN-273-vdd.md | +89 |
| foundry_app/core/models.py | +33 |
| foundry_app/services/generator.py | +6 −3 |
| foundry_app/services/library_indexer.py | +205 −2 |
| foundry_app/services/scaffold.py | +75 −10 |
| tests/test_persona_contracts.py | +453 |
| **Total** | **+2,507 −20** |

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
| 1 | Define artifact-type registry content | BA | 3m | 442,752 | 3,344 | $0.94 |
| 2 | ADR — contract format, location, loader integration | Architect | 5m | 234,395 | 1,771 | $0.50 |
| 3 | Implement registry, persona contracts, loader, compiler emission | Developer | 6m | 376,346 | 3,493 | $0.85 |
| 4 | Verify contracts — tests, lint, AC sweep | Tech-QA | 4m | 398,687 | 3,038 | $0.85 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 4 |
| **Total Duration** | 18m |
| **Total Tokens In** | 1,452,180 |
| **Total Tokens Out** | 11,646 |
| **Total Cost** | $3.14 |