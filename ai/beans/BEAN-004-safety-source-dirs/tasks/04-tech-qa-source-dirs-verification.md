# Task 04: Source Directory Verification

| Field | Value |
|-------|-------|
| **Owner** | tech-qa |
| **Status** | Done |
| **Depends On** | 03 |

## Goal

Verify the source directory implementation against all acceptance criteria. Build traceability matrix, review code, run edge case tests.

## Inputs

- `ai/beans/BEAN-004-safety-source-dirs/bean.md` — acceptance criteria
- `ai/outputs/ba/bean-004-source-dirs-requirements.md` — requirements with edge cases
- `ai/outputs/architect/bean-004-source-dirs-design.md` — design spec
- `ai/outputs/developer/bean-004-source-dirs-notes.md` — implementation notes
- `foundry_app/core/models.py` — modified models
- `foundry_app/services/safety.py` — modified service
- `foundry_app/ui/screens/builder/wizard_pages/safety_page.py` — modified UI
- `tests/test_safety.py` — new/modified tests

## Acceptance Criteria

- [ ] Traceability matrix built via `/build-traceability` (every AC has a test, every test has an AC)
- [ ] Code review completed via `/review-pr`
- [ ] Edge cases from BA requirements are all tested (empty list, overlapping patterns, invalid patterns)
- [ ] Backward compatibility verified: old compositions still parse
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — clean
- [ ] QA report written to `ai/outputs/tech-qa/bean-004-source-dirs-qa-report.md`

## Definition of Done

QA report exists with go/no-go recommendation. All acceptance criteria verified with evidence.
