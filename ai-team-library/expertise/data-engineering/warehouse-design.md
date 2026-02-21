# Warehouse Design

Standards for designing and organizing a cloud data warehouse. Snowflake is the
primary reference; BigQuery and Redshift differences noted where significant.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Platform** | Snowflake | BigQuery for GCP-native; Redshift for AWS-native with existing investment |
| **Layer architecture** | Raw → Staging → Intermediate → Marts | Two-layer (raw → marts) only for very simple use cases |
| **Raw layer** | Unmodified source data, append-only, partitioned by load date | — |
| **Staging layer** | 1:1 source mirrors with type casting, renaming, and deduplication | — |
| **Marts layer** | Business-oriented dimensional models (facts + dimensions) | Wide denormalized tables only for single-purpose dashboards |
| **Access control** | Role-based access per layer (read-raw, read-staging, read-marts) | Row-level security for multi-tenant datasets |
| **Compute isolation** | Separate warehouses for ETL, analysts, and dashboards | Shared warehouse only for low-volume teams |
| **Naming** | `raw_<source>`, `stg_<source>__<entity>`, `int_<entity>`, `fct_<entity>`, `dim_<entity>` | — |

---

## Do / Don't

- **Do** implement a clear layer architecture. Every table belongs to exactly one layer, and data flows only from lower to higher layers (raw → staging → marts).
- **Do** isolate ETL compute from query compute. A long-running transformation should never slow down a dashboard user.
- **Do** use Snowflake's `COPY INTO` or BigQuery's load jobs for bulk ingestion. Never `INSERT INTO ... SELECT` from an external source row by row.
- **Do** partition and cluster tables on frequently filtered columns (date, tenant_id).
- **Do** set data retention policies on raw and staging tables. Keep raw data long-term (compliance); staging can be shorter-lived.
- **Do** use views or secure views for the marts layer when the underlying data is small enough that materialization adds no benefit.
- **Don't** grant analysts write access to raw or staging layers. Marts are the query interface.
- **Don't** create a single warehouse (compute) for all workloads. Contention between ETL and ad-hoc queries causes unpredictable performance.
- **Don't** skip the staging layer. Loading source data directly into marts couples warehouse models to source schemas.
- **Don't** store sensitive data (PII, PHI) in the same schema as general analytics without access controls and masking policies.

---

## Common Pitfalls

1. **Warehouse sprawl.** Creating a new Snowflake warehouse per team without governance leads to cost explosion. Establish a warehouse provisioning policy with size limits and auto-suspend.
2. **No auto-suspend.** Snowflake warehouses left running 24/7 burn credits even when idle. Set `AUTO_SUSPEND = 60` (seconds) and `AUTO_RESUME = TRUE` on every warehouse.
3. **Over-materialization.** Materializing every staging model as a table when views would suffice wastes storage and increases pipeline runtime.
4. **Missing clustering.** Large tables without clustering keys force full scans on common filters. Cluster on the most selective filter columns (date, region, tenant).
5. **PII in the open.** Loading source data with names, emails, or SSNs into a raw layer accessible to all analysts. Apply dynamic data masking or column-level security from day one.
6. **No cost monitoring.** Cloud warehouse costs grow silently. Set up cost alerts, per-warehouse budgets, and query cost attribution from the start.

---

## Checklist

- [ ] Layer architecture is implemented (raw → staging → intermediate → marts)
- [ ] Each layer has defined access controls (role-based grants)
- [ ] ETL, analyst, and dashboard workloads run on separate compute
- [ ] Auto-suspend and auto-resume are configured on all warehouses
- [ ] Tables are partitioned/clustered on frequently filtered columns
- [ ] PII and sensitive data are masked or access-controlled in every layer
- [ ] Data retention policies are defined for raw and staging layers
- [ ] Naming conventions follow the `raw_`, `stg_`, `int_`, `fct_`, `dim_` pattern
- [ ] Cost monitoring and per-warehouse budgets are configured
- [ ] A warehouse provisioning policy governs compute resource creation
