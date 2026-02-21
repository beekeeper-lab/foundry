# Data Quality

Standards for validating, monitoring, and enforcing data quality across pipelines
and warehouse tables. Quality checks are built into every pipeline, not bolted on
after the fact.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Framework** | dbt tests (schema tests + custom singular tests) | Great Expectations for non-dbt pipelines; Soda for SQL-native checks |
| **Test location** | Co-located with transformation code in the same repo | Centralized quality repo only for cross-team shared assertions |
| **Test types** | `not_null`, `unique`, `accepted_values`, `relationships` on every model | Custom SQL tests for complex business rules |
| **Freshness** | dbt source freshness checks on every raw table | Airflow sensors or custom freshness monitors for non-dbt sources |
| **Anomaly detection** | Row count and value range checks with static thresholds | Statistical anomaly detection (e.g., Monte Carlo, Lightup) for high-value tables |
| **Failure handling** | Block downstream models on test failure (dbt `--fail-fast`) | Warn-only for non-critical tests (`severity: warn` in dbt) |
| **Documentation** | Every column has a description in the dbt schema YAML | — |

---

## Do / Don't

- **Do** test every model, not just final marts. Bugs in staging models propagate silently if untested.
- **Do** assert uniqueness and not-null on primary keys of every model. This is the minimum bar.
- **Do** check referential integrity between fact and dimension tables using `relationships` tests.
- **Do** monitor source freshness. A pipeline that succeeds on stale data is worse than one that fails — it produces silently wrong results.
- **Do** set row count thresholds that alert when a table grows or shrinks unexpectedly (e.g., daily orders drop to zero).
- **Do** treat data quality tests as first-class CI. Run them on pull requests against a development warehouse.
- **Don't** rely solely on schema-level tests. Business rule validation (e.g., "revenue is never negative", "end_date >= start_date") catches errors that schema tests miss.
- **Don't** skip tests in production to "speed up" the pipeline. Tests are the only thing standing between bad data and business decisions.
- **Don't** test with outdated or synthetic data that doesn't reflect production patterns. Use a production-like sample.
- **Don't** ignore test failures. Every failure is either a real data issue or a poorly written test — both need resolution.

---

## Common Pitfalls

1. **Testing only the happy path.** Tests that validate expected values but don't check for nulls, duplicates, or out-of-range data miss the most common failure modes.
2. **Stale freshness thresholds.** A freshness check set to 24 hours doesn't catch a source that normally updates hourly. Tune thresholds to the actual update frequency.
3. **Alert fatigue.** Too many warn-level tests that fire constantly. Teams stop reading alerts. Keep critical tests as errors (blocking) and prune or fix noisy warnings.
4. **No data contract with upstream.** Source teams change schemas or semantics without notice. Establish explicit data contracts with schema, freshness, and quality SLAs.
5. **Missing coverage on derived columns.** Computed columns (margins, ratios, age calculations) are often untested. Add assertion tests for business-critical derived values.
6. **Quality checks only at load time.** Data can degrade over time (late-arriving corrections, retroactive updates). Schedule periodic full-table scans for high-value datasets.

---

## Checklist

- [ ] Every model has `not_null` and `unique` tests on its primary key
- [ ] Referential integrity tests exist between facts and dimensions
- [ ] Source freshness is monitored with thresholds tuned to actual update frequency
- [ ] Row count anomaly detection is configured for critical tables
- [ ] Business rule assertions cover derived and computed columns
- [ ] Data quality tests run in CI on pull requests
- [ ] Test failures in production block downstream models (not just warn)
- [ ] Data contracts with upstream sources are documented and version-controlled
- [ ] Alert routing is configured — critical failures page on-call, warnings go to a channel
- [ ] Column-level documentation exists for every model in the schema YAML
