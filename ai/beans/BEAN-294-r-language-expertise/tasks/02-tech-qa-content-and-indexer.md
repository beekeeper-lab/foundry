# Task 02 — Tech-QA: Content-tone parity review + indexer regression + manual verification

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-294 / 02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify that the R expertise pack matches the depth,
section ordering, and prose tone of `python/` and `go/`, that the
defaults declared (tidyverse, renv) are correctly named throughout,
that the indexer test fixtures are consistent with the new pack, and
that the wizard surfaces the R card under the `Languages` category.
Capture observations in `ai/outputs/tech-qa/BEAN-294-manual-verification.md`.

## Inputs

- `ai/beans/BEAN-294-r-language-expertise/bean.md` — full AC list.
- Developer's commits on `bean/BEAN-294-r-language-expertise`.
- `ai-team-library/expertise/r/` — Developer's new pack files.
- `ai-team-library/expertise/python/` and `.../go/` — depth and tone
  benchmarks. Diff section headings between `r/` and `python/` to
  confirm structural parity.
- `ai-team-library/README.md` — expertise table.
- `tests/test_library_indexer.py` — test fixtures.

## Acceptance Criteria

- [ ] Section-header parity: each of the five files in `r/` has a
      section structure that matches the equivalent file in
      `python/` at the H2 level. If R's content legitimately diverges
      (e.g., async section omitted, vectorisation section added),
      document the divergence and confirm it's load-bearing for R.
- [ ] Defaults table parity: `r/conventions.md` has a Defaults table
      with comparable density to `python/conventions.md`. At least
      8-10 rows.
- [ ] Tidyverse default explicitly named in `r/conventions.md`
      (verbatim "tidyverse" appears at least once in the Defaults
      table or the dedicated tidyverse-vs-base-R section).
- [ ] `renv` named as packaging default in `r/packaging.md`.
- [ ] `applies_to` set in `r/conventions.md` is exactly:
      `data-scientist`, `data-analyst`, `data-engineer`, `developer`
      (no more, no less).
- [ ] README expertise table row for `r` exists and is in
      alphabetical order with the existing rows.
- [ ] `tests/test_library_indexer.py` — `EXPECTED_EXPERTISE` includes
      `"r"` in alphabetical order. Spot-check the surrounding
      entries (`python`, `react`, `react-native`).
- [ ] Indexer end-to-end: `LibraryIndex.expertise` returned by
      indexing `ai-team-library/` includes a top-level `r` entry
      with category `Languages` and the four-persona applies-to set.
      Add an explicit test if the existing test surface doesn't
      cover this; otherwise verify the existing test passes with
      the new entry.
- [ ] (manual) Launch `uv run foundry`. Navigate to the Expertise
      Selection page. Expand the `Languages` category. Confirm the
      R card appears alongside Python / Rust / Go / Kotlin / Swift /
      etc. Capture observations in
      `ai/outputs/tech-qa/BEAN-294-manual-verification.md`. If no
      display is available (headless session), document the
      substitution: list the indexer test that asserts R appears
      under `Languages`, and the wizard component that consumes
      `LibraryIndex.expertise` (the Expertise Selection page). Note
      the SHA on the branch.
- [ ] (manual) Compose a team of `developer + tech-qa +
      data-scientist` plus the `r` expertise; click Generate;
      confirm the generated project's `CLAUDE.md` references the R
      conventions. Headless substitution: a generation pipeline
      test asserting `r` appears in the compiled CLAUDE.md when the
      composition includes `r` in `expertise:`. Add the test if not
      already present.
- [ ] `uv run pytest` passes — full suite.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] If any criterion fails or any regression surfaces, do NOT close
      this task as Done. Set Status back to `In Progress`, document
      the failure in the task's Notes section, and return so the
      orchestrator can dispatch a Developer follow-up.

## Definition of Done

- All acceptance criteria checked.
- Manual-verification observation file at
  `ai/outputs/tech-qa/BEAN-294-manual-verification.md`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Bean is ready for the orchestrator's verification + close phase
  (Phase 5 of `/long-run`).

## Notes

**Tone-parity review is editorial, not pedantic.** Tech-QA is
checking for "would a reader switching between python/, go/, and r/
experience a consistent voice?" — not for verbatim parallelism. If
R's conventions legitimately diverge from python's because the
language differs, that's correct; just confirm the divergence is
substantive (load-bearing for R), not stylistic drift.

**Generation E2E.** If an indexer-level test is sufficient to
establish that R is plumbed through the compiler, add one rather
than the more expensive full generation pipeline test. The bean's
manual AC item is about "the wizard shows the card" and "CLAUDE.md
references R" — both can be covered with cheaper unit-level tests
that assert the indexer surfaces R and the compiler emits an R
section in CLAUDE.md when `r` is in the composition's `expertise:`.

**Headless substitution.** Same policy as BEAN-292/293: document the
substitution in `ai/outputs/tech-qa/BEAN-294-manual-verification.md`
with the branch SHA and the automated tests that cover the manual
AC items. Do not mock the library index; use the real library
through the real indexer.
