# Incident Response Runbook: [Service / Failure Mode]

## Metadata

| Field          | Value                                    |
|----------------|------------------------------------------|
| Date           | [YYYY-MM-DD]                             |
| Owner          | [SRE / Platform Engineer name/role]      |
| Related Links  | [Service docs, architecture diagram, SLO definition] |
| Status         | Draft / Reviewed / Tested                |

---

**Service:** [Service name]
**Failure Mode:** [Brief description of the failure this runbook addresses]
**Last Tested:** [Date of last drill or real incident execution]
**Estimated Resolution Time:** [X minutes from detection to resolution]

---

## 1. Detection

### Triggering Alerts

| Alert Name              | Condition                          | Severity |
|-------------------------|------------------------------------|----------|
| [Alert name]            | [Metric > threshold for duration]  | [Sev]    |

### How to Verify This Is a Real Incident

```
Step 1: Check the SLO dashboard for the service.
  - Dashboard: [URL]
  - Look for: [specific metric or panel indicating real user impact]

Step 2: Verify the alert is not a false positive.
  - Command: [specific command to check service health]
  - Expected if real: [what the output looks like during an incident]
  - Expected if false positive: [what the output looks like when healthy]

Step 3: Check for related alerts or upstream issues.
  - [List dependent services and their health check URLs]
```

---

## 2. Triage (Complete Within 5 Minutes)

### Severity Classification

| Severity | Criteria                                           | Response Time |
|----------|----------------------------------------------------|---------------|
| Sev 1    | Complete service outage, all users affected          | Immediate     |
| Sev 2    | Degraded service, significant user impact            | < 15 minutes  |
| Sev 3    | Partial degradation, limited user impact             | < 1 hour      |

### Triage Steps

```
Step 1: Determine scope of impact.
  - Command: [check error rate, affected endpoints, affected regions]
  - Question: Is this affecting all users or a subset?

Step 2: Determine severity using the classification above.

Step 3: If Sev 1 or Sev 2, declare an incident.
  - Create incident channel: [how to create, naming convention]
  - Page incident commander: [how to page]

Step 4: Identify the most likely cause.
  - Recent deployments: [how to check recent deploys]
  - Infrastructure changes: [how to check]
  - Upstream dependency status: [how to check]
  - Traffic anomalies: [how to check]
```

---

## 3. Mitigation

*Execute steps in order. Each step is progressively more invasive. Stop when the
issue is resolved.*

### 3.1 Restart / Recycle

```
Step 1: Restart the affected service instances.
  - Command: [specific restart command]
  - Expected duration: [N minutes]
  - Verify: [how to confirm instances are healthy after restart]
```

- [ ] Service restarted
- [ ] Health checks passing

### 3.2 Scale Up

```
Step 1: Increase service capacity.
  - Command: [specific scale command]
  - Target: [number of instances or resource level]
  - Expected duration: [N minutes]
  - Verify: [how to confirm scaling completed and load distributed]
```

- [ ] Service scaled
- [ ] Load distributed across new instances

### 3.3 Failover

```
Step 1: Fail over to secondary / backup.
  - Command: [specific failover command]
  - Expected duration: [N minutes]
  - Verify: [how to confirm traffic is routing to secondary]
  WARNING: [Any data loss or consistency implications of failover]
```

- [ ] Failover completed
- [ ] Traffic confirmed on secondary

### 3.4 Rollback

```
Step 1: Identify the last known good version.
  - Command: [how to check deployment history]

Step 2: Roll back to the previous version.
  - Command: [specific rollback command]
  - Expected duration: [N minutes]
  - Verify: [how to confirm rollback succeeded]
```

- [ ] Rollback completed
- [ ] Service health restored

---

## 4. Verification

```
Step 1: Check SLO dashboard for recovery.
  - Dashboard: [URL]
  - Look for: Error rate returning to baseline, latency normalizing

Step 2: Verify core functionality.
  - [List specific health checks or smoke tests to run]

Step 3: Monitor for stability.
  - Duration: [N minutes of stable metrics before declaring resolved]
  - Metrics to watch: [specific metrics and their expected ranges]
```

- [ ] Error rate at baseline
- [ ] Latency at baseline
- [ ] No new alerts for [N] minutes
- [ ] Core functionality verified

---

## 5. Communication

### During Incident

| Stage           | Audience            | Channel          | Template                         |
|-----------------|---------------------|------------------|----------------------------------|
| Incident declared | Engineering team   | [Incident channel] | "Incident declared for [service]. Severity: [X]. Impact: [brief]. Investigating." |
| Mitigation in progress | Engineering team | [Incident channel] | "Mitigation in progress: [action being taken]. ETA: [X minutes]." |
| Resolved        | Engineering team     | [Incident channel] | "Incident resolved. Duration: [X minutes]. Impact: [brief]. Post-incident review scheduled." |
| Resolved        | Stakeholders         | [Status page/email] | "Service restored. [Brief user-facing summary]." |

### Post-Incident

- [ ] Post-incident review scheduled within 48 hours
- [ ] Incident timeline documented
- [ ] Stakeholders notified of resolution

---

## 6. Escalation

| Condition                                  | Escalate To          | Contact              |
|--------------------------------------------|----------------------|----------------------|
| Mitigation steps exhausted, still impacted | [Engineering Lead]   | [Contact info]       |
| Data loss suspected                        | [Database Admin]     | [Contact info]       |
| Security implications                      | [Security Engineer]  | [Contact info]       |
| Customer-facing SLA breach imminent        | [Team Lead]          | [Contact info]       |

---

## Definition of Done

- [ ] All detection, triage, mitigation, and verification steps documented
- [ ] Commands are exact and copy-pasteable
- [ ] Runbook tested in drill or real incident
- [ ] Communication templates completed
- [ ] Escalation contacts current
