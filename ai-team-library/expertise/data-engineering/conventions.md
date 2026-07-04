---
id: data-engineering
category: Data & ML
entry: true
last-reviewed: 2026-07
---

# Data Engineering Conventions

## Category
Data & ML

These conventions govern pipelines, orchestration, warehouse layering, dimensional
modeling, and data quality for this team's data platforms. ELT into a cloud
warehouse with dbt transformations is the default; deviations require an ADR.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| Approach | ELT — load raw, transform in warehouse | ETL when PII redaction must happen before landing |
| Platform | Snowflake | BigQuery (GCP-native); Redshift (AWS-native) |
| Layer architecture | Raw → Staging → Intermediate → Marts | Two-layer only for very simple use cases |
| Modeling methodology | Kimball dimensional (star schema) | Data Vault 2.0 for audit-heavy multi-source integration |
| Transformation | dbt models in SQL | Spark/PySpark for non-SQL or multi-TB workloads |
| Orchestrator | Apache Airflow 2.x (managed preferred) | Dagster (asset-centric); Prefect (lightweight/event-driven) |
| Extraction | Incremental (CDC or watermark column) | Full refresh for small dimensions |
| Quality framework | dbt tests co-located with transformation code | Great Expectations for non-dbt pipelines |
| File format | Parquet for staging/lake | CSV only for external interchange; Avro for streaming |
| Naming | `raw_<source>`, `stg_<source>__<entity>`, `int_`, `fct_`, `dim_` | `hub_`/`sat_`/`lnk_` for Data Vault |
| SCDs | Type 2 with `valid_from`/`valid_to`/`is_current` | Type 1 (overwrite) when history is not needed |

---

## 1. Pipelines

- Every pipeline is **idempotent** — re-running for the same date/partition never
  produces duplicates or data loss.
- Land raw data **unmodified** in a staging layer before transforming; never
  transform in-flight during extraction.
- Failed records go to a **dead-letter table** with the error reason, never
  silently dropped.
- Validate incoming schemas against an expected contract and alert on mismatch
  before loading (schema drift defense).
- Log row counts at extraction, load, and transform stages for reconciliation.
- Design for parameterized date ranges from day one so backfills are routine,
  not emergencies. Use a lookback window (or CDC) for late-arriving data.

Full detail: `pipelines.md`

---

## 2. Orchestration

- One DAG per source-to-target pipeline; DAG files define dependencies and
  config, not business logic (logic lives in modules or dbt).
- Every task gets `retries=2`, `retry_delay`, and an explicit `execution_timeout`.
- `catchup=False` unless backfill on deploy is explicitly intended; use
  `execution_date`/`logical_date` partitioning so re-runs hit the right window.
- Credentials via Airflow connections/variables or a secrets backend — never
  hard-coded in DAG files.
- Keep DAG parsing lightweight: no API calls or DB queries at import time.
- Offload heavy computation to Spark, the warehouse, or containers — Airflow is
  an orchestrator, not a compute engine.

Full detail: `orchestration.md`

---

## 3. Warehouse Design

- Data flows only from lower to higher layers (raw → staging → marts); every
  table belongs to exactly one layer with role-based grants per layer.
- Isolate compute: separate warehouses for ETL, analysts, and dashboards.
- Auto-suspend/auto-resume on every Snowflake warehouse; cost alerts and
  per-warehouse budgets from the start.
- Partition/cluster large tables on frequently filtered columns (date, tenant).
- Mask or access-control PII from day one — never load raw PII into a layer all
  analysts can read.

Full detail: `warehouse-design.md`

---

## 4. Data Modeling

- **Document the grain of every fact table** — it is the most important decision
  in dimensional modeling. Never mix grain in one fact table.
- Facts join dimensions via integer surrogate keys, never natural keys.
- Build conformed dimensions shared across facts, each with a single owner.
- Maintain a `dim_date` table with fiscal periods and holidays; never compute
  date logic in queries.
- Verify join cardinality is many-to-one (fact → dimension) to avoid fan-out.

Full detail: `data-modeling.md`

---

## 5. Data Quality

- Minimum bar: `not_null` + `unique` tests on every model's primary key, and
  `relationships` tests between facts and dimensions.
- Monitor source freshness with thresholds tuned to actual update frequency —
  a pipeline succeeding on stale data is worse than one that fails.
- Test failures in production **block downstream models**; warn-only is reserved
  for non-critical checks (and noisy warnings get pruned).
- Add business-rule assertions for derived columns (e.g., "revenue never
  negative"); schema tests alone are not enough.
- Quality tests run in CI on pull requests against a development warehouse.

Full detail: `data-quality.md`

---

## Do / Don't

**Do:**
- Make every pipeline re-runnable for the same inputs with identical results.
- Separate staging models (source mirrors) from business-ready marts.
- Use watermark columns or CDC for incremental extraction.
- Version transformation logic in source control alongside pipeline definitions.
- Configure failure alerting for every scheduled pipeline.

**Don't:**
- Skip the staging layer — it decouples the warehouse from source schemas.
- Build "one big table" denormalized models as the primary layer.
- Put business logic in extraction code or in DAG files.
- Hard-code credentials or environment-specific paths.
- Grant analysts write access to raw or staging layers.

---

## Common Pitfalls

1. **Undefined grain** — ambiguous grain produces wrong aggregations and erodes
   trust. State it in docs and enforce with uniqueness tests.
2. **Silent duplicates** — append-only loads retried without dedup. Use
   `MERGE`/`UPSERT` or deduplicate with a deterministic key.
3. **Late-arriving data** — midnight partition cutoffs miss records. Reprocess a
   lookback window or use CDC.
4. **Scheduler overload** — heavy top-level DAG code and mega-DAGs slow Airflow.
5. **Alert fatigue** — constant warn-level noise trains the team to ignore
   alerts. Keep critical tests blocking; fix or prune the rest.
6. **No cost monitoring** — cloud warehouse spend grows silently without
   budgets, auto-suspend, and query cost attribution.

---

## Checklist

- [ ] Pipeline is idempotent and supports parameterized backfill ranges
- [ ] Raw data lands unmodified; layer architecture enforced with per-layer grants
- [ ] Every fact table has a documented grain and surrogate-key joins
- [ ] Every model has `not_null`/`unique` PK tests; facts↔dims have relationship tests
- [ ] Source freshness monitored; failures block downstream models
- [ ] Every Airflow task has retries and an execution timeout; `catchup=False`
- [ ] No hard-coded credentials; secrets via connections/vault
- [ ] Failure alerting wired for every scheduled pipeline
- [ ] ETL, analyst, and dashboard workloads on separate compute with cost budgets
- [ ] PII masked or access-controlled in every layer
