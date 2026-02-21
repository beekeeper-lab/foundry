# Java Performance

Performance patterns and anti-patterns for Java server applications with
Spring Boot. Covers JVM tuning, database optimization, caching, concurrency,
and observability.

---

## Defaults

| Concern              | Default Choice                        | Override Requires |
|----------------------|---------------------------------------|-------------------|
| JVM                  | Java 21 LTS (GraalVM optional)       | ADR               |
| GC                   | G1GC (default), ZGC for low-latency  | ADR               |
| Connection Pooling   | HikariCP (Spring Boot default)       | Never             |
| Caching              | Spring Cache + Caffeine (local)      | ADR               |
| Distributed Cache    | Redis (Lettuce client)               | ADR               |
| Profiling            | async-profiler / JFR                 | --                |
| Metrics              | Micrometer + Prometheus              | ADR               |
| Load Testing         | Gatling or k6                        | ADR               |

### Alternatives

| Primary        | Alternative          | Notes                            |
|----------------|----------------------|----------------------------------|
| G1GC           | ZGC                  | Sub-ms pauses, higher throughput overhead |
| Caffeine       | Ehcache              | When disk overflow is needed     |
| async-profiler | VisualVM             | GUI-based, less production-safe  |
| Gatling        | JMeter               | JMeter for teams already using it|

---

## JVM and GC Tuning

```bash
# Production JVM flags (Java 21, G1GC)
java \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UseStringDeduplication \
  -Xms512m -Xmx2g \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/var/log/app/heapdump.hprof \
  -XX:+ExitOnOutOfMemoryError \
  -jar app.jar
```

**Rules:**
- Set `-Xms` equal to `-Xmx` in production to avoid heap resize pauses.
- Enable `-XX:+HeapDumpOnOutOfMemoryError` in all environments.
- Use G1GC by default. Switch to ZGC only if GC pauses >200 ms are
  unacceptable and you have measured the impact.
- Enable JDK Flight Recorder (JFR) in production with low-overhead settings
  for continuous profiling.

---

## Connection Pooling (HikariCP)

```yaml
# application.yml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000       # 5 minutes
      connection-timeout: 5000   # 5 seconds
      max-lifetime: 1800000      # 30 minutes
      leak-detection-threshold: 30000  # 30 seconds
```

**Rules:**
- Size the pool based on the formula: `connections = (core_count * 2) + effective_spindle_count`. Start with 20 and tune via load testing.
- Enable `leak-detection-threshold` in development and staging to catch
  unclosed connections.
- Set `max-lifetime` shorter than the database's `wait_timeout` to avoid
  stale connections.
- Monitor pool metrics via Micrometer (`hikaricp.connections.*`).

---

## Caching

```java
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean
    public CaffeineCacheManager cacheManager() {
        var manager = new CaffeineCacheManager();
        manager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(Duration.ofMinutes(5))
            .recordStats());
        return manager;
    }
}

@Service
public class ProductService {

    @Cacheable(value = "products", key = "#id")
    public Product findById(String id) {
        return productRepository.findById(id)
            .orElseThrow(() -> new NotFoundException("Product", id));
    }

    @CacheEvict(value = "products", key = "#id")
    public void update(String id, UpdateProductRequest request) {
        // ... update logic ...
    }
}
```

**Rules:**
- Always set a `maximumSize` and `expireAfterWrite`. Unbounded caches cause OOM.
- Use `@CacheEvict` on every mutation path. Stale cache is worse than no cache.
- Enable `recordStats()` in non-production for hit/miss ratio monitoring.
- For multi-instance deployments, use Redis as the cache backend to avoid
  inconsistency between local caches.

---

## Do / Don't

### Do
- Use virtual threads (Java 21) for I/O-bound workloads -- they eliminate the
  need for reactive frameworks in most cases.
- Profile before optimizing. Use async-profiler or JFR to find the real
  bottleneck.
- Use `Stream` API for collection processing, but avoid parallel streams unless
  the workload is CPU-bound and measured.
- Batch database operations: prefer `saveAll()` over repeated `save()`.
- Use `StringBuilder` in tight loops instead of string concatenation.
- Set `fetch = FetchType.LAZY` on all JPA `@ManyToOne` / `@OneToMany`
  relationships.
- Monitor GC pauses, heap usage, and thread counts via Micrometer/Prometheus.

### Don't
- Use `synchronized` on virtual threads -- it pins the carrier thread. Use
  `ReentrantLock` or `java.util.concurrent` alternatives.
- Create a new `ObjectMapper` per request. Reuse a singleton configured at
  startup.
- Allocate large byte arrays on every request (e.g., buffering entire file
  uploads). Use streaming.
- Use `@Transactional` on read-only queries without `readOnly = true` -- it
  disables Hibernate dirty-checking optimization.
- Ignore N+1 queries. They are the number one cause of slow APIs.
- Use `FetchType.EAGER` on JPA relationships -- it loads the entire object
  graph regardless of need.

---

## Common Pitfalls

1. **N+1 queries** -- Lazy-loading a collection inside a loop fires one query
   per element. Use `@EntityGraph`, `JOIN FETCH`, or batch-size hints
   (`@BatchSize(size = 50)`).
2. **Oversized connection pools** -- More connections != more throughput. Too
   many connections exhaust database resources. Start with 20, load test, and
   tune.
3. **Unbounded caches** -- `@Cacheable` without eviction or size limits causes
   heap exhaustion under load. Always configure Caffeine limits.
4. **Blocking on virtual threads** -- `synchronized`, `ReentrantLock.lock()`,
   and native JNI calls pin virtual threads. Profile with JFR to detect pinning.
5. **Missing database indexes** -- Full table scans on millions of rows. Enable
   Hibernate's `hibernate.show_sql` + `pg_stat_statements` in development to
   find slow queries. Add indexes and verify via `EXPLAIN ANALYZE`.
6. **Startup time in containers** -- Fat Spring Boot JARs take 5-10 s to start.
   Use Spring AOT, CDS (Class Data Sharing), or GraalVM native images to
   reduce startup to <1 s.
7. **Excessive logging in hot paths** -- `log.debug()` with string formatting
   in tight loops has measurable cost even when debug is disabled unless you
   use parameterized logging (`log.debug("msg key={}", value)`).

---

## Checklist

- [ ] JVM flags set: `-Xms == -Xmx`, `HeapDumpOnOutOfMemoryError`, appropriate GC.
- [ ] HikariCP pool sized via load testing; `leak-detection-threshold` enabled in dev.
- [ ] All caches have `maximumSize` and `expireAfterWrite` configured.
- [ ] `@CacheEvict` applied on every mutation path for cached entities.
- [ ] JPA relationships use `FetchType.LAZY`; N+1 queries verified absent via query logs.
- [ ] Read-only `@Transactional` methods marked `readOnly = true`.
- [ ] Virtual threads enabled for I/O-bound controllers (`spring.threads.virtual.enabled=true`).
- [ ] No `synchronized` blocks on virtual-thread paths.
- [ ] Micrometer metrics exported (GC, heap, HikariCP, cache stats).
- [ ] Load tested with Gatling or k6 before production deployment.
- [ ] Profiled with async-profiler or JFR; no known bottlenecks unaddressed.
- [ ] Database indexes verified for all query patterns via `EXPLAIN ANALYZE`.
