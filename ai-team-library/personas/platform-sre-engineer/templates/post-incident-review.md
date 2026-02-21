# Post-Incident Review: [Incident Title]

## Metadata

| Field          | Value                                    |
|----------------|------------------------------------------|
| Date           | [YYYY-MM-DD]                             |
| Owner          | [Incident commander / SRE name]          |
| Related Links  | [Incident channel, alerts, dashboards, deploy logs] |
| Status         | Draft / Reviewed / Final                 |

---

**Incident ID:** [INC-NNNN]
**Severity:** [Sev 1 / Sev 2 / Sev 3]
**Services Affected:** [List of affected services]
**Duration:** [Total time from detection to resolution]
**Date of Incident:** [YYYY-MM-DD HH:MM - HH:MM TZ]

---

## 1. Executive Summary

[2-3 sentence summary: what happened, how long it lasted, what the user impact
was, and how it was resolved.]

---

## 2. Impact

| Metric                    | Value                                    |
|---------------------------|------------------------------------------|
| Duration                  | [X minutes / hours]                      |
| Users affected            | [Number or percentage]                   |
| Error rate during incident| [X%]                                     |
| Requests failed           | [Number]                                 |
| SLO budget consumed       | [X% of monthly budget]                   |
| Revenue impact            | [Estimated or N/A]                       |
| Data loss                 | [Yes -- describe / No]                   |

---

## 3. Timeline

*All timestamps sourced from logs and monitoring. Do not rely on memory.*

| Time (TZ)   | Event                                              | Source          |
|--------------|----------------------------------------------------|-----------------|
| [HH:MM]      | [First anomaly in metrics]                         | [Monitoring]    |
| [HH:MM]      | [Alert fires]                                      | [Alert system]  |
| [HH:MM]      | [On-call acknowledged]                             | [PagerDuty]     |
| [HH:MM]      | [Incident declared, Sev X]                         | [Incident mgmt] |
| [HH:MM]      | [Root cause identified]                            | [Investigation] |
| [HH:MM]      | [Mitigation applied]                               | [Operator]      |
| [HH:MM]      | [Service recovering]                               | [Monitoring]    |
| [HH:MM]      | [Incident resolved]                                | [Monitoring]    |

**Time to Detect (TTD):** [Time from first anomaly to alert]
**Time to Acknowledge (TTA):** [Time from alert to human response]
**Time to Mitigate (TTM):** [Time from acknowledgment to mitigation applied]
**Time to Resolve (TTR):** [Time from detection to full resolution]

---

## 4. Root Cause

[Describe the root cause. Be specific and technical. What failed and why?]

### Contributing Factors

1. [Factor 1: e.g., Missing circuit breaker on dependency call]
2. [Factor 2: e.g., Alert threshold set too high, delayed detection by X minutes]
3. [Factor 3: e.g., Runbook did not cover this specific failure mode]

---

## 5. What Went Well

- [e.g., Alert fired within X minutes of impact starting]
- [e.g., Runbook for service restart was accurate and effective]
- [e.g., Communication was clear and timely throughout]

---

## 6. What Went Poorly

- [e.g., Detection was delayed by X minutes due to alert threshold]
- [e.g., Failover did not work as expected because...]
- [e.g., Runbook was missing steps for this failure mode]

---

## 7. Action Items

| ID   | Action                                  | Owner           | Due Date   | Status     |
|------|-----------------------------------------|-----------------|------------|------------|
| AI-1 | [Specific, actionable item]             | [@person/team]  | [Date]     | [Open]     |
| AI-2 | [Specific, actionable item]             | [@person/team]  | [Date]     | [Open]     |
| AI-3 | [Specific, actionable item]             | [@person/team]  | [Date]     | [Open]     |

**Action item quality check:**
- [ ] Every action item is specific enough that someone else could execute it
- [ ] Every action item has an owner
- [ ] Every action item has a due date
- [ ] No action item is "improve monitoring" or "be more careful" (too vague)

---

## 8. Lessons Learned

[What did this incident teach us about our systems, processes, or assumptions?
Focus on systemic improvements, not individual actions.]

---

## Definition of Done

- [ ] Timeline is complete and sourced from logs/monitoring
- [ ] Root cause and contributing factors identified
- [ ] Impact quantified with specific numbers
- [ ] Action items are concrete, assigned, and deadlined
- [ ] Review conducted blameless -- no individual blame
- [ ] Review shared with the engineering team
- [ ] Action items tracked in the issue tracker
