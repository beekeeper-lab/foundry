# Task 02 — Tech-QA: Tests for Casing Helper and Generated CLAUDE.md Tables

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Add pytest coverage for the casing helpers introduced in task 01 and verify the rendered CLAUDE.md Team + Tech Stack tables use correct casing end-to-end.

## Inputs

- `foundry_app/services/compiler.py` (post-task-01 helpers)
- `tests/test_compiler.py` (existing test file to extend)
- `ai/beans/BEAN-266-fix-claudemd-title-casing/tasks/01-developer-casing-helper.md`

## Required Changes

1. **`tests/test_compiler.py`** (extend)
   - New `TestDisplayNameFromId` class covering:
     - `tech-qa` → `Tech QA`
     - `ux-ui-designer` → `UX/UI Designer`
     - `sql-dba` → `SQL/DBA`
     - `team-lead` → `Team Lead`
     - `ba` → `BA`
     - `technical-writer` → `Technical Writer`
   - New `TestCanonicalizePersonaHeader` class covering:
     - `Tech-QA / Test Engineer` → `Tech-QA`
     - `UX / UI Designer` → `UX/UI Designer`
     - `Business Analyst (BA)` → `Business Analyst`
     - `Integrator / Merge Captain` → `Integrator`
     - `Team Lead` → `Team Lead` (no-op)
   - At least one integration test that calls `compile_project` with a small library fixture and asserts that the resulting `CLAUDE.md` contains exactly `| Tech-QA |` and `| UX/UI Designer |` rows (or the closest canonical forms produced by the helper) in the Team table, and that no `Ux Ui` / `Tech Qa` artefacts appear anywhere in the file.

## Acceptance Criteria

- [ ] `uv run pytest tests/test_compiler.py -q` passes with the new tests included.
- [ ] `uv run pytest -q` full suite still passes.
- [ ] `uv run ruff check foundry_app/` is clean.
- [ ] New tests are deterministic (no sleeps / network).
