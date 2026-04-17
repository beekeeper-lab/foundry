# BEAN-242: Generation Self-Consistency Integration Test

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-242 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The current end-to-end test (`TestEndToEnd` from BEAN-117) verifies that generated files exist and contain expected sections, but it does not catch two classes of framework-integrity failure:

1. **Unresolved Jinja placeholders** — verified today by regenerating `examples/small-python-team.yml` on `test`: `.claude/agents/{team-lead,developer,tech-qa,code-quality-reviewer}.md` each contain `{{ project_name }}`, `{{ expertise | join(", ") }}`, or `{{ strictness }}`. The generator itself prints a warning for `ai/generated/members/code-quality-reviewer.md` unresolved `strictness`, proving partial detection exists but does not cover `.claude/agents/` nor block the build.
2. **Scaffold/validator drift** — the generated `validate-repo` skill checks for `ai/team/composition.yml` and `README.md` at the project root. Neither is emitted by the current scaffold. A freshly generated project fails its own validator.

Both classes were flagged by external critique. Per-service unit tests pass because they test rendering steps in isolation, not the full assembled output.

## Goal

A failing integration test that generates a full project against the real `ai-team-library`, then asserts:

1. **Zero** unresolved Jinja expressions (`{{`, `}}`, `{%`, `%}`) in any generated file (`.md`, `.json`, `.yml`, `.yaml`) — including both `.claude/agents/*.md` and `ai/generated/members/*.md`.
2. The structural paths expected by the generated `validate-repo` skill all exist (including `ai/team/composition.yml` and `README.md`).

The test is **red on `test` at merge-time** and only goes green after BEAN-243 (placeholder fix) and BEAN-244 (composition.yml + README.md emission) ship. It is the TDD driver for those two beans.

## Scope

### In Scope
- New test class in `tests/test_generator.py` (e.g., `TestGenerationSelfConsistency`).
- Uses `examples/small-python-team.yml` with the real `ai-team-library/`.
- Runs the full generation pipeline to `tmp_path`.
- **Placeholder assertion:** recursively walks the output tree, reads every text file (`.md`, `.json`, `.yml`, `.yaml`), and fails if any contain `{{`, `}}`, `{%`, or `%}`.
- **Structural assertion:** asserts the paths expected by `validate-repo` exist — at minimum: `CLAUDE.md`, `README.md`, `ai/team/composition.yml`, `.claude/agents/{persona}.md` per selected persona, `ai/generated/members/{persona}.md` per selected persona, `ai/outputs/{persona}/` per selected persona, `ai/context/`, `ai/tasks/`.
- Test is runnable via `uv run pytest tests/test_generator.py::TestGenerationSelfConsistency`.

### Out of Scope
- Reimplementing the full runnable `validate-repo` skill in Python — the structural check covers a documented subset.
- Overlay-mode testing (`TestOverlayGeneration` covers that).
- Stack-specific validations (pytest exists, npm works) — orthogonal.
- Performance or timing assertions.

## Acceptance Criteria

- [ ] New test class exists in `tests/test_generator.py`.
- [ ] Test generates a project from `examples/small-python-team.yml` to `tmp_path` using real `ai-team-library/`.
- [ ] Placeholder assertion: walk output tree and fail if any `.md`/`.json`/`.yml`/`.yaml` file contains `{{`, `}}`, `{%`, or `%}`.
- [ ] Structural assertion: all paths expected by `validate-repo` exist (explicit list above).
- [ ] Test is **red** when committed (before BEAN-243 and BEAN-244 ship).
- [ ] Test goes **green** after BEAN-243 and BEAN-244 complete.
- [ ] All other tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**TDD-first driver.** Committed red. Turns green as BEAN-243 (placeholder fix) and BEAN-244 (composition.yml + README.md emission) ship.

**Related existing beans (on `test`):**
- BEAN-117 (Done) — built `TestEndToEnd` with structural presence checks. Does NOT scan for placeholder leakage or check for `composition.yml`/`README.md`. This bean extends those gaps.
- BEAN-233 (Done) — slimmed CLAUDE.md. Assertions here must not regress that result.

**Origin:** External code review flagged placeholder leakage in `.claude/agents/*.md` and validator/scaffold mismatch on `ai/team/composition.yml`. Verified both on `test` branch today (2026-04-17).

**Downstream verification:**

| System | Impact | Verification Command |
|--------|--------|---------------------|
| Tests  | New test class | `uv run pytest tests/test_generator.py::TestGenerationSelfConsistency` |
| Lint   | New test file | `uv run ruff check tests/` |
| CI     | Red test on `test` — intentional until fixes ship | n/a |

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
