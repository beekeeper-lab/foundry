# Backup and Recovery Plan

| Field | Value |
|-------|-------|
| **Document ID** | BRP-NNN |
| **Date** | YYYY-MM-DD |
| **Author** | Database Administrator |
| **Status** | Draft / Approved / Active |
| **Database** | _Database name and engine_ |
| **Environment** | Production / Staging / Development |

## Recovery Objectives

| Objective | Target | Justification |
|-----------|--------|---------------|
| **RPO** (Recovery Point Objective) | _e.g., 1 hour_ | _Maximum acceptable data loss_ |
| **RTO** (Recovery Time Objective) | _e.g., 4 hours_ | _Maximum acceptable downtime_ |

## Backup Strategy

### Backup Types and Schedule

| Backup Type | Schedule | Retention | Storage Location |
|-------------|----------|-----------|-----------------|
| Full | _e.g., Weekly, Sunday 02:00 UTC_ | _e.g., 30 days_ | _e.g., S3 bucket_ |
| Incremental | _e.g., Daily, 02:00 UTC_ | _e.g., 7 days_ | _e.g., S3 bucket_ |
| Transaction Log | _e.g., Every 15 minutes_ | _e.g., 72 hours_ | _e.g., S3 bucket_ |

### Backup Configuration

_Specify backup tools, compression, encryption, and any engine-specific settings._

- **Tool:** _e.g., pg_dump, mysqldump, WAL archiving_
- **Compression:** _e.g., gzip, lz4_
- **Encryption:** _e.g., AES-256 at rest, TLS in transit_
- **Parallelism:** _e.g., 4 parallel jobs_

### Storage and Retention

- **Primary storage:** _location and access controls_
- **Secondary storage:** _offsite/cross-region copy (if applicable)_
- **Retention rotation:** _describe the rotation scheme_
- **Data residency:** _compliance requirements for storage location_

## Recovery Procedures

### Scenario 1: Point-in-Time Recovery

_Recover the database to a specific point in time (e.g., before an accidental DELETE)._

1. _Step-by-step recovery instructions_
2. _..._

**Estimated recovery time:** _duration_

### Scenario 2: Full Database Restore

_Recover the entire database from the most recent backup (e.g., after hardware failure)._

1. _Step-by-step recovery instructions_
2. _..._

**Estimated recovery time:** _duration_

### Scenario 3: Single Table Restore

_Recover a specific table without affecting the rest of the database._

1. _Step-by-step recovery instructions_
2. _..._

**Estimated recovery time:** _duration_

## Monitoring and Alerting

| Alert | Condition | Notification |
|-------|-----------|-------------|
| Backup failure | _Backup job exits non-zero_ | _e.g., PagerDuty, Slack_ |
| Backup size anomaly | _Size deviates >20% from baseline_ | _e.g., Slack_ |
| Storage threshold | _Backup storage >80% capacity_ | _e.g., Email_ |

## Restore Testing Schedule

| Test Type | Frequency | Last Tested | Result |
|-----------|-----------|-------------|--------|
| Full restore | _e.g., Monthly_ | _YYYY-MM-DD_ | _Pass / Fail_ |
| Point-in-time restore | _e.g., Quarterly_ | _YYYY-MM-DD_ | _Pass / Fail_ |
| Cross-region restore | _e.g., Quarterly_ | _YYYY-MM-DD_ | _Pass / Fail_ |

## Compliance

_Document any regulatory or policy requirements affecting backup and recovery._

- **Data residency:** _..._
- **Encryption requirements:** _..._
- **Audit logging:** _..._
- **Retention mandates:** _..._
