# Task 02: Tech-QA Verification

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 16:29 |
| **Completed** | 2026-04-17 16:29 |
| **Duration** | < 1m |

## Goal

Independently verify the integration test asserts the documented contract, runs as expected (red now, green after BEAN-243 and BEAN-244), and does not introduce flakiness.

## Inputs

- `tests/test_generator.py` — updated test file
- `ai/beans/BEAN-242-generation-self-consistency-test/bean.md` — acceptance criteria
- The developer task output from Task 01

## Implementation

1. Read the new `TestGenerationSelfConsistency` class.
2. Run `uv run pytest tests/test_generator.py::TestGenerationSelfConsistency -v`. Confirm:
   - The placeholder assertion fails with a clear message identifying the offending files.
   - The structural assertion fails on `ai/team/composition.yml` and `README.md`.
3. Run `uv run pytest` (full suite). Confirm that **only** the new test fails; nothing else regresses.
4. Run `uv run ruff check foundry_app/ tests/`. Confirm clean.
5. Confirm the assertion messages are actionable — a developer reading them must be able to identify BEAN-243/244 as the fix.

## Acceptance Criteria

- [ ] New test exists and is correctly scoped — it asserts both placeholder and structural contracts from the bean.
- [ ] The test fails **as designed** with actionable messages (no brittle fixtures, no missing imports, no skipped asserts).
- [ ] Remaining test suite passes.
- [ ] Lint clean.
- [ ] Verification report appended here summarizing observed failures and confirming every AC in `bean.md` is met.

## Definition of Done

- Verification complete, notes captured below.

## Verification Notes

**Targeted run:** `uv run pytest tests/test_generator.py::TestGenerationSelfConsistency -v` → 2 failed, both as designed.

- `test_no_unresolved_jinja_in_generated_files` fails with a message that enumerates each leaking file and line, e.g.:
  - `.claude/agents/code-quality-reviewer.md:3: ... **{{ project_name }}** ...`
  - `.claude/agents/tech-qa.md:3: ... **{{ project_name }}** ...`
  - `.claude/agents/developer.md:9: ... **{{ project_name }}** ...`
  - `.claude/agents/team-lead.md:3: ... **{{ project_name }}** ...`
  - `ai/generated/members/code-quality-reviewer.md:8: ... **{{ strictness }}** ...`
  - Message explicitly points to BEAN-243 as the fix.
- `test_validate_repo_structural_paths_exist` fails reporting `README.md`, `ai/team/composition.yml`, and `ai/team/` missing. Message explicitly points to BEAN-244 as the fix.

**Full suite:** `uv run pytest` → 2 failed, 1785 passed. No regressions beyond the two intentional new reds.

**Lint:** `uv run ruff check foundry_app/ tests/test_generator.py` → clean. (Pre-existing errors in `tests/test_cli.py` are unrelated to this bean.)

**Acceptance criteria check:**

- [x] New test class `TestGenerationSelfConsistency` added in `tests/test_generator.py`.
- [x] Test generates from `examples/small-python-team.yml` into `tmp_path` using real `ai-team-library/`.
- [x] Placeholder assertion walks output tree and fails on Jinja markers.
- [x] Structural assertion covers every documented path.
- [x] Test is red as committed.
- [x] All other tests pass.
- [x] Lint clean on `foundry_app/` and on the new test file.
- Deferred (by design): turning green after BEAN-243 and BEAN-244 ship — tracked in those beans.

**Conclusion:** Task 01 output matches acceptance criteria. Bean is safe to close as a TDD-red driver.
