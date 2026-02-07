# Task 02: Beans Seed Mode Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 01 |

## Goal

Verify that the `beans` seed mode implementation is complete, correct, and doesn't regress existing functionality.

## Inputs

- `ai/beans/BEAN-001-backlog-seeding/bean.md` — acceptance criteria
- `foundry_app/services/seeder.py` — implementation
- `foundry_app/services/generator.py` — pipeline integration
- `tests/test_seeder.py` — test suite
- `ai/context/bean-workflow.md` — reference structure

## Acceptance Criteria

- [ ] All bean acceptance criteria met (trace each one)
- [ ] Generated `_index.md` matches `bean-workflow.md` structure
- [ ] Generated `_bean-template.md` has all required sections
- [ ] Existing seed modes unaffected (verify test coverage)
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — lint clean
- [ ] QA report written to `ai/outputs/tech-qa/bean-001-beans-seed-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation.
