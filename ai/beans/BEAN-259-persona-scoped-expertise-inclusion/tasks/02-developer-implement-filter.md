# BEAN-259 / Task 02: Developer — Implement Persona-Scoped Expertise Filter

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01-architect-mechanism-adr |
| **Status** | Done |
| **Started** | 2026-04-30 09:22 |
| **Completed** | 2026-04-30 09:33 |
| **Duration** | 11m |

## Goal

Implement the persona-scoped expertise filter per the ADR landed in
Task 01. Every persona's compiled member prompt must contain only the
expertise it actually uses, with backward compatibility for compositions
that don't declare metadata.

## Inputs

- ai/beans/BEAN-259-persona-scoped-expertise-inclusion/bean.md — acceptance criteria
- ai/context/decisions.md — the new ADR from Task 01 (read the most recent ADR — it specifies mechanism A or B, metadata schema, filter behavior, and test cases)
- foundry_app/services/compiler.py — primary compiler
- foundry_app/services/agent_writer.py — per-persona agent file generator
- foundry_app/core/models.py — Pydantic models for persona, expertise, and composition
- ai-team-library/personas/*.yml or front-matter — persona metadata (where new metadata may live, per ADR)
- ai-team-library/expertise/*.yml or front-matter — expertise metadata (where new metadata may live, per ADR)
- tests/test_compiler.py — existing compiler tests; add new ones here
- tests/test_agent_writer.py — existing agent writer tests; add new ones here
- examples/small-python-team.yml — for backward-compat verification (no new metadata yet → unchanged behavior)
- examples/full-stack-web.yml — likely the React/TS composition to verify the filter on

## Acceptance Criteria

- [ ] Library metadata added per the ADR (either on expertise or on persona files, whichever the ADR chose).
- [ ] At least 3 personas have meaningful filter metadata so the test cases below have coverage (e.g., developer, devops-release, ux-ui-designer).
- [ ] At least 3 expertise files have meaningful filter metadata if the ADR chose mechanism A.
- [ ] `compiler.py` and/or `agent_writer.py` honor the filter when building per-persona member prompts.
- [ ] Backward-compat test: a composition with NO new metadata produces the same per-persona output as before this bean (use `small-python-team.yml` for this — current generated output is the snapshot).
- [ ] Forward test: a composition that has the new metadata produces filtered per-persona output. Specifically:
  - DevOps-Release member prompt for a React/TS composition contains no `tsconfig` detail
  - UX/UI Designer member prompt for the same composition contains no `ruff` detail
  - Developer member prompt for the same composition still contains both
- [ ] Token-count measurement script or test: produce a printed comparison showing per-persona prompt size before/after filter for at least one composition. Target: ≥20% reduction for non-Developer personas.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Definition of Done

- All acceptance criteria checked.
- Implementation matches the ADR's mechanism choice.
- No previously-generated project breaks (backward-compat test passes).

## Notes

If the ADR chose mechanism B (per-persona expertise category filter),
the Pydantic model for `PersonaInfo` likely needs a new optional field
for the expertise-category list. Ensure the field's default is the
"accept all" sentinel so backward compat is automatic.

If the ADR chose mechanism A (per-expertise persona-relevance list),
the new field lives on `ExpertiseInfo` instead and the default is
"applies to all personas".

The filter should be applied at the same layer that joins expertise
into the per-persona member prompt today — likely in
`agent_writer.py` or `compiler._build_persona_context`. Don't filter
at a higher layer (e.g., don't strip expertise from the
`CompositionSpec` itself), so that the lean CLAUDE.md still lists the
full expertise set the project uses.
