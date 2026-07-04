# BEAN-274: Compose-Time Contract Graph Validator

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-274 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-05-01 00:27 |
| **Completed** | 2026-05-01 00:47 |
| **Duration** | 20m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-273 |

## Problem Statement

Once personas declare `produces:` and `consumes:` (BEAN-273), the team a user composes can be checked for internal coherence: every consumed type must be produced by *some* persona on the team. If Tech-QA consumes `traceability-input` but no producer is on the team, the team is broken before it starts.

Today no such check exists. `foundry_app/services/validator.py` validates schema but not the workflow contract.

## Goal

`generate_project()` runs a contract-graph check after persona selection and before scaffold. For new generations, an unsatisfied consume aborts with a clear error. For overlay re-generation, the same condition produces a warning and proceeds (don't break existing projects).

## Scope

### In Scope

- New module `foundry_app/services/contract_validator.py` (or extend `validator.py`).
- API: `validate_contract_graph(personas: list[PersonaInfo], registry: ArtifactTypeRegistry) -> ValidationResult` returning structured findings (unsatisfied consumes, orphan produces, missing types).
- Wire into `foundry_app/services/generator.py` between validate and scaffold stages.
- Mode behavior:
  - **Standard generation** (new project): unsatisfied consume → hard fail with remediation hint ("add `developer` to your team to produce `code-change`").
  - **Overlay mode** (re-generation over existing project): same condition → warning logged + recorded in `GenerationManifest`; pipeline continues.
- Orphan produces (a persona produces a type nobody consumes) → warning in both modes (could indicate a missing role or a stale produces declaration).
- Wizard integration: when the user selects personas, show a real-time "Team coherence" indicator (green check / yellow warning / red error) reflecting the contract graph state.
- Tests for: valid team, missing producer, orphan producer, overlay-mode warning behavior, wizard indicator.

### Out of Scope

- Validating artifact *content* (e.g., "user-story has Given/When/Then") — that's a follow-up.
- Suggesting which persona to add (could be a future enhancement).
- Validating extended personas (BEAN-271 establishes tiering; extended persona contracts are out of scope here — focus on core).

## Acceptance Criteria

- [ ] `validate_contract_graph()` exists and returns structured `ValidationResult`.
- [ ] Pipeline calls it between validate and scaffold.
- [ ] Standard generation aborts on unsatisfied consume with a clear, actionable message naming the missing type and suggesting which producer to add.
- [ ] Overlay generation logs a warning, records it in `GenerationManifest`, and proceeds.
- [ ] Orphan produces emit warnings in both modes.
- [ ] Wizard surfaces team coherence in real time.
- [ ] Tests cover all paths (standard pass/fail, overlay warn-and-proceed, orphan warn, wizard indicator).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement contract_validator + pipeline integration + wizard indicator | developer | — | Done |
| 2 | Test coverage — all paths (standard fail, overlay warn, orphan, wizard) | tech-qa | 1 | Done |

> Skipped: BA (default — no requirements ambiguity); Architect (default — design constrained by ADR-013 / BEAN-273's contract format, the bean explicitly marks Architect optional).

## Changes

| File | Lines |
|------|-------|
| `foundry_app/services/validator.py` | +125 (validate_contract_graph + helpers) |
| `foundry_app/services/generator.py` | +100/-? (pipeline integration + manifest fix) |
| `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` | +92 (coherence indicator) |
| `tests/test_validator.py` | +250 (contract-graph unit tests) |
| `tests/test_generator.py` | +193 (pipeline integration + bug-fix coverage) |
| `tests/test_persona_page.py` | +207 (wizard indicator state transitions) |
| `tests/test_persona_tiering.py` | +7 (fixture coherence) |
| `examples/small-python-team.yml` | +11 (added ba, architect for contract coherence) |
| `examples/foundry-dogfood.yml` | +6 (added ba) |
| `examples/security-focused.yml` | +6 (added ba) |
| `ai/beans/BEAN-274-contract-graph-validator/bean.md` + 2 task files | +199 |
| **Total** | 14 files changed, +1186 / -12 |

## Notes

**Depends on BEAN-273.** Cannot land before persona contracts exist.

**Hard fail vs warn — confirmed 2026-04-28.** Standard generation hard-fails; overlay warns. Rationale: don't break existing projects on re-generation; do force correctness for new ones.

**Wizard UX.** The real-time indicator is the user-facing payoff. Keep it simple: badge next to the team summary showing producer/consumer balance. Red on missing producer, yellow on orphan, green when everything connects.

**Coordinate with BEAN-271.** Extended personas may have different artifact types not yet in the registry. Decide whether the validator runs on extended personas at all in this bean (recommend: yes, with a relaxed mode for unknown types, and add the missing types to the registry as discovered).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement contract_validator + pipeline integration + wizard indicator | developer | 6m | 827,777 | 3,303 | $1.54 |
| 2 | Test coverage — all paths (standard fail, overlay warn, orphan, wizard) | tech-qa | 9m | 702,279 | 2,974 | $1.31 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 15m |
| **Total Tokens In** | 1,530,056 |
| **Total Tokens Out** | 6,277 |
| **Total Cost** | $2.85 |