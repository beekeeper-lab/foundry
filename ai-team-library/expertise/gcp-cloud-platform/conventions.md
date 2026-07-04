---
id: gcp-cloud-platform
category: Infrastructure & Platforms
entry: true
last-reviewed: 2026-07
---

# GCP Cloud Platform Conventions

## Category
Infrastructure & Platforms

Standards for deploying and operating workloads on Google Cloud Platform, aligned
to the pillars of the Google Cloud Architecture Framework. Every workload must pass
an architecture review before production launch. Deviations require an ADR.

---

## Defaults

| Concern | Default Approach | Alternatives |
|---------|-----------------|-------------|
| **Operational Excellence** | Cloud Monitoring dashboards + alerting policies + runbooks | Datadog, Grafana Cloud |
| **Security** | IAM least-privilege + encryption everywhere + Security Command Center | Third-party SIEM |
| **Reliability** | Multi-zone (3+) + auto-scaling + health checks | Multi-region active-active (critical workloads) |
| **Performance** | Right-sized Cloud Run/GKE + caching layer (Cloud CDN, Memorystore) | Autoscaling with custom metrics |
| **Cost** | Committed Use Discounts + labeling + billing budgets | Spot VMs (fault-tolerant workloads) |
| **Identity** | Cloud IAM with Workload Identity Federation from corporate IdP | Identity Platform (customer-facing) |
| **Networking** | VPC with private subnets across 3 zones, Private Google Access | Shared VPC, VPC Service Controls |
| **Compute (containers)** | Cloud Run (containerized HTTP workloads) | GKE Autopilot (Kubernetes required), Cloud Functions (event-driven) |
| **Storage / Database** | Cloud Storage Standard with versioning; Cloud SQL PostgreSQL HA | Nearline/Coldline/Archive tiers; AlloyDB, Firestore, Memorystore |
| **Messaging / Analytics** | Pub/Sub; BigQuery | Cloud Tasks, Eventarc; Dataflow, Dataproc |
| **Secrets** | Secret Manager with automatic rotation | KMS (encryption keys only) |
| **IaC** | Terraform (state in Cloud Storage backend) | Deployment Manager, Pulumi |

---

## 1. Identity & Access

- **Least privilege.** Every service account, user, and role binding grants only the
  permissions needed. Start with zero permissions and add incrementally. No
  `roles/owner` or `roles/editor` on service accounts; use IAM Recommender to right-size.
- **No long-lived credentials.** Never export service account keys. Use Workload
  Identity Federation for external workloads and Workload Identity for GKE pods.
- **Federated humans.** Users authenticate through the corporate IdP via OIDC/SAML;
  MFA enforced via Cloud Identity or Workspace.
- **Guardrails.** Organization Policies at org/folder level, VPC Service Controls
  around sensitive data, domain-restricted sharing to block external IAM grants.

Full detail: `core-services.md` (IAM).

---

## 2. Networking

- VPC with public / app / data subnets across **3 zones** minimum for production.
  Never use the default VPC for production.
- **Default-deny ingress** firewall rules; allow only required ports from known
  source ranges or service accounts.
- **Private Google Access** on all subnets; Cloud NAT (one per region) for private
  subnet egress; VPC Flow Logs enabled and exported for audit.
- Connectivity: VPC Peering or Shared VPC between VPCs; Cloud VPN or Interconnect
  to on-premises; Private Service Connect for Google services.

Full detail: `core-services.md` (VPC & Networking).

---

## 3. Compute

- **Cloud Run is the default** for containerized HTTP workloads. Set min instances
  to 1+ for latency-sensitive services (cold starts cost 1–3 s). Images live in
  Artifact Registry with vulnerability scanning.
- **GKE Autopilot** when Kubernetes is required; GKE Standard only for custom node
  needs (GPUs, specific machine types). Enable Workload Identity and Dataplane V2;
  prefer Gateway API for routing.
- **Cloud Functions** for lightweight event-driven work (Pub/Sub, Storage,
  Firestore triggers, scheduled tasks). Set timeout explicitly; tune memory from
  256 MB based on metrics.
- Every workload runs under a **dedicated service account** with scoped IAM roles.

Full detail: `core-services.md` (Compute).

---

## 4. Data & Messaging

- **Pub/Sub:** one topic per event type; dead-letter topic after 5 delivery
  attempts; acknowledgment deadline 60–120 s (default 10 s is too short); Pub/Sub
  schemas (Avro/Protobuf) for type safety. Alert on `oldest_unacked_message_age`
  > 5 min and any dead-letter messages.
- **BigQuery:** datasets per business domain; partition by date and cluster on
  filter columns; `require_partition_filter = true` on large tables; authorized
  views and policy tags for PII columns; audit logging on Data Access.
- **Cloud Storage:** uniform bucket-level access (no ACLs), versioning, lifecycle
  rules (Nearline at 90 days, Coldline at 365), public-access block enforced via
  organization policy.

Full detail: `core-services.md` (Messaging, Analytics, Cloud Storage).

---

## 5. Reliability & Observability

- Deploy across 3 zones with health checks at load balancer, GKE, and application
  levels. Auto-scale on target utilization (Cloud Run: 60% concurrency, GKE HPA:
  70% CPU); connection draining 30 s.
- Circuit breakers for external calls; retry with exponential backoff and jitter;
  graceful degradation when dependencies fail.
- Backup tiers: Critical RPO <1 h / RTO <15 min (multi-zone + cross-region
  replica); Standard RPO <4 h / RTO <1 h; Non-critical RPO <24 h / RTO <4 h.
  Test DR quarterly — untested backups are not backups.
- Observability is a **launch requirement**: one dashboard per service with golden
  signals (latency, traffic, errors, saturation), Cloud Trace with OpenTelemetry,
  structured JSON logs to Cloud Logging (30 d non-prod / 90 d prod retention).
  Every alert links to a runbook.

Full detail: `well-architected.md` (Operational Excellence, Reliability).

---

## 6. Security & Cost

- **Defense in depth:** Organization Policies → VPC Service Controls → firewall
  rules → Private Google Access → service accounts/IAM → CMEK/DLP/policy tags.
- **Encryption:** at rest by default (CMEK via Cloud KMS for regulated workloads,
  90-day automatic rotation); TLS 1.2+ in transit. Security Command Center for
  continuous findings and compliance monitoring.
- **Cost:** label every resource (`environment`, `team`, `cost-center`,
  `managed-by`); export billing to BigQuery; budgets with alerts at 50/80/100%;
  CUDs for steady-state (20–57% savings), Spot VMs for fault-tolerant work;
  stop non-production resources outside business hours; delete idle disks, IPs,
  load balancers, and Cloud SQL instances.

Full detail: `well-architected.md` (Security, Cost Optimization).

---

## Do / Don't

**Do:**
- Run a Google Cloud Architecture Framework review before production launch, and quarterly after.
- Use multiple GCP projects (dev/staging/prod) organized under folders.
- Provision everything via Terraform; label every resource.
- Use Workload Identity Federation instead of exported service account keys.
- Use managed services over self-managed infrastructure; automate scaling, patching, backups.
- Enable Cloud Audit Logs (Admin Activity and Data Access) in all projects.

**Don't:**
- Export service account keys or create user-managed keys for applications.
- Deploy production in a single zone or on the default VPC.
- Hardcode project IDs, regions, or resource names — use Terraform variables.
- Run BigQuery queries without partition filters on large tables.
- Treat the Architecture Framework as a one-time checklist, or skip DR testing.
- Over-provision "just in case" — use auto-scaling and right-sizing instead.

---

## Common Pitfalls

1. **Exported service account keys** embedded in CI/CD never expire and are hard to
   track. Use Workload Identity Federation or attached service accounts.
2. **Single-zone deployments** — one zone outage takes down the application. Deploy
   across 3 zones with health checks and auto-failover.
3. **Unpartitioned BigQuery tables** — full scans on multi-TB tables generate massive
   costs. Partition, cluster, and enforce `require_partition_filter`.
4. **Overly broad IAM roles** (`roles/owner`/`roles/editor` on service accounts).
   Use scoped predefined or custom roles; right-size with IAM Recommender.
5. **Unmonitored Pub/Sub backlogs** delay data processing silently. Alert on oldest
   unacked message age and dead-letter counts.
6. **No observability until a production incident.** Dashboards, alerts, and traces
   are launch requirements, not post-launch enhancements.
7. **Ignoring cost until the bill arrives** — idle Cloud SQL, oversized clusters,
   no budget alerts. Weekly cost review with billing export and 50/80/100% budgets.

---

## Checklist

- [ ] Architecture Framework review completed before production launch
- [ ] Projects structured under org folders (dev/staging/prod separation)
- [ ] IAM least-privilege; no `roles/owner` on service accounts; no exported keys
- [ ] MFA enforced for all human users
- [ ] VPC spans 3+ zones, private subnets, Private Google Access, Flow Logs exported
- [ ] Firewall default-deny ingress
- [ ] Cloud Audit Logs enabled (Admin Activity + Data Access) in all projects
- [ ] Cloud Storage: uniform access, versioning, lifecycle rules
- [ ] Cloud SQL HA with encryption and automated backups
- [ ] Pub/Sub dead-letter topics + backlog monitoring
- [ ] BigQuery partitioned/clustered with partition-filter enforcement
- [ ] Dashboards with golden signals; alerts linked to runbooks; Cloud Trace enabled
- [ ] Backup RPO/RTO per tier; DR drills quarterly
- [ ] All resources labeled; billing budgets at 50/80/100%; CUDs evaluated
- [ ] Terraform for all provisioning, state in Cloud Storage backend
