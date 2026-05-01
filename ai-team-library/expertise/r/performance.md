# R Performance

Performance profiling, vectorisation patterns, and memory-management
discipline for R 4.3+ projects. R's copy-on-modify semantics and interpreter
overhead make naive code surprisingly slow; the patterns below close the gap.
Measure first, optimise second, document always.

---

## Defaults

| Concern              | Default Tool / Approach                  |
|----------------------|------------------------------------------|
| Profiling (CPU)      | `profvis` (interactive flame graph)      |
| Microbenchmarks      | `bench::mark()`                          |
| Macro timing         | `tictoc` (named timers)                  |
| Memory profiling     | `profvis` (built-in alloc tracking) + `lobstr::obj_size()` |
| Large in-memory tables | `data.table`                           |
| Out-of-core / arrow data | `arrow`, `duckdb`                    |
| Parallelism (multi-core) | `future` + `furrr`                   |
| Iteration            | Vectorised first; `purrr::map_*` second; `for` last |
| Caching              | `memoise` (function-level)               |

### Alternatives

- **`microbenchmark`** — older microbenchmarking package. `bench::mark()` is
  preferred (cleaner output, statistical comparison, GC tracking).
- **`Rprof`** + **`profvis`** — `Rprof()` is the underlying sampler;
  `profvis()` is the visualiser. Use `profvis()` directly in normal work.
- **`parallel`** (stdlib) — `mclapply()` / `parLapply()` work but are clunky.
  Prefer the `future`/`furrr` API.
- **`Rcpp`** — drop into C++ for hot loops the R-level patterns cannot help.
  Reach for it only after vectorisation and `data.table` are exhausted.

---

## Profiling Before Optimising

Never optimise without a profile. Intuition about R bottlenecks is wrong
even more often than in other languages because R's interpreter cost is
non-uniform.

### Interactive profiling with profvis

```r
library(profvis)

profvis({
  data <- read.csv("big-file.csv")
  result <- data |>
    dplyr::group_by(customer_id) |>
    dplyr::summarise(total = sum(amount))
  write.csv(result, "out.csv")
})
```

`profvis()` opens an interactive flame graph in the RStudio Viewer (or your
browser) showing CPU time and memory allocation per line. Look for:

- Lines that consume most of the time (the wide bars).
- Spikes of memory allocation (the orange bars) — those are usually
  copy-on-modify events.

### Microbenchmarking with bench

```r
library(bench)

x <- runif(1e6)
bench::mark(
  loop      = { s <- 0; for (v in x) s <- s + v; s },
  vector    = sum(x),
  iterations = 50,
  check     = FALSE
)
```

`bench::mark()` reports mean, median, and IQR; tracks memory allocation
and GC events; and warns when expressions return different values (set
`check = FALSE` only when you intentionally compare incompatible code).

---

## Vectorisation

Vectorisation is the single largest performance lever in R. Replacing a
loop with a vector op typically yields 50-1000x speedups.

```r
x <- runif(1e6)

# BAD — O(n) interpreter dispatches, ~2 s
total <- 0
for (i in seq_along(x)) {
  total <- total + x[i]
}

# GOOD — single C call, ~3 ms
total <- sum(x)
```

### Vectorise the predicate, not the loop

```r
# BAD
for (i in seq_along(orders$total)) {
  if (orders$total[i] > 100) orders$tier[i] <- "premium"
}

# GOOD — vectorised assignment
orders$tier[orders$total > 100] <- "premium"

# GOOD — dplyr equivalent
orders <- orders |> mutate(tier = if_else(total > 100, "premium", "standard"))
```

### Use `purrr::map_*` for non-vectorisable work

When you genuinely need iteration (e.g., calling an API per row), prefer
`purrr` over `for` — the typed return variants (`map_dbl`, `map_chr`,
`map_lgl`) catch type errors that `lapply` would silently allow.

```r
# Fetches one record per id, returns a tibble
results <- ids |> purrr::map(fetch_record) |> dplyr::bind_rows()
```

---

## data.table for Large In-Memory Work

`data.table` is the high-performance alternative to `data.frame`/`tibble`.
Use it when:

- The dataset has > ~1M rows.
- Group-and-aggregate is the dominant operation.
- Memory pressure matters (data.table modifies in place, avoiding copies).

```r
library(data.table)
dt <- as.data.table(orders)

# Group-by-summarise — fast and memory-efficient
result <- dt[, .(total = sum(amount), n = .N), by = customer_id]

# In-place update — no copy
dt[total > 100, tier := "premium"]

# Indexed lookup — O(log n) after setting a key
setkey(dt, customer_id)
dt[J("cust-42")]
```

`data.table` and `dplyr` interoperate via `dtplyr` (lazy data.table backend
for the dplyr verbs), letting you keep tidyverse syntax with data.table
performance when needed.

---

## Out-of-Core Data with arrow / duckdb

When data exceeds RAM, do not load it. Stream from disk.

```r
library(arrow)

# Lazy reference to a Parquet file — nothing loaded yet
ds <- arrow::open_dataset("path/to/parquet/")

# Build a dplyr pipeline; arrow pushes computation into the engine
result <- ds |>
  dplyr::filter(year == 2025) |>
  dplyr::group_by(customer_id) |>
  dplyr::summarise(total = sum(amount)) |>
  dplyr::collect()  # only now does data come into R
```

`duckdb` plays the same role for analytical SQL workloads — register R data
frames or Parquet files as DuckDB tables and run SQL or `dplyr` against
them out-of-core.

---

## Parallelism with future and furrr

`future` is the unified parallel-execution API. `furrr` provides
`future_map_*()` — the parallel analogues of `purrr::map_*()`.

```r
library(future)
library(furrr)

# Pick a backend
plan(multisession, workers = 4)   # cross-platform, separate R processes
# plan(multicore, workers = 4)    # forking — Linux/macOS only, faster startup

# Parallel map
results <- ids |> future_map(fetch_record, .progress = TRUE) |> bind_rows()

# Restore sequential execution
plan(sequential)
```

Use `multisession` (separate R processes) by default; it works on every
platform. Reach for `multicore` (forked workers) only on Linux/macOS where
shared memory and faster startup matter.

### When parallelism does not help

- The work is already vectorised (R's vectorised ops are C-level threads
  internally for some functions; further parallelism adds overhead).
- The per-task work is small (< ~10 ms). Worker IPC dominates.
- The task allocates large objects per iteration. Inter-process serialisation
  costs swamp the savings.

Always benchmark sequential vs. parallel; do not assume parallel is faster.

---

## Memory and Copy-on-Modify

R is copy-on-modify: assigning to one element of a vector copies the entire
vector. This is the most common silent-performance trap.

```r
# BAD — quadratic memory and time
x <- c()
for (i in 1:10000) x <- c(x, i)

# GOOD — pre-allocate
x <- integer(10000)
for (i in seq_along(x)) x[i] <- i

# BETTER — vectorise
x <- seq_len(10000)
```

### Inspect object size before assuming

```r
library(lobstr)

obj_size(orders)              # bytes used
obj_size(orders, customers)   # combined size with shared storage accounted for
mem_used()                    # process memory snapshot
```

`lobstr::obj_size()` is honest about shared storage — `obj_size(x, y)` is
*not* `obj_size(x) + obj_size(y)` if they share components.

### Reference semantics with R6 and environments

When an algorithm naturally wants reference semantics (mutable shared
state, observer patterns), use `R6` classes or environments — both bypass
copy-on-modify. Reach for them deliberately, not as a default.

---

## Caching with memoise

For pure functions whose results are stable for given inputs, `memoise`
provides drop-in caching:

```r
library(memoise)

fetch_tax_rate <- memoise(function(region, category) {
  # expensive HTTP call
  api_client$get_rate(region, category)
})

# Bound the cache to disk so it survives restarts
cache <- cachem::cache_disk(file.path(tempdir(), "tax-cache"))
fetch_tax_rate <- memoise(fetch_tax_rate, cache = cache)
```

Only memoise pure functions (same input → same output). Set a cache backend
with bounded size (`cache_mem(max_size = ...)`) for long-running processes.

---

## Do / Don't

**Do:**

- Profile before optimising — `profvis()` is the first stop, not your gut.
- Vectorise: replace explicit loops with `sum`, `mean`, `dplyr` verbs, etc.
- Pre-allocate vectors before filling them; never grow with `c()` in a loop.
- Use `data.table` (or `dtplyr`) when row counts exceed ~1M.
- Stream large datasets via `arrow` / `duckdb` instead of loading everything.
- Use `future` + `furrr` for parallelism; pick `multisession` by default.
- Cache pure functions with `memoise` — bounded size and (when needed) disk.
- Inspect object size with `lobstr::obj_size()`, not `object.size()`
  (the latter does not account for shared storage).

**Don't:**

- Optimise without profiling data — you will optimise the wrong thing.
- Grow vectors with `c(x, new)` or data frames with `rbind(df, new_row)`
  inside loops — both trigger O(n²) copies.
- Use `apply()` on data frames where `purrr::map_*` or vectorised dplyr
  works — `apply()` coerces to matrix and silently corrupts mixed types.
- Reach for `Rcpp` before exhausting vectorisation, `data.table`, and
  `arrow` — most R performance problems are algorithmic, not language-level.
- Parallelise tiny tasks; the IPC overhead beats the parallelism gain.
- Forget `plan(sequential)` after a parallel section — leftover workers
  hog memory and confuse later code.

---

## Common Pitfalls

1. **Growing vectors in a loop.** `x <- c(x, val)` reallocates and copies on
   every iteration. For 10,000 iterations that is 50 million element copies.
   Pre-allocate or use `vapply`/`map_*`.

2. **`apply()` on a data frame.** `apply(df, 1, fn)` coerces the data frame
   to a matrix first — every column becomes the type of the most-general
   column, silently corrupting numerics into strings if any column is
   character. Use `purrr::pmap_*()` or row-wise dplyr instead.

3. **Hidden copies under `<-` with named subsetting.** `df$col[idx] <- val`
   copies the entire data frame in older R versions. Modern R is smarter,
   but `data.table`'s `:=` is still the only zero-copy path for very large
   tables.

4. **Profiling without enough work.** A function that runs in 5 ms gives
   noisy `profvis()` output. Wrap the call in a `replicate(100, ...)` or
   profile a longer pipeline so the sampler has enough data.

5. **Parallelising a fast vectorised op.** `sum()` is already a single C
   call — wrapping it in `future_map()` makes it slower. Profile first;
   only parallelise tasks that are slow per-iteration.

6. **Forgetting `gc()` reflects past, not current, memory.** `gc()` reports
   memory after collection, but R's allocator does not always release
   freed pages back to the OS. `gc()` reduction does not always show up in
   `htop`. Use `lobstr::mem_used()` for the live R-side picture.

7. **Using `microbenchmark` instead of `bench::mark()`.** `bench` reports
   memory allocations and GC events alongside timing, which is what you
   need to interpret the result. `microbenchmark` only times.

8. **Reading a Parquet file with `read.csv`.** Using the wrong reader
   (CSV path on Parquet, or vice versa) silently produces empty or
   corrupt output. Use `arrow::read_parquet()` / `arrow::read_csv_arrow()`
   for type-stable, multi-threaded reads.

---

## Checklist

- [ ] Hot paths identified via `profvis()` (not guessing)
- [ ] `bench::mark()` covers critical hot paths to catch regressions
- [ ] No vector growth (`c(x, new)`) inside loops — pre-allocated or vectorised
- [ ] Loops replaced with vectorised ops or `purrr::map_*` where possible
- [ ] `data.table` (or `dtplyr`) used when row counts exceed ~1M
- [ ] `arrow` / `duckdb` used for out-of-core / Parquet workloads
- [ ] Parallel work uses `future` + `furrr`; backend explicit (`plan()`)
- [ ] `plan(sequential)` restored after parallel sections
- [ ] Caches via `memoise` are bounded (size or TTL); pure functions only
- [ ] Memory inspected with `lobstr::obj_size()`, not `object.size()`
- [ ] Benchmark results recorded as a baseline for regression detection
- [ ] Optimisation changes documented with before/after numbers
