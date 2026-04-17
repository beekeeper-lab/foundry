# Task 01: Self-Consistency Integration Test

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 16:29 |
| **Completed** | 2026-04-17 16:29 |
| **Duration** | < 1m |

## Goal

Add a failing integration test class `TestGenerationSelfConsistency` to `tests/test_generator.py` that drives BEAN-243 and BEAN-244 to green.

## Inputs

- `tests/test_generator.py` — existing end-to-end test patterns (see `TestEndToEnd` from BEAN-117)
- `examples/small-python-team.yml` — composition fixture used by the test
- `ai-team-library/` — real library (no mocks)
- `ai-team-library/claude/skills/validate-repo/SKILL.md` — authoritative contract for structural paths

## Implementation

1. Add a `TestGenerationSelfConsistency` class in `tests/test_generator.py`.
2. Run the full generation pipeline against `examples/small-python-team.yml` with the real `ai-team-library/` into `tmp_path`.
3. **Placeholder assertion:** walk the output tree, read every `.md`, `.json`, `.yml`, `.yaml` file, fail if any contain `{{`, `}}`, `{%`, or `%}`. On failure, the error message lists each offending file and the first offending line.
4. **Structural assertion:** for each persona in the composition, assert presence of `.claude/agents/<persona>.md` and `ai/generated/members/<persona>.md`. Assert presence of `CLAUDE.md`, `README.md`, `ai/team/composition.yml`, `ai/context/`, `ai/tasks/`, and `ai/outputs/<persona>/` per persona.
5. Keep the existing `TestEndToEnd` untouched.

## Acceptance Criteria

- [ ] New test class `TestGenerationSelfConsistency` exists in `tests/test_generator.py`.
- [ ] Test generates a project from `examples/small-python-team.yml` into `tmp_path` using the real `ai-team-library/`.
- [ ] Placeholder assertion walks output tree and fails if any `.md`/`.json`/`.yml`/`.yaml` file contains `{{`, `}}`, `{%`, or `%}`.
- [ ] Structural assertion covers every path listed in the bean scope.
- [ ] Test is **red** as committed (fails on current `test` branch because placeholder leakage and `ai/team/composition.yml` + `README.md` are absent).
- [ ] All other tests pass (`uv run pytest` — only the new test fails).
- [ ] Lint clean (`uv run ruff check foundry_app/ tests/`).

## Definition of Done

- Test file changes committed on feature branch.
- `uv run pytest` shows exactly the expected new red test and every other test green.
- `uv run ruff check foundry_app/ tests/` clean.
