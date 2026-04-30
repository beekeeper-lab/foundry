# BEAN-259 / Task 03: Tech-QA — Verify Persona-Scoped Expertise Filter

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Depends On** | 02-developer-implement-filter |
| **Status** | Done |
| **Started** | 2026-04-30 09:33 |
| **Completed** | 2026-04-30 09:38 |
| **Duration** | 5m |

## Goal

Independently verify every BEAN-259 acceptance criterion. Crucially,
verify backward compatibility — old compositions must produce
unchanged output.

## Inputs

- ai/beans/BEAN-259-persona-scoped-expertise-inclusion/bean.md — acceptance criteria
- ai/context/decisions.md — the BEAN-259 ADR (mechanism choice and contracts)
- ai-team-library/personas/, ai-team-library/expertise/ — metadata changes to inspect
- foundry_app/services/compiler.py, foundry_app/services/agent_writer.py — implementation
- tests/test_compiler.py, tests/test_agent_writer.py — new tests
- examples/small-python-team.yml — backward-compat smoke
- examples/full-stack-web.yml — filter-effective smoke

## Acceptance Criteria

- [ ] ADR present in `ai/context/decisions.md` and matches the mechanism the implementation uses.
- [ ] Library metadata declared per the ADR; at least 3 personas / 3 expertise files have meaningful new metadata.
- [ ] Generate `examples/small-python-team.yml` to a tmp dir. Compare per-persona member prompts to a fresh `git stash; generate; git stash pop; generate` baseline (or to a known-good snapshot the developer captured pre-change). Confirm zero change in the no-metadata path.
- [ ] Generate `examples/full-stack-web.yml` (or whatever the ADR / developer designated as the React/TS smoke composition). Confirm:
  - DevOps-Release member prompt contains no `tsconfig` detail
  - UX/UI Designer member prompt contains no `ruff` detail
  - Developer member prompt contains both
- [ ] Token reduction: developer's measurement shows ≥20% reduction for at least one non-Developer persona.
- [ ] `uv run pytest` — full suite passes.
- [ ] `uv run ruff check foundry_app/` — clean.
- [ ] Spot check: pick one persona at random and compare its filtered member prompt to the unfiltered version. The diff should be exactly the expertise content that does not apply to that persona.

## Definition of Done

- Verification report at `ai/outputs/tech-qa/bean-259-verification.md`.
- All checks PASS or specific FAILs reported back to the developer.
