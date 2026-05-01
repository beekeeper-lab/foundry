# Task 02 — Tech-QA: Indexer test, tone consistency, README check, manual

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-291 / 02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Bind the new persona's discoverability into the test suite, verify
content quality matches sibling depth, confirm the README + hand-off
back-reference are wired correctly, and record manual verification.

## Inputs

- `ai-team-library/personas/extended/data-scientist/` — files produced
  by Task 01.
- `ai-team-library/personas/extended/data-analyst/persona.md` —
  modified back-reference site.
- `ai-team-library/README.md` — modified persona table.
- `tests/test_library_indexer.py` — existing indexer tests; extend.

## Acceptance Criteria

- [ ] `tests/test_library_indexer.py` has a regression test that
      indexes the real `ai-team-library/` and asserts the
      `extended/data-scientist` persona is present in
      `LibraryIndex.personas`. The test also asserts the persona has
      `tier == "extended"` and the expected `templates` (the four
      template files from Task 01).
- [ ] Tone-consistency review (recorded in
      `ai/outputs/tech-qa/BEAN-291-content-review.md`):
        - Section headers in `data-scientist/persona.md` match
          `data-analyst/persona.md` 1:1 (diff the `^## ` lines).
        - Voice is parallel to siblings (modeling-focused vocabulary
          where data-analyst uses BI vocabulary).
        - No leftover placeholder text (`TODO`, `[fill in]`, `???`).
- [ ] README check: `ai-team-library/README.md` mentions
      `data-scientist` somewhere in the persona table; documented
      count moved from 24 → 25 (grep for both strings).
- [ ] Symmetric hand-off: `data-analyst/persona.md` mentions
      `Data Scientist` in its hand-off / collaboration section; and
      `data-scientist/persona.md` mentions `Data Analyst` in its
      hand-off / collaboration section.
- [ ] `uv run pytest` — all tests pass (including the new indexer
      assertion).
- [ ] `uv run ruff check foundry_app/` — clean.
- [ ] **Manual**: launch the wizard, confirm Data Scientist appears in
      the Persona Selection page under the extended tier, and that a
      team of `team-lead + researcher-librarian + data-scientist +
      developer + tech-qa` validates green. Record the verification (or
      a documented headless-environment substitute) at
      `ai/outputs/tech-qa/BEAN-291-manual-verification.md`.

## Definition of Done

- New indexer assertion in place and green.
- Content review doc + manual verification doc committed.
- Status updated to Done; the telemetry hook stamps Completed/Duration.
