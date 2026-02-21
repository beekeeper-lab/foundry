# Data Quality Checklist: [Dataset / Pipeline Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Engineer name]           |
| Related links | [Pipeline spec / task links]   |
| Status        | Draft / Reviewed / Approved    |

*Data quality validation rules for a dataset or pipeline output. Each rule becomes an automated check in the pipeline.*

---

## Dataset Overview

- **Dataset:** [e.g., warehouse.fact_orders]
- **Pipeline:** [e.g., daily_orders_pipeline]
- **Grain:** [What does one row represent?]
- **Expected volume:** [e.g., ~50K rows/day]
- **Refresh cadence:** [e.g., Daily]

---

## Completeness Checks

| Column | Rule | Threshold | Action on Failure |
|--------|------|-----------|-------------------|
| [e.g., order_id] | Not null | 100% | Fail pipeline |
| [e.g., customer_id] | Not null | 100% | Fail pipeline |
| [e.g., order_date] | Not null | 100% | Fail pipeline |
| [e.g., email] | Not null | >= 95% | Warn + continue |

---

## Uniqueness Checks

| Column(s) | Rule | Threshold | Action on Failure |
|-----------|------|-----------|-------------------|
| [e.g., order_id] | Unique | 100% | Fail pipeline |
| [e.g., customer_id, order_date] | Unique combination | >= 99.9% | Warn + investigate |

---

## Validity Checks

| Column | Rule | Expected | Action on Failure |
|--------|------|----------|-------------------|
| [e.g., total_amount] | Range | >= 0 and < 1,000,000 | Dead-letter flagged rows |
| [e.g., order_status] | Allowed values | [pending, confirmed, shipped, delivered, cancelled] | Fail pipeline |
| [e.g., email] | Format | Valid email regex | Warn + flag |

---

## Referential Integrity Checks

| From Table.Column | To Table.Column | Threshold | Action on Failure |
|-------------------|-----------------|-----------|-------------------|
| [fact_orders.customer_id] | [dim_customer.id] | 100% | Fail pipeline |
| [fact_orders.product_id] | [dim_product.id] | >= 99.5% | Warn + dead-letter |

---

## Volume & Freshness Checks

| Check | Rule | Threshold | Action on Failure |
|-------|------|-----------|-------------------|
| Row count | Daily delta vs previous day | < 50% variance | Alert + investigate |
| Row count | Minimum expected | > 0 rows | Fail pipeline |
| Freshness | Max age of newest record | < 25 hours | Alert + investigate |

---

## Distribution Checks

| Column | Metric | Expected Range | Action on Failure |
|--------|--------|----------------|-------------------|
| [e.g., total_amount] | Mean | [$50 - $200] | Warn + investigate |
| [e.g., order_status] | Cardinality | [3-5 distinct values] | Warn + investigate |
| [e.g., country_code] | Top-N distribution | [US > 40%] | Warn if anomalous |

---

## Automation Notes

- **Framework:** [e.g., Great Expectations / dbt tests / custom assertions]
- **Execution point:** [e.g., Post-transform, pre-load to serving layer]
- **Alert channel:** [e.g., Slack #data-quality-alerts]
- **Dashboard:** [Link to quality monitoring dashboard if available]
