# Task 02 — Tech-QA: Verify Approval Gate

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 19:18 |
| **Completed** | 2026-04-17 19:18 |
| **Duration** | < 1m |

## Goal

Add pytest coverage for `bean_approval` (happy path + failure cases) and verify the full acceptance criteria of BEAN-260.

## Inputs

- `foundry_app/services/bean_approval.py` (from Task 01)
- `ai/beans/_bean-template.md` (template used for fixture construction)
- `.claude/local/skills/internal/approve-bean/SKILL.md` (from Task 01)
- `.claude/local/commands/internal/approve-bean.md` (from Task 01)
- `ai/context/bean-workflow.md` (from Task 01 — verify "Approval Gate" subsection exists)

## Required Changes

1. **`tests/test_bean_approval.py`** (new) — at least three tests:
   - `test_well_formed_bean_passes_approval_check`: fixture bean with all fields → `ok=True`, `missing=[]`.
   - `test_missing_acceptance_criteria_rejected`: bean with only placeholder `- [ ] Criterion 1` lines → `ok=False`, `"Acceptance Criteria"` in `missing`.
   - `test_missing_scope_rejected`: bean with empty `## Scope` section → `ok=False`, `"Scope"` in `missing` (or a similarly specific label).
   - Add one more: `test_missing_category_rejected` or `test_missing_problem_statement_rejected` to exercise one more branch.

## Acceptance Criteria

- [ ] `tests/test_bean_approval.py` exists with ≥3 tests covering happy path + ≥2 failure cases.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] `.claude/local/skills/internal/approve-bean/SKILL.md` and `.claude/local/commands/internal/approve-bean.md` exist.
- [ ] `ai/context/bean-workflow.md` includes an `#### Approval Gate` subsection.

## Example Output

Follow `tests/test_library_indexer.py` fixture style — `tmp_path` + inline markdown written via `Path.write_text`.
