# Pipeline Specification: [Pipeline Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Engineer name]           |
| Related links | [Task / design spec links]     |
| Status        | Draft / Reviewed / Approved    |

*Specification for a data pipeline covering source, transformation, target, and operational requirements. Write this before coding to surface unknowns and align with stakeholders.*

---

## Pipeline Overview

- **Purpose:** [What business need does this pipeline serve?]
- **Source(s):** [Source system(s), table(s), API(s)]
- **Target:** [Destination table(s), dataset(s), or service(s)]
- **Refresh cadence:** [Real-time / Hourly / Daily / Weekly]
- **Processing mode:** [Batch / Streaming / Micro-batch]

---

## Source Specification

| Source | System | Format | Access Method | Refresh Cadence | SLA |
|--------|--------|--------|---------------|-----------------|-----|
| [e.g., orders] | [e.g., PostgreSQL] | [e.g., relational] | [e.g., CDC via Debezium] | [e.g., real-time] | [e.g., <5min lag] |

**Source schema:** [Link to schema definition or inline DDL]

---

## Transformation Logic

| Step | Description | Input | Output | Logic Summary |
|------|-------------|-------|--------|---------------|
| 1 | [e.g., Deduplicate on order_id] | [raw_orders] | [deduped_orders] | [Keep latest by updated_at] |
| 2 | [e.g., Join with customers] | [deduped_orders, dim_customer] | [enriched_orders] | [Left join on customer_id] |
| 3 | [e.g., Apply business rules] | [enriched_orders] | [fact_orders] | [Calculate total with tax] |

---

## Target Specification

| Target Table | Schema | Partition Key | Clustering Key | Write Mode |
|-------------|--------|---------------|----------------|------------|
| [e.g., warehouse.fact_orders] | [Link or inline] | [e.g., order_date] | [e.g., customer_id] | [e.g., Upsert on order_id] |

---

## Data Quality Checks

| Check | Type | Threshold | Action on Failure |
|-------|------|-----------|-------------------|
| [e.g., Row count delta] | [Anomaly] | [<20% variance] | [Alert + block downstream] |
| [e.g., Null rate on order_id] | [Completeness] | [0%] | [Fail pipeline] |
| [e.g., Total amount range] | [Validity] | [>0 and <1M] | [Dead-letter flagged rows] |

---

## Orchestration

- **DAG name:** [e.g., daily_orders_pipeline]
- **Schedule:** [e.g., 0 2 * * * (daily at 02:00 UTC)]
- **Dependencies:** [Upstream DAGs or datasets that must complete first]
- **Retry policy:** [e.g., 3 retries with 5-minute exponential backoff]
- **SLA:** [e.g., Complete by 04:00 UTC]
- **Alerting:** [e.g., Slack #data-alerts on failure or SLA breach]

---

## Risks and Unknowns

| Risk / Unknown | Impact | Mitigation |
|----------------|--------|------------|
| [e.g., Source schema may change without notice] | [High] | [Add schema drift detection at ingestion] |
| [e.g., Volume spike during promotions] | [Medium] | [Auto-scaling + backpressure handling] |

---

## Dependencies

- [ ] [e.g., Source system access credentials provisioned]
- [ ] [e.g., Target table created with migration script]
- [ ] [e.g., Orchestrator configured with required connections]
