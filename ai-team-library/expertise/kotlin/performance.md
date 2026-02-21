# Kotlin Performance

Performance patterns and anti-patterns for Kotlin applications. Covers
coroutine tuning, memory management, JVM optimization, database access,
caching, and profiling for both server-side and Android.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| JVM                  | JDK 21 (server) / ART (Android)      | ADR               |
| Coroutine Dispatcher | `Dispatchers.IO` (I/O), `.Default` (CPU) | Never          |
| Profiling (Server)   | VisualVM / async-profiler             | ADR               |
| Profiling (Android)  | Android Studio Profiler               | Never             |
| Connection Pooling   | HikariCP                              | ADR               |
| Caching              | Caffeine (in-process)                 | ADR               |
| Distributed Cache    | Redis                                 | ADR               |
| Metrics              | Micrometer + Prometheus               | ADR               |
| Load Testing         | k6 or Gatling                         | ADR               |
| Serialization        | kotlinx.serialization                 | ADR               |

### Alternatives

| Primary              | Alternative          | When                                  |
|----------------------|----------------------|---------------------------------------|
| HikariCP             | R2DBC pool           | Fully reactive / non-blocking stack   |
| Caffeine             | Guava Cache          | Already using Guava heavily           |
| async-profiler       | JFR (Flight Recorder)| Production-safe continuous profiling  |
| Micrometer           | OpenTelemetry        | Vendor-neutral observability          |
| Gatling              | k6                   | Prefer scripting over Scala DSL       |

---

## Coroutine Performance

```kotlin
// Use appropriate dispatchers
suspend fun processOrders(ids: List<String>): List<Order> = coroutineScope {
    ids.map { id ->
        async(Dispatchers.IO) { // I/O-bound: use IO dispatcher
            orderRepository.findById(id)
        }
    }.awaitAll().filterNotNull()
}

// Limit concurrency with a Semaphore
private val semaphore = Semaphore(10)

suspend fun processWithLimit(id: String): Order {
    return semaphore.withPermit {
        orderRepository.findById(id)
    }
}

// Use Flow operators for backpressure
fun processStream(): Flow<Result> = flow {
    orderRepository.findAllPending()
        .collect { order ->
            emit(processOne(order))
        }
}.buffer(capacity = 64) // Buffer for producer-consumer decoupling
    .flowOn(Dispatchers.IO)
```

**Rules:**
- Use `Dispatchers.IO` for blocking I/O (database, file, network).
  `Dispatchers.Default` for CPU-bound computation (parsing, sorting, hashing).
- Limit concurrent coroutines with `Semaphore` or `Channel` to prevent
  resource exhaustion.
- Use `Flow.buffer()` and `Flow.conflate()` to manage backpressure.
- Avoid `Dispatchers.Unconfined` in production — it resumes on the caller's
  thread, causing unpredictable behavior.
- Use `withTimeout` to prevent coroutines from hanging indefinitely.
- Profile coroutine counts with kotlinx-coroutines-debug in development.

---

## Memory Management

```kotlin
// Use sequences for lazy evaluation on large collections
val result = largeList
    .asSequence()
    .filter { it.isActive }
    .map { it.toSummary() }
    .take(100)
    .toList() // Terminal operation triggers evaluation

// Avoid unnecessary object creation in hot paths
// BAD: creates intermediate list
val names = users.filter { it.isActive }.map { it.name }

// GOOD: single pass with sequence
val names = users.asSequence().filter { it.isActive }.map { it.name }.toList()

// Use value classes for type-safe wrappers without allocation overhead
@JvmInline
value class OrderId(val value: String)

@JvmInline
value class CustomerId(val value: String)
```

**Rules:**
- Use `Sequence` for chains of collection operations on large datasets (>1000
  elements). Sequences are lazy and avoid intermediate allocations.
- Use `@JvmInline value class` for type-safe wrappers. They are erased at
  compile time (no heap allocation in most cases).
- Avoid autoboxing in hot paths: use primitive arrays (`IntArray`) instead of
  `Array<Int>` which boxes to `Integer[]`.
- Pre-size collections with `ArrayList(capacity)` or `buildList(capacity)` when
  the size is known.
- Use `lazy` for expensive initializations that may not be needed.
- Android: avoid object allocations in `onDraw()` and tight loops.

---

## Database Performance (HikariCP + Spring Data)

```kotlin
// build.gradle.kts — HikariCP is the Spring Boot default
// application.yml
// spring:
//   datasource:
//     hikari:
//       maximum-pool-size: 20
//       minimum-idle: 5
//       connection-timeout: 30000
//       idle-timeout: 600000
//       max-lifetime: 1800000

// Use Spring Data projections for read-only queries
interface OrderSummary {
    val id: String
    val total: BigDecimal
    val status: String
}

@Query("SELECT o.id, o.total, o.status FROM Order o WHERE o.customerId = :customerId")
fun findSummariesByCustomer(customerId: String): List<OrderSummary>

// Batch operations for bulk inserts
@Modifying
@Query("UPDATE Order o SET o.status = :status WHERE o.id IN :ids")
fun updateStatusBatch(ids: List<String>, status: String): Int
```

**Rules:**
- Size connection pool based on: `(CPU cores * 2) + effective spindle count`.
  Start with 20 and tune via load testing.
- Use projections or DTOs for read queries. Fetching full entities for display
  wastes memory and bandwidth.
- Batch writes with `saveAll()` or native batch queries for bulk operations.
- Enable query logging in development (`spring.jpa.show-sql=true`) and slow
  query logging in production.
- Use `@Transactional(readOnly = true)` for read-only operations to enable
  JPA/Hibernate optimizations.

---

## Caching (Caffeine)

```kotlin
@Configuration
@EnableCaching
class CacheConfig {
    @Bean
    fun cacheManager(): CacheManager = CaffeineCacheManager().apply {
        setCaffeine(
            Caffeine.newBuilder()
                .maximumSize(10_000)
                .expireAfterWrite(10.minutes.toJavaDuration())
                .recordStats()
        )
    }
}

@Service
class UserService(private val repo: UserRepository) {
    @Cacheable("users")
    suspend fun findById(id: String): User? = repo.findByIdOrNull(id)

    @CacheEvict("users", key = "#user.id")
    suspend fun update(user: User): User = repo.save(user)
}
```

**Rules:**
- Always set a maximum size on caches. Unbounded caches cause OOM.
- Invalidate on every mutation path. Stale cache is worse than no cache.
- Use `expireAfterWrite` for time-based eviction. Choose TTL based on data
  staleness tolerance.
- Export cache stats to Micrometer/Prometheus. Monitor hit rates (target >80%).
- For multi-instance deployments, use Redis to avoid cross-instance
  inconsistency.

---

## Profiling

```bash
# async-profiler — low-overhead CPU + allocation profiling
# Attach to running JVM
./asprof -d 30 -f profile.html <pid>

# JFR (Java Flight Recorder) — production-safe
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr -jar app.jar

# Analyze with JFR
jfr print --events jdk.ObjectAllocationInNewTLAB recording.jfr
```

**Rules:**
- Always profile before optimizing. Measure, don't guess.
- Use async-profiler or JFR in production (low overhead, <2%).
- Profile CPU, memory allocation, and lock contention separately.
- Use JMH for micro-benchmarks of hot code paths.
- Android: use Android Studio Profiler for CPU, memory, network, and energy.
- Monitor GC pauses with `-Xlog:gc*` and tune with `-XX:+UseG1GC` or
  `-XX:+UseZGC` for low-latency.

---

## Do / Don't

### Do
- Profile before optimizing. Use async-profiler or JFR to find the actual bottleneck.
- Use `Sequence` for multi-step collection operations on large datasets.
- Use `@JvmInline value class` for type-safe primitives without boxing overhead.
- Use `Dispatchers.IO` for blocking calls, `.Default` for CPU-bound work.
- Limit concurrent coroutines with `Semaphore` or bounded `Channel`.
- Use HikariCP connection pooling with tuned pool sizes.
- Batch database operations for bulk inserts/updates.
- Set timeouts on all I/O operations (`withTimeout`, HTTP client timeouts).
- Export metrics with Micrometer and monitor cache hit rates.

### Don't
- Optimize without profiling. You will optimize the wrong thing.
- Use `Dispatchers.Unconfined` in production code.
- Create coroutines in tight loops without bounding concurrency.
- Use `Array<Int>` when `IntArray` suffices (avoids boxing).
- Ignore GC pauses. Monitor and tune GC for your workload.
- Use reflection in hot paths. Prefer kotlinx.serialization (compile-time)
  over Jackson (reflection-based) for performance-critical serialization.
- Fetch full JPA entities for read-only display. Use projections.
- Use `runBlocking` on dispatcher threads — it blocks the thread and wastes
  the pool.

---

## Common Pitfalls

1. **Coroutine thread starvation** -- Running blocking I/O on `Dispatchers.Default`
   exhausts the shared CPU thread pool. Always use `Dispatchers.IO` or
   `withContext(Dispatchers.IO)` for blocking calls.
2. **Excessive intermediate collections** -- Chained `.filter{}.map{}.flatMap{}`
   on lists creates a new list per operation. Use `asSequence()` for lazy
   evaluation.
3. **Autoboxing in hot paths** -- `List<Int>` boxes every element to `Integer`.
   Use `IntArray` or `@JvmInline value class` for primitives in
   performance-sensitive code.
4. **N+1 queries** -- Lazy-loaded JPA relationships trigger a query per item.
   Use `@EntityGraph`, `JOIN FETCH`, or projections to batch-load.
5. **Unbounded coroutine fan-out** -- Launching `async {}` per item in a large
   list without limits floods the dispatcher and downstream services. Use
   `Semaphore` or `Channel`-based worker pools.
6. **`StateFlow` over-emission on Android** -- Emitting every intermediate state
   from a ViewModel causes unnecessary recomposition. Use `distinctUntilChanged()`
   and `debounce()` to coalesce rapid updates.
7. **String template in logging** -- `log.info("Processing $orderId")` eagerly
   evaluates the template even when INFO is disabled. Use SLF4J placeholders:
   `log.info("Processing orderId={}", orderId)`.
8. **Missing database indexes** -- Full table scans on large tables. Enable slow
   query logging and run `EXPLAIN ANALYZE` on all query patterns.

---

## Checklist

- [ ] Profiled with async-profiler or JFR (CPU, allocation, locks) before optimization.
- [ ] `Dispatchers.IO` used for all blocking I/O; `.Default` for CPU-bound work.
- [ ] Coroutine concurrency bounded with `Semaphore` or `Channel`.
- [ ] `Sequence` used for multi-step collection operations on large datasets.
- [ ] `@JvmInline value class` used for type-safe wrappers in hot paths.
- [ ] HikariCP pool sized via load testing; connection limits configured.
- [ ] All caches have maximum size and eviction policy (Caffeine).
- [ ] Cache stats exported to Micrometer/Prometheus; hit rate monitored (>80%).
- [ ] JPA projections used for read-only queries; no unnecessary entity fetching.
- [ ] Database queries batch writes; slow query logging enabled.
- [ ] GC tuned for workload (`G1GC` or `ZGC`); GC pauses monitored.
- [ ] HTTP client and server timeouts configured.
- [ ] Load tested with k6 or Gatling before production deployment.
- [ ] No reflection in hot paths; kotlinx.serialization preferred.
