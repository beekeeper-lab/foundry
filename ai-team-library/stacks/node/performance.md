# Node.js Performance

Performance patterns and anti-patterns for Node.js server applications.
Covers event-loop health, memory management, I/O optimization, caching,
and observability.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| HTTP Framework       | Fastify (fast-json-stringify built-in)| ADR               |
| Serialization        | `fast-json-stringify` via schemas     | ADR               |
| Caching Layer        | Redis (`ioredis`)                     | ADR               |
| Connection Pooling   | Framework/driver built-in pools       | ADR               |
| Profiling            | `node --prof` / Clinic.js             | --                |
| Metrics              | Prometheus client (`prom-client`)     | ADR               |
| Load Testing         | `autocannon` or `k6`                  | ADR               |

### Alternatives

| Primary         | Alternative        | Notes                            |
|-----------------|--------------------|----------------------------------|
| `ioredis`       | `@redis/client`    | Official client, less mature     |
| Clinic.js       | 0x                 | Flamegraph-only, lighter         |
| `autocannon`    | k6                 | k6 for complex scripted scenarios|
| `prom-client`   | OpenTelemetry SDK  | For full tracing + metrics       |

---

## Event-Loop Health

The event loop is single-threaded. Blocking it blocks every request.

```typescript
// BAD: synchronous JSON parse of a large payload blocks the loop
const data = JSON.parse(fs.readFileSync("large-file.json", "utf-8"));

// GOOD: stream-parse large files
import { createReadStream } from "node:fs";
import { pipeline } from "node:stream/promises";
import { parser } from "stream-json";
import { streamArray } from "stream-json/streamers/StreamArray";

await pipeline(
  createReadStream("large-file.json"),
  parser(),
  streamArray(),
  async function* (source) {
    for await (const { value } of source) {
      await processItem(value);
    }
  },
);
```

**Rules:**
- Never perform CPU work >5 ms on the main thread. Offload to `worker_threads`
  or a job queue.
- Use `setImmediate()` to yield in tight loops so the event loop can process
  other callbacks.
- Monitor event-loop lag via `monitorEventLoopDelay()` from `node:perf_hooks`.

---

## Connection and Resource Pooling

```typescript
// PostgreSQL connection pool (pg library)
import { Pool } from "pg";

const pool = new Pool({
  connectionString: config.DATABASE_URL,
  max: 20,                   // max connections in pool
  idleTimeoutMillis: 30_000, // close idle connections after 30 s
  connectionTimeoutMillis: 5_000,
});

// Always release connections -- use pool.query() for single statements
const { rows } = await pool.query("SELECT * FROM orders WHERE id = $1", [id]);
```

**Rules:**
- Size the connection pool to match the expected concurrency, not the max Node
  cluster size. Start with `max = 20` and tune via load testing.
- Set `idleTimeoutMillis` to avoid holding stale connections.
- Use the pool's `query()` shorthand for single statements. Only check out
  a client when running transactions.
- Close the pool on `SIGTERM` to avoid connection leaks during shutdown.

---

## Do / Don't

### Do
- Define Fastify response schemas -- they enable `fast-json-stringify`, which
  is 2-5x faster than `JSON.stringify`.
- Use streams for large payloads (file uploads/downloads, CSV exports).
- Cache frequently-read, rarely-changed data in Redis with a TTL.
- Use `Promise.all()` for independent async operations instead of sequential
  `await`.
- Profile before optimizing. Use `autocannon` for throughput and Clinic.js for
  bottleneck diagnosis.
- Set `keepAlive: true` on HTTP agents for outbound requests.
- Enable gzip/brotli compression via `@fastify/compress` for text responses.

### Don't
- Use `JSON.parse` / `JSON.stringify` on large objects synchronously.
- Create a new database connection per request -- use a connection pool.
- Cache without a TTL -- stale data and memory growth are inevitable.
- Use `cluster` module as a substitute for proper horizontal scaling.
- Pre-optimize without profiling data. Measure first.
- Buffer entire request/response bodies when streaming is possible.
- Ignore backpressure when piping streams -- use `pipeline()` from
  `node:stream/promises`.

---

## Common Pitfalls

1. **Unintentional serialization cost** -- Fastify without a response schema
   falls back to `JSON.stringify`, losing the `fast-json-stringify` advantage.
   Always declare response schemas.
2. **Memory leaks from closures** -- Closures capturing request-scoped objects
   inside long-lived caches or event listeners will leak. Use `WeakRef` or
   scope lifetimes carefully.
3. **N+1 queries** -- Fetching a list then querying each item individually.
   Use `JOIN`, `IN (...)`, or a DataLoader pattern to batch.
4. **Unbounded concurrency** -- `Promise.all(thousandItems.map(fetch))` opens
   thousands of connections simultaneously. Use `p-limit` or `p-map` with a
   concurrency cap.
5. **Missing graceful shutdown** -- Killing the process without draining
   in-flight requests causes client errors. Handle `SIGTERM`, stop accepting
   new connections, finish active requests, then exit.
6. **Ignoring DNS caching** -- Node.js does not cache DNS by default. High-QPS
   outbound calls to the same host trigger redundant lookups. Use
   `cacheable-lookup` or a local DNS cache.

---

## Checklist

- [ ] Response schemas defined on all routes (enables `fast-json-stringify`).
- [ ] Database connections use a pool with `max`, `idleTimeoutMillis`, and `connectionTimeoutMillis` set.
- [ ] No synchronous file I/O or CPU-heavy work on the main thread.
- [ ] Streams used for payloads >1 MB (uploads, downloads, exports).
- [ ] Redis cache has a TTL on every key.
- [ ] Independent async operations use `Promise.all()` (not sequential `await`).
- [ ] Unbounded concurrency capped with `p-limit` or equivalent.
- [ ] Graceful shutdown handles `SIGTERM`: stop listener, drain connections, exit.
- [ ] Event-loop lag monitored via `monitorEventLoopDelay()` or metrics.
- [ ] Load tested with `autocannon` or `k6` before production deployment.
- [ ] Compression enabled for text-based responses (`@fastify/compress`).
- [ ] Outbound HTTP agents use `keepAlive: true`.
