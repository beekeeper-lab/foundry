---
id: finops
category: Business Practices
entry: true
last-reviewed: 2026-07
---

# FinOps Conventions

## Category
Business Practices

Standards for cloud financial operations: resource tagging and cost allocation,
waste detection and right-sizing, budget alerting, and commitment-based discount
planning (Reserved Instances, Savings Plans). Consistent tagging is the foundation —
without it, cost attribution is impossible and every other practice degrades.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| Cost visibility | AWS Cost Explorer + CUR (Cost and Usage Reports) | Azure Cost Management, GCP Billing Export, CloudHealth, Apptio Cloudability |
| Tagging enforcement | AWS SCP + Cloud Custodian policies | Azure Policy, GCP Org Policies, Terraform Sentinel |
| Tag governance | Centralized taxonomy in version-controlled YAML | Spreadsheet / wiki (not recommended) |
| Cost allocation | AWS Cost Categories + cost allocation tags | Azure Cost Management scopes, GCP billing labels |
| Allocation model | Showback first, then migrate to chargeback | Direct chargeback, proportional split, fixed allocation |
| Right-sizing | AWS Compute Optimizer | Azure Advisor, GCP Recommender, Densify, Spot.io |
| Waste detection | Scheduled Lambda / Cloud Custodian scans for idle resources | Trusted Advisor, CloudHealth |
| Anomaly detection | AWS Cost Anomaly Detection | Anodot, CloudHealth, custom threshold alerts |
| Budget alerts | AWS Budgets with SNS → Slack/PagerDuty | Azure Budgets, GCP Budget Alerts, CloudHealth |
| Commitment type | Compute Savings Plans (flexible) | EC2 Instance Savings Plans, Reserved Instances, GCP CUDs |
| Commitment term | 1-year, No Upfront | 3-year / All Upfront for stable workloads |
| Coverage target | 70–80% of steady-state compute | Higher for mature, predictable workloads |
| Review cadence | Weekly optimization review, monthly deep-dive and commitment utilization review | Quarterly (too infrequent) |

---

## 1. Tagging & Cost Allocation

Every cloud resource carries the mandatory tag schema, enforced at provisioning time —
retrofitting tags across thousands of resources is expensive and error-prone.

| Tag Key | Purpose | Enforced |
|---------|---------|----------|
| `env` | Environment (`prod`, `staging`, `dev`, `sandbox`) | Yes |
| `team` | Owning team | Yes |
| `service` | Application or service name | Yes |
| `cost-center` | Finance cost center code (`CC-4200`) | Yes |
| `owner` | Responsible individual or group email | Yes |
| `managed-by` | Provisioning method (`terraform`, `cdk`, `manual`) | Recommended |
| `data-classification` | Data sensitivity level | Recommended |

- Define the taxonomy centrally in a version-controlled YAML file that all IaC references;
  use enumerated allowed values, not free-form text.
- Lowercase, hyphen-separated tag keys (`cost-center`, not `CostCenter`), one logical schema
  mapped across AWS/Azure/GCP.
- Enforce with SCPs, Terraform Sentinel, or Cloud Custodian; scan continuously and flag
  non-compliant resources within 24 hours.
- Activate user-defined tags as cost allocation tags in the AWS Billing console — otherwise
  tagged spend still shows as unallocated.
- Start with showback (visibility builds cost awareness); move to chargeback only with mature
  tagging, agreed allocation keys for shared services, and finance buy-in.

Full detail: `tagging-allocation.md`

---

## 2. Waste Detection & Idle Resources

- Establish a baseline cost per environment, per service, and per team before optimizing.
- Automate idle-resource detection: unattached EBS volumes, stopped instances older than
  7 days, unused Elastic IPs, empty load balancers, idle RDS instances, snapshots > 90 days.
- Never delete without confirming ownership — use a quarantine period:
  tag → stop → wait 14 days → terminate.
- Set automated shutdown schedules for non-production environments (nights, weekends), but
  balance against developer velocity with fast-provisioning patterns (containers,
  snapshotted AMIs).
- Track data transfer costs explicitly — often the fastest-growing line item. Use VPC
  endpoints, CDN offloading, and AZ consolidation where HA allows.

Full detail: `cost-optimization.md`

---

## 3. Right-Sizing

- Collect CPU, memory, network, and disk I/O metrics over a minimum 14-day window.
- Candidates: average utilization < 40% AND p99 < 70%. Never size on averages alone —
  use P95/P99 to respect peak demand.
- Change one size down (or switch family), validate in staging with a load test, apply via
  IaC, then monitor 7 days post-change.
- Rollback trigger: latency p99 increases > 10% or error rate increases.
- Right-size **before** purchasing commitments — reservations on over-provisioned instances
  lock in waste.
- Use Spot/Preemptible instances for fault-tolerant workloads (batch, CI/CD runners,
  dev/test).

Full detail: `cost-optimization.md`

---

## 4. Budget Alerts & Forecasting

- Tiered thresholds per budget: 50%, 80%, 90%, 100% actual, plus a forecast-based alert at
  100% projected.
- Budgets per cost center / team / service — never a single organization-wide budget; it
  masks team-level overspend.
- Route alerts to the responsible team only; escalate to management only at 100%.
  Broadcast-to-everyone causes alert fatigue.
- Forecast from at least 6 months of CUR trend data (month-over-month growth per team).
- Report amortized costs, not cash-basis — upfront RI payments distort monthly reports as
  lump sums.

Full detail: `budgets-planning.md`

---

## 5. Commitment Planning (RIs / Savings Plans)

- Require **3+ months of stable usage data** before any commitment purchase.
- Default purchase: Compute Savings Plans, 1-year, No Upfront — flexible across instance
  families, sizes, OS, tenancy, and regions. Consider 3-year or All Upfront only after
  6 months of stable utilization.
- Target 70–80% commitment coverage of baseline compute; leave 20–30% on-demand/Spot for
  variability. 100% coverage eliminates scaling flexibility.
- Track utilization weekly; target > 95%. Sell unused commitments on the RI/SP marketplace
  if workloads change.
- Track expirations and plan renewals 60 days in advance.
- Centralize purchasing through a FinOps team or Cloud Center of Excellence (CCoE) — team-level
  purchasing causes commitment sprawl.

Decision shortcuts:

| Workload | Recommendation |
|----------|----------------|
| Stable, same instance type 1+ year | EC2 Instance SP or Standard RI |
| Stable compute, family/region may change | Compute Savings Plan |
| Variable/bursty, interruption-tolerant | Spot (no commitment) |
| Short-lived (< 12 months) or migrating to containers/serverless | On-demand or short-term Compute SP |

Full detail: `budgets-planning.md`

---

## Do / Don't

**Do:**
- Enforce mandatory tags at provisioning time via policy-as-code.
- Establish cost baselines before optimizing — you cannot improve what you have not measured.
- Right-size before buying reservations.
- Quarantine before deleting (tag → stop → wait 14 days → terminate).
- Set tiered budget alerts per cost center with a forecast-based 100% alert.
- Track commitment utilization weekly (> 95% target) and expirations 60 days out.

**Don't:**
- Allow free-form tag values — typos (`prodution`, `stagin`) break allocation.
- Rely on account-level separation alone; shared-services accounts need resource-level tags.
- Buy 3-year commitments for workloads that may migrate, retire, or re-architect.
- Purchase commitments without 3 months of stable usage data.
- Treat cost optimization as a one-time project — spend drifts continuously.
- Ignore data transfer costs or expiring commitments.

---

## Common Pitfalls

1. **Tag drift.** Tags set at creation get dropped by automation or replacement operations;
   Terraform `ignore_changes` on tags can silently drop required tags. Monitor continuously
   with Cloud Custodian or AWS Config.
2. **Shared resources without split keys.** A shared RDS cluster shows as 100% cost for one
   team. Tag `shared-resource: true` and use a proportional allocation key.
3. **Right-sizing too aggressively.** Sizing on average CPU ignores peaks — use P95/P99 over
   14+ days and load-test after resizing.
4. **Zombie resources.** Test resources get forgotten. Auto-tag idle instances
   (CPU < 5% for 7+ days) and unattached volumes on a schedule.
5. **Buying commitments too early or too broadly.** First-month purchases lock in the wrong
   instance types; 100% coverage targets eliminate flexibility.
6. **Alert fatigue.** Everyone gets every budget alert, so nobody reads them. Route by cost
   center; escalate only at 100%.
7. **Cost allocation tags not activated / amortization ignored.** Tagged spend appears
   unallocated; lump-sum RI payments distort monthly reporting.

---

## Checklist

- [ ] Tag taxonomy in version-controlled YAML; mandatory tags enforced at provisioning
- [ ] Cost allocation tags activated in the billing console
- [ ] Untagged spend tracked as a reduction target (goal: < 5% of total)
- [ ] Cost baseline established per environment, service, and team
- [ ] Automated waste detection runs weekly; quarantine-before-delete enforced
- [ ] Right-sizing reviews monthly using 14-day P95/P99 utilization data
- [ ] Non-production environments on automated shutdown schedules
- [ ] Budget alerts per cost center at 50/80/90/100% + forecast alert
- [ ] Commitments purchased centrally after 3+ months of usage data; 70–80% coverage
- [ ] Commitment utilization tracked weekly (> 95%); expirations planned 60 days ahead
- [ ] Amortized cost reporting used in dashboards; showback published weekly
