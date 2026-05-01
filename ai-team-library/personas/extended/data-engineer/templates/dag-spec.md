# DAG Specification: [DAG Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Engineer name]           |
| Related links | [Task / pipeline spec links]   |
| Status        | Draft / Reviewed / Approved    |

*Orchestration DAG definition covering task dependencies, scheduling, retry policies, and SLA requirements.*

---

## DAG Overview

- **DAG ID:** [e.g., daily_orders_pipeline]
- **Purpose:** [What this DAG orchestrates and why]
- **Schedule:** [e.g., 0 2 * * * (daily at 02:00 UTC)]
- **Catchup:** [Yes / No]
- **Max active runs:** [e.g., 1]
- **Tags:** [e.g., production, orders, daily]

---

## Task Definitions

| Task ID | Operator | Description | Retry | Timeout |
|---------|----------|-------------|-------|---------|
| [e.g., extract_orders] | [e.g., PythonOperator] | [Extract from source DB] | [3x, 5min backoff] | [30min] |
| [e.g., validate_source] | [e.g., DataQualityOperator] | [Run source quality checks] | [2x, 2min backoff] | [10min] |
| [e.g., transform_orders] | [e.g., PythonOperator] | [Apply business transformations] | [3x, 5min backoff] | [60min] |
| [e.g., validate_target] | [e.g., DataQualityOperator] | [Run target quality checks] | [2x, 2min backoff] | [10min] |
| [e.g., notify_complete] | [e.g., SlackOperator] | [Send completion notification] | [1x, 1min] | [5min] |

---

## Task Dependencies

```
extract_orders >> validate_source >> transform_orders >> validate_target >> notify_complete
```

*Or describe as a dependency table:*

| Task | Depends On |
|------|-----------|
| [validate_source] | [extract_orders] |
| [transform_orders] | [validate_source] |
| [validate_target] | [transform_orders] |
| [notify_complete] | [validate_target] |

---

## SLA & Alerting

| Metric | Threshold | Action |
|--------|-----------|--------|
| [DAG completion] | [By 04:00 UTC] | [Alert #data-alerts on breach] |
| [Task failure] | [Any task] | [Alert #data-alerts immediately] |
| [Long running task] | [>2x expected duration] | [Warning to #data-alerts] |

---

## Configuration & Connections

| Parameter | Value | Source |
|-----------|-------|--------|
| [e.g., source_db_conn] | [source_postgres] | [Airflow connection] |
| [e.g., target_db_conn] | [warehouse_postgres] | [Airflow connection] |
| [e.g., batch_size] | [10000] | [Airflow variable] |

---

## Failure & Recovery

- **On task failure:** [Retry with backoff, then alert on final failure]
- **On SLA miss:** [Alert team, continue processing]
- **Manual recovery:** [Steps to manually trigger a backfill or rerun]
- **Dead-letter handling:** [Where rejected records go and how to reprocess]

---

## Testing Checklist

- [ ] DAG parses without errors
- [ ] Task dependencies are acyclic
- [ ] Each task is idempotent and safe to retry
- [ ] SLA alerting is configured and tested
- [ ] Backfill behavior is verified for historical date ranges
- [ ] Connection IDs exist in the target environment
