# Budgets & Commitment Planning

Standards for budget alerts, reserved instance and Savings Plans purchasing, and long-term
commitment strategies. Budget alerts catch overspend early; commitment-based discounts
(Reserved Instances, Savings Plans) reduce steady-state costs by 30–60%.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Budget alerts** | AWS Budgets with SNS → Slack/PagerDuty | Azure Budgets, GCP Budget Alerts, CloudHealth alerts |
| **Commitment type** | Compute Savings Plans (flexible) | EC2 Instance Savings Plans, Reserved Instances, GCP CUDs |
| **Commitment term** | 1-year, No Upfront (balance savings vs. flexibility) | 3-year for stable workloads, All Upfront for max discount |
| **Coverage target** | 70–80% of steady-state compute covered by commitments | Higher for mature, predictable workloads |
| **Review cadence** | Monthly commitment utilization review | Quarterly (too infrequent), weekly (overkill for most) |

---

## Do / Don't

- **Do** set budget alerts at multiple thresholds: 50%, 80%, 90%, 100%, and a forecast-based
  alert at 100% projected.
- **Do** start with Compute Savings Plans before Reserved Instances — they offer flexibility
  across instance families, sizes, OS, tenancy, and regions.
- **Do** right-size workloads before purchasing commitments — buying reservations for
  over-provisioned instances locks in waste.
- **Do** track commitment utilization weekly. Unused reservations are wasted money.
  Target > 95% utilization.
- **Do** use the RI/SP marketplace to sell unused commitments if workloads change.
- **Do** separate budget alerts by account, team, and service so that the right people
  are notified.
- **Don't** buy 3-year commitments for workloads that may migrate, be retired, or change
  architecture within that window.
- **Don't** purchase commitments without at least 3 months of stable usage data.
- **Don't** set a single organization-wide budget — it masks team-level overspend.
  Set budgets per cost center.
- **Don't** ignore expiring commitments. Track expiration dates and plan renewals or
  replacements 60 days in advance.

---

## Common Pitfalls

1. **Buying commitments too early.** Purchasing Reserved Instances for a workload in its
   first month locks you into an instance type before usage patterns stabilize. Wait at
   least 3 months of steady-state usage data before committing.

2. **100% coverage targets.** Trying to cover all compute with commitments eliminates
   flexibility for scaling. Target 70–80% coverage of baseline compute; let the remaining
   20–30% run on-demand or Spot to handle variability.

3. **Alert fatigue.** Every team gets every budget alert, so nobody reads them. Route alerts
   to the specific team and cost center responsible. Escalate to management only at 100%.

4. **Ignoring amortization in reporting.** Upfront RI payments distort monthly reports if
   shown as a lump sum. Always report amortized costs to give an accurate monthly picture.

5. **Commitment sprawl.** Multiple teams independently purchasing RIs leads to fragmentation,
   overlap, and unused inventory. Centralize commitment purchasing through a FinOps team or
   Cloud Center of Excellence (CCoE), with team input on requirements.

---

## Budget Alert Configuration

```python
# Terraform — AWS Budget with tiered alerts
resource "aws_budgets_budget" "team_monthly" {
  name         = "payments-team-monthly"
  budget_type  = "COST"
  limit_amount = "15000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = ["user:team$payments"]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 50
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = [aws_sns_topic.budget_alerts.arn]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 80
    threshold_type            = "PERCENTAGE"
    notification_type         = "ACTUAL"
    subscriber_sns_topic_arns = [aws_sns_topic.budget_alerts.arn]
  }

  notification {
    comparison_operator       = "GREATER_THAN"
    threshold                 = 100
    threshold_type            = "PERCENTAGE"
    notification_type         = "FORECASTED"
    subscriber_sns_topic_arns = [aws_sns_topic.budget_escalation.arn]
  }
}

resource "aws_sns_topic" "budget_alerts" {
  name = "budget-alerts-payments"
}

resource "aws_sns_topic" "budget_escalation" {
  name = "budget-escalation-payments"
}
```

---

## Savings Plans Purchase Workflow

```
1. Gather 3+ months of usage data from Cost Explorer / CUR
2. Run Savings Plans recommendations (AWS Console or API)
3. Validate recommendations against planned architecture changes
4. Start with Compute Savings Plans (most flexible)
5. Purchase 1-year, No Upfront for initial commitments
6. Monitor utilization weekly — target > 95%
7. After 6 months of stable utilization, consider 3-year or All Upfront for deeper discounts
8. Review expiring commitments 60 days before expiration
```

```bash
# AWS CLI — get Savings Plans purchase recommendations
aws savingsplans get-savings-plans-purchase-recommendation \
  --savings-plans-type COMPUTE_SP \
  --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT \
  --lookback-period-in-days SIXTY_DAYS \
  --output json

# AWS CLI — check current Savings Plans utilization
aws ce get-savings-plans-utilization \
  --time-period Start="2026-01-01",End="2026-02-01" \
  --output table
```

---

## Reserved Instance Management

```bash
# AWS CLI — list active Reserved Instances with utilization
aws ec2 describe-reserved-instances \
  --filters Name=state,Values=active \
  --query 'ReservedInstances[].{
    ID: ReservedInstancesId,
    Type: InstanceType,
    Count: InstanceCount,
    End: End,
    State: State
  }' \
  --output table

# AWS CLI — check RI coverage to find on-demand gaps
aws ce get-reservation-coverage \
  --time-period Start="2026-01-01",End="2026-02-01" \
  --group-by Type=DIMENSION,Key=INSTANCE_TYPE \
  --output table
```

---

## Commitment Decision Matrix

| Workload Characteristic | Recommendation |
|------------------------|----------------|
| Stable, predictable, same instance type for 1+ year | EC2 Instance Savings Plan or Standard RI |
| Stable compute but may change instance family/region | Compute Savings Plan |
| Variable/bursty, tolerates interruption | Spot Instances (no commitment) |
| Short-lived project (< 12 months) | On-demand only |
| Migrating to containers/serverless within 12 months | Short-term Compute SP or on-demand |
| Multi-cloud with shifting workloads | On-demand; optimize per-provider separately |

---

## Forecast-Based Budgeting

```sql
-- Athena query — 6-month cost trend for budget forecasting
SELECT
  DATE_TRUNC('month', line_item_usage_start_date) AS month,
  resource_tags_user_team AS team,
  SUM(line_item_unblended_cost) AS monthly_cost,
  LAG(SUM(line_item_unblended_cost), 1) OVER (
    PARTITION BY resource_tags_user_team
    ORDER BY DATE_TRUNC('month', line_item_usage_start_date)
  ) AS previous_month_cost,
  ROUND(
    (SUM(line_item_unblended_cost) - LAG(SUM(line_item_unblended_cost), 1) OVER (
      PARTITION BY resource_tags_user_team
      ORDER BY DATE_TRUNC('month', line_item_usage_start_date)
    )) / NULLIF(LAG(SUM(line_item_unblended_cost), 1) OVER (
      PARTITION BY resource_tags_user_team
      ORDER BY DATE_TRUNC('month', line_item_usage_start_date)
    ), 0) * 100, 1
  ) AS mom_growth_pct
FROM cost_and_usage_report
WHERE line_item_usage_start_date >= DATE_ADD('month', -6, CURRENT_DATE)
  AND line_item_line_item_type != 'Tax'
GROUP BY 1, 2
ORDER BY team, month;
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| Azure Reservations | Azure-native commitment discounts for VMs, SQL, Cosmos DB |
| GCP Committed Use Discounts (CUDs) | GCP-native commitment pricing for Compute Engine |
| Spot.io (NetApp) | Automated commitment management and Spot optimization |
| ProsperOps | Autonomous Savings Plans management with algorithmic purchasing |
| nOps | Automated AWS commitment optimization with financial guarantees |
| Zesty | Real-time RI and Savings Plans management |

---

## Checklist

- [ ] Budget alerts configured per team/cost-center at 50%, 80%, 90%, 100% thresholds
- [ ] Forecast-based alert set at 100% projected spend
- [ ] Alert routing sends notifications to responsible team, escalates at 100%
- [ ] At least 3 months of usage data collected before commitment purchases
- [ ] Compute Savings Plans purchased for baseline compute (70–80% coverage target)
- [ ] Commitment utilization tracked weekly; target > 95% utilization
- [ ] Expiring commitments tracked with 60-day advance renewal planning
- [ ] Commitment purchasing centralized through FinOps team or CCoE
- [ ] Amortized cost reporting used in dashboards (not cash-basis)
- [ ] Commitment strategy reviewed quarterly and adjusted for workload changes
