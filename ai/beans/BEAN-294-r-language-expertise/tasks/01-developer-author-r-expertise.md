# Task 01 — Developer: Author the R expertise pack

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-294 / 01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Create a complete `r` expertise pack at the `Languages` category with
five files (`conventions.md`, `packaging.md`, `performance.md`,
`security.md`, `testing.md`) that match the depth and section ordering
of `python/` and `go/`. Tidyverse is the documented default; `renv` is
the packaging default. Add the `r` row to `ai-team-library/README.md`'s
expertise table. Update the indexer test fixtures so `r` appears in
`EXPECTED_EXPERTISE` (alphabetical), is categorised under `Languages`,
and declares `applies_to: [data-scientist, data-analyst, data-engineer,
developer]`.

## Inputs

- `ai/beans/BEAN-294-r-language-expertise/bean.md` — full Problem
  Statement, Goal, Scope, Acceptance Criteria, and the rationale for
  defaults (tidyverse, renv) and the applies-to set.
- `ai-team-library/expertise/python/` — primary structural reference.
  Five files, identical section ordering to follow. Use as the depth
  benchmark.
- `ai-team-library/expertise/go/` — secondary structural reference for
  tone consistency.
- `ai-team-library/expertise/rust/conventions.md` — reference for the
  ADR-required-alternative pattern (rust documents `tokio` default
  with `async-std` / `smol` alternatives; r should document tidyverse
  default with base R as the documented alternative).
- `ai-team-library/README.md` — expertise table row to add.
- `tests/test_library_indexer.py` — `EXPECTED_EXPERTISE` constant
  (~line 41). Add `"r"` in alphabetical order (between `python` and
  `react` — but check: the list looks like it's mixed; insert
  alphabetically per the existing pattern).
- `tests/test_library_indexer.py` — category test and applies-to
  test (`test_applies_to_parsed_from_conventions_md`, line ~711). If
  there's a parametric category-coverage test, R needs to land in it.

## Acceptance Criteria

- [ ] `ai-team-library/expertise/r/conventions.md` exists with
      `## Category\nLanguages` header, an `## Applies To` block
      listing `data-scientist`, `data-analyst`, `data-engineer`, and
      `developer`, a `## Defaults` table at python-level depth, a
      `## Do / Don't` section, file/project layout guidance, naming,
      and a `## Tidyverse vs. base R` section explaining when each is
      the right call.
- [ ] `conventions.md` names tidyverse explicitly as the default
      style (the `(file-contains:…::tidyverse)` AC).
- [ ] `ai-team-library/expertise/r/packaging.md` exists with `renv`
      as the default lockfile-based dep manager, sections for CRAN /
      Bioconductor / `remotes` install patterns, `DESCRIPTION` /
      `NAMESPACE` / project-layout guidance, and a release flow with
      `devtools` + `pkgdown`.
- [ ] `ai-team-library/expertise/r/performance.md` exists covering
      profiling (`profvis`, `bench`), vectorisation patterns,
      `data.table` for large data, and parallelism (`future` /
      `furrr`). Memory-management gotchas (copy-on-modify) named.
- [ ] `ai-team-library/expertise/r/security.md` exists covering
      credential handling (`keyring`, `.Renviron`, no committed
      `.Rprofile` secrets), parameterised `DBI` queries, avoiding
      `eval(parse())` on untrusted input, and package-supply-chain
      practices (lockfile, vetted sources).
- [ ] `ai-team-library/expertise/r/testing.md` exists covering
      `testthat` (3rd-edition), `covr` for coverage, `lintr` and
      `styler`, snapshot-test patterns for ggplot2 outputs, and CI
      integration patterns.
- [ ] `ai-team-library/README.md`'s expertise table includes a row
      for `r` (the `(file-contains:…::| r )` AC).
- [ ] `tests/test_library_indexer.py::EXPECTED_EXPERTISE` includes
      `"r"` in alphabetical order. The indexer's discovery test
      (line ~123) passes with the new entry.
- [ ] If `test_library_indexer.py` has a category-coverage test that
      enumerates all expertise → category mappings, R appears under
      `Languages` in that test.
- [ ] If `test_library_indexer.py` has an applies-to test that
      enumerates all expertise → applies_to mappings, the R entry
      asserts the four-persona set listed in the bean.
- [ ] `uv run pytest` passes locally.
- [ ] `uv run ruff check foundry_app/` passes locally (this bean does
      not modify `foundry_app/`, but lint is part of the quality
      gate).

## Definition of Done

- All acceptance criteria checked.
- Code committed on branch `bean/BEAN-294-r-language-expertise`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Hand off to Tech-QA via `/handoff` (or by setting Task 02 to ready).

## Notes

**Match the depth, not the topics, to python/.** Python's pack covers
type hints, async, packaging via uv. R's equivalents are different
(no static types, no async — base R is mostly synchronous; instead
you have NSE/tidy-evaluation, vectorisation, NSE pitfalls, and
`renv`-based packaging). Author topics that are load-bearing for R
practitioners; do not force python's exact topic list.

**Tidyverse-first means dplyr / tidyr / ggplot2 / tibble / readr /
purrr** — name them explicitly in the Defaults table. Note `arrow` /
`duckdb` for large-data interop. For ML, mention `tidymodels` as the
modern unified framework (parsnip, recipes, workflows, yardstick).

**Keep `lintr` and `styler` distinct.** `lintr` is the linter (CI
gate); `styler` is the auto-formatter (`gofmt` analogue). Both ship
with project-local config files (`.lintr`, `.styler.toml` is rare —
most use defaults).

**File length budget.** Aim for ~150-180 lines per file (python's
files are roughly that size). Total ~750-900 lines across the five
files. The bean's Notes call out the molecularity-gate exemption
(content-authoring), so you do not need to split this further.

**Indexer test layout.** `EXPECTED_EXPERTISE` is alphabetical. After
inserting `r`, the order should be `python, r, react, react-native,
rust, …`. Double-check by reading the constant before inserting.
