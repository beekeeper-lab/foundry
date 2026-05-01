# Task 02: Tech-QA Verification

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 16:39 |
| **Completed** | 2026-04-17 16:39 |
| **Duration** | < 1m |

## Goal

Independently verify the root-cause fix lands the documented behavior and that BEAN-242's placeholder test now passes while BEAN-244's structural test remains the only expected red.

## Inputs

- Task 01 output: `foundry_app/services/compiler.py`, `foundry_app/services/agent_writer.py`, `tests/test_compiler.py`, `tests/test_agent_writer.py`
- BEAN-242's `TestGenerationSelfConsistency`
- Acceptance criteria in `bean.md`

## Verification

**Targeted tests:**

```
uv run pytest tests/test_compiler.py tests/test_agent_writer.py tests/test_generator.py
```

Result: 226 passed, 1 failed (only the intentional BEAN-244 `test_validate_repo_structural_paths_exist`). The BEAN-242 placeholder test (`test_no_unresolved_jinja_in_generated_files`) is **green**. The new tests in compiler and agent_writer all pass.

**Full suite:**

```
uv run pytest
```

Result: 1793 passed, 1 failed (BEAN-244 structural red — still intentional until that bean ships). No unrelated regressions.

**Lint:**

```
uv run ruff check foundry_app/
```

Result: All checks passed.

Pre-existing lint errors in `tests/test_compiler.py` (5x, lines 853/979/1049/1057/1068) are unrelated to this bean — they sit in test code that pre-dates BEAN-243 and the bean's AC scopes lint to `foundry_app/`.

**Manual regen:**

```
uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean243-check-new
grep -rn '{{' /tmp/bean243-check-new | grep -v '.git/'
```

Result: zero matches. Pre-fix leaks in `.claude/agents/{team-lead,developer,tech-qa,code-quality-reviewer}.md` and `ai/generated/members/code-quality-reviewer.md` are gone.

**Warning coverage check:**

The agent_writer now emits a warning whenever an output `.claude/agents/*.md` still contains `{{ ... }}`. The new `TestAgentPlaceholderRendering::test_warning_emitted_for_unknown_placeholder` test validates that path with a deliberately broken persona fixture.

## Acceptance Criteria Check

- [x] Root cause identified and documented (see Task 01).
- [x] Fix applied at root cause (per-persona context + pre-extraction substitution). No post-hoc string replacement.
- [x] Unit tests at compiler and agent-writer layers assert full rendering.
- [x] Placeholder warning scans `.claude/agents/*.md`.
- [x] Regenerated `small-python-team` contains zero unresolved Jinja markers.
- [x] BEAN-242 placeholder assertion passes.
- [x] All tests pass (apart from BEAN-244 intentional red).
- [x] Lint clean on `foundry_app/`.

## Definition of Done

- Verification complete. All AC met.
