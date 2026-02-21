# MLOps Stack Conventions

These conventions apply to all ML/AI and LLM operations projects on this team.
They are opinionated by design — consistency across training pipelines, model
registries, and inference services matters more than individual preference.
Deviations require an ADR with justification.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Experiment tracking** | MLflow Tracking (open-source, self-hosted) | Weights & Biases for richer experiment comparison; Neptune.ai for team-scale collaboration; ClearML for end-to-end orchestration |
| **Model registry** | MLflow Model Registry | SageMaker Model Registry in AWS-native orgs; Vertex AI Model Registry on GCP; custom registry backed by OCI artifact store |
| **Training orchestration** | Kubeflow Pipelines on Kubernetes | SageMaker Pipelines in AWS; Vertex AI Pipelines on GCP; Metaflow for data-science-friendly DAGs; Airflow for teams already using it |
| **Feature store** | Feast (open-source) | Tecton for managed feature serving; SageMaker Feature Store in AWS; Vertex AI Feature Store on GCP; Hopsworks for real-time features |
| **Model serving** | Seldon Core on Kubernetes | TorchServe for PyTorch-specific workloads; TensorFlow Serving for TF models; BentoML for rapid prototyping; vLLM for LLM inference |
| **LLM integration** | LangChain with provider abstraction layer | LlamaIndex for retrieval-heavy workflows; direct SDK calls for single-provider use; Semantic Kernel in .NET ecosystems |
| **RAG vector store** | pgvector in PostgreSQL | Pinecone for managed vector search; Weaviate for hybrid search; Qdrant for high-performance filtering; Chroma for local development |
| **Prompt management** | Version-controlled prompt templates in Git | LangSmith for prompt testing and tracing; Humanloop for non-technical prompt iteration; PromptLayer for logging and analytics |
| **Model monitoring** | Evidently AI (open-source) | Arize for production observability; WhyLabs for data profiling; Fiddler for explainability; NannyML for performance estimation |
| **CI/CD for models** | GitHub Actions with MLflow integration | GitLab CI with DVC pipelines; Jenkins with custom ML stages; Argo Workflows for Kubernetes-native CI |
| **Data versioning** | DVC (Data Version Control) | LakeFS for Git-like data lake branching; Delta Lake for versioned tables; Pachyderm for data-aware pipelines |
| **GPU infrastructure** | Kubernetes with NVIDIA GPU Operator | Cloud-managed GPU instances (SageMaker, Vertex AI); Modal or Anyscale for serverless GPU; on-premise HPC clusters |

---

## Do / Don't

- **Do** version every artifact: code, data, model weights, hyperparameters, and environment definition. Reproducibility requires all five.
- **Do** track every experiment with parameters, metrics, and artifact references. No experiment runs without a tracking entry.
- **Do** separate training, validation, and serving code paths. Training notebooks are not production inference code.
- **Do** pin all dependency versions in training environments. Use Docker images or conda lock files for full reproducibility.
- **Do** implement model validation gates before deployment: performance thresholds, bias checks, and data-drift detection.
- **Do** use feature stores for any feature consumed by more than one model or shared between training and serving.
- **Do** test prompts systematically against evaluation datasets. Prompt changes are code changes — review and version them.
- **Do** set cost budgets and alerts for GPU compute, API calls, and vector-store usage.
- **Do** log all LLM inputs and outputs (with PII redaction) for debugging, evaluation, and compliance.
- **Don't** train models in notebooks and copy weights manually to production. Use automated pipelines with artifact promotion.
- **Don't** hardcode API keys, model endpoints, or provider-specific logic. Use configuration and abstraction layers.
- **Don't** skip data validation before training. Validate schema, distributions, and freshness with automated checks.
- **Don't** deploy models without a rollback plan. Shadow deployments or canary releases allow safe rollback to the previous version.
- **Don't** embed prompts as string literals scattered across the codebase. Centralize prompts in versioned template files.
- **Don't** use raw cosine similarity for RAG retrieval without evaluating recall on a test set. Measure retrieval quality explicitly.
- **Don't** ignore inference latency and throughput requirements. Profile serving performance under realistic load before launch.

---

## Tool Conventions

### MLflow

- One MLflow experiment per project. Runs within the experiment represent individual training iterations.
- Log all hyperparameters with `mlflow.log_params()` at the start of each run. Log metrics with `mlflow.log_metrics()` at each evaluation step.
- Register production-ready models in the Model Registry. Use stage transitions (Staging → Production → Archived) with approval gates.
- Store artifacts (model weights, evaluation plots, sample predictions) with `mlflow.log_artifact()`. Never store artifacts outside the tracking server.
- Tag runs with metadata: `git_commit`, `dataset_version`, `author`, and `experiment_type` (baseline, hyperparameter-search, ablation).

### Kubeflow Pipelines

- Each pipeline step is a containerized component with explicit input/output contracts defined via Kubeflow SDK.
- Use `dsl.pipeline` decorators. Keep pipeline definitions in dedicated `pipelines/` directories, separate from component logic.
- Parameterize pipelines for environment (dev, staging, prod) and dataset version. Never hardcode paths or credentials in pipeline YAML.
- Cache expensive steps (data preprocessing, feature engineering) using Kubeflow's built-in caching by setting `enable_caching=True`.
- Resource requests (`cpu`, `memory`, `gpu`) must be explicit on every step. No unbounded resource consumption.

### LangChain / LLM Frameworks

- Wrap all LLM calls in a provider abstraction layer. Switching from OpenAI to Anthropic or a local model should require only configuration changes.
- Use structured output parsers (Pydantic models) for every LLM call that produces structured data. Never parse LLM text output with regex.
- Implement retry logic with exponential backoff for all external API calls. Set timeout limits appropriate to the use case.
- Chain-of-thought, retrieval, and tool-use steps are separate, composable components — not monolithic chain definitions.
- Trace all LLM calls (prompt, completion, tokens, latency) using callbacks or middleware for observability.

### Feast / Feature Stores

- Feature definitions live in version-controlled Python files under `feature_repo/`. Each feature view maps to a single data source.
- Feature names follow `<entity>_<feature>_<aggregation>_<window>` convention (e.g., `user_purchase_count_7d`).
- Materialize features on a schedule aligned with upstream data freshness. Never serve stale features without a TTL warning.
- Online store (Redis, DynamoDB) serves real-time inference. Offline store (BigQuery, S3/Parquet) serves training. Both must stay in sync.
- Entity keys must be consistent between training and serving. Training–serving skew in entity resolution is a top-priority bug.

---

## Common Pitfalls

1. **Training–serving skew.** The model was trained on features computed one way but served features computed differently. Use a feature store or shared preprocessing library to guarantee identical transformations in both paths.
2. **Untracked experiments.** A team member trains a model locally, copies the weights to S3, and deploys. No one can reproduce it. Require all training to go through the experiment tracking system with mandatory parameter logging.
3. **Prompt drift.** Prompts are edited directly in production without review or versioning. A subtle wording change degrades quality. Treat prompts as code: version-control them, review changes, and run evaluations before deployment.
4. **Silent model degradation.** The model performs well at launch but accuracy drops as data distribution shifts. Monitor prediction distributions, feature drift, and outcome metrics continuously. Set alerting thresholds.
5. **RAG retrieval without evaluation.** A RAG pipeline is deployed with default chunking and embedding settings. Retrieval recall is poor but no one measures it. Build an evaluation set of question–answer pairs and measure retrieval quality before launch.
6. **GPU cost runaway.** A training job or inference cluster is left running after an experiment ends. Set autoscaling to zero, use spot/preemptible instances for training, and implement cost alerts at the project level.
7. **Leaking PII through LLM calls.** User data is sent to external LLM APIs without redaction. Implement a PII detection and scrubbing layer before any data leaves the system boundary.
8. **Monolithic pipelines.** A single script handles data loading, preprocessing, training, evaluation, and deployment. One failure restarts everything. Break into discrete, cacheable pipeline steps with clear inputs and outputs.

---

## Checklist

- [ ] Every experiment is tracked with parameters, metrics, and artifact references
- [ ] Model artifacts are stored in the model registry with version metadata
- [ ] Training environments are fully reproducible (pinned dependencies, Docker images)
- [ ] Data versioning is in place for training and evaluation datasets
- [ ] Feature transformations are shared between training and serving (no skew)
- [ ] Model validation gates (performance, bias, drift) run before promotion to production
- [ ] Prompts are version-controlled, reviewed, and evaluated against test sets
- [ ] LLM calls are logged with PII redaction for observability and compliance
- [ ] RAG retrieval quality is measured on an evaluation dataset
- [ ] Model monitoring (drift, performance, latency) is active in production
- [ ] Cost budgets and alerts are configured for GPU compute and API usage
- [ ] Rollback mechanism is tested and documented for every deployed model
