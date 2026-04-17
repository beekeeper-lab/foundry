# Task 02: Verify Orchestration Model Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Add regression tests that lock in the Team Orchestration Model
surfaces introduced by Task 01. Verify acceptance criteria from the
bean, including the grep invariant and cold-start readability.

## Inputs

- `tests/test_compiler.py` — `TestLeanClaudeMd` class
- `tests/test_scaffold.py` — composition.yml emission tests
- `ai-team-library/personas/team-lead/persona.md` — source
- Generated-project output from a round-trip through the pipeline

## Changes Required

1. Add a test in `TestLeanClaudeMd` asserting the generated
   `CLAUDE.md` contains `## Team Orchestration Model`, mentions
   "available bench", names **Developer** and **Tech-QA** as
   mandatory, and lists at least one opt-in role (Architect).
2. Add a test to `test_scaffold.py` asserting the emitted
   `composition.yml` contains an `orchestration:` block with
   `orchestrator_role: team-lead`, `team_model: available-bench`,
   and `software-development` mandatory roles.
3. Add a test asserting the library `team-lead/persona.md` source
   contains `## Orchestration Rules`.
4. Run `uv run pytest` and `uv run ruff check foundry_app/`; both
   must pass.

## Acceptance Criteria

- [ ] Tests cover the CLAUDE.md, composition.yml, and team-lead
      persona surfaces.
- [ ] `uv run pytest` passes with the new tests.
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] A manual grep of the generated CLAUDE.md for "all members" /
      "entire team" / "full team wave" returns no contradicting
      matches.

## Definition of Done

- Regression tests land in the suite.
- Full test suite green, lint clean.
- Bean acceptance criteria are verified.
