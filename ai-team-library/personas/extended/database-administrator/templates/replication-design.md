# Replication Design Document

| Field | Value |
|-------|-------|
| **Document ID** | REP-NNN |
| **Date** | YYYY-MM-DD |
| **Author** | Database Administrator |
| **Status** | Draft / Approved / Active |
| **Database Engine** | _e.g., PostgreSQL 16, MySQL 8_ |
| **Topology** | Primary-Replica / Multi-Primary / Cascading |

## Purpose

_Why replication is needed. Reference availability SLAs, read scaling requirements, or geographic distribution needs._

## Topology

_Describe the replication topology. Include a diagram._

```
┌─────────────┐     async      ┌─────────────┐
│   Primary   │ ──────────────▶│  Replica 1   │
│  (writes)   │                │  (reads)     │
└─────────────┘                └─────────────┘
       │
       │         async      ┌─────────────┐
       └───────────────────▶│  Replica 2   │
                            │  (reads)     │
                            └─────────────┘
```

### Node Inventory

| Node | Role | Location | Replication Method | Lag Threshold |
|------|------|----------|--------------------|---------------|
| _node-1_ | Primary | _region_ | — | — |
| _node-2_ | Replica | _region_ | _async/sync/semi-sync_ | _e.g., <5s_ |

## Replication Configuration

- **Method:** _Synchronous / Asynchronous / Semi-synchronous_
- **Trade-off rationale:** _Why this method was chosen (consistency vs. performance)_
- **Replication format:** _e.g., Statement-based, Row-based, Logical_
- **Filtering:** _Any tables or schemas excluded from replication_

## Read/Write Routing

- **Write routing:** _All writes go to primary via ..._
- **Read routing:** _Reads distributed to replicas via ... (application-level, proxy, DNS)_
- **Consistency requirements:** _Read-after-write consistency strategy_

## Failover Procedure

### Automatic Failover

1. _How failure is detected (health checks, heartbeat timeout)_
2. _How the new primary is selected_
3. _How clients are redirected_
4. _How other replicas are reconfigured_

**Expected failover time:** _duration_

### Manual Failover

1. _Step-by-step manual failover instructions_
2. _..._

**Decision criteria:** _When to trigger manual failover vs. waiting for automatic_

## Failback Procedure

_How to restore the original topology after a failover event._

1. _Step-by-step failback instructions_
2. _..._

**Data reconciliation:** _How to handle writes that occurred on the promoted replica_

## Monitoring and Alerting

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Replication lag | _e.g., >5 seconds_ | _PagerDuty_ |
| Replication stopped | _Boolean_ | _PagerDuty_ |
| Connection count | _e.g., >80% pool_ | _Slack_ |

## Conflict Resolution (Multi-Primary Only)

_If using multi-primary replication, describe how write conflicts are detected and resolved._

- **Detection method:** _..._
- **Resolution strategy:** _Last-write-wins / Application-level / Custom_
- **Conflict logging:** _Where conflicts are recorded for audit_

## Network Requirements

| Path | Bandwidth | Latency | Encryption |
|------|-----------|---------|------------|
| _Primary → Replica 1_ | _estimate_ | _estimate_ | _TLS_ |

## Testing Plan

- [ ] Replication setup verified with representative data
- [ ] Failover tested (automatic path)
- [ ] Failover tested (manual path)
- [ ] Failback tested and original topology restored
- [ ] Lag monitoring alerts verified
- [ ] Read/write routing verified under load
