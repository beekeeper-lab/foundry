# Model Training & Experiment Tracking

Guidelines for building reproducible training pipelines and systematic experiment
tracking across the ML lifecycle.

---

## Training Pipeline Architecture

### Pipeline Stages

Every training pipeline follows this stage sequence:

1. **Data ingestion** — Pull versioned data from the offline store or data lake.
2. **Data validation** — Verify schema, distributions, nulls, and freshness.
3. **Feature engineering** — Compute features using shared transformation code.
4. **Model training** — Train the model with logged hyperparameters.
5. **Model evaluation** — Score against holdout sets; compare to baseline.
6. **Artifact registration** — Push model + metadata to the model registry.

```yaml
# Example: Kubeflow pipeline definition
apiVersion: pipelines/v1
kind: Pipeline
metadata:
  name: training-pipeline
steps:
  - name: ingest-data
    image: ml-pipelines/data-ingest:v1.2
    params:
      dataset_version: "2026-02-01"
      source: "s3://data-lake/features/v3/"
  - name: validate-data
    image: ml-pipelines/data-validate:v1.0
    depends_on: [ingest-data]
    params:
      expectations_suite: "training_data_v3"
  - name: train-model
    image: ml-pipelines/trainer:v2.1
    depends_on: [validate-data]
    resources:
      gpu: 1
      memory: 16Gi
    params:
      experiment_name: "churn-prediction"
      hyperparams:
        learning_rate: 0.001
        batch_size: 256
        epochs: 50
  - name: evaluate-model
    image: ml-pipelines/evaluator:v1.3
    depends_on: [train-model]
    params:
      baseline_run_id: "abc123"
      min_accuracy: 0.85
      max_drift: 0.05
  - name: register-model
    image: ml-pipelines/registry:v1.1
    depends_on: [evaluate-model]
    params:
      model_name: "churn-predictor"
      stage: "staging"
```

### Data Validation

Validate training data before every run:

```python
# Great Expectations integration
import great_expectations as gx

context = gx.get_context()
checkpoint = context.get_checkpoint("training_data_checkpoint")
result = checkpoint.run(batch_parameters={"path": data_path})

if not result.success:
    raise DataValidationError(
        f"Training data failed validation: {result.describe()}"
    )
```

Key validations:
- **Schema:** Column names, types, and order match the expected feature set.
- **Distributions:** Feature value ranges fall within historical bounds (no extreme drift).
- **Completeness:** Null rates stay below configured thresholds per column.
- **Freshness:** Data timestamp is within the expected recency window.
- **Volume:** Row count is within expected range (catches truncated or duplicated data).

---

## Experiment Tracking

### What to Log

Every experiment run must log:

| Category | Items |
|----------|-------|
| **Parameters** | All hyperparameters, random seeds, model architecture choices |
| **Data** | Dataset version, split ratios, sampling strategy, preprocessing hash |
| **Metrics** | Loss curves, accuracy/F1/AUC on train/val/test, latency benchmarks |
| **Artifacts** | Model weights, confusion matrices, feature importance plots, sample predictions |
| **Environment** | Docker image tag, GPU type, Python version, dependency lock file hash |
| **Metadata** | Git commit SHA, author, experiment intent (baseline/ablation/hyperopt), wall-clock time |

```python
import mlflow

with mlflow.start_run(run_name="churn-v3-lr-sweep") as run:
    mlflow.set_tags({
        "git_commit": "a1b2c3d",
        "dataset_version": "v3.1",
        "experiment_type": "hyperparameter-search",
    })
    mlflow.log_params({
        "learning_rate": 0.001,
        "batch_size": 256,
        "epochs": 50,
        "model_architecture": "gradient-boosting",
    })

    model, metrics = train(config)

    mlflow.log_metrics({
        "train_accuracy": metrics["train_acc"],
        "val_accuracy": metrics["val_acc"],
        "test_accuracy": metrics["test_acc"],
        "val_auc": metrics["val_auc"],
        "training_time_seconds": metrics["wall_time"],
    })
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("feature_importance.json")
    mlflow.sklearn.log_model(model, "model")
```

### Experiment Organization

- **One experiment per project/problem** (e.g., `churn-prediction`, `fraud-detection`).
- **Run names** include the intent and key variable: `baseline-xgboost`, `lr-sweep-0.01-0.1`, `ablation-no-embeddings`.
- **Tags** distinguish run types: `baseline`, `hyperparameter-search`, `ablation`, `production-candidate`.
- **Parent–child runs** group hyperparameter sweeps. The parent run holds the sweep configuration; children hold individual trial results.

### Hyperparameter Optimization

```python
import optuna

def objective(trial):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-1, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
    }

    with mlflow.start_run(nested=True, run_name=f"trial-{trial.number}"):
        mlflow.log_params(params)
        model, metrics = train(params)
        mlflow.log_metrics(metrics)
        return metrics["val_auc"]

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100, timeout=3600)
```

---

## Reproducibility

### Environment Pinning

```dockerfile
# Training Dockerfile
FROM nvidia/cuda:12.2-runtime-ubuntu22.04

COPY requirements.lock /app/requirements.lock
RUN pip install --no-deps -r /app/requirements.lock

COPY src/ /app/src/
ENV PYTHONHASHSEED=42
WORKDIR /app
ENTRYPOINT ["python", "-m", "trainer.main"]
```

### Seed Management

```python
import random
import numpy as np
import torch

def set_seed(seed: int = 42) -> None:
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### Data Versioning with DVC

```bash
# Track a training dataset
dvc add data/training/v3/features.parquet
git add data/training/v3/features.parquet.dvc .gitignore
git commit -m "Track training data v3"

# Reproduce a pipeline
dvc repro training_pipeline.yaml
```

---

## GPU Resource Management

- Request specific GPU types in pipeline configs (`nvidia.com/gpu: 1`, `gpu_type: a100`).
- Use spot/preemptible instances for hyperparameter sweeps and ablation studies.
- Set `idle_timeout` on GPU clusters to prevent cost runaway from abandoned jobs.
- Profile GPU memory usage before scaling. Many models fit on smaller GPUs than assumed.
- Use gradient accumulation and mixed precision (`torch.cuda.amp`) to reduce memory requirements.
