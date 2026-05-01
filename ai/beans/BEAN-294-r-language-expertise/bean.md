# BEAN-294: R Language Expertise

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-294 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 18:26 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | BEAN-291 |

## Problem Statement

The library ships expertise packs for the languages a modern team
typically reaches for — `python`, `go`, `rust`, `java`, `dotnet`,
`typescript`, `node`, `kotlin`, `swift` — but not for **R**, the
dominant language for statistical computing, applied research, and
data-science modeling work. After BEAN-291 added the `data-scientist`
persona, this gap is acutely visible: a user composing a team for
academic research, ML modeling, or statistical analysis has the
*persona* but no R *expertise pack* to ground modeling conventions,
package management, or testing patterns. They would have to author
those conventions inside their generated project's `.claude/local/`
every time, instead of pulling them from the library.

Reported 2026-05-01 by the user via `/backlog-refinement`.

## Goal

The library ships an `r` expertise pack at the `Languages` category
that a user can select for any project where R is the primary or a
significant secondary language. The pack is content-complete on first
ship — defaults are picked, do/don't lists are concrete, common
pitfalls are named — so a generated project's CLAUDE.md links to the
pack and the user gets immediately useful guidance without further
authoring.

## Scope

### In Scope

- **New expertise directory** at `ai-team-library/expertise/r/` with
  the same five-file shape as `python/` and `go/`:
    - `conventions.md` — non-negotiable defaults table, do/don't list,
      file/project layout, naming, and style. **Tidyverse is the
      default style** (dplyr / tidyr / ggplot2 / tibble); base R is
      the documented "ADR-required alternative" for academic /
      statistical-purist projects.
    - `packaging.md` — package management with **`renv`** as the
      default (lockfile-based, reproducible); CRAN / Bioconductor /
      remotes installation patterns; project structure (DESCRIPTION,
      NAMESPACE, R/, tests/, vignettes/); package release flow with
      `devtools` and `pkgdown`.
    - `performance.md` — profiling with `profvis` and `bench`;
      vectorisation patterns; `data.table` for large-data work;
      parallelism with `future` / `furrr`; memory-management gotchas
      (copy-on-modify, large-object handling).
    - `security.md` — credential handling (`keyring`, `.Renviron`,
      avoiding committed `.Rprofile` secrets); SQL-injection-safe
      database access with parameterised queries via `DBI`; safe
      handling of user-provided expressions (avoid `eval(parse())`);
      package-supply-chain practices (pin to lockfile, vet packages
      from untrusted sources).
    - `testing.md` — `testthat` (3rd-edition) for unit tests;
      `covr` for coverage; `lintr` and `styler` for static analysis;
      snapshot-test patterns for ggplot2 outputs; CI integration.
- **Category metadata** — `## Category\nLanguages` at the top of
  `conventions.md`, matching the rust/go/kotlin pattern.
- **Applies-to set** — declare `applies_to:` for the new persona-
  scoped inclusion (BEAN-259) listing: `data-scientist` (extended),
  `data-analyst` (extended), `data-engineer` (extended), and
  `developer` (core). Tech-QA is broad-tech and inherits from project
  conventions, so do not list it explicitly.
- **README update** — add a row for `r` in the
  `ai-team-library/README.md` expertise table.
- **Indexer regression** — extend `tests/test_library_indexer.py`:
  `EXPECTED_EXPERTISE` includes `"r"`; the persona-categories test
  includes the `Languages` category for `r`; the applies-to test (if
  one exists at the time of execution) includes the four-persona set.
- **Tone parity** — match the prose voice and structural depth of
  `python/` and `go/` so a reader switching between language packs
  experiences a consistent style.

### Out of Scope

- **`r-shiny` expertise** (web apps with Shiny). Sufficiently distinct
  from language conventions to warrant its own pack — file as a
  follow-up bean if there is demand.
- **`r-bayesian` expertise** (Bayesian-stats focus with Stan / brms /
  rstanarm). Same rationale — separate pack if demand emerges.
- **Domain-specific R packages** (radioactive-decay analysis, biology,
  finance, epidemiology). Project-local content per the same rule
  applied in BEAN-291.
- **Modifying existing expertise packs** to cross-reference R. The
  cross-references can be added incrementally as users compose teams.
- **R-version policy** beyond stating a default — no migration tooling
  or version-management documentation; R-version handling is part of
  `renv` and is sufficiently covered by linking to its docs.
- **Splitting the pack into per-file beans.** The five files form one
  coherent expertise pack; splitting would create artificial review
  boundaries (see Notes).

## Acceptance Criteria

- [ ] (file:ai-team-library/expertise/r/conventions.md)
      Conventions file exists with a `## Category\nLanguages` header,
      a Defaults table whose rows match the rust/go/python depth, a
      Do/Don't list, and a section on tidyverse-vs-base-R style.
- [ ] (file:ai-team-library/expertise/r/packaging.md)
      Packaging file exists, defaulting to `renv`, with `DESCRIPTION`/
      `NAMESPACE`/project-layout guidance and a release flow with
      `devtools`.
- [ ] (file:ai-team-library/expertise/r/performance.md)
      Performance file exists covering profiling (`profvis`,
      `bench`), vectorisation, `data.table`, and parallelism
      (`future` / `furrr`).
- [ ] (file:ai-team-library/expertise/r/security.md)
      Security file exists covering credentials (`keyring`,
      `.Renviron`), parameterised DB access via `DBI`, and
      package-supply-chain practices.
- [ ] (file:ai-team-library/expertise/r/testing.md)
      Testing file exists covering `testthat` (3rd-edition), `covr`,
      `lintr`, `styler`, and snapshot-testing patterns.
- [ ] (file-contains:ai-team-library/expertise/r/conventions.md::tidyverse)
      Conventions file names tidyverse as the default style.
- [ ] (file-contains:ai-team-library/expertise/r/conventions.md::Languages)
      Conventions file declares the `Languages` category.
- [ ] (file-contains:ai-team-library/README.md::| r )
      README expertise table includes a row for the `r` pack.
- [ ] (test:tests/test_library_indexer.py) `EXPECTED_EXPERTISE`
      includes `"r"` in alphabetical order; the indexer discovers the
      pack and surfaces it in `LibraryIndex.expertise`; the category
      test asserts `r → Languages`; the applies-to test (if present)
      asserts the four-persona set.
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).
- [ ] (manual) Launch the wizard, navigate to the Expertise Selection
      page, expand the `Languages` category, and confirm the R card
      appears alongside Python / Rust / Go / Kotlin / Swift / etc.
      Compose a team of `developer + tech-qa + data-scientist` plus
      the `r` expertise; the generated project's `CLAUDE.md` should
      reference the R conventions.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Author the R expertise pack (5 files + README + indexer fixtures) | developer | — | Done |
| 2 | Content-tone parity review + indexer regression + manual verification | tech-qa | 01 | Done |

> Skipped: BA (default), Architect (default)
> Wave: **Developer → Tech-QA**. Architect not required — content for
> an existing category slot, no new abstractions or module boundaries.
> BA not required — the bean Notes already pin down defaults
> (tidyverse), file shape (5 files), and applies-to set.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Why now.** BEAN-291 added the `data-scientist` persona without a
language-level expertise pack to back it. R is the natural pairing
and the missing-language gap that closes the loop on the
academic-research / modeling use case the user has been validating.

**Why tidyverse as the default.** Modern R has bifurcated; tidyverse
is what the data-science world has converged on (Posit / RStudio
ecosystem, every modern textbook, every common-knowledge package).
Base R remains correct and powerful for academic statistics work and
package authors who want minimal dependencies. The pack codifies
tidyverse as the default and documents the base-R alternative behind
an ADR — same pattern as Rust's `tokio` default with `async-std` /
`smol` alternatives in `expertise/rust/conventions.md`.

**Why renv as the packaging default.** `renv` is the project-local
lockfile-based dependency manager that has effectively replaced
`packrat`. It interoperates with CRAN, Bioconductor, and remotes,
and is the recommendation in Posit's modern R-project tooling. No
serious alternative is in active use today.

**Applies-to set rationale.** R is the dominant language for the
three Data & Analytics personas (`data-scientist`, `data-analyst`,
`data-engineer`) and is also a primary-language choice for some
`developer` projects (academic research, statistical computing,
quantitative finance). Including `developer` lets a non-data project
that picks R get the conventions without forcing the user to add a
data persona just to inherit the pack.

**Sibling references.** Use
`ai-team-library/expertise/python/` and `ai-team-library/expertise/go/`
as structural templates. They share the same five-file shape and
section ordering. The R pack should match this scale and tone.

**Splitting decision.** The molecularity gate flagged this bean's
estimated ~750 net lines as exceeding the strict 300-line blast-
radius budget. Splitting `conventions.md` from `testing.md` /
`security.md` etc. would create artificial review boundaries — the
five files form one coherent expertise pack, and a half-shipped pack
would be confusing to users. Same content-authoring exemption applied
to BEAN-291 (~1200 lines, single bean). Documented here so the
exemption is explicit.

**Out-of-scope follow-ups noted but not yet filed.**

- `r-shiny` expertise — file when there is demand for Shiny web-app
  conventions in a generated project.
- `r-bayesian` expertise — file when there is demand for the
  Stan / brms / rstanarm patterns specifically.
- `R` content additions to `expertise/data-engineering/conventions.md`
  cross-referencing this pack — file when the data-engineering pack
  next gets a content review.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Author the R expertise pack (5 files + README + indexer fixtures) | developer | 9m | 835,474 | 5,454 | $1.70 |
| 2 | Content-tone parity review + indexer regression + manual verification | tech-qa | 5m | 656,831 | 3,112 | $1.55 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | — (comma-separated, actual not planned) |
| **Bounces** | — (Tech-QA → Developer kicks) |
| **Scope changes** | — (in-flight scope edits) |
| **Contract violations** | — (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | — (BEAN-272's NONE-justified) |
| **Dispatch mode** | — (in-process / tmux-worker / mixed) |