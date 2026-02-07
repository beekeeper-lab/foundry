# Python Performance

Performance profiling, optimization patterns, and pitfalls for Python 3.12+
applications. Measure first, optimize second, document always.

---

## Defaults

| Concern              | Default Tool / Approach            |
|----------------------|------------------------------------|
| Profiling (CPU)      | `cProfile` + `snakeviz`            |
| Profiling (line)     | `scalene`                          |
| Profiling (memory)   | `memray`                           |
| Benchmarking         | `pytest-benchmark`                 |
| Async runtime        | `asyncio` (stdlib)                 |
| Concurrency (I/O)    | `asyncio` or `concurrent.futures.ThreadPoolExecutor` |
| Concurrency (CPU)    | `concurrent.futures.ProcessPoolExecutor` or `multiprocessing` |
| Caching              | `functools.lru_cache` / `functools.cache` |
| Data processing      | `polars` (prefer over pandas for new work) |

### Alternatives

- **`py-spy`** -- sampling profiler that attaches to running processes without
  code changes. Great for profiling production.
- **`line_profiler`** -- decorator-based line profiler. Use when `scalene`
  overhead is too high.
- **`uvloop`** -- drop-in asyncio event loop replacement. 2-4x faster for
  I/O-heavy async workloads.
- **`pandas`** -- established data library. Use if the project already depends
  on it; prefer `polars` for new projects (faster, no GIL contention).

---

## Profiling Before Optimizing

Never optimize without a profile. Intuition about bottlenecks is wrong more
often than not.

### CPU Profiling with cProfile

```python
import cProfile
import pstats

# Profile a function call
profiler = cProfile.Profile()
profiler.enable()
result = expensive_function()
profiler.disable()

# Print top 20 by cumulative time
stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(20)
```

Visualize with `snakeviz`:

```bash
python -m cProfile -o profile.out my_script.py
snakeviz profile.out
```

### Memory Profiling with memray

```bash
# Record memory allocations
memray run my_script.py

# Generate a flamegraph
memray flamegraph memray-my_script.py.bin -o flamegraph.html

# Track leaks (allocations not freed by end)
memray flamegraph --leaks memray-my_script.py.bin -o leaks.html
```

---

## Benchmarking with pytest-benchmark

Add `pytest-benchmark` to dev dependencies and write benchmarks alongside
tests:

```python
import pytest
from my_app.services.parser import parse_document


@pytest.mark.slow
def test_parse_performance(benchmark) -> None:
    """Benchmark document parsing to catch regressions."""
    large_doc = load_fixture("large_document.xml")
    result = benchmark(parse_document, large_doc)
    assert result.is_valid


@pytest.mark.slow
def test_batch_insert_performance(benchmark, db_session) -> None:
    """Benchmark batch insert to verify O(n) scaling."""
    records = [make_record(i) for i in range(1000)]
    benchmark(db_session.bulk_save_objects, records)
```

Run benchmarks separately from the main test suite:

```bash
pytest -m slow --benchmark-only --benchmark-sort=mean
```

---

## Common Optimization Patterns

### Use Generators for Large Sequences

```python
# BAD -- loads entire file into memory
def read_records(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f]

# GOOD -- yields one record at a time
def read_records(path: str) -> Iterator[dict]:
    with open(path) as f:
        for line in f:
            yield json.loads(line)
```

### Use `__slots__` for Memory-Heavy Data Classes

```python
from dataclasses import dataclass

# Without __slots__: each instance has a __dict__ (~200 bytes overhead)
@dataclass
class Point:
    x: float
    y: float

# With __slots__: fixed memory layout (~64 bytes per instance)
@dataclass(slots=True)
class Point:
    x: float
    y: float
```

For millions of instances, `slots=True` reduces memory by 50-70%.

### Use `functools.lru_cache` for Expensive Pure Functions

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def compute_tax_rate(region: str, category: str) -> Decimal:
    """Look up tax rate from external service -- results are stable."""
    return tax_service.get_rate(region, category)
```

Only cache pure functions (same input always gives same output). Set
`maxsize` to control memory usage. Use `cache` (unbounded) only when the
key space is known and small.

### Async for I/O-Bound Work

```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            r.json() for r in responses
            if isinstance(r, httpx.Response) and r.status_code == 200
        ]
```

### ProcessPoolExecutor for CPU-Bound Work

```python
from concurrent.futures import ProcessPoolExecutor
from my_app.services.transform import transform_chunk

def process_large_dataset(chunks: list[bytes]) -> list[Result]:
    """Distribute CPU-bound work across processes."""
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(transform_chunk, chunks))
    return results
```

---

## Do / Don't

**Do:**
- Profile before optimizing -- use `cProfile`, `scalene`, or `memray`.
- Write `pytest-benchmark` tests for hot paths to catch regressions.
- Use generators and iterators for large sequences to control memory.
- Use `__slots__` on data classes when creating millions of instances.
- Use `asyncio` for I/O-bound concurrency (network, disk).
- Use `ProcessPoolExecutor` for CPU-bound parallelism (bypasses GIL).
- Use `polars` over `pandas` for new data processing work.
- Set `maxsize` on `lru_cache` to bound memory usage.

**Don't:**
- Optimize without profiling data -- you will optimize the wrong thing.
- Use threads for CPU-bound work -- the GIL serializes them.
- Cache impure functions (functions with side effects or time-dependent output).
- Use `multiprocessing` with large objects passed between processes -- the
  serialization overhead can exceed the parallelism gains.
- Pre-allocate or pre-compute "just in case" -- lazy evaluation is usually
  cheaper overall.
- Use `asyncio.gather()` without `return_exceptions=True` -- one failure
  cancels all tasks silently.
- Convert between pandas DataFrames and Python lists repeatedly in hot loops.

---

## Common Pitfalls

1. **Optimizing without profiling.** The most common performance mistake is
   guessing the bottleneck. Profile first. The real bottleneck is almost never
   where you expect it.

2. **Using threads for CPU-bound work.** Python's GIL means threads only help
   for I/O-bound tasks. For CPU work, use `ProcessPoolExecutor` or
   `multiprocessing`.

3. **Unbounded `lru_cache`.** `@lru_cache` with no `maxsize` grows without
   limit. For functions called with many distinct arguments, this is a memory
   leak. Always set `maxsize` or use TTL-based caching.

4. **Loading entire files into memory.** Reading a 2 GB CSV into a list
   exhausts RAM. Use generators, `polars.scan_csv()` (lazy), or chunked
   reading.

5. **Creating millions of dataclass instances without `__slots__`.** Each
   instance carries a `__dict__` with ~200 bytes overhead. `slots=True`
   eliminates this.

6. **Synchronous I/O in an async application.** Calling `requests.get()` inside
   an `async def` blocks the entire event loop. Use `httpx.AsyncClient` or
   run blocking I/O in a thread via `asyncio.to_thread()`.

7. **String concatenation in loops.** `result += chunk` creates a new string
   each iteration (O(n^2)). Use `"".join(chunks)` or `io.StringIO` instead.

8. **Premature use of C extensions or Cython.** Before reaching for C, verify
   that algorithmic improvements, caching, and concurrency are exhausted.
   A better algorithm in Python beats a bad algorithm in C.

---

## Checklist

- [ ] Hot paths identified via profiling (not guessing)
- [ ] `pytest-benchmark` tests cover critical hot paths
- [ ] Large sequences use generators/iterators, not lists
- [ ] `__slots__` used on data classes with high instance counts
- [ ] `lru_cache` has explicit `maxsize` set
- [ ] I/O-bound concurrency uses `asyncio` (not threads)
- [ ] CPU-bound concurrency uses `ProcessPoolExecutor` (not threads)
- [ ] No synchronous blocking calls inside `async def` functions
- [ ] No string concatenation in loops -- use `"".join()` or `StringIO`
- [ ] Memory profiling run for data-heavy services (memray or scalene)
- [ ] Benchmark results recorded as baseline for regression detection
- [ ] Optimization changes documented with before/after measurements
