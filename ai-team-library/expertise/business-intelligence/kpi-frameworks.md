# KPI Frameworks, Metric Definitions & SLIs

Standards for defining, organizing, and maintaining Key Performance Indicators
(KPIs), business metrics, and Service Level Indicators (SLIs). A metric without
a clear definition, owner, and measurement method is not a metric — it is a
guess.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **KPI framework** | OKR-aligned metrics — every KPI maps to an Objective and Key Result | Balanced Scorecard for multi-perspective governance; AARRR (pirate metrics) for product-led growth |
| **Metric catalog** | Central YAML/Markdown catalog in version control (dbt metrics or dedicated repo) | BI platform metric layer (Looker Explores, Metabase Models); wiki-based catalog as a fallback |
| **Metric naming** | `<entity>_<aggregation>_<time_grain>` (e.g., `orders_count_daily`) | `<domain>.<metric>` dot notation for large organizations with many domains |
| **SLI definition** | Ratio-based: `good_events / total_events` over a rolling window | Threshold-based: percentage of requests below a latency target |
| **SLO targets** | Set from historical baselines (p50 of trailing 90 days) with progressive tightening | Business-driven targets agreed with stakeholders regardless of baseline |
| **Error budgets** | `1 - SLO` expressed as allowed bad minutes/requests per period | Burn-rate alerts instead of static thresholds |
| **Review cadence** | Monthly metric review with stakeholders; quarterly KPI refresh | Weekly for early-stage products with rapidly shifting priorities |

---

## Do / Don't

- **Do** write a plain-English definition for every metric before implementing it. If you cannot explain it in one sentence, the metric is too complex or conflates multiple concepts.
- **Do** specify the exact SQL or formula, including filters, joins, and null handling. "Revenue" is not a definition; "Sum of `invoice_amount` from `invoices` where `status = 'paid'` and `invoice_date` within the reporting period" is.
- **Do** assign a single owner to every metric. The owner is responsible for correctness, freshness, and deprecation.
- **Do** classify metrics into tiers: Tier 1 (board/investor-level, ≤ 10), Tier 2 (department-level, ≤ 30), Tier 3 (team operational, unbounded).
- **Do** version metric definitions. When a calculation changes, record the old and new definitions, the effective date, and the reason.
- **Do** set SLOs based on data, not aspiration. Start with a historical baseline and tighten over time.
- **Do** pair every SLI with an error budget and a response plan for budget exhaustion.
- **Don't** create metrics without linking them to a decision or action. If no one changes behavior based on the metric, it is a vanity metric.
- **Don't** use averages as SLIs for latency — use percentiles (p95, p99). Averages hide tail latency that degrades user experience.
- **Don't** set SLO targets at 100%. A 100% target means zero error budget and any incident is a violation. 99.9% is usually the practical ceiling.
- **Don't** change metric definitions silently. Breaking changes to metrics need the same rigor as breaking API changes — announce, document, and migrate.
- **Don't** conflate leading and lagging indicators. Measure both, but use leading indicators for operational decisions and lagging indicators for strategic review.

---

## KPI Hierarchy

```
Company OKRs
  └── Department KPIs (Tier 1)
        └── Team Metrics (Tier 2)
              └── Operational Metrics (Tier 3)
                    └── SLIs / SLOs (system health)
```

### Tier 1 — Strategic KPIs

- Reported to board/investors. Maximum 10 metrics.
- Examples: ARR, Net Revenue Retention, Customer Acquisition Cost, NPS.
- Review cadence: monthly executive review, quarterly board update.
- Change control: requires executive approval to add, modify, or retire.

### Tier 2 — Department KPIs

- Owned by department heads. Maximum 30 across the organization.
- Examples: Sales pipeline velocity, engineering deployment frequency, support CSAT.
- Review cadence: monthly department review.
- Change control: requires department head approval.

### Tier 3 — Operational Metrics

- Owned by team leads. No hard limit, but prune quarterly.
- Examples: queue wait time, cache hit ratio, feature adoption rate.
- Review cadence: weekly team standup.
- Change control: team lead can modify; notify downstream consumers.

---

## Metric Definition Template

```yaml
metric:
  name: orders_count_daily
  display_name: "Daily Order Count"
  description: >
    Total number of orders placed per calendar day (UTC).
    Includes all order statuses except 'cancelled'.
  tier: 3
  owner: fulfillment-team
  domain: commerce
  type: count
  entity: orders
  time_grain: daily
  formula: "COUNT(*) FROM orders WHERE status != 'cancelled' GROUP BY DATE(created_at AT TIME ZONE 'UTC')"
  filters:
    - "status != 'cancelled'"
  null_handling: "Dates with zero orders return 0 (zero-fill)"
  data_source: analytics.marts.fct_orders
  freshness_sla: "Updated by 06:00 UTC daily"
  caveats:
    - "Does not include draft orders or subscription renewals (tracked separately)"
  version: 2
  version_history:
    - version: 1
      date: "2025-01-15"
      change: "Initial definition"
    - version: 2
      date: "2025-06-01"
      change: "Excluded cancelled orders (previously included all statuses)"
```

---

## SLI / SLO Framework

### Defining SLIs

An SLI measures one dimension of service quality as a ratio:

```
SLI = good_events / total_events
```

| SLI Category | Good Event Definition | Example |
|-------------|----------------------|---------|
| **Availability** | Request returns a non-5xx response | 99.95% of API calls succeed |
| **Latency** | Request completes within threshold | 95% of requests < 200ms (p95) |
| **Freshness** | Data updated within SLA window | 99% of dashboard refreshes complete within 1 hour of schedule |
| **Correctness** | Output matches expected result | 99.99% of metric computations produce valid (non-null, in-range) values |

### Setting SLOs

1. **Measure baseline** — collect the SLI over 30–90 days.
2. **Set initial SLO** — use the p50 of the observed SLI (not the best day, not the worst).
3. **Calculate error budget** — `error_budget = 1 - SLO`. For a 99.9% SLO over 30 days: 43.2 minutes of allowed downtime.
4. **Define response tiers:**

| Error Budget Consumed | Response |
|----------------------|----------|
| < 50% | Normal operations |
| 50–75% | Review recent changes; increase monitoring |
| 75–100% | Freeze non-critical deployments; prioritize reliability work |
| > 100% | Incident response; postmortem required |

---

## Common Pitfalls

1. **Metric proliferation.** Teams create metrics for everything, resulting in hundreds of unmaintained definitions. Cap Tier 1 at 10, Tier 2 at 30, and prune Tier 3 quarterly.
2. **Definition drift.** The same metric name means different things in different dashboards because the definition was copied and modified locally. Enforce single-source-of-truth definitions in the semantic layer.
3. **Goodhart's Law.** When a metric becomes a target, people optimize for the metric at the expense of the underlying goal. Pair every target metric with a counter-metric (e.g., pair "tickets closed" with "reopen rate").
4. **SLO theater.** SLOs are set but never enforced — error budgets are ignored, and violations trigger no action. Tie error budget exhaustion to concrete consequences (deployment freezes, reliability sprints).
5. **Missing time zone specification.** "Daily active users" computed in UTC shows different numbers than the same metric computed in US/Pacific. Specify the time zone in every time-grain metric definition.
6. **Trailing indicator bias.** Dashboards show only lagging indicators (revenue, churn) with no leading indicators (pipeline velocity, feature adoption). Include at least one leading indicator per strategic KPI.

---

## Checklist

- [ ] Every KPI maps to a documented business objective or OKR
- [ ] Every metric has a plain-English definition, formula, owner, and data source
- [ ] Metric naming follows `<entity>_<aggregation>_<time_grain>` convention
- [ ] Metrics are classified into Tier 1 / Tier 2 / Tier 3
- [ ] Tier 1 metrics are capped at ≤ 10; Tier 2 at ≤ 30
- [ ] Metric definitions are versioned with change history
- [ ] Null handling is documented for every metric
- [ ] SLIs are defined as `good_events / total_events` ratios
- [ ] SLOs are set from historical baselines, not aspirational targets
- [ ] Error budgets are calculated and response tiers are defined
- [ ] Time zone is specified for every time-grain metric
- [ ] Quarterly metric review is scheduled to prune stale definitions
