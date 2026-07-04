# Spring Boot Observability

Actuator, Micrometer, and logging conventions for production Boot services.
Baseline log formatting/level rules live in the `java` pack; this file covers
the Spring-specific wiring. The goal: every service answers "is it healthy,
what is it doing, and why is this request slow" without code changes at 2am.

---

## 1. Actuator Hygiene

Actuator is mandatory — and locked down. Its endpoints leak configuration,
environment, and heap data if exposed carelessly.

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, prometheus   # explicit allowlist, never "*"
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
  server:
    port: 8081        # management traffic off the app port
```

**Rules:**
- Expose an explicit allowlist. `include: "*"` is forbidden; `env`,
  `heapdump`, `threaddump`, and `configprops` never ship exposed in prod.
- Serve management on a separate port reachable only inside the
  cluster/network; keep it off the public ingress.
- Use the Kubernetes probe groups: `/actuator/health/liveness` and
  `/actuator/health/readiness`. Liveness must not include downstream
  dependencies — a flapping database should fail readiness (stop traffic),
  not liveness (restart loop).
- Custom `HealthIndicator`s for each critical dependency; assign them to the
  readiness group deliberately.
- Populate `info` from build metadata (`springBoot { buildInfo() }` in
  Gradle) so `/actuator/info` reports version and commit.

---

## 2. Metrics with Micrometer

Micrometer is the metrics facade; the backend (Prometheus by default) is a
dependency choice, not a code change.

- Boot auto-instruments HTTP server/client requests, JVM, datasource pools,
  and caches. Do not hand-roll what auto-config provides.
- Custom business metrics go through an injected `MeterRegistry`:

```java
orderCounter = Counter.builder("orders.placed")
    .tag("channel", channel)
    .register(registry);
```

- Naming: dot-separated lowercase (`orders.placed`); Micrometer maps to each
  backend's convention. Units in the name only where conventional
  (`.seconds`, `.bytes`).
- **Bound tag cardinality.** Tags are for low-cardinality dimensions (status,
  channel, outcome). Never tag with user IDs, order IDs, or raw URIs — each
  distinct value is a new time series and will take the metrics backend down.
- Use `@Timed`/`Timer` for latency-sensitive operations; prefer percentiles
  (histogram buckets) over averages when alerting.
- Define common tags once (application, region, instance) via
  `management.metrics.tags.*`, not per-meter.

---

## 3. Tracing

- Use Micrometer Tracing (the Boot 3 successor to Sleuth) with an OTLP or
  Zipkin exporter. Trace/span IDs propagate across `RestClient`/`WebClient`
  calls and into logs automatically once the bridge is on the classpath.
- Set a sane sampling probability in prod (e.g. 0.1); 1.0 is for dev only.
- Propagate context to async work: virtual-thread executors and
  `@Async` pools need context propagation configured, or traces break at
  every thread hop.

---

## 4. Structured Logging

- Boot 3.4+ has native structured logging:
  `logging.structured.format.console: ecs` (or `logstash`) — prefer it over
  hand-configured encoder XML. JSON in prod, human-readable in dev, per the
  `java` pack.
- Trace correlation: with tracing on the classpath, Boot injects
  `traceId`/`spanId` into the MDC and the default log pattern. Every log line
  in prod must carry the trace ID.
- Add request-scoped context (tenant, principal) to the MDC in one filter;
  clear it in `finally`. Do not pass context by string-concatenating it into
  messages.
- Log levels are runtime-adjustable via the (internal-only) `loggers`
  actuator endpoint — prefer that to redeploying for a debug session.

---

## 5. Alert on the Golden Signals

Dashboards and alerts belong to the service, versioned with it:

- **Traffic / errors:** `http.server.requests` rate split by `status` and
  `outcome`; alert on 5xx ratio, not absolute counts.
- **Latency:** p95/p99 from the same timer's histogram.
- **Saturation:** datasource pool usage (`hikaricp.connections.*`), JVM
  memory, executor queue depth.
- Every alert page links to a runbook; an alert without a documented response
  is noise.

---

## Checklist

- [ ] Actuator exposure is an explicit allowlist; management on a separate, internal port.
- [ ] Liveness and readiness probes split; downstream deps only in readiness.
- [ ] Prometheus (or chosen backend) registry wired; common tags set globally.
- [ ] Custom metrics named `lowercase.dotted`; no unbounded tag cardinality.
- [ ] Micrometer Tracing configured with sampling < 1.0 in prod.
- [ ] Structured JSON logs in prod with traceId/spanId on every line.
- [ ] MDC enrichment via a single filter with guaranteed cleanup.
- [ ] Alerts defined on error ratio, latency percentiles, and pool saturation, each with a runbook.
