# GCP Architecture Framework

Operational standards aligned to the pillars of the Google Cloud Architecture Framework.
Every workload must pass an architecture review before production launch.

---

## Defaults

| Pillar | Default Approach | Alternatives |
|--------|-----------------|-------------|
| **Operational Excellence** | Cloud Monitoring dashboards + alerting policies + runbooks | Datadog, Grafana Cloud |
| **Security** | IAM least-privilege + encryption everywhere + Security Command Center | Third-party SIEM, CrowdStrike |
| **Reliability** | Multi-zone + auto-scaling + health checks | Multi-region active-active (critical workloads) |
| **Performance Optimization** | Right-sized Cloud Run/GKE + caching layer | Autoscaling with custom metrics, CDN for static |
| **Cost Optimization** | Committed Use Discounts + labeling + billing budgets | Spot VMs (fault-tolerant), Autoscaler to zero |
| **Sustainability** | Right-size resources + serverless + managed services | Carbon-aware scheduling, low-carbon regions |

---

## Operational Excellence

### Observability

- **Metrics:** Cloud Monitoring custom metrics for business KPIs (orders/min, error rate).
  Infrastructure metrics collected automatically via the Ops Agent or built-in integrations.
- **Logs:** Structured JSON logs shipped to Cloud Logging. Set retention to 30 days
  for non-production, 90 days for production. Route to Cloud Storage or BigQuery for long-term.
- **Traces:** Cloud Trace for distributed tracing. Instrument all service-to-service calls
  with OpenTelemetry.
- **Dashboards:** One dashboard per service showing golden signals (latency, traffic,
  errors, saturation).

### Alerting Policies

```yaml
# Terraform: Cloud Monitoring alert for Cloud Run error rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate - my-service"
  combiner     = "OR"

  conditions {
    display_name = "5xx error rate > 1%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0.01
      duration        = "300s"
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.pagerduty.id]
}
```

### Runbooks

- Every alert links to a runbook in the team wiki.
- Runbooks include: symptom, likely causes, diagnostic steps, remediation steps, escalation path.
- Review runbooks quarterly. Delete runbooks for retired alerts.

---

## Security

### Defense in Depth

```
Organization boundary (Organization Policies)
  └── VPC Service Controls (data perimeter)
       └── VPC boundary (firewall rules, Flow Logs)
            └── Subnet boundary (Private Google Access)
                 └── Workload boundary (service accounts, IAM)
                      └── Data boundary (CMEK, DLP, policy tags)
```

### Key Services

| Service | Purpose |
|---------|---------|
| Security Command Center | Aggregated security findings, vulnerability scanning, threat detection |
| Cloud Armor | DDoS protection and WAF for Cloud Load Balancing |
| Cloud IAM | Identity and access management for all GCP resources |
| VPC Service Controls | Data exfiltration prevention perimeters |
| Cloud DLP | Sensitive data discovery and de-identification |
| Cloud Audit Logs | API audit log for all GCP project activity |
| Cloud KMS | Managed encryption key creation and rotation |
| Binary Authorization | Deploy-time attestation for container images |
| Chronicle | SIEM and threat intelligence platform |

### Encryption Standards

- **At rest:** All GCP storage services encrypt data at rest by default with
  Google-managed keys. Use Customer-Managed Encryption Keys (CMEK) via Cloud KMS
  for regulated workloads requiring key rotation control.
- **In transit:** TLS 1.2+ for all external connections. Internal traffic between
  GCP services uses Google's ALTS (Application Layer Transport Security).
- **Key rotation:** Enable automatic key rotation for Cloud KMS keys (90 days recommended).

---

## Reliability

### Multi-Zone Architecture

- Deploy across **3 zones** minimum within a region for production workloads.
- Use **health checks** at load balancer, GKE, and application levels.
- Configure **auto-scaling** with target utilization (Cloud Run: 60% concurrency,
  GKE HPA: 70% CPU).
- Set **connection draining timeout** on load balancer backends to allow in-flight
  requests to complete (30s).

### Failure Isolation

- Use **circuit breakers** for external service calls (Istio/Envoy on GKE, or application-level).
- Implement **retry with exponential backoff and jitter** for transient failures.
- Design for **graceful degradation** — serve cached content when a dependency is down.
- **Chaos engineering:** Use Chaos Toolkit or Litmus to test failover procedures.

### Backup & Recovery

| Tier | RPO | RTO | Strategy |
|------|-----|-----|----------|
| Critical (payments, auth) | <1 hour | <15 min | Multi-zone + cross-region read replica |
| Standard (API, web) | <4 hours | <1 hour | Multi-zone + automated backups |
| Non-critical (batch, reports) | <24 hours | <4 hours | Single-zone + daily backups |

---

## Performance Optimization

### Right-Sizing

- Start with the smallest viable Cloud Run allocation or GKE pod request. Scale based on metrics.
- Use **Active Assist Recommender** for right-sizing Compute Engine, GKE, and Cloud SQL.
- Review right-sizing monthly during cost review.

### Caching Strategy

| Layer | Service | TTL |
|-------|---------|-----|
| CDN | Cloud CDN | Static assets: 1 year. API: 0 (pass-through) |
| Application | Memorystore Redis | Session: 30 min. Reference data: 1 hour |
| Database | Cloud SQL read replicas | N/A (eventual consistency acceptable for reads) |

### Performance Testing

- Load test before every major release with realistic traffic patterns.
- Establish baseline latency (p50, p95, p99) and alert on regression.
- Use Cloud Trace spans to identify bottlenecks in the critical path.

---

## Cost Optimization

### Visibility

- **Labeling:** Every resource labeled with `cost-center`, `environment`, `team`, `service`.
  Enforce with organization policy constraints.
- **Billing Export:** Export billing data to BigQuery for custom reporting and analysis.
- **Budgets:** Set monthly budgets with alerts at 50%, 80%, 100%, and 120%.
- **Recommender:** Review Active Assist cost recommendations weekly.

### Savings Strategies

| Strategy | Savings | Commitment |
|----------|---------|-----------|
| Committed Use Discounts (CUDs) | 20–57% | 1 or 3 year |
| Spot VMs (GKE, Dataproc) | 60–91% | None (can be preempted) |
| Cloud Run min instances = 0 | Variable | None (pay per request) |
| BigQuery flat-rate / editions | 20–50% | Flex (hourly) to 3-year |
| Cloud Storage lifecycle rules | 10–40% | None |

### Waste Elimination

- Delete unused persistent disks, unattached static IPs, and idle load balancers.
- Stop non-production resources outside business hours (Cloud Scheduler + Cloud Functions).
- Use Cloud Storage lifecycle policies to transition infrequently accessed data to cheaper tiers.
- Review and shut down idle Cloud SQL instances ($50–200+/month even with no traffic).
- Use BigQuery slot monitoring to identify over-provisioned reservations.

---

## Do / Don't

- **Do** run a Google Cloud Architecture Framework review before production launch.
- **Do** implement all pillars, not just security and reliability.
- **Do** schedule quarterly reviews to assess architecture against new best practices.
- **Do** use managed services over self-managed infrastructure where possible.
- **Do** automate scaling, patching, and backup processes.
- **Don't** treat the Architecture Framework as a one-time checklist. It is ongoing.
- **Don't** ignore cost optimization — GCP bills grow silently without active management.
- **Don't** skip disaster recovery testing. Untested backups are not backups.
- **Don't** over-provision "just in case." Use auto-scaling and right-sizing instead.

---

## Common Pitfalls

1. **No observability until production incident.** Teams deploy without dashboards,
   alerts, or traces, then scramble during outages. Solution: observability is a
   launch requirement, not a post-launch enhancement.
2. **Ignoring cost until the bill arrives.** An idle Cloud SQL instance, oversized
   GKE cluster, or unpartitioned BigQuery table bleeds money. Solution: weekly cost
   review with billing export to BigQuery and automated recommendations.
3. **Single-region deployment for global users.** Users far from the region experience
   high latency. Solution: use Cloud CDN for static content, consider multi-region
   for latency-sensitive APIs.
4. **No capacity planning.** Auto-scaling is configured but maximum limits are set
   too low or scaling policies react too slowly. Solution: load test with 2x expected
   peak traffic and verify scaling behavior.
5. **Compliance drift.** Resources are compliant at launch but drift over time.
   Solution: Security Command Center with Security Health Analytics for continuous
   compliance monitoring. Use organization policies for preventive controls.

---

## Checklist

- [ ] Google Cloud Architecture Framework review completed
- [ ] Cloud Monitoring dashboards with golden signals for every service
- [ ] Alerting policies configured with notification channels and linked runbooks
- [ ] Cloud Trace enabled for distributed service calls with OpenTelemetry
- [ ] Security Command Center enabled with Security Health Analytics
- [ ] Encryption at rest (CMEK where required) and in transit for all data
- [ ] Multi-zone deployment with health checks and auto-scaling
- [ ] Backup strategy defined with RPO/RTO per service tier
- [ ] DR drills scheduled quarterly with documented results
- [ ] Cost labeling enforced via organization policies
- [ ] Billing budgets set with alerts at 50%, 80%, 100% thresholds
- [ ] Committed Use Discounts evaluated for steady-state workloads
- [ ] Active Assist recommendations reviewed monthly
- [ ] Non-production resources scheduled to stop outside business hours
