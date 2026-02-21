# Pipeline Orchestration

Standards for scheduling, dependency management, and execution of data pipelines.
Apache Airflow is the default orchestrator. Alternatives require an ADR.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Orchestrator** | Apache Airflow 2.x (managed service preferred, e.g., MWAA, Cloud Composer) | Dagster for asset-centric workflows; Prefect for lightweight/event-driven pipelines |
| **DAG structure** | One DAG per source-to-target pipeline | Umbrella DAGs only for cross-pipeline dependencies via `ExternalTaskSensor` |
| **Task granularity** | One task per logical unit (extract, load, transform) | Avoid single-task DAGs and 200-task mega-DAGs equally |
| **Scheduling** | Cron expressions with explicit `start_date` and `catchup=False` | Event-driven triggers (S3 sensor, API webhook) when data arrival is unpredictable |
| **Retries** | `retries=2`, `retry_delay=timedelta(minutes=5)` on every task | Increase for tasks calling flaky external APIs |
| **Idempotency** | Tasks use `execution_date` / `logical_date` partitioning to be re-runnable | — |
| **Deployment** | DAGs in a Git repo, deployed via CI/CD to the DAGs folder | Never edit DAGs directly on the Airflow server |

---

## Do / Don't

- **Do** keep DAGs simple and declarative. A DAG file defines dependencies and configuration, not business logic. Put logic in separate Python modules or dbt models.
- **Do** use Airflow connections and variables for external system credentials. Never hard-code connection details in DAG files.
- **Do** set `catchup=False` unless you explicitly need historical backfill on deploy.
- **Do** use `execution_date`/`logical_date` to partition work so that re-runs process the correct time window.
- **Do** set explicit `timeout` on every task to prevent hung tasks from blocking the scheduler.
- **Do** use task groups to organize related tasks visually without creating separate DAGs.
- **Don't** use `depends_on_past=True` without understanding that it serializes all runs — a single failure blocks all subsequent runs.
- **Don't** put heavy computation in the Airflow worker. Offload to Spark, a warehouse, or a container. Airflow is an orchestrator, not a compute engine.
- **Don't** use dynamic DAG generation that produces hundreds of DAGs. This overwhelms the scheduler.
- **Don't** trigger DAGs manually in production as a regular practice. If you need ad-hoc runs, build a parameterized trigger endpoint.

---

## Common Pitfalls

1. **Scheduler overload.** Too many DAGs, short polling intervals, or heavy top-level DAG code slows the scheduler. Keep DAG parsing lightweight — no database calls or API requests at parse time.
2. **Silent task failures.** Tasks that swallow exceptions appear successful. Always let exceptions propagate; Airflow marks the task as failed and triggers alerts.
3. **Zombie tasks.** Long-running tasks without timeouts consume worker slots indefinitely. Set `execution_timeout` on every task.
4. **Backfill chaos.** Running `airflow backfill` without understanding `depends_on_past` and `catchup` settings produces unexpected parallel runs or skipped dates.
5. **DAG spaghetti.** Cross-DAG dependencies via `ExternalTaskSensor` chains create invisible coupling. Document cross-DAG dependencies and consider consolidating tightly coupled DAGs.
6. **Environment drift.** DAGs that work in dev but fail in production because of missing connections, variables, or Python packages. Test DAGs in a staging Airflow environment before deploying to production.

---

## Checklist

- [ ] One DAG per source-to-target pipeline (no monolith DAGs)
- [ ] DAGs are version-controlled and deployed via CI/CD
- [ ] `catchup=False` is set unless backfill is explicitly intended
- [ ] Every task has `retries`, `retry_delay`, and `execution_timeout` configured
- [ ] Business logic lives in external modules, not in DAG files
- [ ] Connections and credentials use Airflow connections/variables or a secrets backend
- [ ] Alerting is configured for task failures (email, Slack, PagerDuty)
- [ ] Cross-DAG dependencies are documented and minimized
- [ ] DAG parsing is lightweight — no API calls or DB queries at import time
- [ ] Staging environment mirrors production for DAG testing
