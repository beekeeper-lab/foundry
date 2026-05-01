# Pipeline Runbook: [Pipeline Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Engineer name]           |
| Related links | [Pipeline spec / DAG links]    |
| Status        | Draft / Reviewed / Approved    |

*Operational runbook for a data pipeline. Covers lineage, SLAs, monitoring, and troubleshooting procedures.*

---

## Pipeline Overview

- **Pipeline name:** [e.g., daily_orders_pipeline]
- **Purpose:** [One-sentence description of what the pipeline does]
- **Schedule:** [e.g., Daily at 02:00 UTC]
- **Expected duration:** [e.g., 45 minutes]
- **SLA:** [e.g., Complete by 04:00 UTC]
- **Owner:** [Team or individual responsible]
- **Alert channel:** [e.g., Slack #data-alerts]

---

## Data Lineage

### Source → Target Flow

```
[Source System A] ──→ [Staging Table] ──→ [Transform] ──→ [Target Table] ──→ [Downstream Consumer]
```

| Stage | System | Table / Dataset | Description |
|-------|--------|----------------|-------------|
| Source | [e.g., PostgreSQL (prod)] | [e.g., public.orders] | [Raw order data] |
| Staging | [e.g., Warehouse] | [e.g., staging.raw_orders] | [Ingested raw data] |
| Transform | [e.g., Warehouse] | [e.g., transform.clean_orders] | [Deduplicated and validated] |
| Target | [e.g., Warehouse] | [e.g., warehouse.fact_orders] | [Serving layer] |

### Downstream Consumers

| Consumer | Dataset Used | SLA Dependency |
|----------|-------------|----------------|
| [e.g., BI Dashboard] | [warehouse.fact_orders] | [Refreshes at 05:00 UTC] |
| [e.g., ML Feature Store] | [warehouse.fact_orders] | [Needs data by 04:30 UTC] |

---

## Monitoring

### Key Metrics

| Metric | Expected | Alert Threshold |
|--------|----------|-----------------|
| [Rows processed] | [~50K/day] | [< 10K or > 200K] |
| [Duration] | [~45min] | [> 90min] |
| [Error rate] | [< 0.1%] | [> 1%] |

### Where to Monitor

- **Orchestrator UI:** [e.g., Airflow at https://airflow.example.com/dags/daily_orders]
- **Metrics dashboard:** [Link to Grafana/Datadog dashboard]
- **Logs:** [e.g., CloudWatch log group /pipelines/daily_orders]

---

## Troubleshooting

### Common Failures

#### 1. [Source connection timeout]

**Symptoms:** Extract task fails with connection timeout error.

**Root cause:** Source database under heavy load or network connectivity issue.

**Resolution:**
1. Check source database health and current connections
2. Retry the failed task from the orchestrator UI
3. If persistent, check network connectivity and firewall rules
4. Escalate to source system DBA if the issue is on their side

#### 2. [Data quality check failure]

**Symptoms:** Quality validation task fails after transformation.

**Root cause:** Source data anomaly or transformation logic bug.

**Resolution:**
1. Check the quality check logs for specific failed assertions
2. Inspect the source data for the failing records
3. If source data anomaly: investigate with source team, add to dead-letter if appropriate
4. If transformation bug: fix logic, add test case, redeploy

#### 3. [SLA breach]

**Symptoms:** Pipeline completes after SLA deadline.

**Root cause:** Increased data volume, resource contention, or upstream delay.

**Resolution:**
1. Check pipeline task durations to identify the bottleneck
2. Check for upstream pipeline delays
3. If volume spike: consider adjusting batch sizes or parallelism
4. If resource contention: coordinate with other pipelines on scheduling
5. Notify downstream consumers of the delay

---

## Manual Operations

### Trigger a backfill

```bash
# [Example command to backfill a date range]
# airflow dags backfill daily_orders_pipeline --start-date 2024-01-01 --end-date 2024-01-31
```

### Manually reprocess failed records

```bash
# [Steps to reprocess records from dead-letter queue]
```

### Emergency stop

```bash
# [How to pause/stop the pipeline in case of emergency]
```

---

## Contacts

| Role | Name | Contact |
|------|------|---------|
| Pipeline owner | [Name] | [Slack / email] |
| Source system DBA | [Name] | [Slack / email] |
| On-call data engineer | [Rotation] | [PagerDuty / Slack] |
