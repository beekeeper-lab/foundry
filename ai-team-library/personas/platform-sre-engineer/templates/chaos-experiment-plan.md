# Chaos Experiment Plan: [Experiment Title]

## Metadata

| Field          | Value                                    |
|----------------|------------------------------------------|
| Date           | [YYYY-MM-DD]                             |
| Owner          | [SRE / Platform Engineer name/role]      |
| Related Links  | [Architecture doc, SLO definition, runbook] |
| Status         | Draft / Approved / Executed / Closed     |

---

**Target Service:** [Service name]
**Environment:** [Production / Staging / Development]
**Scheduled Date:** [YYYY-MM-DD HH:MM TZ]
**Estimated Duration:** [X minutes]

---

## 1. Hypothesis

[State the hypothesis as a specific, falsifiable prediction about system
behavior under the injected failure condition.]

> **When** [failure condition is introduced], **we expect** [specific system
> behavior], **as measured by** [specific metrics], **within** [time bounds].

**Example:** When the primary database instance is terminated, we expect the
application to fail over to the read replica within 30 seconds, with read
requests continuing at p99 latency < 500ms and write requests queued and
retried within 60 seconds, as measured by the SLO dashboard and application
error rate metrics.

---

## 2. Failure Injection

| Field                  | Value                                    |
|------------------------|------------------------------------------|
| Failure Type           | [Network partition / Instance termination / Latency injection / Resource exhaustion / Dependency failure] |
| Injection Method       | [Tool: e.g., Chaos Monkey, Litmus, tc, kill, custom script] |
| Injection Target       | [Specific component, instance, or network path] |
| Injection Parameters   | [Duration, magnitude, percentage of traffic] |
| Injection Command      | [Exact command or configuration]         |

---

## 3. Blast Radius Controls

| Control                | Value                                    |
|------------------------|------------------------------------------|
| Scope                  | [Single instance / Single AZ / Percentage of traffic / Full service] |
| Affected Users         | [Estimated percentage or user count]     |
| Maximum Duration       | [Hard limit -- experiment terminates after this] |
| Traffic Percentage     | [If using traffic splitting, what percentage is affected] |

**Guardrails:**
- [ ] Experiment runs in [environment] only
- [ ] Maximum duration of [X minutes] enforced by [mechanism]
- [ ] Traffic limited to [X%] of total via [mechanism]
- [ ] [Additional guardrail specific to this experiment]

---

## 4. Abort Criteria

*If any of these conditions are met, abort the experiment immediately.*

| Condition                                | Action              |
|------------------------------------------|----------------------|
| [Error rate exceeds X% for > Y seconds]  | Abort and rollback  |
| [Latency exceeds Xms at p99 for > Y sec] | Abort and rollback  |
| [Unrelated service impacted]              | Abort and rollback  |
| [Manual abort triggered by operator]      | Abort and rollback  |

**Abort Procedure:**
```
Step 1: Stop failure injection.
  - Command: [specific command to stop injection]

Step 2: Verify system is recovering.
  - Check: [specific metrics and dashboards]

Step 3: If system does not recover within [X minutes], execute incident
         response runbook: [link to runbook].
```

---

## 5. Observability Setup

*Confirm all monitoring is in place BEFORE starting the experiment.*

- [ ] SLO dashboard open and baselined: [URL]
- [ ] Error rate metric visible: [metric name]
- [ ] Latency metric visible: [metric name]
- [ ] Infrastructure metrics visible: [CPU, memory, connections]
- [ ] Log aggregation query prepared: [query]
- [ ] Distributed tracing enabled for target service
- [ ] Alert routing confirmed: alerts will fire to [channel/rotation]

---

## 6. Execution Checklist

### Pre-Experiment

- [ ] Hypothesis documented and reviewed
- [ ] Blast radius controls confirmed
- [ ] Abort criteria and procedure reviewed
- [ ] Observability setup verified
- [ ] Team notified: [channel]
- [ ] Stakeholder approval obtained (if production)
- [ ] No other experiments or deployments in progress

### During Experiment

- [ ] Failure injection started at [HH:MM]
- [ ] Monitoring observed continuously
- [ ] Experiment log maintained (notes on observed behavior)

### Post-Experiment

- [ ] Failure injection stopped
- [ ] System verified healthy
- [ ] Results documented (Section 7)
- [ ] Team notified of completion

---

## 7. Results

*Complete after experiment execution.*

**Hypothesis Confirmed:** [Yes / No / Partially]

### Observations

| Time (TZ)   | Observation                                        |
|--------------|----------------------------------------------------|
| [HH:MM]      | [Failure injected]                                |
| [HH:MM]      | [First observed impact]                           |
| [HH:MM]      | [System response -- failover, degradation, etc.]  |
| [HH:MM]      | [Recovery observed]                               |
| [HH:MM]      | [Experiment ended]                                |

### Metrics During Experiment

| Metric              | Baseline       | During Experiment | Post-Recovery |
|---------------------|----------------|-------------------|---------------|
| Error rate          | [X%]           | [X%]              | [X%]          |
| Latency (p99)       | [X ms]         | [X ms]            | [X ms]        |
| [Other metric]      | [X]            | [X]               | [X]           |

### Findings

1. [Finding 1: What was learned]
2. [Finding 2: What was learned]
3. [Finding 3: What was learned]

---

## 8. Action Items

| ID   | Action                                  | Owner           | Due Date   | Priority   |
|------|-----------------------------------------|-----------------|------------|------------|
| AI-1 | [Specific action from findings]         | [@person/team]  | [Date]     | [P1/P2/P3] |
| AI-2 | [Specific action from findings]         | [@person/team]  | [Date]     | [P1/P2/P3] |

---

## Definition of Done

- [ ] Hypothesis clearly stated and falsifiable
- [ ] Blast radius controls and abort criteria defined
- [ ] Observability confirmed before execution
- [ ] Results documented with metrics
- [ ] Action items created for findings
- [ ] Results shared with the team
