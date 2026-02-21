# Go Performance

Performance patterns and anti-patterns for Go applications. Covers memory
management, concurrency tuning, profiling, database optimization, caching, and
observability.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| Runtime              | Go 1.22+ (latest stable)             | ADR               |
| GC Tuning            | `GOGC=100` (default)                 | ADR               |
| Profiling            | `pprof` (stdlib)                     | Never             |
| Tracing              | `runtime/trace`                      | Never             |
| Connection Pooling   | `database/sql` pool settings         | ADR               |
| Caching              | In-process (`sync.Map`, LRU)         | ADR               |
| Distributed Cache    | Redis                                | ADR               |
| Metrics              | Prometheus client (`promhttp`)       | ADR               |
| Load Testing         | k6 or `vegeta`                       | ADR               |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| `GOGC=100`           | `GOMEMLIMIT`         | Container environments with hard memory limits |
| In-process LRU       | `groupcache`         | Multi-instance cache coherence        |
| `pprof`              | Datadog continuous profiler | Production profiling with APM   |
| Prometheus           | OpenTelemetry        | Vendor-neutral observability          |
| k6                   | `hey` / `wrk`        | Quick ad-hoc HTTP benchmarks          |

---

## Memory Management

```go
// Pre-allocate slices when size is known.
items := make([]Order, 0, len(ids)) // Known capacity avoids reallocation.

// Use sync.Pool for frequently allocated short-lived objects.
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func processRequest(data []byte) string {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()

    buf.Write(data)
    // ... process ...
    return buf.String()
}
```

**Rules:**
- Pre-allocate slices and maps with `make([]T, 0, cap)` when the capacity is
  known or estimable.
- Use `sync.Pool` for high-frequency allocations (buffers, encoders, temporary
  structs) to reduce GC pressure.
- Avoid allocations in hot paths. Use `go test -benchmem` to measure allocs per
  operation.
- Use `GOMEMLIMIT` in container environments to set a soft memory limit and
  prevent OOM kills. Combine with `GOGC=100` (or higher) for best effect.
- Prefer stack allocation: small, non-escaping values stay on the stack. Use
  `go build -gcflags="-m"` to check escape analysis.

---

## Concurrency Performance

```go
// Bounded worker pool with errgroup.
func (s *Service) ProcessBatch(ctx context.Context, ids []string) error {
    g, ctx := errgroup.WithContext(ctx)
    g.SetLimit(runtime.NumCPU()) // Match CPU-bound concurrency to cores.

    for _, id := range ids {
        g.Go(func() error {
            return s.processOne(ctx, id)
        })
    }
    return g.Wait()
}

// Use buffered channels for producer-consumer with backpressure.
work := make(chan Job, 100) // Buffer prevents producer blocking.
```

**Rules:**
- For CPU-bound work, limit goroutines to `runtime.NumCPU()`. More goroutines
  add scheduling overhead without throughput gain.
- For I/O-bound work, goroutine count can exceed CPU count but should still be
  bounded (use `errgroup.SetLimit` or a semaphore channel).
- Use buffered channels for decoupling producer and consumer speeds.
- Avoid `sync.Mutex` in hot paths. Prefer channel-based designs or
  `sync/atomic` for counters and flags.
- Profile goroutine counts with `runtime.NumGoroutine()` or `pprof` to detect
  leaks.

---

## Connection Pooling (database/sql)

```go
db, err := sql.Open("pgx", connStr)
if err != nil {
    return fmt.Errorf("open db: %w", err)
}

db.SetMaxOpenConns(25)              // Max simultaneous connections.
db.SetMaxIdleConns(10)              // Keep idle connections ready.
db.SetConnMaxLifetime(30 * time.Minute) // Prevent stale connections.
db.SetConnMaxIdleTime(5 * time.Minute)  // Reclaim unused connections.
```

**Rules:**
- Set `MaxOpenConns` based on the formula: `(CPU cores * 2) + effective spindle
  count`. Start with 25 and tune via load testing.
- Set `ConnMaxLifetime` shorter than the database's connection timeout.
- Monitor pool stats with `db.Stats()` and export to Prometheus.
- Use `pgxpool` (for PostgreSQL) when you need more control over connection
  lifecycle.
- Always pass `context.Context` to query methods for cancellation.

---

## Profiling

```go
import _ "net/http/pprof" // Registers pprof handlers on DefaultServeMux.

// In production, use a separate mux on a non-public port.
debugMux := http.NewServeMux()
debugMux.HandleFunc("/debug/pprof/", pprof.Index)
debugMux.HandleFunc("/debug/pprof/profile", pprof.Profile)
debugMux.HandleFunc("/debug/pprof/heap", pprof.Handler("heap").ServeHTTP)

go http.ListenAndServe("localhost:6060", debugMux) // Internal only.
```

```bash
# CPU profile (30-second sample).
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap profile (current allocations).
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine dump (detect leaks).
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Trace (scheduling, GC, syscalls).
curl -o trace.out http://localhost:6060/debug/pprof/trace?seconds=5
go tool trace trace.out
```

**Rules:**
- Always profile before optimizing. Measure, don't guess.
- Use CPU profiles to find hot functions, heap profiles to find memory hogs.
- Use goroutine profiles to detect leaks (growing count over time).
- Use `runtime/trace` for scheduling and GC analysis.
- Never expose `pprof` on public-facing ports. Bind to `localhost` or an
  internal network.
- Run benchmarks with `-benchmem` to track allocations alongside timing.

---

## Caching

```go
// Simple in-process cache with sync.Map for read-heavy workloads.
var cache sync.Map

func GetUser(ctx context.Context, id string) (User, error) {
    if v, ok := cache.Load(id); ok {
        return v.(User), nil
    }

    user, err := repo.FindByID(ctx, id)
    if err != nil {
        return User{}, err
    }

    cache.Store(id, user)
    return user, nil
}

// For bounded caches, use an LRU library (e.g., hashicorp/golang-lru).
cache, _ := lru.New[string, User](10000) // Max 10k entries.
```

**Rules:**
- Always set a maximum size on caches. Unbounded caches cause OOM.
- Invalidate on every mutation path. Stale cache is worse than no cache.
- Use `sync.Map` only for read-heavy, append-mostly workloads. For other
  patterns, use a `sync.RWMutex`-protected map or an LRU library.
- For multi-instance deployments, use Redis as the cache backend to avoid
  inconsistency between local caches.
- Measure cache hit rates. A cache with <80% hit rate may not be worth the
  complexity.

---

## Do / Don't

### Do
- Profile before optimizing. Use `pprof` to find the actual bottleneck.
- Pre-allocate slices and maps when size is known.
- Use `sync.Pool` for high-frequency short-lived allocations.
- Use `strings.Builder` instead of `+` or `fmt.Sprintf` in tight loops.
- Batch database operations: use bulk INSERT and batch reads.
- Set `GOMEMLIMIT` in container environments to prevent OOM kills.
- Use `context.Context` for timeouts on all I/O operations.
- Monitor goroutine count, heap size, GC pauses, and connection pool stats.

### Don't
- Optimize without profiling. You will optimize the wrong thing.
- Use `sync.Mutex` where `sync.RWMutex` or `atomic` suffices.
- Create goroutines in hot loops without bounding concurrency.
- Allocate in hot paths (use `benchmem` to verify).
- Use `reflect` in hot paths. It is orders of magnitude slower than typed code.
- Use `encoding/json` in extreme throughput scenarios without benchmarking
  alternatives (`json-iterator`, `easyjson`, `sonic`).
- Use `interface{}` / `any` for performance-critical data structures.
- Ignore GC pauses. Monitor with `runtime.ReadMemStats` or Prometheus.

---

## Common Pitfalls

1. **Goroutine leaks from unbounded concurrency** -- Spawning a goroutine per
   request without limits exhausts memory. Use `errgroup.SetLimit`, worker
   pools, or semaphore channels.
2. **Excessive allocations from string concatenation** -- Using `+` in loops
   creates a new string per iteration. Use `strings.Builder` or `bytes.Buffer`.
3. **`sync.Map` misuse** -- `sync.Map` is optimized for read-heavy workloads
   with stable keys. For frequently updated maps, a `sync.RWMutex`-protected
   map is faster.
4. **Unbounded caches** -- Caching without eviction causes heap growth until
   OOM. Always use LRU or TTL-based eviction.
5. **Blocking on DNS in hot paths** -- DNS resolution can take 100+ ms. Use
   connection pooling and persistent connections to avoid repeated DNS lookups.
6. **JSON marshal/unmarshal overhead** -- `encoding/json` uses reflection and
   allocates heavily. For hot paths, consider `json-iterator` or code-generated
   marshalers (`easyjson`).
7. **Missing database indexes** -- Full table scans on large tables. Enable
   slow query logging and run `EXPLAIN ANALYZE` on all query patterns.
8. **Over-tuning GOGC** -- Setting `GOGC` too low increases GC frequency
   (higher CPU). Setting it too high increases memory usage. Profile with
   `runtime/trace` before changing.

---

## Checklist

- [ ] Profiled with `pprof` (CPU, heap, goroutine) before optimization.
- [ ] Slices and maps pre-allocated with known/estimated capacity.
- [ ] `sync.Pool` used for high-frequency allocations in hot paths.
- [ ] `go test -benchmem` shows zero or minimal allocations in hot paths.
- [ ] `GOMEMLIMIT` set in container deployments.
- [ ] Database connection pool sized via load testing (`SetMaxOpenConns`).
- [ ] All caches have maximum size and eviction policy.
- [ ] Goroutine concurrency bounded (`errgroup.SetLimit`, worker pools).
- [ ] HTTP client and server timeouts configured.
- [ ] Prometheus metrics exported (goroutines, heap, GC, pool stats).
- [ ] Load tested with k6 or `vegeta` before production deployment.
- [ ] No `reflect` usage in hot paths without benchmarked justification.
- [ ] `pprof` endpoint not exposed on public-facing ports.
