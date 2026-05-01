# R Testing

Testing strategy and patterns for R projects: unit tests with `testthat`
(3rd edition), coverage with `covr`, static analysis with `lintr` and
`styler`, and snapshot tests for ggplot2 outputs. CI integration patterns
included.

---

## Defaults

| Concern              | Default Tool / Approach                  |
|----------------------|------------------------------------------|
| Test framework       | `testthat` (3rd edition)                 |
| Coverage             | `covr` (line + expression coverage)      |
| Linter               | `lintr` (CI gate)                        |
| Formatter check      | `styler::style_pkg(dry = "fail")`        |
| Snapshot testing     | `testthat::expect_snapshot()` for text; `vdiffr::expect_doppelganger()` for ggplot |
| Mocking              | `mockery` (function stubs); `httptest2` (HTTP) |
| Property-based       | `hedgehog` (Haskell-style PBT for R)     |
| CI runner            | GitHub Actions with `r-lib/actions/check-r-package` |

### Alternatives

- **`tinytest`** — minimalist alternative to testthat; no dependencies.
  Good for tiny utility packages.
- **`RUnit`** — older xUnit-style framework. Avoid for new work.
- **`vcr`** — cassette-based HTTP mocking. Use when `httptest2` does not
  fit your client.

---

## Project Layout

```
package-root/
  R/
    pricing.R
    discount.R
  tests/
    testthat.R                  # one-line entry point: `testthat::test_check("orderpricing")`
    testthat/
      helper-fixtures.R         # loaded automatically before tests
      setup.R                   # one-time setup (DB, env vars)
      teardown.R                # one-time cleanup
      test-pricing.R            # tests for R/pricing.R
      test-discount.R           # tests for R/discount.R
      _snaps/                   # snapshot files (committed)
```

Test files mirror the source: `R/pricing.R` → `tests/testthat/test-pricing.R`.
`helper-*.R` files are sourced before any test runs and are the right place
for shared fixtures and helper functions.

---

## Configuration

```
# DESCRIPTION
Suggests:
    testthat (>= 3.0.0),
    covr,
    vdiffr,
    mockery
Config/testthat/edition: 3
```

`Config/testthat/edition: 3` opts into the 3rd-edition behaviour: stricter
warnings, snapshot tests, parallel runners. Always opt in for new packages.

```r
# tests/testthat.R
library(testthat)
library(orderpricing)
test_check("orderpricing")
```

---

## Writing Tests

### Unit test example

```r
# tests/testthat/test-pricing.R
test_that("no discount is applied below the threshold", {
  result <- calculate_discount(
    tibble::tibble(total = c(40, 30)),
    tier = "standard",
    min_total = 50
  )
  expect_equal(result$discount, c(0, 0))
  expect_equal(result$final_total, c(40, 30))
})

test_that("premium tier applies a 15% discount above the threshold", {
  result <- calculate_discount(tibble::tibble(total = 100), tier = "premium")
  expect_equal(result$discount, 15)
  expect_equal(result$final_total, 85)
})

test_that("negative totals raise a classed error", {
  expect_error(
    calculate_discount(tibble::tibble(total = -1)),
    class = "calculate_discount_error"
  )
})
```

`test_that()` blocks are reporter-friendly and isolate failures.
`expect_*()` is the assertion family — every test should make at least one
assertion.

### Fixture and helper patterns

```r
# tests/testthat/helper-fixtures.R
make_orders <- function(n = 3) {
  tibble::tibble(
    customer_id = paste0("cust-", seq_len(n)),
    total = seq.int(50, by = 25, length.out = n)
  )
}
```

Helpers in `helper-*.R` are auto-loaded. Use them for fixture builders, not
fixture data — building the fixture per-test keeps tests independent and
readable.

### Mocking with mockery

```r
test_that("fetch_record returns parsed body on 200", {
  mockery::stub(
    fetch_record,
    "httr2::req_perform",
    function(req) list(status_code = 200, body = '{"id":1}')
  )
  result <- fetch_record(id = 1)
  expect_equal(result$id, 1)
})
```

`mockery::stub()` replaces a function by name within the scope of one test.
Reach for it when the unit under test calls a network or filesystem API
that you do not want to hit in unit tests.

### HTTP testing with httptest2

For higher-fidelity HTTP testing, `httptest2` records real responses to
disk on first run, then replays them on subsequent runs:

```r
httptest2::with_mock_dir("api-fixtures", {
  test_that("fetches and parses orders", {
    result <- fetch_orders(customer_id = "cust-1")
    expect_s3_class(result, "tbl_df")
  })
})
```

Commit the `api-fixtures/` directory; tests then run offline forever after.

---

## Snapshot Testing

### Text / structured output

```r
test_that("summary table shape is stable", {
  result <- summarise_orders(make_orders(3))
  expect_snapshot(print(result))
})
```

`expect_snapshot()` records the output to `_snaps/<test-file>.md` on first
run. Subsequent runs diff against the snapshot. Review snapshot diffs
exactly like code diffs — they are the test.

To regenerate after intentional output changes:

```r
testthat::snapshot_accept()  # accept all
testthat::snapshot_accept("test-pricing")  # accept one file
```

### ggplot2 / visual snapshots with vdiffr

```r
test_that("revenue plot renders correctly", {
  p <- plot_revenue(make_orders(10))
  vdiffr::expect_doppelganger("revenue-by-customer", p)
})
```

`vdiffr` writes the plot to SVG, normalises rendering quirks across
platforms, and diffs against the baseline. Run
`vdiffr::manage_cases()` interactively to review and accept changes.

---

## Coverage with covr

```r
# Local
covr::package_coverage()
covr::report()  # opens an interactive browser with line-by-line coverage

# CI — fail under threshold
cov <- covr::package_coverage()
threshold <- 80
if (covr::percent_coverage(cov) < threshold) {
  stop(sprintf("Coverage %.1f%% below threshold %d%%",
               covr::percent_coverage(cov), threshold))
}

# Upload to Codecov / Coveralls
covr::codecov()
```

Aim for 80% line coverage minimum. Branch coverage is the better metric —
`covr::package_coverage(type = "all")` reports both.

---

## Linter and Formatter Gates

```r
# lintr — CI gate
lintr::lint_package()
# Returns a (zero-length) list of lints — non-empty fails CI

# styler — CI gate (dry=fail mode rejects unformatted code)
styler::style_pkg(dry = "on")  # dry-run; report changes
# In CI:
result <- styler::style_pkg(dry = "fail")
if (!is.null(result) && nrow(result) > 0) {
  stop("styler reformatted files — commit the formatting changes")
}
```

`.lintr` config (project root):

```
linters: linters_with_defaults(
  line_length_linter(100L),
  object_name_linter(styles = c("snake_case", "SNAKE_CASE")),
  cyclocomp_linter(complexity_limit = 15L),
  T_and_F_symbol_linter(),
  undesirable_function_linter()
)
exclusions: list("renv", "data-raw", "tests/testthat/_snaps")
```

---

## CI Integration

GitHub Actions example (`.github/workflows/check.yaml`):

```yaml
on: [push, pull_request]

jobs:
  R-CMD-check:
    runs-on: ${{ matrix.config.os }}
    strategy:
      fail-fast: false
      matrix:
        config:
          - {os: ubuntu-latest,   r: 'release'}
          - {os: ubuntu-latest,   r: 'devel'}
          - {os: macos-latest,    r: 'release'}
          - {os: windows-latest,  r: 'release'}
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: ${{ matrix.config.r }}
      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: any::rcmdcheck, any::lintr, any::styler, any::covr
      - uses: r-lib/actions/check-r-package@v2
      - name: Lint
        run: Rscript -e 'lintr::lint_package()'
      - name: Style
        run: Rscript -e 'res <- styler::style_pkg(dry = "fail"); if (!is.null(res)) quit(status = 1)'
      - name: Coverage
        if: matrix.config.os == 'ubuntu-latest' && matrix.config.r == 'release'
        run: Rscript -e 'covr::codecov()'
```

The matrix runs `R CMD check` on three OSes and on R-devel — the latter
catches deprecation warnings before they become errors.

---

## Property-Based Testing (Optional)

For numeric or string-domain functions, property-based tests catch edge
cases that example-based tests miss.

```r
library(hedgehog)

test_that("discount never exceeds total", {
  forall(gen.c(of = 100, gen.element(seq(0, 1000, by = 0.5))), function(totals) {
    result <- calculate_discount(tibble::tibble(total = totals), tier = "premium")
    expect_true(all(result$discount >= 0))
    expect_true(all(result$discount <= result$total))
    expect_true(all(result$final_total >= 0))
  })
})
```

`hedgehog` is the R port of Haskell's hedgehog property-based testing
library. Use it for any function with a numeric or string input range.

---

## Do / Don't

**Do:**

- Opt into `Config/testthat/edition: 3` in every new package.
- Mirror `R/` structure under `tests/testthat/` (`R/foo.R` →
  `test-foo.R`).
- Use fixture builders (helpers) over committed fixture data.
- Snapshot text and structured output with `expect_snapshot()`.
- Snapshot ggplot output with `vdiffr::expect_doppelganger()`.
- Run `covr` in CI with a coverage threshold gate.
- Run `lintr` and `styler --dry=fail` in CI on every PR.
- Test the empty-input case for any function that summarises or groups.
- Use `mockery::stub()` to isolate units from network or filesystem.

**Don't:**

- Use `setup.R` to mutate the user's environment without restoring it in
  `teardown.R`.
- Commit snapshot diffs without reviewing them line-by-line.
- Skip the sad path — every classed error needs a triggering test.
- Test private helpers directly when a public-API test would also exercise
  them — public-API tests survive refactors.
- Use `Sys.sleep()` to wait for asynchronous work; poll with a deadline
  instead.
- Disable a test with no comment explaining why; either fix it or delete
  it with a `TODO` and an issue link.
- Rely on test order — `testthat` shuffles tests by default in edition 3.

---

## Common Pitfalls

1. **Missing `Config/testthat/edition: 3` in `DESCRIPTION`.** Without it,
   you are still on edition 2: weaker warnings handling, no snapshot
   support, sequential execution. Opt into edition 3 explicitly.

2. **Stale snapshots.** When output legitimately changes, `_snaps/*` files
   need to be updated. Run `testthat::snapshot_accept()` after reviewing
   the diff in your PR. Do not blindly accept.

3. **Random failures from non-deterministic tests.** Tests that depend on
   time, RNG, or hash order will be flaky. Set `set.seed()` at the top of
   tests that use random numbers; freeze time with `withr::with_options`
   or a clock-injection pattern.

4. **`expect_equal()` on floating-point values.** Use the `tolerance`
   argument (defaults to `sqrt(.Machine$double.eps)` ≈ 1.5e-8). For very
   small or very large numbers, set tolerance explicitly.

5. **Tests that hit the real network.** `R CMD check` on CRAN runs without
   network access. A test that silently relies on `httr2::req_perform()`
   reaching the internet fails on the CRAN runner. Mock with
   `mockery`/`httptest2` or skip with `skip_on_cran()`.

6. **Skipping coverage on integration paths.** A unit-test-only suite
   reports 95% coverage but misses the bug at the boundary. Include at
   least one integration test that exercises the package end to end.

7. **`vdiffr` snapshots breaking across R versions.** Different R versions
   render fonts and SVG slightly differently. Restrict `vdiffr` runs to
   one OS + R version in CI; `skip_if_not(vdiffr::is_checking_locally())`
   on others.

8. **Forgetting `library(testthat)` in `tests/testthat.R`.** The entry
   file must load testthat and the package, then call `test_check()`. A
   missing `library(testthat)` produces confusing "could not find
   `test_check`" errors.

---

## Checklist

- [ ] `Config/testthat/edition: 3` set in `DESCRIPTION`
- [ ] `tests/testthat.R` entry file present and minimal
- [ ] Test files mirror `R/` structure (`R/foo.R` → `test-foo.R`)
- [ ] Helpers in `helper-*.R`; one-time setup/teardown via `setup.R`/`teardown.R`
- [ ] Every classed error has a triggering test (`expect_error(..., class = ...)`)
- [ ] Empty-input case tested for every summariser
- [ ] Snapshot tests for stable text output (`expect_snapshot`)
- [ ] `vdiffr` snapshots for ggplot output, restricted to one CI OS + R version
- [ ] `covr::package_coverage()` runs in CI with ≥ 80% threshold
- [ ] `lintr::lint_package()` runs in CI and is clean
- [ ] `styler::style_pkg(dry = "fail")` runs in CI and is clean
- [ ] CI matrix covers Ubuntu / macOS / Windows on R-release; Ubuntu on R-devel
- [ ] No `Sys.sleep()` in tests; poll with deadlines instead
- [ ] Tests do not depend on network access (or guard with `skip_on_cran()`)
