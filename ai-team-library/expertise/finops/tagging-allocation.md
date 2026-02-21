# Tagging & Cost Allocation

Standards for resource tagging, cost allocation models, and showback/chargeback reporting.
Consistent tagging is the foundation of all FinOps practices — without it, cost attribution
is impossible. Enforce tagging via policy-as-code before resources are provisioned.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Tagging enforcement** | AWS SCP + Cloud Custodian policies | Azure Policy, GCP Org Policies, Terraform Sentinel |
| **Cost allocation** | AWS Cost Categories + cost allocation tags | Azure Cost Management scopes, GCP billing labels |
| **Reporting** | AWS Cost and Usage Report (CUR) → Athena → QuickSight | Azure Cost Analysis, GCP BigQuery export, CloudHealth, Looker |
| **Allocation model** | Showback (visibility first, then migrate to chargeback) | Direct chargeback, proportional split, fixed allocation |
| **Tag governance** | Centralized tag taxonomy in version-controlled YAML | Tag spreadsheet (not recommended), wiki page |

---

## Mandatory Tag Schema

Every cloud resource must carry these tags. Enforce at provisioning time — retrofitting tags
across thousands of resources is expensive and error-prone.

| Tag Key | Purpose | Example Values | Enforced |
|---------|---------|----------------|----------|
| `env` | Environment | `prod`, `staging`, `dev`, `sandbox` | Yes |
| `team` | Owning team | `platform`, `payments`, `data-eng` | Yes |
| `service` | Application or service name | `api-gateway`, `user-service` | Yes |
| `cost-center` | Finance cost center code | `CC-4200`, `CC-3100` | Yes |
| `owner` | Responsible individual or group email | `payments-team@example.com` | Yes |
| `managed-by` | Provisioning method | `terraform`, `cdk`, `manual` | Recommended |
| `data-classification` | Data sensitivity level | `public`, `internal`, `confidential` | Recommended |

```yaml
# tagging-taxonomy.yml — single source of truth for allowed tag values
tags:
  env:
    required: true
    allowed_values: [prod, staging, dev, sandbox]
  team:
    required: true
    allowed_values: [platform, payments, data-eng, ml, infra, security]
  service:
    required: true
    pattern: "^[a-z][a-z0-9-]{2,40}$"
  cost-center:
    required: true
    pattern: "^CC-\\d{4}$"
  owner:
    required: true
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$"
  managed-by:
    required: false
    allowed_values: [terraform, cdk, cloudformation, pulumi, manual]
```

---

## Do / Don't

- **Do** define the tag taxonomy centrally and version-control it — a YAML file in a shared
  repository that all IaC references.
- **Do** enforce mandatory tags at provisioning time using SCPs, Terraform Sentinel, or
  Cloud Custodian `mark-for-op` policies.
- **Do** use lowercase, hyphen-separated tag keys (`cost-center`, not `CostCenter`) for
  consistency across providers.
- **Do** tag at the most granular level possible — individual resources, not just resource
  groups or accounts.
- **Do** automate tag compliance reports and publish weekly to team leads.
- **Don't** allow free-form tag values — typos (`prodution`, `stagin`) make allocation
  unreliable. Use enumerated allowed values.
- **Don't** rely on account-level separation alone for cost allocation. Shared-services
  accounts need resource-level tags to split costs accurately.
- **Don't** create provider-specific tag keys. Use the same logical schema across AWS, Azure,
  and GCP, mapped to each provider's tagging/labeling system.
- **Don't** wait until month-end to check tag compliance. Untagged resources compound daily.

---

## Common Pitfalls

1. **Tag drift.** Tags are set at creation but modified or removed later by automation,
   updates, or replacement operations. Use Cloud Custodian or AWS Config rules to continuously
   monitor and remediate tag drift. Terraform's `ignore_changes` on tags can silently drop
   required tags — audit this.

2. **Shared resources without split keys.** A shared RDS cluster used by three services shows
   up as 100% cost for one team. Add a `shared-resource: true` tag and use a proportional
   allocation key (e.g., query count, connection hours) in your cost model.

3. **Too many tags.** AWS allows 50 tags per resource but managing 30+ tags per resource
   creates friction. Keep mandatory tags to 5–7; use optional tags sparingly with clear
   ownership.

4. **Inconsistent casing and naming.** `Environment`, `environment`, `env`, `ENV` are all
   different tag keys. Standardize on one convention and enforce it in CI. Prefer lowercase
   with hyphens.

5. **Cost allocation tags not activated.** In AWS, user-defined tags must be explicitly
   activated as cost allocation tags in the Billing console. Forgetting this step means
   tagged resources still appear as "unallocated" in Cost Explorer.

---

## Cost Allocation Models

### Showback (Recommended starting point)

Teams see their costs but are not directly billed. This builds cost awareness without the
organizational overhead of internal billing.

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐
│ CUR / Billing│ ──► │  ETL + Allocation │ ──► │  Dashboard    │
│   Export     │      │  (Athena / dbt)   │      │  (QuickSight) │
└─────────────┘      └──────────────────┘      └──────────────┘
                            │
                     Tag-based grouping:
                     team → service → env
```

### Chargeback

Costs are charged back to business units via internal invoices. Requires mature tagging,
agreed-upon allocation keys for shared services, and finance buy-in.

| Component | Allocation Method |
|-----------|-------------------|
| EC2 / Compute | Direct — tagged to owning team |
| RDS / Databases | Direct or proportional (by connection count) |
| S3 / Storage | Direct — bucket-level tags |
| Data transfer | Proportional — by service traffic volume |
| Shared services (VPN, DNS, logging) | Fixed split or headcount-based |
| Support plan | Proportional — by team's share of total spend |

---

## Showback Report Example

```sql
-- Athena query against AWS CUR for monthly team-level showback
SELECT
  line_item_usage_account_id AS account_id,
  resource_tags_user_team AS team,
  resource_tags_user_service AS service,
  resource_tags_user_env AS environment,
  product_product_name AS aws_service,
  SUM(line_item_unblended_cost) AS total_cost,
  SUM(line_item_usage_amount) AS total_usage
FROM cost_and_usage_report
WHERE month = '2026-01'
  AND line_item_line_item_type != 'Tax'
GROUP BY 1, 2, 3, 4, 5
ORDER BY total_cost DESC;
```

```sql
-- Identify untagged spend (resources missing mandatory tags)
SELECT
  line_item_usage_account_id AS account_id,
  product_product_name AS aws_service,
  line_item_resource_id AS resource_id,
  SUM(line_item_unblended_cost) AS untagged_cost
FROM cost_and_usage_report
WHERE month = '2026-01'
  AND (resource_tags_user_team IS NULL OR resource_tags_user_team = '')
  AND line_item_unblended_cost > 0
GROUP BY 1, 2, 3
ORDER BY untagged_cost DESC
LIMIT 50;
```

---

## Tag Enforcement via Policy-as-Code

```python
# Cloud Custodian — enforce mandatory tags, auto-stop non-compliant instances
policies:
  - name: enforce-mandatory-tags
    resource: ec2
    filters:
      - or:
          - "tag:env": absent
          - "tag:team": absent
          - "tag:service": absent
          - "tag:cost-center": absent
          - "tag:owner": absent
    actions:
      - type: tag
        key: tag-compliance
        value: "non-compliant"
      - type: notify
        to:
          - resource-owner
        subject: "EC2 instance missing mandatory tags — action required"
        transport:
          type: sqs
          queue: custodian-notifications
```

```hcl
# Terraform Sentinel — block resource creation without required tags
import "tfplan/v2" as tfplan

mandatory_tags = ["env", "team", "service", "cost-center", "owner"]

main = rule {
  all tfplan.resource_changes as _, rc {
    rc.type in ["aws_instance", "aws_db_instance", "aws_s3_bucket"] and
    rc.change.after.tags is not null and
    all mandatory_tags as tag {
      tag in keys(rc.change.after.tags)
    }
  }
}
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Azure Cost Management | Azure-native cost allocation and budgets |
| GCP Billing Export + BigQuery | GCP-native cost analysis at scale |
| CloudHealth | Multi-cloud allocation with business-mapping features |
| Apptio Cloudability | Enterprise showback/chargeback with finance integrations |
| Vantage | Developer-friendly multi-cloud cost reporting |
| nOps | Automated AWS cost optimization with commitment management |

---

## Checklist

- [ ] Tag taxonomy defined in version-controlled YAML with allowed values
- [ ] Mandatory tags enforced at provisioning time (SCP, Sentinel, or policy-as-code)
- [ ] Cost allocation tags activated in billing console (AWS-specific)
- [ ] Tag compliance scanned continuously; non-compliant resources flagged within 24 hours
- [ ] Shared-resource allocation keys documented and agreed upon by stakeholders
- [ ] Showback dashboard published weekly with team-level cost breakdown
- [ ] Untagged spend identified and tracked as a reduction target (goal: < 5% of total)
- [ ] Tag schema reviewed quarterly and updated for new teams/services
- [ ] Cross-provider tag mapping documented for multi-cloud environments
- [ ] Finance team has access to cost reports and allocation methodology documentation
