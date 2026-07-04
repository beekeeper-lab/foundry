---
id: aws-cloud-platform
category: Infrastructure & Platforms
entry: true
last-reviewed: 2026-07
---

# AWS Cloud Platform Conventions

## Category
Infrastructure & Platforms

Standards for deploying and operating workloads on Amazon Web Services. All AWS
usage must follow the Well-Architected Framework, and every workload must pass
a Well-Architected Review before production launch. Deviations require an ADR.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|-------------|
| Operational Excellence | CloudWatch dashboards + alarms + runbooks | Datadog, Grafana Cloud |
| Security | IAM least-privilege + encryption everywhere + GuardDuty | Third-party SIEM, CrowdStrike |
| Reliability | Multi-AZ + auto-scaling + health checks | Multi-region active-active (critical workloads) |
| Performance Efficiency | Right-sized Fargate tasks + caching layer | Graviton instances, Lambda (burst) |
| Cost Optimization | Reserved capacity + Savings Plans + tagging | Spot instances, S3 Intelligent-Tiering |
| Sustainability | Right-size resources + Graviton + managed services | Serverless-first, auto-scale to zero |
| Identity | IAM with OIDC federation from corporate IdP | IAM Identity Center (SSO), Cognito (customer-facing) |
| Networking | VPC with public + private subnets across 3 AZs | Transit Gateway (multi-VPC), PrivateLink |
| Compute | ECS Fargate (containerized workloads) | Lambda (<15 min, event-driven), EKS, EC2 (bare metal/GPU) |
| Storage | S3 Standard with versioning enabled | S3-IA, S3 Glacier (archive), EFS (shared filesystem) |
| Database | RDS PostgreSQL Multi-AZ | Aurora (high throughput), DynamoDB (NoSQL), ElastiCache |
| Secrets | Secrets Manager with automatic rotation | SSM Parameter Store (non-rotating config), KMS (keys) |
| IaC | CloudFormation or CDK (TypeScript) | Terraform (multi-cloud teams), Pulumi |

---

## 1. Identity and Access (IAM)

- **Least privilege.** Every role, user, and policy grants only the permissions
  needed for the specific task. Start with zero permissions and add
  incrementally. Never `"Action": "*"` or `"Resource": "*"`.
- **No long-lived credentials.** Applications use IAM roles with temporary STS
  credentials. Never embed access keys in code or config files.
- **Federated humans.** Users authenticate through the corporate IdP via OIDC or
  SAML. No IAM users with console passwords in production accounts.
- **Guardrails.** Service Control Policies at the Organization level deny
  actions outside approved regions; MFA required for sensitive operations
  (IAM changes, S3 bucket deletion).
- Use IAM Access Analyzer to generate least-privilege policies from actual usage.

Full detail: `core-services.md`.

---

## 2. Networking (VPC)

- Purpose-built VPC per environment — never the default VPC — spanning
  **3 Availability Zones** minimum with public (ALB, NAT), private (app), and
  data (RDS, ElastiCache) subnet tiers.
- NAT Gateway per AZ, not shared, for resilience.
- Security groups default-deny inbound; allow only required ports from known
  sources. NACLs are a sparing second layer for broad denies.
- VPC Flow Logs enabled and shipped to CloudWatch Logs or S3 for audit.
- Use VPC Endpoints (Gateway for S3/DynamoDB, Interface for others) to keep
  traffic off the public internet.

Full detail: `core-services.md`.

---

## 3. Compute

- **ECS Fargate is the default.** ALB in front, auto-scaling on CPU/memory or
  custom CloudWatch metrics, images in ECR with scanning enabled, container
  health checks defined in the task definition.
- **Lambda for event-driven work** (API Gateway, S3 events, SQS, EventBridge
  schedules): start at 256 MB and tune, set timeouts explicitly (most functions
  <30s), share common code via Layers, and use Provisioned Concurrency for
  latency-sensitive endpoints.
- Right-size from the smallest viable task size and scale up on metrics; review
  Compute Optimizer recommendations monthly.

Full detail: `core-services.md`.

---

## 4. Storage and Data

- **S3:** versioning on all application-data buckets, encryption (SSE-S3, or
  SSE-KMS for regulated workloads), account-level Block Public Access, lifecycle
  rules (IA at 90 days, Glacier at 365, abort incomplete multipart uploads after
  7 days), cross-region replication for critical data.
- **RDS PostgreSQL:** Multi-AZ in production, KMS encryption at rest, automated
  backups (14-day retention prod / 7-day non-prod), Enhanced Monitoring and
  Performance Insights on, no public accessibility — data subnets only.
- **Connections:** IAM database authentication (no passwords in config) and
  RDS Proxy for Lambda-to-RDS connection pooling.
- **Encryption everywhere:** all storage encrypted with KMS at rest; TLS 1.2+
  in transit, enforced at ALB, CloudFront, and API Gateway; annual automatic
  rotation for customer-managed KMS keys.

Full detail: `core-services.md` (S3/RDS), `well-architected.md` (encryption standards).

---

## 5. Reliability and Recovery

- Multi-AZ across 3 AZs with health checks at ALB, ECS, and application levels;
  auto-scaling with target tracking (CPU 60%, request count per target).
- Circuit breakers for external calls, retry with exponential backoff and
  jitter, graceful degradation (serve cached content when a dependency is down).
- Define RPO/RTO per tier: critical <1h/<15min (Multi-AZ + cross-region
  replica), standard <4h/<1h, non-critical <24h/<4h.
- Untested backups are not backups — run quarterly DR drills and GameDay
  chaos exercises with documented results.

Full detail: `well-architected.md`.

---

## 6. Observability and Cost

- **Observability is a launch requirement:** one dashboard per service with
  golden signals (latency, traffic, errors, saturation); structured JSON logs to
  CloudWatch (30-day retention non-prod, 90-day prod, archive to S3); X-Ray
  tracing on all service-to-service calls; every alarm links to a runbook.
- **Security services on in all accounts:** GuardDuty, Security Hub, Config
  (with auto-remediation for critical compliance rules), CloudTrail in all
  regions.
- **Cost:** tag every resource with `Environment`, `Team`, `CostCenter`,
  `ManagedBy` (enforced via tag policies); AWS Budgets with alerts at 50/80/100%;
  Cost Anomaly Detection on; weekly Cost Explorer review; delete unused EBS
  volumes, idle load balancers, and unused NAT Gateways ($32/month each); stop
  non-production resources outside business hours.

Full detail: `well-architected.md`.

---

## Do / Don't

**Do:**
- Run a Well-Architected Review before production launch, and quarterly after.
- Use multiple AWS accounts (dev/staging/prod) via AWS Organizations.
- Use managed services over self-managed infrastructure where possible.
- Provision all resources via IaC; automate scaling, patching, and backups.
- Enable CloudTrail in all accounts and all regions.
- Encrypt all data at rest and in transit.

**Don't:**
- Use the root account for daily operations — lock it with MFA and alerts.
- Create IAM users with access keys for applications; use IAM roles.
- Deploy production workloads in a single Availability Zone or the default VPC.
- Hardcode account IDs, regions, or ARNs — use SSM parameters or CDK context.
- Leave S3 buckets without encryption, versioning, or access logging.
- Over-provision "just in case" — use auto-scaling and right-sizing instead.
- Treat the Well-Architected Framework as a one-time checklist.

---

## Common Pitfalls

1. **Over-permissive IAM policies.** Wildcard actions/resources create a blast
   radius. Use IAM Access Analyzer to generate least-privilege policies.
2. **Single-AZ deployments.** One AZ outage takes down the application. Deploy
   across 3+ AZs with health checks and auto-failover.
3. **Unrestricted security groups.** `0.0.0.0/0` on port 22/3389 is an open
   invitation. Use SSM Session Manager — no SSH ports needed.
4. **No observability until a production incident.** Dashboards, alarms, and
   traces are launch requirements, not post-launch enhancements.
5. **Ignoring cost until the bill arrives.** Forgotten NAT Gateways, oversized
   RDS, unused EBS bleed money. Weekly cost review plus automated waste detection.
6. **Untested disaster recovery.** Backups exist but have never been restored.
   Schedule quarterly DR drills and verify data integrity.
7. **Lambda cold starts in synchronous paths.** Use Provisioned Concurrency for
   user-facing endpoints, or Fargate for always-on workloads.
8. **Compliance drift.** Compliant at launch, drifting after. Use AWS Config
   rules with auto-remediation for critical checks.

---

## Checklist

- [ ] Well-Architected Review completed using the AWS Well-Architected Tool
- [ ] Accounts structured with Organizations; SCPs enforce region restrictions
- [ ] IAM least-privilege everywhere; no wildcards, no long-lived access keys
- [ ] MFA enforced for all human users and the root account
- [ ] VPC spans 3+ AZs with public/private/data subnets; Flow Logs enabled
- [ ] Security groups default-deny; VPC endpoints keep traffic private
- [ ] CloudTrail, GuardDuty, Security Hub, and Config enabled in all accounts
- [ ] All S3 buckets: encryption, versioning, Block Public Access
- [ ] RDS Multi-AZ with encryption at rest and automated backups
- [ ] CloudWatch dashboards with golden signals; alarms linked to runbooks
- [ ] X-Ray tracing enabled for distributed service calls
- [ ] Backup strategy with RPO/RTO per tier; quarterly DR drills
- [ ] All resources tagged (Environment, Team, CostCenter, ManagedBy) via IaC
- [ ] AWS Budgets with 50/80/100% alerts; Savings Plans evaluated
- [ ] Non-production resources scheduled to stop outside business hours
