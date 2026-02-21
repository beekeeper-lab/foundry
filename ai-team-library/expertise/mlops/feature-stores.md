# Feature Stores

Guidelines for managing, versioning, and serving ML features consistently across
training and inference workloads.

---

## Why Feature Stores

Feature stores solve three problems:

1. **Training–serving skew.** Features computed differently in training and serving produce silent model degradation. A feature store guarantees identical transformations.
2. **Feature duplication.** Multiple teams recompute the same features independently, wasting compute and introducing inconsistencies. A shared store provides reusable, governed features.
3. **Point-in-time correctness.** Training on features computed without respecting event timestamps causes data leakage. Feature stores enforce point-in-time joins.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Feature Store                      │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Offline Store │  │ Online Store  │                 │
│  │ (BigQuery /   │  │ (Redis /      │                 │
│  │  S3+Parquet)  │  │  DynamoDB)    │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                  │                         │
│  ┌──────▼───────┐  ┌──────▼───────┐                 │
│  │  Training     │  │  Serving      │                 │
│  │  (batch read) │  │  (low-latency │                 │
│  │               │  │   point read) │                 │
│  └──────────────┘  └──────────────┘                 │
│                                                      │
│  ┌──────────────────────────────────┐               │
│  │  Feature Registry (definitions,  │               │
│  │  owners, lineage, documentation) │               │
│  └──────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Offline vs. Online

| Aspect | Offline Store | Online Store |
|--------|--------------|-------------|
| **Purpose** | Training, batch scoring, analytics | Real-time inference |
| **Latency** | Seconds to minutes | Single-digit milliseconds |
| **Storage** | Data lake (S3/GCS + Parquet, BigQuery, Snowflake) | Key-value store (Redis, DynamoDB) |
| **Query** | Point-in-time joins over historical data | Entity-key lookups for latest values |
| **Freshness** | Batch materialized (hourly/daily) | Streaming materialized or on-demand |

---

## Feature Definitions

### Naming Convention

Follow `<entity>_<feature>_<aggregation>_<window>`:

| Example | Meaning |
|---------|---------|
| `user_purchase_count_7d` | Number of purchases by a user in the last 7 days |
| `product_view_avg_price_30d` | Average price of products viewed in 30 days |
| `merchant_chargeback_rate_90d` | Chargeback rate for a merchant over 90 days |
| `user_session_duration_p95_1d` | 95th percentile session duration in the last day |

### Feast Feature Definition

```python
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64
from datetime import timedelta

# Entity definition
user = Entity(
    name="user_id",
    description="Unique user identifier",
    join_keys=["user_id"],
)

# Data source
user_features_source = FileSource(
    path="s3://feature-data/user_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Feature view
user_activity_features = FeatureView(
    name="user_activity_features",
    entities=[user],
    ttl=timedelta(days=7),
    schema=[
        Field(name="purchase_count_7d", dtype=Int64),
        Field(name="avg_order_value_30d", dtype=Float32),
        Field(name="session_count_1d", dtype=Int64),
        Field(name="churn_risk_score", dtype=Float32),
    ],
    source=user_features_source,
    online=True,
    tags={
        "owner": "ml-platform",
        "domain": "user-behavior",
        "pii": "false",
    },
)
```

### Feature Documentation

Every feature must have:

| Field | Required | Description |
|-------|----------|-------------|
| **Name** | Yes | Following the naming convention |
| **Description** | Yes | Plain-English explanation of what the feature represents |
| **Owner** | Yes | Team or individual responsible for correctness |
| **Data source** | Yes | Upstream table or stream the feature is derived from |
| **Computation logic** | Yes | SQL, Python, or pseudocode for the transformation |
| **Update frequency** | Yes | How often the feature is refreshed |
| **SLA** | Yes | Maximum acceptable staleness |
| **PII flag** | Yes | Whether the feature contains or derives from PII |

---

## Materialization

### Batch Materialization

```python
from feast import FeatureStore
from datetime import datetime, timedelta

store = FeatureStore(repo_path="feature_repo/")

# Materialize features to the online store
store.materialize(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
)
```

Schedule materialization aligned with upstream data freshness:

- Run materialization **after** upstream ETL completes.
- Use Airflow sensors or event-driven triggers — not fixed cron schedules that may race.
- Monitor materialization latency and failure rates. Alert if materialization falls behind SLA.

### Streaming Materialization

For features requiring sub-minute freshness:

```python
# Streaming feature computation (conceptual)
from feast import StreamFeatureView

stream_view = StreamFeatureView(
    name="user_realtime_features",
    entities=[user],
    schema=[
        Field(name="click_count_5min", dtype=Int64),
        Field(name="cart_value_current", dtype=Float32),
    ],
    source=kafka_source,
    aggregations=[
        Aggregation(column="clicks", function="count", time_window=timedelta(minutes=5)),
    ],
    online=True,
)
```

---

## Training & Serving Integration

### Training: Point-in-Time Joins

```python
import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Entity dataframe with timestamps for point-in-time correctness
entity_df = pd.DataFrame({
    "user_id": [1001, 1002, 1003],
    "event_timestamp": [
        pd.Timestamp("2026-01-15"),
        pd.Timestamp("2026-01-16"),
        pd.Timestamp("2026-01-17"),
    ],
})

# Get historical features — respects point-in-time semantics
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_activity_features:purchase_count_7d",
        "user_activity_features:avg_order_value_30d",
        "user_activity_features:churn_risk_score",
    ],
).to_df()
```

### Serving: Online Lookup

```python
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo/")

# Low-latency feature retrieval for inference
features = store.get_online_features(
    features=[
        "user_activity_features:purchase_count_7d",
        "user_activity_features:avg_order_value_30d",
        "user_activity_features:churn_risk_score",
    ],
    entity_rows=[{"user_id": 1001}],
).to_dict()
```

---

## Data Quality & Monitoring

### Feature Validation

```python
def validate_features(feature_df: pd.DataFrame, expectations: dict) -> list[str]:
    """Validate feature values against expected ranges."""
    violations = []
    for col, rules in expectations.items():
        if col not in feature_df.columns:
            violations.append(f"Missing feature: {col}")
            continue
        if "min" in rules and feature_df[col].min() < rules["min"]:
            violations.append(f"{col} below minimum: {feature_df[col].min()}")
        if "max" in rules and feature_df[col].max() > rules["max"]:
            violations.append(f"{col} above maximum: {feature_df[col].max()}")
        if "null_rate" in rules:
            actual_null_rate = feature_df[col].isnull().mean()
            if actual_null_rate > rules["null_rate"]:
                violations.append(f"{col} null rate {actual_null_rate:.2%} exceeds threshold")
    return violations
```

### Feature Drift Detection

Monitor feature distributions in production against training baselines:

- **Population Stability Index (PSI)** — detect distribution shifts. Alert when PSI > 0.2.
- **Null rate monitoring** — sudden null spikes indicate upstream pipeline failures.
- **Cardinality changes** — unexpected new categories in categorical features.
- **Freshness monitoring** — alert when features are older than their SLA.
