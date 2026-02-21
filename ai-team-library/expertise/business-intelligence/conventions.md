# Business Intelligence Stack Conventions

These conventions apply to all business intelligence and analytics projects on
this team. They are opinionated by design — consistency across dashboards,
metrics, and reports matters more than individual preference. Deviations require
an ADR with justification.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **BI platform** | Metabase (open-source, self-hosted) | Looker for governed semantic layer at scale; Tableau for advanced visual analytics; Power BI in Microsoft-centric orgs |
| **Semantic layer** | Looker LookML or dbt metrics layer | Metabase models for simpler use cases; Tableau data sources with published extracts |
| **Metric store** | dbt metrics with versioned YAML definitions | Looker Explores; Airflow-computed aggregates in a metrics mart |
| **Dashboard framework** | One dashboard per business domain; max 8 tiles per dashboard | Single-page executive views with drill-through for detail |
| **Data visualization** | Chart type selected by data relationship (see `data-visualization.md`) | Custom D3.js visualizations only when BI platform charts are insufficient |
| **Alerting** | Threshold-based alerts in the BI platform with Slack/email delivery | PagerDuty integration for SLI breaches; custom alerting via Airflow sensors |
| **Access control** | Row-level security via BI platform groups mapped to SSO roles | Column-level masking for PII; embedded analytics with signed tokens for external users |
| **Refresh cadence** | Hourly for operational dashboards; daily for strategic dashboards | Real-time streaming for latency-critical metrics (< 5 min); weekly for cost-heavy full refreshes |
| **Version control** | LookML / dbt models in Git; dashboard-as-code where supported | Manual dashboard exports for platforms without code-based definitions |
| **Documentation** | Every metric has a plain-English definition, owner, and data source in the metric catalog | Inline dashboard descriptions as a fallback |

---

## Do / Don't

- **Do** define every metric exactly once in a shared semantic layer or metric store. Dashboards reference the canonical definition; they never recompute it.
- **Do** assign an owner to every dashboard and every metric. Ownership means someone is accountable for accuracy, freshness, and retirement.
- **Do** use consistent naming conventions for metrics: `<entity>_<aggregation>_<time_grain>` (e.g., `orders_count_daily`, `revenue_sum_monthly`).
- **Do** document the business definition, calculation logic, data source, and known caveats for every metric in a central catalog.
- **Do** set explicit refresh schedules and stale-data alerts for every dashboard.
- **Do** apply row-level security rather than duplicating dashboards per team or region.
- **Do** test metric definitions against known-good values before promoting to production.
- **Don't** let users build ad-hoc calculated fields inside dashboards. Push logic into the semantic layer so it is governed and reusable.
- **Don't** create "god dashboards" with 20+ tiles. Split into domain-specific dashboards with clear navigation.
- **Don't** use pie charts for more than 5 categories or for comparisons across time. Use bar charts instead.
- **Don't** embed raw database column names in user-facing labels. Use human-readable names from the semantic layer.
- **Don't** skip null handling. Define how each metric treats missing data (exclude, zero-fill, or interpolate) and document the choice.
- **Don't** grant broad database access to the BI tool service account. Scope permissions to the marts and views it needs.

---

## Tool Conventions

### Looker

- All logic lives in LookML. Dashboards are "thin" — they select dimensions, measures, and filters from Explores.
- One LookML project per data domain. Cross-domain joins use `explore` refinements, not monolithic models.
- Naming: views match the underlying table name; measures use `<aggregation>_<field>` (e.g., `count_orders`, `sum_revenue`).
- Use `datagroups` for cache management tied to the ETL schedule, not hard-coded `persist_for` durations.
- Derived tables must have `sql_trigger_value` or `datagroup_trigger` — never unbounded PDTs.

### Tableau

- Published data sources are the single source of truth. Workbooks connect to published sources, not raw database connections.
- Use extracts for performance; live connections only when real-time freshness is required and the source can handle the load.
- Naming: workbooks use `<Domain> - <Topic>` (e.g., `Sales - Pipeline Overview`). Sheets within a workbook use concise action-oriented names.
- Calculated fields that represent business logic belong in the published data source, not in individual workbooks.
- Apply Tableau Server site roles aligned with SSO groups. Use project-level permissions, not workbook-level.

### Metabase

- Define reusable models (Metabase Models or dbt models exposed via the database) as the foundation for questions.
- Use Collections to organize dashboards by business domain. Pin key dashboards to the top of each collection.
- Native queries (SQL) are acceptable for complex logic but must include a comment header explaining the metric and owner.
- Use Sandboxing (row-level security) for multi-tenant or role-based data access.
- Schedule dashboard subscriptions for stakeholders who need push delivery, with clear frequency and recipient lists.

---

## Common Pitfalls

1. **Metric inconsistency.** Two dashboards show different "revenue" numbers because they use different filters, time zones, or join logic. Centralize the definition in the semantic layer and have both dashboards reference it.
2. **Dashboard sprawl.** Hundreds of dashboards accumulate with no ownership or retirement process. Implement a quarterly review: archive dashboards with zero views in the past 90 days.
3. **Vanity metrics.** Dashboards display impressive-looking numbers that do not drive decisions. Every metric on a dashboard should have a documented decision it supports or an action it triggers.
4. **Stale data without warning.** A dashboard shows data from 3 days ago but nothing indicates it is stale. Add last-refreshed timestamps and stale-data alerts to every dashboard.
5. **Over-permissioned service accounts.** The BI tool's database user has full read access to every schema, including PII tables. Scope the service account to production marts and curated views only.
6. **Ignoring mobile and accessibility.** Dashboards designed on wide monitors break on tablets or for users with color vision deficiency. Test responsive layouts and use colorblind-safe palettes.

---

## Checklist

- [ ] Every metric is defined once in a semantic layer or metric catalog
- [ ] Every metric has a plain-English definition, owner, data source, and known caveats
- [ ] Naming follows `<entity>_<aggregation>_<time_grain>` convention
- [ ] Every dashboard has an owner and a documented purpose
- [ ] Dashboards have ≤ 8 tiles; larger views are split into linked sub-dashboards
- [ ] Refresh schedule is explicit and stale-data alerts are configured
- [ ] Row-level security is applied; no duplicated dashboards per team
- [ ] Service account permissions are scoped to marts and curated views only
- [ ] Dashboard changes are reviewed (code review for LookML/dbt; peer review for visual dashboards)
- [ ] Quarterly dashboard audit is scheduled to retire unused dashboards
