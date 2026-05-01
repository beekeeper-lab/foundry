# BEAN-294 — Tech-QA Manual-Verification Observations

| Field | Value |
|-------|-------|
| **Bean** | BEAN-294 (Add R Language Expertise Pack) |
| **Branch** | `bean/BEAN-294-r-language-expertise` |
| **SHA at verification** | `e6a5dd2` (Developer's Task 01) + Tech-QA Task 02 commit on top |
| **Date** | 2026-05-01 |
| **Verifier** | tech-qa |
| **Display available?** | No — headless session. Manual wizard walk + Generate-button walk substituted with automated tests against the real library through the real indexer + real `compile_project`. |

## Headless substitution rationale

The bean's two manual AC items are written as wizard walks:
1. "Launch `uv run foundry`, expand Languages category, confirm R card appears."
2. "Compose `developer + tech-qa + data-scientist` + R, click Generate, confirm CLAUDE.md references R conventions."

No display is available in this session, so per the task file's
explicit "headless substitution" guidance these are converted to
automated tests that exercise the same load-bearing path:

- The wizard's Expertise Selection page consumes
  `LibraryIndex.expertise` produced by `build_library_index`. The
  page renders any expertise whose `category == "Languages"` under
  the Languages group. So if the real-library indexer surfaces R
  with category `Languages`, the wizard will display it.
- The Generate button runs `compile_project` (via
  `generate_project`), which emits the Tech Stack table row plus the
  standalone `ai/generated/expertise/r.md`. So if a real-library
  `compile_project` call with R in the spec produces both artefacts,
  the manual wizard walk would as well.

Both substitution tests run the **real** `ai-team-library/` (no
mocked `LibraryIndex`, no synthetic expertise files).

## Mapping each AC item to its automated coverage

| AC | Coverage |
|----|----------|
| Section-header parity (5 files mirror python/) | Manual diff below — broadly mirrored, with substantive R-specific divergences. |
| Defaults table density >=8 rows | 12 data rows in `r/conventions.md` (vs 9 for `python/conventions.md`). |
| Verbatim "tidyverse" in `r/conventions.md` | 7 occurrences — Defaults table row + dedicated section 4. |
| Verbatim "renv" in `r/packaging.md` | 34 occurrences across the file. |
| `r/conventions.md` Applies To = 4 personas | Lines 6–11: `data-scientist`, `data-analyst`, `data-engineer`, `developer`. |
| README expertise row | Line 85, in the language cluster (after `swift`, before `react-native`). |
| `EXPECTED_EXPERTISE` includes `r` | `tests/test_library_indexer.py` line 71 (between `python-qt-pyside6` and `react`). |
| `LibraryIndex.expertise` surfaces `r` with category `Languages` | `tests/test_library_indexer.py::TestExpertiseCategories::test_all_expertise_have_expected_category` (Developer added `"r": "Languages"` at line 677). Plus Tech-QA's `tests/test_compiler.py::TestBean294RExpertiseIntegration::test_indexer_surfaces_r_under_languages` (real library, real indexer). |
| BEAN-271 `applies_to`-stripping consistency | `tests/test_library_indexer.py::TestExpertiseAppliesTo::test_real_library_curated_applies_to` lines 893–907. Locks the same pattern python/typescript/react use: bare extended-tier names get pruned, `developer` is the surviving entry. |
| (manual) Wizard displays R card under Languages | Substituted by `test_indexer_surfaces_r_under_languages` (the wizard reads `LibraryIndex.expertise[category=="Languages"]`). |
| (manual) Generated CLAUDE.md references R conventions | Substituted by `test_compile_project_emits_r_in_claude_md` — Tech-QA addition; real library, real `compile_project`, asserts both the Tech Stack row (`ai/generated/expertise/r.md`) and the standalone file's R-specific content (verbatim "tidyverse"). |
| `uv run pytest` passes full suite | 2450 passed (was 2448 on Developer's commit; +2 new). |
| `uv run ruff check foundry_app/` clean | Clean. |

## Section-header diff: r/ vs python/

Independently re-walked each file. Cells marked **"R-only"** are
load-bearing for R (NSE / tidyverse-vs-base, vectorisation gotchas,
copy-on-modify, package supply chain). Cells marked **"py-only"** are
language-specific (type hints, async).

### conventions.md

| python | r | Notes |
|--------|---|-------|
| Category | Category | match |
| Applies To | Applies To | match |
| Defaults | Defaults | match (12 rows R, 9 rows python) |
| 1. Project Structure | 1. Project Structure | match |
| 2. Naming Conventions | 2. Naming Conventions | match |
| 3. Formatting and Linting | 3. Formatting and Style | match (rename, same intent) |
| 4. Type Hints | (omitted) | py-only — R has no static types |
| 5. Import Ordering | (omitted) | py-only — R uses `library()`/`::`, no import-order convention |
| 6. Docstring Style | 6. Documentation (roxygen2) | match (rename, same intent) |
| 7. Virtual Environment & Dep Mgmt | (deferred to packaging.md/renv) | conventions.md→packaging.md split |
| 8. Logging Conventions | (omitted) | py-specific — R logging conventions are weaker |
| 9. Error Handling | 7. Error Handling | match |
| 10. Testing | (deferred to testing.md) | conventions.md→testing.md split |
| (omitted) | 4. Tidyverse vs. base R | R-only — load-bearing dialect choice |
| (omitted) | 5. Function Design | R-only — covers NSE, defensive args |
| Do/Don't | Do/Don't | match |
| Common Pitfalls | Common Pitfalls | match |
| Checklist | Checklist | match |

### packaging.md

| python | r | Notes |
|--------|---|-------|
| Defaults | Defaults | match |
| pyproject.toml Reference | DESCRIPTION Reference | match (rename, same intent) |
| Dependency Management with uv | Dependency Management with renv | match (rename, same intent) |
| Versioning | Versioning | match |
| Building and Publishing | Build and Test Loop with devtools / Release Flow | match (R splits into two sections) |
| Entry Points and CLI Scripts | (omitted) | py-only — R packages don't expose console scripts |
| (omitted) | Documentation Site with pkgdown | R-only — pkgdown is a default tool |
| (omitted) | Project Layout (non-package analyses) | R-only — analysis-vs-package distinction is meaningful in R |
| Do/Don't, Common Pitfalls, Checklist | same | match |

### performance.md

| python | r | Notes |
|--------|---|-------|
| Defaults | Defaults | match |
| Profiling Before Optimizing | Profiling Before Optimising | match (UK/US spelling) |
| Benchmarking with pytest-benchmark | (folded into Profiling) | minor consolidation |
| Common Optimization Patterns | Vectorisation / data.table / arrow-duckdb / future-furrr / Memory & Copy-on-Modify / Caching | R splits the patterns into named sections — substantive expansion (load-bearing) |
| Do/Don't, Common Pitfalls, Checklist | same | match |

### security.md

| python | r | Notes |
|--------|---|-------|
| Defaults | Defaults | match |
| Dependency Auditing | Package Supply Chain | match (rename, same intent) |
| Secrets Management | Secrets Management | match |
| Input Validation | Untrusted Input — Never `eval(parse())` | match (R-specific framing of the same concern) |
| SQL Injection Prevention | Safe Database Access with DBI | match (R-specific framing) |
| Safe HTTP Clients | Safe HTTP Clients | match |
| Path Traversal Prevention | File Path Safety | match (rename, same intent) |
| Do/Don't, Common Pitfalls, Checklist | same | match |

### testing.md

| python | r | Notes |
|--------|---|-------|
| Defaults | Defaults | match |
| Project Layout | Project Layout | match |
| Configuration | Configuration | match |
| Writing Tests | Writing Tests | match |
| Do/Don't, Common Pitfalls, Checklist | same | match |
| (omitted) | Snapshot Testing (vdiffr) | R-only — ggplot snapshots are an R idiom |
| (omitted) | Coverage with covr | R-only — equivalent of pytest-cov, named separately |
| (omitted) | Linter and Formatter Gates | R-only — `lintr` + `styler` are tested explicitly |
| (omitted) | CI Integration | R-only — GitHub Actions matrix sample |
| (omitted) | Property-Based Testing (Optional) | R-only — `hedgehog` PBT note |

R's `testing.md` is the largest divergence: 9 H2 sections vs python's
5. The added sections are all load-bearing for R (vdiffr, covr,
lintr/styler, CI, hedgehog). Tone-parity is preserved — every added
section follows the same Defaults/Do/Don't pattern.

**Conclusion:** R's section structure broadly mirrors python/. All
divergences are R-specific (NSE, tidyverse, vectorisation,
roxygen2/renv/pkgdown, vdiffr, covr) or python-specific (async, type
hints) — none are stylistic drift.

## BEAN-271 applies-to-stripping consistency

`r/conventions.md` lists four personas in markdown source:
`data-scientist`, `data-analyst`, `data-engineer`, `developer`.

The indexer's BEAN-271 migration prunes bare extended-tier names
(`data-scientist`, `data-analyst`, `data-engineer` — extended-tier
since BEAN-291), leaving only the surviving core-tier entry:
`developer`. The same pattern is already locked for python (lists 5
in markdown, indexer surfaces 2: developer, tech-qa) and react
(lists ~5, indexer surfaces 1: developer). R's behavior is
consistent with that precedent — Developer's
`tests/test_library_indexer.py::TestExpertiseAppliesTo::test_real_library_curated_applies_to`
addition (lines 893–907) pins this and confirms it.

**No escalation kicked back to Developer.** The deviation is
mechanical, not stylistic, and the markdown source preserves the
four-persona intent for human readers and the wizard.

## Tech-QA additions to the test suite

| Test (file::class::name) | Purpose |
|---|---|
| `tests/test_compiler.py::TestBean294RExpertiseIntegration::test_indexer_surfaces_r_under_languages` | Real library, real indexer — confirm `expertise_by_id("r")` returns a populated `ExpertiseInfo` with `category == "Languages"` and `conventions.md` in `files`. Backstops the wizard's display path. |
| `tests/test_compiler.py::TestBean294RExpertiseIntegration::test_compile_project_emits_r_in_claude_md` | Real library, real `compile_project` — `developer + tech-qa` + R; assert generated `CLAUDE.md` Tech Stack table references `ai/generated/expertise/r.md`, and the standalone file surfaces verbatim "tidyverse" from the real conventions.md. Substitutes the manual Generate-button walk. |

## README placement note (minor finding, non-blocking)

The README expertise table is grouped by category, not strictly
alphabetical (e.g. `python-qt-pyside6` precedes `react`; `go` follows
`dotnet`). Developer placed `r` after `swift` (last of the language
cluster) and before `react-native`, which is consistent with the
established cluster ordering. AC text says "alphabetical order" but
the existing list isn't alphabetical, so the placement is correct
relative to existing precedent. No change requested.

## Test counts

| Category | Count |
|----------|-------|
| Tests added by Developer (Task 01) | 0 new test functions; 3 fixture/assertion additions in `tests/test_library_indexer.py` (`EXPECTED_EXPERTISE`, category map, applies-to block) |
| Tests added by Tech-QA (Task 02) | 2 (`test_indexer_surfaces_r_under_languages`, `test_compile_project_emits_r_in_claude_md`) |
| Full `uv run pytest` pass count | 2450 (was 2448 on Developer's commit; +2 new) |
| `uv run ruff check foundry_app/` | clean |

## Verdict

All BEAN-294 acceptance criteria are satisfied. No regressions
observed. The R expertise pack is well-formed, tone-parallel with
`python/`, indexed correctly, and reachable end-to-end through the
compiler. The bean is ready for the orchestrator's verification +
close phase.
