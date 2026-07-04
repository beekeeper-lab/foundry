---
id: azure-cloud-platform
category: Infrastructure & Platforms
entry: true
last-reviewed: 2026-07
---

# Azure Cloud Platform Conventions

## Category
Infrastructure & Platforms

Standards for deploying and operating workloads on Microsoft Azure, covering identity,
networking, compute, storage, messaging, and databases. All Azure usage must follow the
Azure Well-Architected Framework, and every workload must pass a Well-Architected Review
before production launch. Deviations require an ADR.

---

## Defaults

| Concern | Default Approach | Alternatives |
|---------|-----------------|-------------|
| Reliability | Zone-redundant deployments + auto-scaling + health probes | Multi-region active-active (critical workloads) |
| Security | Entra ID RBAC + encryption everywhere + Defender for Cloud | Third-party SIEM (Splunk, Sentinel SOAR) |
| Cost Optimization | Azure Reservations + auto-scale + tagging | Spot VMs (fault-tolerant), dev/test pricing |
| Operational Excellence | Azure Monitor + Log Analytics + workbooks + alerts | Datadog, Grafana Cloud, New Relic |
| Performance Efficiency | Right-sized resources + caching + CDN | Arm-based VMs (Ampere), serverless-first |
| Identity | Microsoft Entra ID with conditional access; Managed Identities service-to-service | Entra External ID (customer-facing) |
| Networking | VNet with public + private subnets across 3 Availability Zones | Virtual WAN (multi-VNet), Private Link |
| Compute | Azure App Service (web apps/APIs) | AKS (Kubernetes), Functions (event-driven, <10 min), Container Apps |
| Storage | Azure Blob Storage with soft delete enabled | Azure Files, Data Lake Storage Gen2 (analytics) |
| Database | Azure Cosmos DB (globally distributed NoSQL) | Azure SQL Database, PostgreSQL Flexible Server |
| Messaging | Azure Service Bus (Premium in production) | Event Grid (routing), Event Hubs (streaming), Storage Queues |
| Secrets | Azure Key Vault with soft delete and purge protection | App Configuration (non-secret config) |
| IaC | Bicep (Azure-native) | Terraform (multi-cloud), Pulumi, ARM templates (legacy) |

---

## 1. Identity and Access

- **Least privilege.** Every role assignment grants only what the task needs. Use built-in
  RBAC roles at the narrowest scope before creating custom roles; audit overprivileged
  assignments with Azure Policy.
- **No long-lived credentials.** Managed Identities for all Azure service-to-service
  authentication. Never embed client secrets or certificates in code.
- **Conditional Access:** enforce MFA, device compliance, and location policies for all
  human users. Block legacy authentication protocols.
- **Privileged Identity Management (PIM):** just-in-time activation for privileged roles,
  time-limited assignments with approval workflows. Quarterly access reviews that
  auto-remove stale access.
- Enable Azure Policy at the Management Group level; deny deployments outside approved
  regions. Tag every service principal with `team`, `environment`, and `purpose`.

Full detail: `core-services.md` (Identity), `well-architected.md` (Identity Security).

---

## 2. Networking

- VNet with public, app, and data subnets across **3 Availability Zones** minimum for
  production. One NAT Gateway per AZ for zone-redundant outbound.
- **NSGs on every subnet, default deny inbound.** Allow only required ports from known
  sources; use ASGs to group NICs by function for readable rules. Ship NSG Flow Logs to
  Log Analytics for audit.
- **Private Endpoints for all PaaS services** — keep traffic off the public internet.
  ExpressRoute or Site-to-Site VPN for on-premises; VNet Peering or Virtual WAN between VNets.

Full detail: `core-services.md` (VNet & Networking).

---

## 3. Compute

- **App Service** is the default for web apps/APIs: Premium v2/v3 plans in production
  (zone-redundant, VNet integration), `httpsOnly` + TLS 1.2 minimum, deployment slots for
  blue-green with auto-swap, auto-scaling on CPU/memory/queue length, System-Assigned
  Managed Identity for Key Vault/Storage/database access.
- **AKS** for Kubernetes workloads: separate system and user node pools spread across 3 AZs,
  Azure CNI networking, cluster autoscaler on user pools, **Workload Identity** (not pod
  identity) for Azure resource access, images in ACR with vulnerability scanning.
- **Functions** for event-driven work: Consumption plan for bursty loads (10 min max),
  Premium plan for VNet integration, pre-warmed instances, and 60 min timeout.

Full detail: `core-services.md` (Compute).

---

## 4. Data: Storage, Cosmos DB, Service Bus

- **Blob Storage:** ZRS for production (GRS for DR of critical data), public network access
  disabled with Private Endpoints, soft delete with 14-day retention, lifecycle rules
  (Cool at 90 days, Archive at 365 days).
- **Cosmos DB:** Session consistency by default (Strong only when business logic requires);
  choose a high-cardinality partition key *before* writing data; autoscale throughput
  (start max 4000 RU/s and tune); zone redundancy per region; continuous backup with
  30-day PITR; Managed Identity + Cosmos RBAC for data plane (no connection strings);
  singleton SDK client per application.
- **Service Bus:** Premium tier in production; topics/subscriptions for pub-sub, queues with
  sessions for FIFO; dead-letter queues enabled and monitored with alerts; PeekLock mode
  with explicit completion — never ReceiveAndDelete.

Full detail: `core-services.md` (Storage, Database, Messaging).

---

## 5. Reliability and Recovery

- Zone-redundant SKUs everywhere: App Service Premium v3, AKS zone-spread, Cosmos DB zone
  redundancy, Storage ZRS. Health probes at gateway, load balancer, and application levels.
- Circuit breakers for external calls (Polly, resilience4j); retry with exponential backoff
  and jitter; graceful degradation via cached content; fault injection with Azure Chaos Studio.
- Tiered RPO/RTO: critical <1h/<15min (multi-region + Cosmos multi-write), standard
  <4h/<1h (zone-redundant + snapshots), non-critical <24h/<4h.
- Azure Site Recovery for VMs, Front Door for global failover. **Quarterly DR drills with
  documented results — untested recovery is not recovery.**

Full detail: `well-architected.md` (Reliability).

---

## 6. Operations and Cost

- **Observability is a launch requirement:** Azure Monitor metrics, structured logs in
  Log Analytics (30d non-prod / 90d prod retention), Application Insights distributed
  tracing with correlation IDs, dashboards showing golden signals per service.
- Every alert links to a runbook (symptom, likely causes, diagnostics, remediation,
  escalation). Review runbooks quarterly.
- All provisioning via IaC (Bicep/Terraform) — no manual portal deployments in staging or
  production. CI/CD with environment approvals; feature flags via App Configuration.
- **Cost:** tag every resource with `Environment`, `Team`, `CostCenter`, `ManagedBy`
  (enforced by Azure Policy); budgets with alerts at 50/80/100%; weekly cost review;
  Reservations/Savings Plans for steady state; stop non-prod resources off-hours; delete
  orphaned disks and unattached IPs.
- Right-size from the smallest viable SKU using metrics, not estimates; load test with 2x
  expected peak before major releases (Azure Load Testing) and alert on p95/p99 regression.

Full detail: `well-architected.md` (Cost Optimization, Operational Excellence, Performance Efficiency).

---

## Do / Don't

**Do:**
- Use Management Groups and separate subscriptions for dev, staging, and production.
- Run a Well-Architected Review before production, and implement all five pillars.
- Use Private Endpoints to keep traffic off the public internet.
- Enable Microsoft Defender for Cloud across all subscriptions.
- Prefer managed services (PaaS/serverless) over self-managed infrastructure.
- Encrypt all data at rest and in transit; automate scaling, patching, and backups.
- Provision everything via IaC (Bicep/Terraform).

**Don't:**
- Create service principals with client secrets for applications — use Managed Identities.
- Deploy production resources in a single Availability Zone.
- Use default networking; build purpose-built VNets with NSGs on every subnet.
- Leave storage accounts with public network access enabled.
- Hardcode subscription, tenant, or resource IDs — use Bicep/Terraform references.
- Treat the Well-Architected Framework as a one-time checklist, or skip DR testing.
- Over-provision "just in case" — use auto-scaling and right-sizing instead.

---

## Common Pitfalls

1. **Over-permissive RBAC.** Owner/Contributor at subscription scope when a resource-group
   role suffices. Assign at the narrowest scope and audit with Azure Policy.
2. **Single-zone deployments.** One zone outage takes down the application. Deploy across
   3 AZs with zone-redundant SKUs.
3. **NSGs without deny rules.** Default rules allow intra-VNet traffic, enabling lateral
   movement. Explicitly deny between tiers.
4. **Cosmos DB hot partitions.** A poor partition key throttles some physical partitions
   while others idle. Analyze key distribution before production launch.
5. **Service Bus message loss.** ReceiveAndDelete drops messages on consumer failure. Use
   PeekLock with explicit completion.
6. **No observability until a production incident.** Dashboards, alerts, and traces are
   launch requirements, not post-launch enhancements.
7. **Ignoring cost until the bill arrives.** Idle nodes, orphaned disks, and forgotten
   premium tiers bleed money. Weekly cost review plus Azure Advisor recommendations.
8. **Compliance drift.** Compliant at launch, drifting after. Use Azure Policy deny/audit
   effects with auto-remediation.

---

## Checklist

- [ ] Subscriptions structured with Management Groups (dev/staging/prod separation)
- [ ] Well-Architected Review completed before production launch
- [ ] RBAC uses least-privilege built-in roles at narrowest scope; MFA via Conditional Access
- [ ] Managed Identities for all service-to-service auth; no client secrets
- [ ] VNet spans 3+ AZs; NSGs default-deny inbound; NSG Flow Logs retained
- [ ] Private Endpoints for PaaS services; storage public access disabled
- [ ] Microsoft Defender for Cloud enabled across all subscriptions
- [ ] Encryption at rest and in transit everywhere; Key Vault with soft delete + purge protection
- [ ] Zone-redundant deployment with health probes and auto-scaling
- [ ] Cosmos DB: sound partition key, autoscale throughput, continuous backup
- [ ] Service Bus Premium with dead-letter monitoring in production
- [ ] Azure Monitor dashboards, metric alerts with action groups, linked runbooks
- [ ] Application Insights distributed tracing enabled for all services
- [ ] Backup strategy with RPO/RTO per tier; quarterly DR drills documented
- [ ] All resources tagged (Environment, Team, CostCenter, ManagedBy) via Azure Policy
- [ ] Cost budgets with 50/80/100% alerts; Reservations/Savings Plans evaluated
- [ ] All infrastructure provisioned via IaC (Bicep/Terraform)
