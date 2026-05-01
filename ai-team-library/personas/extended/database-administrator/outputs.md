# Outputs: Database Administrator

This document defines the deliverables the Database Administrator persona produces, their quality standards, and their downstream consumers.

---

## 1. Schema Migration Plan

| Field | Value |
|-------|-------|
| **Deliverable** | Schema Migration Plan |
| **Cadence** | One per schema change; batched per release when practical |
| **Template** | `personas/database-administrator/templates/schema-migration-plan.md` |
| **Format** | Markdown document with embedded SQL |

### Description

A versioned plan for modifying the database schema, including the change rationale, forward migration SQL, rollback migration SQL, data migration steps (if applicable), and deployment sequence. Each plan covers one logical change and is designed to be executed atomically.

### Quality Bar

- Every migration has both an **up** (forward) and **down** (rollback) script
- Migration scripts are idempotent or guarded against re-execution
- Data migrations handle NULL values, default population, and constraint ordering
- Rollback has been tested against a database with representative data
- Breaking changes are flagged and include a compatibility window or phased rollout plan
- Migration order and dependencies are explicit
- Estimated execution time is provided for large tables

### Downstream Consumers

- **Developer** — integrates migration into application deployment pipeline
- **DevOps / Release Engineer** — schedules and executes migration in staging and production
- **Tech-QA** — verifies migration and rollback in test environments

---

## 2. Query Optimization Report

| Field | Value |
|-------|-------|
| **Deliverable** | Query Optimization Report |
| **Cadence** | As needed; triggered by performance monitoring or Developer request |
| **Template** | `personas/database-administrator/templates/query-optimization-report.md` |
| **Format** | Markdown document with execution plan output |

### Description

An analysis of one or more underperforming queries, including the current execution plan, identified bottlenecks, proposed optimizations (index changes, query rewrites, schema adjustments), and before/after performance metrics.

### Quality Bar

- Includes the original query and its EXPLAIN/ANALYZE output
- Root cause is identified (missing index, full table scan, suboptimal join order, lock contention)
- Proposed fix includes the specific change (CREATE INDEX, query rewrite, configuration tweak)
- Before/after metrics are provided (execution time, rows scanned, I/O cost)
- Side effects are documented (write overhead from new indexes, impact on other queries)
- Recommendation is prioritized by impact and effort

### Downstream Consumers

- **Developer** — implements query changes or index additions in application code and migrations
- **Architect** — incorporates findings into capacity planning and design decisions
- **Team Lead** — tracks optimization work and prioritizes follow-up tasks

---

## 3. Backup and Recovery Plan

| Field | Value |
|-------|-------|
| **Deliverable** | Backup and Recovery Plan |
| **Cadence** | Once per project; updated when infrastructure or requirements change |
| **Template** | `personas/database-administrator/templates/backup-recovery-plan.md` |
| **Format** | Markdown document |

### Description

A comprehensive plan defining backup strategy (full, incremental, differential), schedule, retention policy, storage location, encryption requirements, and recovery procedures. Includes explicit RPO (Recovery Point Objective) and RTO (Recovery Time Objective) targets with justification.

### Quality Bar

- RPO and RTO targets are explicitly stated with business justification
- Backup types (full, incremental, differential) and schedule are defined
- Retention policy specifies duration and rotation scheme
- Storage location and encryption method are documented
- Recovery procedure is step-by-step and has been tested with a successful restore
- Restore time estimate is based on actual test data, not theoretical calculation
- Monitoring and alerting for backup failures are defined
- Compliance requirements (data residency, encryption at rest) are addressed

### Downstream Consumers

- **DevOps / Release Engineer** — implements and automates backup infrastructure
- **Security Engineer** — reviews encryption and access control for backup storage
- **Team Lead** — tracks backup testing schedule and compliance status

---

## 4. Replication Design Document

| Field | Value |
|-------|-------|
| **Deliverable** | Replication Design Document |
| **Cadence** | Once per replication topology; updated when scaling requirements change |
| **Template** | `personas/database-administrator/templates/replication-design.md` |
| **Format** | Markdown document with topology diagrams |

### Description

A design document specifying the replication topology (primary-replica, multi-primary, cascading), configuration parameters, failover and failback procedures, lag monitoring thresholds, and read/write routing strategy.

### Quality Bar

- Topology diagram clearly shows all nodes, roles, and data flow direction
- Replication method is specified (synchronous, asynchronous, semi-synchronous) with trade-off rationale
- Failover procedure is step-by-step and includes both automatic and manual paths
- Failback procedure restores the original topology after failover
- Lag monitoring thresholds and alerting rules are defined
- Read/write routing strategy is documented (application-level, proxy, DNS-based)
- Conflict resolution strategy is defined for multi-primary topologies
- Network and bandwidth requirements are estimated

### Downstream Consumers

- **Architect** — incorporates replication topology into system design
- **DevOps / Release Engineer** — provisions and configures replication infrastructure
- **Developer** — implements read/write routing in application code
- **Tech-QA** — tests failover and failback procedures

---

## 5. Database Health Report

| Field | Value |
|-------|-------|
| **Deliverable** | Database Health Report |
| **Cadence** | End of every sprint/cycle; or on-demand for incidents |
| **Format** | Markdown document with metrics tables |

### Description

A periodic summary of database health indicators including query performance trends, storage utilization, replication status, backup success rates, connection pool usage, and capacity projections.

### Quality Bar

- Metrics are sourced from monitoring tools, not manually estimated
- Trends include at least two data points for comparison
- Anomalies and degradations are flagged with root-cause hypotheses
- Capacity projections include growth rate and estimated time to threshold
- Actionable recommendations are prioritized by urgency
- Backup and replication status is verified, not assumed
