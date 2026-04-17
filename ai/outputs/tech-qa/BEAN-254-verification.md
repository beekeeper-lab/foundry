# BEAN-254 — Tech-QA Verification

## Summary

- Full test suite: **1854 passed** (up from 1811 baseline; +43 new/updated assertions in `tests/test_seeder.py`).
- `uv run ruff check foundry_app/`: **All checks passed**.
- Regression coverage: a dedicated assertion (`test_does_not_write_ai_tasks_index`) fails if the seeder regresses to writing `ai/tasks/_index.md`.

## Acceptance Criteria Check

| # | Criterion | Status |
|---|-----------|--------|
| 1 | `ai/beans/BEAN-001-bootstrap/bean.md` emitted with `Status: Approved` and tasks/ populated | Pass — covered by `TestBasicGeneration::test_bean_status_is_approved` and `TestDetailedMode::test_detailed_has_multiple_tasks_per_persona`. |
| 2 | `ai/tasks/` empty (no orphan tasks) | Pass — `TestBasicGeneration::test_does_not_write_ai_tasks_index`. |
| 3 | `ai/beans/_index.md` lists BEAN-001 | Pass — `TestBacklogIndex::test_index_created_when_missing`. |
| 4 | Problem Statement references `project-charter.md` when present, falls back otherwise | Pass — `TestCharterReference` pair. |
| 5 | Seeder tests updated; new test asserts starter bean exists and expected task files | Pass — `tests/test_seeder.py` fully rewritten (40 tests). |
| 6 | `uv run pytest` clean | Pass — 1854 passed. |
| 7 | `uv run ruff check foundry_app/` clean | Pass. |

## Notable Test Additions

- `TestBacklogIndex::test_index_preserves_existing_rows` — guards the upsert path: pre-existing `_index.md` rows are retained.
- `TestBacklogIndex::test_index_not_duplicated_on_rerun` — idempotency on re-seed.
- `TestBasicGeneration::test_does_not_write_ai_tasks_index` — regression guard against the audit complaint returning.
- `TestCharterReference` — both branches of the Problem Statement content.
