# Microservices Observability

Standards for distributed tracing, metrics, logging correlation, and monitoring
across microservices. The three pillars of observability — logs, metrics, traces —
must work together to diagnose issues in distributed systems.

---

## Defaults

| Concern              | Default Choice                          | Override Requires |
|----------------------|-----------------------------------------|-------------------|
| Tracing Standard     | OpenTelemetry (OTLP)                    | ADR               |
| Trace Backend        | Jaeger or Grafana Tempo                 | ADR               |
| Metrics Format       | Prometheus (OpenMetrics)                | ADR               |
| Metrics Backend      | Prometheus + Grafana                    | ADR               |
| Log Format           | Structured JSON                         | Never             |
| Log Aggregation      | Loki or Elasticsearch                   | ADR               |
| Correlation ID       | W3C Trace Context (`traceparent`)       | Never             |
| Health Checks        | `/healthz` (liveness), `/readyz` (readiness) | Never        |
| Dashboards           | Grafana with per-service dashboards     | ADR               |
| Alerting             | Prometheus Alertmanager                 | ADR               |

### Alternatives

| Primary              | Alternative          | When                                     |
|----------------------|----------------------|------------------------------------------|
| Jaeger               | Grafana Tempo        | Already using Grafana stack               |
| Jaeger               | Zipkin               | Simple setup, lighter footprint           |
| Prometheus           | Datadog / New Relic  | Managed SaaS observability preferred      |
| Loki                 | Elasticsearch        | Full-text search on logs required         |
| Alertmanager         | PagerDuty / OpsGenie | Enterprise incident management needed     |

---

## Distributed Tracing

### Trace Context Propagation

```
┌──────────┐  traceparent  ┌────────────┐  traceparent  ┌──────────┐
│  API GW  │──────────────▶│  Order     │──────────────▶│Inventory │
│          │               │  Service   │               │ Service  │
└──────────┘               └─────┬──────┘               └──────────┘
  span-1                    span-2 │                      span-3
                                   │  traceparent
                                   ▼
                            ┌────────────┐
                            │  Payment   │
                            │  Service   │
                            └────────────┘
                              span-4
```

### OpenTelemetry Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Initialize tracing.
provider = TracerProvider(
    resource=Resource.create({
        "service.name": "order-service",
        "service.version": "1.4.2",
        "deployment.environment": "production",
    })
)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://otel-collector:4317"))
)
trace.set_tracer_provider(provider)

# Auto-instrument frameworks.
FastAPIInstrumentor.instrument()
HTTPXClientInstrumentor().instrument()

# Manual instrumentation for business logic.
tracer = trace.get_tracer("order-service")

async def process_order(order_id: str) -> OrderResult:
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        with tracer.start_as_current_span("validate_order"):
            await validate(order_id)

        with tracer.start_as_current_span("reserve_inventory"):
            await inventory_client.reserve(order_id)

        with tracer.start_as_current_span("charge_payment"):
            result = await payment_client.charge(order_id)

        span.set_attribute("order.status", result.status)
        return result
```

**Rules:**
- Use OpenTelemetry as the instrumentation standard. It is vendor-neutral.
- Auto-instrument HTTP frameworks, HTTP clients, database drivers, and message brokers.
- Add manual spans for significant business operations within a service.
- Propagate W3C `traceparent` header on all outbound HTTP and gRPC calls.
- Include `service.name`, `service.version`, and `deployment.environment` in trace resources.
- Use `BatchSpanProcessor` in production, never `SimpleSpanProcessor` (blocks on export).
- Set span attributes for business context: order IDs, customer IDs, operation results.
- Do not trace health check endpoints — they generate noise without value.

### Span Naming Conventions

| Operation Type    | Naming Pattern            | Example                        |
|-------------------|---------------------------|--------------------------------|
| HTTP server       | `HTTP {method} {route}`   | `HTTP GET /v1/orders/{id}`     |
| HTTP client       | `HTTP {method} {host}`    | `HTTP POST inventory-service`  |
| Database          | `{db.system} {operation}` | `postgresql SELECT`            |
| Message publish   | `{topic} publish`         | `order.created publish`        |
| Message consume   | `{topic} process`         | `order.created process`        |
| Business logic    | `{operation_name}`        | `process_order`                |

---

## Metrics

### RED Method (Request-Driven Services)

```python
from prometheus_client import Counter, Histogram, Gauge

# Rate — requests per second.
request_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status_code"],
)

# Errors — error rate.
request_errors = Counter(
    "http_request_errors_total",
    "Total HTTP request errors",
    ["service", "method", "endpoint", "error_type"],
)

# Duration — latency distribution.
request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["service", "method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# In-flight requests (saturation signal).
requests_in_flight = Gauge(
    "http_requests_in_flight",
    "Currently processing HTTP requests",
    ["service"],
)
```

### USE Method (Resource-Oriented)

```python
# Utilization — how busy the resource is.
connection_pool_usage = Gauge(
    "db_connection_pool_active",
    "Active database connections",
    ["service", "pool_name"],
)

# Saturation — queued work.
connection_pool_pending = Gauge(
    "db_connection_pool_pending",
    "Pending database connection requests",
    ["service", "pool_name"],
)

# Errors — resource errors.
connection_pool_errors = Counter(
    "db_connection_pool_errors_total",
    "Database connection pool errors",
    ["service", "pool_name", "error_type"],
)
```

### Business Metrics

```python
# Domain-specific metrics — what matters to the business.
orders_created = Counter(
    "orders_created_total",
    "Total orders created",
    ["service", "order_type", "currency"],
)

order_value = Histogram(
    "order_value_dollars",
    "Order value distribution in dollars",
    ["service", "order_type"],
    buckets=[10, 25, 50, 100, 250, 500, 1000, 5000],
)

payment_failures = Counter(
    "payment_failures_total",
    "Payment processing failures",
    ["service", "payment_method", "failure_reason"],
)
```

**Rules:**
- Expose a `/metrics` endpoint in Prometheus format on every service.
- Use the RED method for request-driven services: Rate, Errors, Duration.
- Use the USE method for resources: Utilization, Saturation, Errors.
- Add business metrics for domain-significant events (orders, payments, signups).
- Use histograms for latency, not summaries. Histograms are aggregatable across instances.
- Label metrics with `service`, `method`, `endpoint`. Avoid high-cardinality labels
  (no user IDs, request IDs, or timestamps in labels).
- Define histogram buckets based on your SLOs. If your SLO is 200ms, include buckets
  around that threshold.

---

## Structured Logging

### Log Correlation

```python
import structlog
from opentelemetry import trace

def add_trace_context(logger, method_name, event_dict):
    """Inject trace context into every log entry."""
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        add_trace_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

# Every log entry automatically includes trace_id and span_id.
logger.info("order_processed", order_id="ord-123", total=59.98, items=3)
# Output:
# {"event": "order_processed", "order_id": "ord-123", "total": 59.98,
#  "items": 3, "trace_id": "abc123...", "span_id": "def456...",
#  "level": "info", "timestamp": "2026-01-15T10:30:00Z"}
```

**Rules:**
- All logs must be structured JSON in production. Human-readable format in development only.
- Include `trace_id` and `span_id` in every log entry for trace-to-log correlation.
- Use static event names (snake_case) as the first argument. Dynamic data goes in
  keyword arguments. Never use f-strings in log messages.
- Log levels: `debug` for dev diagnostics, `info` for operational events, `warning`
  for recoverable issues, `error` for failures requiring attention.
- Include `service_name` and `environment` as base context in all log entries.
- Never log secrets, tokens, passwords, or full PII. Use redacted identifiers.
- Set a correlation ID (`X-Request-ID`) at the API gateway and propagate it through
  all services via context variables.

---

## Health Checks

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/healthz")
async def liveness():
    """Is the process alive? Only checks that the server can respond."""
    return {"status": "ok"}

@app.get("/readyz")
async def readiness():
    """Can the service handle traffic? Checks dependencies."""
    checks = {
        "database": await check_database(),
        "kafka": await check_kafka_connection(),
        "cache": await check_redis(),
    }
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    return Response(
        content=json.dumps({"status": "ready" if all_healthy else "not_ready", "checks": checks}),
        status_code=status_code,
        media_type="application/json",
    )
```

**Rules:**
- `/healthz` (liveness): checks only that the process is running. No dependency checks.
  If this fails, the orchestrator restarts the container.
- `/readyz` (readiness): checks that all dependencies are reachable. If this fails,
  the service is removed from load balancing until it recovers.
- Never include database queries or external calls in the liveness check.
- Health checks must respond within 1 second. Slow health checks cause false positives.
- Do not trace or log health check requests — they generate noise.

---

## Alerting

### SLO-Based Alerts

```yaml
# Prometheus alerting rules — based on SLOs, not arbitrary thresholds.
groups:
  - name: order-service-slos
    rules:
      # Error rate SLO: 99.9% success rate (0.1% error budget).
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_request_errors_total{service="order-service"}[5m]))
            /
            sum(rate(http_requests_total{service="order-service"}[5m]))
          ) > 0.001
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Order service error rate exceeds 0.1% SLO"
          dashboard: "https://grafana.example.com/d/order-service"

      # Latency SLO: 99% of requests under 500ms.
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket{service="order-service"}[5m])) by (le)
          ) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Order service p99 latency exceeds 500ms SLO"

      # Circuit breaker opened — downstream dependency failure.
      - alert: CircuitBreakerOpen
        expr: circuit_breaker_state{state="open"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Circuit breaker {{ $labels.dependency }} is open"
```

**Rules:**
- Alert on SLO violations (error budget burn rate), not individual request failures.
- Use `for` duration to avoid flapping alerts. At least 5 minutes for warnings.
- Every alert must have a runbook link or dashboard link in annotations.
- Critical alerts page on-call. Warning alerts go to a channel for review.
- Alert on symptoms (high error rate, high latency), not causes (high CPU).
  Cause-based alerts fire too late or not at all.

---

## Do / Don't

### Do
- Use OpenTelemetry as the single instrumentation standard across all services.
- Propagate W3C `traceparent` header on every outbound call (HTTP, gRPC, messaging).
- Include `trace_id` and `span_id` in every structured log entry.
- Use the RED method (Rate, Errors, Duration) for request-driven service metrics.
- Alert on SLO burn rate, not individual failures.
- Add business metrics alongside technical metrics (orders created, payments processed).
- Create a Grafana dashboard for every service showing RED metrics and dependencies.

### Don't
- Use high-cardinality labels in metrics (user IDs, request IDs, timestamps).
- Log unstructured messages in production. Structured JSON only.
- Use `SimpleSpanProcessor` in production — it blocks the request on trace export.
- Alert on causes (CPU, memory) instead of symptoms (error rate, latency).
- Skip tracing internal service calls. A trace with gaps is nearly useless.
- Trace health check endpoints. They add noise without diagnostic value.
- Ignore consumer lag metrics for event-driven services.

---

## Common Pitfalls

1. **Missing trace propagation** — Service A starts a trace but Service B creates a
   new root trace instead of continuing the context. The distributed trace is broken.
   Fix: auto-instrument HTTP clients and verify `traceparent` header propagation.

2. **High-cardinality metric labels** — Using user IDs or request paths with parameters
   as metric labels. Prometheus cardinality explodes, causing OOM.
   Fix: use route templates (`/v1/orders/{id}`) not resolved paths (`/v1/orders/123`).

3. **Log-trace gap** — Logs and traces use different correlation IDs and cannot be
   cross-referenced. Fix: inject `trace_id` from OpenTelemetry into structlog context.

4. **Alert fatigue** — Hundreds of low-value alerts firing constantly. On-call ignores
   them and misses real incidents. Fix: alert only on SLO violations. Delete alerts
   that have never led to action.

5. **Tracing everything** — Tracing every database query and cache lookup at full
   detail. Trace storage costs explode and traces become unreadable.
   Fix: sample traces in production (e.g., 10% sample rate) and always capture error traces.

6. **No dashboards** — Metrics are collected but nobody looks at them. Incidents are
   debugged with `kubectl logs`. Fix: create a standard dashboard template for every
   service showing RED metrics, dependency health, and resource usage.

---

## Checklist

- [ ] OpenTelemetry SDK initialized with `service.name`, `service.version`, `deployment.environment`.
- [ ] Auto-instrumentation enabled for HTTP server, HTTP client, database, and message broker.
- [ ] W3C `traceparent` header propagated on all outbound calls.
- [ ] `trace_id` and `span_id` included in every structured log entry.
- [ ] `/metrics` endpoint exposed in Prometheus format on every service.
- [ ] RED metrics (Rate, Errors, Duration) implemented for all request-handling endpoints.
- [ ] Business metrics defined for domain-significant events.
- [ ] No high-cardinality labels in Prometheus metrics.
- [ ] `/healthz` (liveness) and `/readyz` (readiness) endpoints implemented.
- [ ] SLO-based alerting rules with runbook/dashboard links.
- [ ] Grafana dashboard created for the service with RED metrics and dependency health.
- [ ] Trace sampling configured for production (sample rate + always-on for errors).
