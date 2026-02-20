# ETL/ELT Pipelines

Patterns and standards for building data extraction, transformation, and loading
pipelines. ELT (extract-load-transform) is the default approach for cloud
warehouses; ETL is appropriate when transformations must happen before landing.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Approach** | ELT — load raw data, transform in warehouse | ETL when source cleanup or PII redaction must happen before landing |
| **Extraction** | Incremental (CDC or watermark column) | Full refresh for small dimensions or when source lacks reliable watermark |
| **Loading** | Append to raw/staging layer, merge into target | Overwrite-partition for immutable event data |
| **Transformation** | dbt models in SQL | Spark/PySpark for non-SQL transformations or multi-TB datasets |
| **Scheduling** | Airflow DAGs with explicit dependencies | Prefect or Dagster when Airflow operational overhead is too high |
| **Idempotency** | Every pipeline run produces the same result for the same inputs | — |
| **File format** | Parquet (columnar, compressed) for staging/lake | CSV only for external system interchange; Avro for streaming |

---

## Do / Don't

- **Do** design every pipeline to be idempotent. Re-running a pipeline for the same date/partition must not produce duplicates or data loss.
- **Do** use watermark columns (`updated_at`, `modified_date`) for incremental extraction rather than relying on source-side CDC unless CDC is explicitly provisioned.
- **Do** land raw data unmodified in a staging layer before transforming. Never transform in-flight during extraction.
- **Do** version your transformation logic in source control alongside the pipeline definition.
- **Do** log row counts at extraction, loading, and transformation stages for reconciliation.
- **Don't** build pipelines that silently drop rows. Failed records go to a dead-letter table with the error reason.
- **Don't** hard-code connection strings, credentials, or environment-specific paths. Use environment variables or a secrets manager.
- **Don't** depend on source system ordering. Always sort or deduplicate explicitly.
- **Don't** schedule pipelines without alerting. Every pipeline must have a failure notification channel.
- **Don't** mix business logic into extraction code. Extraction reads; transformation applies logic.

---

## Common Pitfalls

1. **Late-arriving data.** Pipelines that close a partition at midnight miss records arriving after the cutoff. Use a lookback window (e.g., re-process the previous 3 days) or switch to CDC.
2. **Schema drift.** Source systems add or rename columns without notice. Validate incoming schemas against an expected contract and alert on mismatch before loading.
3. **Silent duplicates.** Append-only loads without deduplication create duplicate rows when a pipeline is retried. Use `MERGE`/`UPSERT` or deduplicate in the transformation layer with a deterministic key.
4. **Monolith pipelines.** A single DAG that extracts from 20 sources, transforms, and loads makes debugging and reprocessing painful. Decompose into one DAG per source-to-target path.
5. **Ignoring backfill.** Pipelines designed only for daily incremental loads break when you need to reload six months of history. Design for parameterized date ranges from day one.
6. **Tight coupling to source schemas.** Mapping source columns directly to warehouse columns means every upstream change breaks your pipeline. Use a staging layer as a buffer.

---

## Checklist

- [ ] Pipeline is idempotent — re-runs produce identical results
- [ ] Raw data lands unmodified in a staging/raw layer
- [ ] Incremental extraction uses a reliable watermark or CDC mechanism
- [ ] Row counts are logged at each stage for reconciliation
- [ ] Failed records are routed to a dead-letter table, not silently dropped
- [ ] Schemas are validated against an expected contract before loading
- [ ] Pipeline supports parameterized date ranges for backfill
- [ ] No hard-coded credentials or environment-specific paths
- [ ] Failure alerting is configured for every scheduled pipeline
- [ ] Transformation logic is version-controlled and tested
