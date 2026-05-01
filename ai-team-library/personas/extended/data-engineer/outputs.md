# Data Engineer -- Outputs

This document enumerates every artifact the Data Engineer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. ETL/ELT Pipeline Code

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Data Pipeline Implementation                       |
| **Cadence**        | Continuous; one or more PRs per assigned task      |
| **Template**       | `pipeline-spec.md`                                 |
| **Format**         | Source code (Python, SQL, or stack-appropriate)     |

**Description.** Working pipeline code that ingests, transforms, and loads data
according to the specifications defined in data requirements and pipeline
contracts. This is the Data Engineer's primary output.

**Quality Bar:**
- Satisfies all acceptance criteria in the originating task.
- Pipeline is idempotent -- rerunning produces identical results.
- Transformations are deterministic and handle nulls, duplicates, and edge
  cases explicitly.
- No hardcoded connection strings, credentials, or environment-specific values.
- Error handling prevents partial writes or corrupted state in target systems.
- Follows the project's coding conventions (see stack `conventions.md`).
- Incremental processing is preferred over full reloads where feasible.

**Downstream Consumers:** Code Quality Reviewer (for review), Tech QA (for
testing), DevOps-Release (for deployment), Architect (for data platform
oversight).

---

## 2. Data Models

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Data Model Definitions                             |
| **Cadence**        | When new data entities or relationships are needed |
| **Template**       | `data-model-spec.md`                               |
| **Format**         | DDL scripts, schema definitions, ER diagrams       |

**Description.** Schema definitions for warehouse tables, staging areas, and
serving layers. Includes dimensional models, normalized models, or hybrid
approaches as appropriate for the use case.

**Quality Bar:**
- Schema follows naming conventions (consistent casing, meaningful names).
- Primary keys, foreign keys, and constraints are explicitly defined.
- Partition keys are chosen based on query patterns, not convenience.
- Schema changes include migration scripts with rollback procedures.
- Changes are backward-compatible or versioned with a migration plan.
- Data types are appropriate for the data (no VARCHAR for everything).
- Documentation includes entity descriptions and column-level definitions.

**Downstream Consumers:** Developer (for application integration), Business
Analyst (for data product validation), Architect (for data platform design).

---

## 3. Orchestration DAGs

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Pipeline Orchestration Workflows                   |
| **Cadence**        | When new pipelines are introduced or modified      |
| **Template**       | `dag-spec.md`                                      |
| **Format**         | DAG definitions (Airflow, Dagster, or equivalent)  |

**Description.** Orchestration workflow definitions that schedule, coordinate,
and monitor pipeline execution. DAGs define task dependencies, retry policies,
SLAs, and alerting configuration.

**Quality Bar:**
- DAG dependencies accurately reflect data flow requirements.
- Retry policies are configured with appropriate backoff and limits.
- SLAs are defined for critical pipelines with alerting on breach.
- Tasks are idempotent and safe to retry independently.
- Scheduling intervals match data source refresh cadence.
- DAG documentation describes purpose, dependencies, and SLA expectations.
- No circular dependencies or unnecessary sequential constraints.

**Downstream Consumers:** DevOps-Release (for deployment and monitoring),
Team Lead (for pipeline health tracking), Tech QA (for end-to-end testing).

---

## 4. Data Quality Validation Rules

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Data Quality Test Suite                            |
| **Cadence**        | Accompanies every pipeline implementation          |
| **Template**       | `data-quality-checklist.md`                        |
| **Format**         | Test code, validation rules, or quality framework config |

**Description.** Automated validation rules that verify data correctness at
ingestion, transformation, and serving boundaries. Quality checks run as
pipeline steps and gate downstream processing.

**Quality Bar:**
- Row count assertions verify no unexpected data loss or duplication.
- Null rate checks enforce expectations on required fields.
- Type and format validation catches schema drift early.
- Referential integrity checks verify foreign key relationships.
- Distribution checks detect anomalies in value ranges and cardinalities.
- Quality checks are parameterized and reusable across similar datasets.
- Failed checks produce clear, actionable error messages.

**Downstream Consumers:** Tech QA (for quality assessment), Business Analyst
(for data product confidence), Team Lead (for pipeline health tracking).

---

## 5. Pipeline Documentation

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Pipeline Runbook and Lineage Documentation         |
| **Cadence**        | Accompanies every pipeline implementation          |
| **Template**       | `pipeline-runbook.md`                              |
| **Format**         | Markdown                                           |

**Description.** Operational documentation covering data lineage, pipeline
behavior, SLA definitions, and troubleshooting procedures. Enables other
team members to understand, operate, and debug pipelines.

**Quality Bar:**
- Lineage map shows source-to-target data flow with transformation steps.
- SLA definitions include expected completion times and alerting thresholds.
- Troubleshooting section covers common failure modes and resolution steps.
- Schema documentation includes column-level descriptions and business context.
- Documentation stays current -- updated when pipeline behavior changes.
- A team member unfamiliar with the pipeline can operate it using only the
  runbook.

**Downstream Consumers:** DevOps-Release (for operations), Team Lead (for
capacity planning), Architect (for data platform oversight).

---

## 6. Schema Migration Scripts

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Schema Migration with Rollback                     |
| **Cadence**        | When data models change                            |
| **Template**       | None (follows migration tool conventions)          |
| **Format**         | SQL migration scripts or migration framework files |

**Description.** Versioned migration scripts that evolve database schemas
safely. Each migration includes both forward and rollback procedures to
enable safe deployment and recovery.

**Quality Bar:**
- Migrations are versioned and ordered.
- Each migration has a corresponding rollback script.
- Migrations are backward-compatible or include a data backfill step.
- Large table migrations include a plan for minimizing downtime.
- Migrations are tested against a representative dataset before production.
- No data loss during migration -- existing data is preserved or explicitly
  archived.

**Downstream Consumers:** DevOps-Release (for deployment), Developer (for
application compatibility), Architect (for schema governance).

---

## Output Format Guidelines

- Code follows the stack-specific conventions document (`stacks/<stack>/conventions.md`).
- Tests follow the same conventions as production code: same linting, same
  formatting, same naming rules.
- Pipeline documentation is written as if the reader has no prior context about
  the pipeline.
- All outputs are committed to the project repository. No deliverables live
  outside version control.
