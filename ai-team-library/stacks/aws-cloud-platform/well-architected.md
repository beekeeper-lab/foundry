# AWS Well-Architected Framework

Operational standards aligned to the six pillars of the AWS Well-Architected Framework.
Every workload must pass a Well-Architected Review before production launch.

---

## Defaults

| Pillar | Default Approach | Alternatives |
|--------|-----------------|-------------|
| **Operational Excellence** | CloudWatch dashboards + alarms + runbooks | Datadog, Grafana Cloud |
| **Security** | IAM least-privilege + encryption everywhere + GuardDuty | Third-party SIEM, CrowdStrike |
| **Reliability** | Multi-AZ + auto-scaling + health checks | Multi-region active-active (critical workloads) |
| **Performance Efficiency** | Right-sized Fargate tasks + caching layer | Graviton instances (cost/perf), Lambda (burst) |
| **Cost Optimization** | Reserved capacity + Savings Plans + tagging | Spot instances (fault-tolerant), S3 Intelligent-Tiering |
| **Sustainability** | Right-size resources + Graviton + managed services | Serverless-first, auto-scale to zero |

---

## Operational Excellence

### Observability

- **Metrics:** CloudWatch custom metrics for business KPIs (orders/min, error rate).
  Infrastructure metrics (CPU, memory, disk) collected automatically.
- **Logs:** Structured JSON logs shipped to CloudWatch Logs. Set retention to 30 days
  for non-production, 90 days for production. Archive to S3 for long-term.
- **Traces:** AWS X-Ray for distributed tracing. Instrument all service-to-service calls.
- **Dashboards:** One dashboard per service showing golden signals (latency, traffic,
  errors, saturation).

### Alarms

```yaml
# CloudWatch alarm for API error rate
Type: AWS::CloudWatch::Alarm
Properties:
  AlarmName: HighApiErrorRate
  MetricName: 5XXError
  Namespace: AWS/ApplicationELB
  Statistic: Sum
  Period: 300
  EvaluationPeriods: 2
  Threshold: 10
  ComparisonOperator: GreaterThanThreshold
  AlarmActions:
    - !Ref AlertSNSTopic
```

### Runbooks

- Every alarm links to a runbook in the team wiki.
- Runbooks include: symptom, likely causes, diagnostic steps, remediation steps, escalation path.
- Review runbooks quarterly. Delete runbooks for retired alarms.

---

## Security

### Defense in Depth

```
Account boundary (SCPs)
  └── VPC boundary (NACLs, Flow Logs)
       └── Subnet boundary (route tables)
            └── Instance boundary (security groups)
                 └── Application boundary (IAM roles, encryption)
                      └── Data boundary (KMS, S3 policies)
```

### Key Services

| Service | Purpose |
|---------|---------|
| GuardDuty | Threat detection — anomalous API calls, compromised credentials |
| Security Hub | Aggregated security findings, compliance checks |
| Config | Resource configuration compliance and drift detection |
| Inspector | Vulnerability scanning for EC2, ECR images, Lambda |
| Macie | S3 sensitive data discovery (PII, credentials) |
| CloudTrail | API audit log for all AWS account activity |
| KMS | Managed encryption key creation and rotation |
| WAF | Web application firewall for CloudFront and ALB |

### Encryption Standards

- **At rest:** All storage services (S3, RDS, EBS, EFS) encrypted with KMS.
  Use AWS-managed keys for standard workloads. Customer-managed keys (CMK) for
  regulated workloads requiring key rotation control.
- **In transit:** TLS 1.2+ for all connections. Enforce via security policies on
  ALB, CloudFront, and API Gateway.
- **Key rotation:** Enable automatic key rotation for KMS CMKs (annual).

---

## Reliability

### Multi-AZ Architecture

- Deploy across **3 Availability Zones** minimum.
- Use **health checks** at ALB, ECS, and application levels.
- Configure **auto-scaling** with target tracking (CPU 60%, request count per target).
- Set **deregistration delay** on ALB to allow in-flight requests to complete (30s).

### Failure Isolation

- Use **circuit breakers** for external service calls.
- Implement **retry with exponential backoff and jitter** for transient failures.
- Design for **graceful degradation** — serve cached content when a dependency is down.
- **Chaos engineering:** Run GameDay exercises to test failover procedures.

### Backup & Recovery

| Tier | RPO | RTO | Strategy |
|------|-----|-----|----------|
| Critical (payments, auth) | <1 hour | <15 min | Multi-AZ + cross-region read replica |
| Standard (API, web) | <4 hours | <1 hour | Multi-AZ + automated snapshots |
| Non-critical (batch, reports) | <24 hours | <4 hours | Single-AZ + daily snapshots |

---

## Performance Efficiency

### Right-Sizing

- Start with the smallest viable instance/task size. Scale up based on metrics.
- Use **Compute Optimizer** recommendations for EC2, ECS, and Lambda.
- Review right-sizing monthly during cost review.

### Caching Strategy

| Layer | Service | TTL |
|-------|---------|-----|
| CDN | CloudFront | Static assets: 1 year. API: 0 (pass-through) |
| Application | ElastiCache Redis | Session: 30 min. Reference data: 1 hour |
| Database | RDS read replicas | N/A (eventual consistency acceptable for reads) |

### Performance Testing

- Load test before every major release with realistic traffic patterns.
- Establish baseline latency (p50, p95, p99) and alert on regression.
- Use X-Ray traces to identify bottlenecks in the critical path.

---

## Cost Optimization

### Visibility

- **Tagging:** Every resource tagged with `CostCenter`, `Environment`, `Team`, `Service`.
  Enforce with tag policies in AWS Organizations.
- **Cost Explorer:** Review weekly. Track cost by service, account, and tag.
- **Budgets:** Set monthly budgets with alerts at 50%, 80%, 100%, and 120%.
- **Anomaly Detection:** Enable Cost Anomaly Detection for unexpected spikes.

### Savings Strategies

| Strategy | Savings | Commitment |
|----------|---------|-----------|
| Savings Plans (Compute) | 20–40% | 1 or 3 year |
| Reserved Instances | 30–60% | 1 or 3 year |
| Spot Instances | 60–90% | None (can be interrupted) |
| Graviton (ARM) | 20–40% | None |
| S3 Intelligent-Tiering | 10–40% | None |

### Waste Elimination

- Delete unused EBS volumes, unattached Elastic IPs, and idle load balancers.
- Stop non-production resources outside business hours (Lambda scheduler or Instance Scheduler).
- Use S3 lifecycle policies to transition infrequently accessed data to cheaper tiers.
- Review and terminate unused NAT Gateways ($32/month each even with no traffic).

---

## Do / Don't

- **Do** run a Well-Architected Review (AWS Well-Architected Tool) before production launch.
- **Do** implement all six pillars, not just security and reliability.
- **Do** schedule quarterly reviews to assess architecture against new best practices.
- **Do** use managed services over self-managed infrastructure where possible.
- **Do** automate scaling, patching, and backup processes.
- **Don't** treat the Well-Architected Framework as a one-time checklist. It is ongoing.
- **Don't** ignore cost optimization — AWS bills grow silently without active management.
- **Don't** skip disaster recovery testing. Untested backups are not backups.
- **Don't** over-provision "just in case." Use auto-scaling and right-sizing instead.

---

## Common Pitfalls

1. **No observability until production incident.** Teams deploy without dashboards,
   alarms, or traces, then scramble during outages. Solution: observability is a
   launch requirement, not a post-launch enhancement.
2. **Ignoring cost until the bill arrives.** A forgotten NAT Gateway, oversized
   RDS instance, or unused EBS volume bleeds money. Solution: weekly cost review
   and automated waste detection.
3. **Single-region deployment for global users.** Users in Asia experience 200ms+
   latency to us-east-1. Solution: use CloudFront for static content, consider
   multi-region for latency-sensitive APIs.
4. **No capacity planning.** Auto-scaling is configured but maximum limits are set
   too low or scaling policies react too slowly. Solution: load test with 2x expected
   peak traffic and verify scaling behavior.
5. **Compliance drift.** Resources are compliant at launch but drift over time.
   Solution: AWS Config rules with auto-remediation for critical compliance checks.

---

## Checklist

- [ ] Well-Architected Review completed using AWS Well-Architected Tool
- [ ] CloudWatch dashboards with golden signals for every service
- [ ] Alarms configured with SNS notifications and linked runbooks
- [ ] X-Ray tracing enabled for distributed service calls
- [ ] GuardDuty, Security Hub, and Config enabled in all accounts
- [ ] Encryption at rest and in transit for all data stores and connections
- [ ] Multi-AZ deployment with health checks and auto-scaling
- [ ] Backup strategy defined with RPO/RTO per service tier
- [ ] DR drills scheduled quarterly with documented results
- [ ] Cost tagging enforced via AWS Organizations tag policies
- [ ] AWS Budgets set with alerts at 50%, 80%, 100% thresholds
- [ ] Savings Plans or Reserved Instances evaluated for steady-state workloads
- [ ] Compute Optimizer recommendations reviewed monthly
- [ ] Non-production resources scheduled to stop outside business hours
