# Model Versioning & Deployment

Guidelines for managing model lifecycle from registry to production, including
versioning, promotion, deployment strategies, and monitoring.

---

## Model Registry

### Model Metadata

Every registered model must include:

| Field | Description |
|-------|-------------|
| **Model name** | Unique identifier following `<domain>-<task>` (e.g., `fraud-detection`, `churn-predictor`) |
| **Version** | Auto-incremented integer or semantic version |
| **Stage** | Development → Staging → Production → Archived |
| **Training run ID** | Link back to the experiment tracking run |
| **Dataset version** | Version of training data used |
| **Metrics** | Performance scores on evaluation datasets |
| **Signature** | Input/output schema (feature names, types, shapes) |
| **Dependencies** | Pinned library versions required for inference |
| **Owner** | Team or individual responsible for the model |
| **Changelog** | What changed from the previous version |

### MLflow Model Registration

```python
import mlflow

# Register a model from a training run
model_uri = f"runs:/{run_id}/model"
model_details = mlflow.register_model(
    model_uri=model_uri,
    name="churn-predictor",
    tags={
        "dataset_version": "v3.1",
        "training_run_id": run_id,
        "owner": "ml-platform",
    },
)

# Promote to staging
client = mlflow.tracking.MlflowClient()
client.transition_model_version_stage(
    name="churn-predictor",
    version=model_details.version,
    stage="Staging",
)
```

### Stage Transitions

```
Development ──▶ Staging ──▶ Production ──▶ Archived
     │              │             │
     │         Validation    Monitoring
     │         gate runs     detects
     │              │        degradation
     │              ▼             │
     │         Automated          ▼
     │         tests pass    Rollback or
     │                       retrain
     ▼
  Rejected
  (failed validation)
```

**Development → Staging:** Requires passing automated validation (accuracy above
threshold, no bias regression, input/output schema valid).

**Staging → Production:** Requires successful shadow deployment or A/B test, load
testing under production traffic patterns, and sign-off from the model owner.

**Production → Archived:** Triggered by a newer version reaching Production or
by model retirement. Archived models remain available for audit and rollback.

---

## Validation Gates

### Pre-Deployment Checks

```python
from dataclasses import dataclass


@dataclass
class ValidationResult:
    passed: bool
    checks: dict[str, bool]
    details: dict[str, str]


def validate_model_for_promotion(
    model_name: str,
    model_version: int,
    baseline_version: int | None = None,
) -> ValidationResult:
    """Run validation gates before promoting a model."""
    checks = {}

    # 1. Performance threshold
    metrics = load_metrics(model_name, model_version)
    checks["accuracy_threshold"] = metrics["test_accuracy"] >= 0.85
    checks["auc_threshold"] = metrics["test_auc"] >= 0.80

    # 2. No regression vs. baseline
    if baseline_version:
        baseline_metrics = load_metrics(model_name, baseline_version)
        checks["no_accuracy_regression"] = (
            metrics["test_accuracy"] >= baseline_metrics["test_accuracy"] - 0.01
        )

    # 3. Bias check
    bias_report = run_bias_analysis(model_name, model_version)
    checks["bias_check"] = all(
        group_metric >= 0.80 for group_metric in bias_report.values()
    )

    # 4. Input/output schema valid
    checks["schema_valid"] = validate_model_signature(model_name, model_version)

    # 5. Latency benchmark
    latency = benchmark_inference_latency(model_name, model_version)
    checks["latency_p99"] = latency["p99_ms"] <= 100

    return ValidationResult(
        passed=all(checks.values()),
        checks=checks,
        details={k: "PASS" if v else "FAIL" for k, v in checks.items()},
    )
```

### Bias & Fairness

- Evaluate model performance across protected groups (gender, age, ethnicity where applicable).
- Set minimum performance thresholds per group (e.g., AUC >= 0.80 for every demographic segment).
- Log bias metrics alongside accuracy metrics in the model registry.
- Re-evaluate bias when training data changes or the model is retrained.

---

## Deployment Strategies

### Shadow Deployment

Run the new model in parallel with the production model. Both receive the same
traffic, but only the production model's predictions are served to users.

```yaml
# Shadow deployment configuration
deployment:
  name: churn-predictor
  primary:
    model: churn-predictor
    version: 5
    traffic: 100%    # serves all responses
  shadow:
    model: churn-predictor
    version: 6
    traffic: 100%    # receives all requests, responses logged but not served
  comparison:
    metrics: [accuracy, latency_p99, prediction_distribution]
    duration: 7d
    auto_promote: false
```

### Canary Deployment

Gradually shift traffic from the old model to the new model, monitoring for regressions.

```yaml
# Canary rollout stages
deployment:
  name: fraud-detector
  canary:
    model_version: 12
    stages:
      - traffic_percent: 5
        duration: 1h
        rollback_if:
          error_rate_increase: 0.5%
          latency_p99_increase: 20ms
      - traffic_percent: 25
        duration: 4h
        rollback_if:
          accuracy_drop: 1%
      - traffic_percent: 50
        duration: 12h
      - traffic_percent: 100
        duration: 24h
        # Full rollout after 24h observation
```

### A/B Testing

For models where business metrics matter more than offline accuracy:

```yaml
# A/B test configuration
experiment:
  name: recommendation-model-v7
  control:
    model: recommendation-v6
    traffic: 50%
  treatment:
    model: recommendation-v7
    traffic: 50%
  primary_metric: conversion_rate
  guardrail_metrics: [latency_p99, error_rate]
  duration: 14d
  min_sample_size: 10000
```

---

## Model Monitoring

### What to Monitor

| Signal | What It Detects | Alert Threshold |
|--------|----------------|-----------------|
| **Prediction distribution** | Model behavior shift | KL divergence > 0.1 vs. baseline |
| **Feature drift** | Input data distribution change | PSI > 0.2 on any feature |
| **Accuracy (when labels available)** | Model degradation | Accuracy drops > 2% from baseline |
| **Latency** | Infrastructure or model issues | p99 > SLA threshold |
| **Error rate** | Service failures | > 0.1% error rate |
| **Traffic volume** | Anomalous usage patterns | > 3 standard deviations from norm |

### Monitoring Implementation

```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import (
    DataDriftPreset,
    TargetDriftPreset,
)


def generate_drift_report(
    reference_data,
    production_data,
    feature_columns: list[str],
    target_column: str | None = None,
) -> Report:
    """Generate a data drift report comparing production to reference."""
    column_mapping = ColumnMapping(
        target=target_column,
        numerical_features=[c for c in feature_columns if c.startswith("num_")],
        categorical_features=[c for c in feature_columns if c.startswith("cat_")],
    )

    report = Report(metrics=[
        DataDriftPreset(),
        TargetDriftPreset() if target_column else None,
    ])
    report.run(
        reference_data=reference_data,
        current_data=production_data,
        column_mapping=column_mapping,
    )
    return report
```

### Retraining Triggers

Automate retraining based on monitoring signals:

- **Scheduled:** Retrain on a fixed cadence (weekly, monthly) with fresh data.
- **Drift-triggered:** Retrain when feature drift or prediction drift exceeds thresholds.
- **Performance-triggered:** Retrain when labeled outcomes show accuracy degradation.
- **Data-triggered:** Retrain when a new version of the training dataset is published.

Always validate the retrained model through the full promotion pipeline before
replacing the production model.

---

## Rollback

### Rollback Procedure

1. Identify the last known-good model version from the registry.
2. Switch the serving endpoint to the previous version (instant for model servers with version routing).
3. Log the rollback event with the reason and the failing model version.
4. Investigate root cause — do not simply retrain and redeploy without understanding the failure.

```python
def rollback_model(model_name: str, target_version: int) -> None:
    """Roll back a model to a previous version."""
    client = mlflow.tracking.MlflowClient()

    # Demote current production version
    current_prod = get_production_version(model_name)
    if current_prod:
        client.transition_model_version_stage(
            name=model_name,
            version=current_prod,
            stage="Archived",
        )

    # Promote target version back to production
    client.transition_model_version_stage(
        name=model_name,
        version=target_version,
        stage="Production",
    )

    # Log rollback event
    log_rollback_event(
        model_name=model_name,
        from_version=current_prod,
        to_version=target_version,
    )
```

### Rollback Testing

- Test the rollback procedure in staging before every production deployment.
- Ensure the previous model version's serving infrastructure is still available (container images, feature dependencies).
- Verify that rollback completes within the agreed SLA (typically < 5 minutes).
