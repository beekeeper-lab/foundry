# Azure Well-Architected Framework

Operational standards aligned to the five pillars of the Azure Well-Architected Framework.
Every workload must pass a Well-Architected Review before production launch.

---

## Defaults

| Pillar | Default Approach | Alternatives |
|--------|-----------------|-------------|
| **Reliability** | Zone-redundant deployments + auto-scaling + health probes | Multi-region active-active (critical workloads) |
| **Security** | Entra ID RBAC + encryption everywhere + Defender for Cloud | Third-party SIEM (Splunk, Sentinel SOAR) |
| **Cost Optimization** | Azure Reservations + auto-scale + tagging | Spot VMs (fault-tolerant), dev/test pricing |
| **Operational Excellence** | Azure Monitor + Log Analytics + workbooks + alerts | Datadog, Grafana Cloud, New Relic |
| **Performance Efficiency** | Right-sized resources + caching + CDN | Arm-based VMs (Ampere), serverless-first |

---

## Reliability

### Zone-Redundant Architecture

- Deploy across **3 Availability Zones** minimum for production workloads.
- Use **zone-redundant** SKUs: App Service Premium v3, AKS with zone-spread,
  Cosmos DB with zone redundancy, Storage ZRS.
- Configure **health probes** at Application Gateway, Load Balancer, and application levels.
- Set **auto-scaling rules** with target-based scaling (CPU 60%, request queue depth).

### Failure Isolation

- Use **circuit breakers** for external service calls (Polly for .NET, resilience4j for Java).
- Implement **retry with exponential backoff and jitter** for transient failures.
- Design for **graceful degradation** — serve cached content when a dependency is down.
- **Chaos engineering:** Use Azure Chaos Studio to inject faults and test resilience.

### Backup & Recovery

| Tier | RPO | RTO | Strategy |
|------|-----|-----|----------|
| Critical (payments, auth) | <1 hour | <15 min | Multi-region + Cosmos DB multi-write |
| Standard (API, web) | <4 hours | <1 hour | Zone-redundant + automated snapshots |
| Non-critical (batch, reports) | <24 hours | <4 hours | LRS + daily snapshots |

### Disaster Recovery

- **Azure Site Recovery** for VM-based workloads (replication to secondary region).
- **Cosmos DB automatic failover** with multi-region writes for globally distributed data.
- **Azure Front Door** for global load balancing with automatic failover between regions.
- **Recovery drills:** Schedule quarterly and document results. Untested recovery is not recovery.

---

## Security

### Defense in Depth

```
Management Group boundary (Azure Policy)
  └── Subscription boundary (RBAC, Defender for Cloud)
       └── Resource Group boundary (RBAC, locks)
            └── VNet boundary (NSGs, Private Endpoints)
                 └── Service boundary (Managed Identity, encryption)
                      └── Data boundary (Key Vault, Cosmos DB RBAC)
```

### Key Services

| Service | Purpose |
|---------|---------|
| Microsoft Defender for Cloud | Unified security posture management and threat protection |
| Microsoft Sentinel | Cloud-native SIEM and SOAR for security analytics |
| Azure Policy | Resource governance, compliance enforcement, auto-remediation |
| Azure Key Vault | Secrets, certificates, and encryption key management |
| Azure DDoS Protection | Network-level DDoS mitigation for public endpoints |
| Microsoft Entra ID Protection | Identity risk detection and conditional access |
| Azure Firewall | Centralized network security with threat intelligence filtering |
| Web Application Firewall (WAF) | OWASP protection on Application Gateway and Front Door |

### Encryption Standards

- **At rest:** All storage services (Blob, Cosmos DB, SQL, Disks) encrypted with
  platform-managed keys by default. Customer-managed keys (CMK) in Key Vault for
  regulated workloads requiring key rotation control.
- **In transit:** TLS 1.2+ for all connections. Enforce via App Service minimum TLS
  version, Application Gateway SSL policy, and Cosmos DB settings.
- **Key rotation:** Enable automatic key rotation in Key Vault. Rotation policy
  configurable per key (30, 60, 90 days).

### Identity Security

- **Conditional Access policies:** Require MFA for all users, block legacy authentication,
  require compliant devices for privileged access.
- **Privileged Identity Management (PIM):** Just-in-time role activation for privileged
  roles. Time-limited assignments with approval workflows.
- **Access Reviews:** Quarterly review of role assignments. Auto-remove stale access.

---

## Cost Optimization

### Visibility

- **Tagging:** Every resource tagged with `CostCenter`, `Environment`, `Team`, `Service`.
  Enforce with Azure Policy tag inheritance and required tags.
- **Cost Management:** Review weekly in Azure Cost Management. Track cost by resource group,
  subscription, and tag. Export cost data to Log Analytics for custom reporting.
- **Budgets:** Set monthly budgets with alerts at 50%, 80%, 100%, and 120%.
- **Anomaly alerts:** Enable cost anomaly detection for unexpected spending spikes.

### Savings Strategies

| Strategy | Savings | Commitment |
|----------|---------|-----------|
| Azure Reservations (Compute) | 20–40% | 1 or 3 year |
| Azure Savings Plans | 15–30% | 1 or 3 year |
| Spot VMs | 60–90% | None (can be evicted) |
| Arm-based VMs (Ampere Altra) | 20–40% | None |
| Dev/Test pricing | 40–60% | MSDN subscription |
| Cosmos DB reserved capacity | 20–65% | 1 or 3 year |

### Waste Elimination

- Delete orphaned disks, unattached public IPs, and empty resource groups.
- Stop non-production resources outside business hours (Azure Automation, Start/Stop VMs).
- Use Blob Storage lifecycle management to transition infrequently accessed data to Cool/Archive.
- Review and downgrade over-provisioned App Service plans and AKS node pools.
- Use Azure Advisor cost recommendations to identify idle and right-sizing opportunities.

---

## Operational Excellence

### Observability

- **Metrics:** Azure Monitor metrics for infrastructure (CPU, memory, requests).
  Custom metrics for business KPIs (orders/min, error rate) via Application Insights.
- **Logs:** Structured logs shipped to Log Analytics workspace. Set retention to 30 days
  for non-production, 90 days for production. Archive to Storage for long-term.
- **Traces:** Application Insights distributed tracing. Instrument all service-to-service calls
  with correlation IDs via the Application Insights SDK or OpenTelemetry.
- **Dashboards:** Azure Workbooks or Grafana dashboards showing golden signals (latency,
  traffic, errors, saturation) per service.

### Alerts

```json
{
  "type": "Microsoft.Insights/metricAlerts",
  "properties": {
    "description": "High API error rate",
    "severity": 2,
    "enabled": true,
    "evaluationFrequency": "PT5M",
    "windowSize": "PT15M",
    "criteria": {
      "odata.type": "Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria",
      "allOf": [
        {
          "name": "HighErrorRate",
          "metricName": "Http5xx",
          "metricNamespace": "Microsoft.Web/sites",
          "operator": "GreaterThan",
          "threshold": 10,
          "timeAggregation": "Total"
        }
      ]
    },
    "actions": [
      { "actionGroupId": "/subscriptions/{sub}/resourceGroups/{rg}/providers/microsoft.insights/actionGroups/ops-team" }
    ]
  }
}
```

### Runbooks

- Every alert links to a runbook in the team wiki or Azure Automation.
- Runbooks include: symptom, likely causes, diagnostic steps, remediation steps, escalation path.
- Review runbooks quarterly. Delete runbooks for retired alerts.

### Deployment Practices

- **Infrastructure as Code:** Bicep or Terraform for all resource provisioning.
  No manual portal deployments in staging or production.
- **CI/CD:** Azure DevOps Pipelines or GitHub Actions with environment approvals.
- **Deployment slots:** Use App Service slots for zero-downtime deployments.
- **Feature flags:** Use Azure App Configuration feature management for gradual rollouts.

---

## Performance Efficiency

### Right-Sizing

- Start with the smallest viable SKU. Scale up based on metrics, not estimates.
- Use **Azure Advisor** performance recommendations for VMs, App Service, and databases.
- Review right-sizing monthly during cost and performance review.
- Use **Arm-based VMs (Dpsv5/Dplsv5)** for better price-performance on compatible workloads.

### Caching Strategy

| Layer | Service | TTL |
|-------|---------|-----|
| CDN | Azure Front Door / CDN | Static assets: 1 year. API: 0 (pass-through) |
| Application | Azure Cache for Redis | Session: 30 min. Reference data: 1 hour |
| Database | Cosmos DB integrated cache | Read-heavy queries: 5 min (configurable) |

### Performance Testing

- Load test before every major release with Azure Load Testing (managed JMeter).
- Establish baseline latency (p50, p95, p99) and alert on regression.
- Use Application Insights performance profiler to identify bottlenecks.
- Monitor Cosmos DB RU consumption per partition to detect hot partitions early.

---

## Do / Don't

- **Do** run a Well-Architected Review (Azure Well-Architected Review tool) before production.
- **Do** implement all five pillars, not just security and reliability.
- **Do** schedule quarterly reviews to assess architecture against new best practices.
- **Do** use managed services (PaaS/serverless) over self-managed infrastructure where possible.
- **Do** automate scaling, patching, and backup processes.
- **Don't** treat the Well-Architected Framework as a one-time checklist. It is ongoing.
- **Don't** ignore cost optimization — Azure bills grow silently without active management.
- **Don't** skip disaster recovery testing. Untested backups are not backups.
- **Don't** over-provision "just in case." Use auto-scaling and right-sizing instead.

---

## Common Pitfalls

1. **No observability until production incident.** Teams deploy without dashboards,
   alerts, or traces, then scramble during outages. Solution: observability is a
   launch requirement, not a post-launch enhancement.
2. **Ignoring cost until the bill arrives.** Forgotten premium-tier services, idle
   AKS nodes, or orphaned disks bleed money. Solution: weekly cost review
   and Azure Advisor waste recommendations.
3. **Single-region deployment for global users.** Users in Asia experience 200ms+
   latency to East US. Solution: use Azure Front Door for static content, consider
   multi-region with Cosmos DB multi-write for latency-sensitive workloads.
4. **No capacity planning.** Auto-scaling is configured but maximum limits are set
   too low or scaling rules react too slowly. Solution: load test with 2x expected
   peak traffic using Azure Load Testing and verify scaling behavior.
5. **Compliance drift.** Resources are compliant at launch but drift over time.
   Solution: Azure Policy with deny and audit effects plus auto-remediation tasks.

---

## Checklist

- [ ] Well-Architected Review completed using Azure Well-Architected Review tool
- [ ] Azure Monitor dashboards with golden signals for every service
- [ ] Metric alerts configured with action groups and linked runbooks
- [ ] Application Insights distributed tracing enabled for all services
- [ ] Microsoft Defender for Cloud enabled across all subscriptions
- [ ] Encryption at rest and in transit for all data stores and connections
- [ ] Zone-redundant deployment with health probes and auto-scaling
- [ ] Backup strategy defined with RPO/RTO per service tier
- [ ] DR drills scheduled quarterly with documented results
- [ ] Cost tagging enforced via Azure Policy tag inheritance
- [ ] Azure Cost Management budgets set with alerts at 50%, 80%, 100% thresholds
- [ ] Azure Reservations or Savings Plans evaluated for steady-state workloads
- [ ] Azure Advisor recommendations reviewed monthly
- [ ] Non-production resources scheduled to stop outside business hours
