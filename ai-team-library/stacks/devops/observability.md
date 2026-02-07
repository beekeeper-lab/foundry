# Observability

Standards for logging, metrics, tracing, and health checks.
If you cannot observe it, you cannot operate it.

---

## Defaults

- **Telemetry framework:** OpenTelemetry (OTel) for traces, metrics, and logs.
  Single SDK, vendor-neutral.
- **Three pillars:** Logs (what happened), Metrics (how much / how fast),
  Traces (where time was spent across services).
- **Health checks:** Every service exposes `/healthz` (liveness) and `/readyz`
  (readiness) endpoints.
- **Alerting philosophy:** Alert on symptoms (error rate, latency), not causes.
  Dashboards surface causes during investigation.

---

## Do / Don't

- **Do** instrument with OpenTelemetry SDK from day one. Retrofitting is expensive.
- **Do** use structured logging (JSON in production). Every log line includes
  `trace_id`, `service_name`, `environment`.
- **Do** define SLIs (Service Level Indicators) and SLOs (Service Level Objectives)
  for every user-facing service.
- **Do** set up dashboards for the four golden signals: latency, traffic, errors,
  saturation.
- **Do** propagate trace context across service boundaries (W3C Trace Context headers).
- **Don't** log at DEBUG level in production. Use INFO as the baseline.
- **Don't** create alerts that nobody acts on. Every alert must have a runbook link.
- **Don't** rely solely on logs. Logs without traces make distributed debugging
  nearly impossible.
- **Don't** use custom metric names when OTel semantic conventions exist.
- **Don't** sample traces at less than 1% unless volume justifies it. Start at 100%
  and reduce based on cost.

---

## Common Pitfalls

1. **Too many alerts, all ignored.** Alert fatigue is worse than no alerts. Solution:
   start with three alerts per service (error rate, p99 latency, availability).
   Add more only when there is an incident that would have been caught earlier.
2. **Logs but no correlation.** Thousands of log lines with no way to connect them
   to a single request. Solution: inject `trace_id` into every log entry via OTel
   context propagation.
3. **Metrics cardinality explosion.** Adding `user_id` as a metric label creates
   millions of time series. Solution: high-cardinality data belongs in traces,
   not metrics. Keep metric labels low-cardinality (environment, region, status_code).
4. **No baseline.** The team cannot tell if current latency is normal or degraded
   because there is no historical baseline. Solution: establish SLOs in the first
   sprint. Compare current performance against them.
5. **Health checks that always return 200.** The endpoint exists but checks nothing.
   Solution: readiness checks verify downstream dependencies (database, cache,
   critical APIs).

---

## OpenTelemetry Setup

```python
# otel_setup.py -- Initialize OpenTelemetry for a Python service
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

def init_telemetry(service_name: str, environment: str) -> None:
    """Initialize OTel tracing and metrics with OTLP export."""
    resource = Resource.create({
        "service.name": service_name,
        "deployment.environment": environment,
    })

    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    # Metrics
    reader = PeriodicExportingMetricReader(OTLPMetricExporter())
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
```

---

## Health Check Endpoints

```python
# health.py -- Liveness and readiness probes
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/healthz")
def liveness():
    """Liveness: is the process alive and not deadlocked?"""
    return {"status": "ok"}

@app.get("/readyz")
async def readiness():
    """Readiness: can this instance serve traffic?"""
    checks = {
        "database": await check_db_connection(),
        "cache": await check_redis_connection(),
    }
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    return Response(
        content=json.dumps({"status": "ready" if all_healthy else "not_ready", "checks": checks}),
        status_code=status_code,
        media_type="application/json",
    )
```

---

## SLO Definition Template

| Signal       | SLI                                     | SLO Target | Window  |
|-------------|------------------------------------------|------------|---------|
| Availability | % of requests returning non-5xx          | 99.9%      | 30 days |
| Latency      | % of requests completing under 300ms     | 95%        | 30 days |
| Error rate   | % of requests returning 5xx              | < 0.1%     | 30 days |

Burn-rate alerts: alert when the error budget is being consumed 10x faster than
sustainable over the SLO window.

---

## Alternatives

| Tool              | When to consider                                  |
|-------------------|---------------------------------------------------|
| Datadog           | Fully managed, unified logs/metrics/traces        |
| Grafana + Loki    | Open-source stack, cost-effective at scale        |
| Prometheus        | Kubernetes-native metrics, pull-based model       |
| Jaeger            | Open-source distributed tracing                   |
| Honeycomb         | High-cardinality observability, event-based model |

---

## Checklist

- [ ] OpenTelemetry SDK is initialized for traces, metrics, and logs
- [ ] Every service exports telemetry to an OTLP-compatible collector
- [ ] Structured JSON logging includes `trace_id`, `service_name`, `environment`
- [ ] `/healthz` and `/readyz` endpoints are implemented and wired to orchestrator probes
- [ ] Four golden signals dashboard exists for every user-facing service
- [ ] SLIs and SLOs are defined and visible to the team
- [ ] Alerts fire on symptom thresholds, not arbitrary static values
- [ ] Every alert links to a runbook with triage steps
- [ ] Trace context propagates across all service-to-service calls
- [ ] Metric labels are low-cardinality (no user IDs, request IDs, etc.)
- [ ] Log retention policy is defined (30 days hot, 90 days warm, 1 year cold)
