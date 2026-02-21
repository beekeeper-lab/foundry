# Platform / SRE Engineer -- Outputs

This document enumerates every artifact the Platform / SRE Engineer is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. SLO Definition

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | SLO Definition                                     |
| **Cadence**        | One per service; reviewed quarterly or when service behavior changes |
| **Template**       | `personas/platform-sre-engineer/templates/slo-definition.md` |
| **Format**         | Markdown                                           |

**Description.** A formal specification of the reliability contract for a
service, defining what "reliable enough" means in measurable terms. The SLO
definition establishes the Service Level Indicators (SLIs) that measure user-
facing behavior, the target thresholds that constitute acceptable performance,
and the error budget policy that governs what happens when reliability degrades.

**Quality Bar:**
- Every SLO is tied to a user-facing behavior, not an internal metric. "99.9%
  of checkout requests complete successfully within 2 seconds" not "CPU stays
  below 80%."
- SLIs are precisely defined: the numerator, denominator, measurement window,
  and data source are specified unambiguously.
- Error budget is calculated and documented: the acceptable amount of unreliability
  over the measurement window and the policy for what happens when it is
  exhausted.
- Alerting thresholds are derived from the SLO: burn-rate alerts fire when the
  error budget is being consumed faster than planned.
- The SLO has been reviewed and agreed upon by the service owner, platform team,
  and relevant stakeholders.
- Historical data is referenced to validate that the target is achievable and
  meaningful.

**Downstream Consumers:** Team Lead (for prioritization when error budget is
at risk), Architect (for system design reliability requirements), Developer
(for understanding performance expectations), Compliance / Risk Analyst (for
availability commitments).

---

## 2. Incident Response Runbook

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Incident Response Runbook                          |
| **Cadence**        | One per critical service; updated after each post-incident review |
| **Template**       | `personas/platform-sre-engineer/templates/incident-response-runbook.md` |
| **Format**         | Markdown                                           |

**Description.** A structured procedure for detecting, triaging, mitigating,
and resolving incidents for a specific service or failure mode. The runbook
provides the on-call engineer with the exact steps to diagnose the problem,
apply a mitigation, verify recovery, and communicate status -- without requiring
prior context or expertise with the specific system.

**Quality Bar:**
- Detection criteria are explicit: which alerts fire, what the alert message
  means, and how to verify the alert is a true positive.
- Triage steps help the responder determine severity and scope within the first
  five minutes.
- Mitigation steps are ordered from least-risk to most-risk: restart, scale,
  failover, rollback, with exact commands for each.
- Verification steps confirm the incident is resolved: which metrics to check,
  what normal looks like, and how long to monitor before declaring resolution.
- Communication templates are included: who to notify, when, and what to say at
  each stage of the incident.
- The runbook has been executed successfully during a drill or real incident.

**Downstream Consumers:** On-call engineer (primary user), Team Lead (for
incident status tracking), DevOps / Release Engineer (for deployment-related
incidents).

---

## 3. Capacity Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Capacity Plan                                      |
| **Cadence**        | Quarterly or before major launches; updated when traffic patterns change |
| **Template**       | `personas/platform-sre-engineer/templates/capacity-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A forward-looking analysis of system resource requirements
based on current utilization, growth trends, and projected demand. The capacity
plan identifies when the system will approach resource limits and recommends
scaling actions to maintain performance and reliability ahead of demand.

**Quality Bar:**
- Current utilization is measured, not estimated: CPU, memory, storage, network,
  database connections, and queue depth for each critical component.
- Growth projections are based on historical trends and planned business events
  (launches, marketing campaigns, seasonal patterns).
- Headroom thresholds are defined: the utilization level at which scaling action
  must be taken, with lead time for provisioning.
- Scaling recommendations are specific: what to scale, how to scale (vertical,
  horizontal, architectural), estimated cost, and implementation timeline.
- Load test results validate that the system handles the projected peak with
  acceptable performance.
- Single points of failure and bottlenecks are identified with their capacity
  limits.

**Downstream Consumers:** Architect (for system design decisions), Team Lead
(for resource planning and budgeting), DevOps / Release Engineer (for
infrastructure provisioning).

---

## 4. Post-Incident Review

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Post-Incident Review                               |
| **Cadence**        | One per severity 1 or 2 incident; optional for severity 3 |
| **Template**       | `personas/platform-sre-engineer/templates/post-incident-review.md` |
| **Format**         | Markdown                                           |

**Description.** A blameless analysis of an incident that documents what
happened, why it happened, how it was resolved, and what will be done to prevent
recurrence. The post-incident review transforms operational pain into system
improvement by producing concrete, tracked action items.

**Quality Bar:**
- The timeline is precise: timestamps for detection, response, mitigation, and
  resolution sourced from logs and monitoring, not memory.
- Root cause analysis goes beyond the proximate cause to identify contributing
  factors: what made the system vulnerable, what delayed detection, what
  complicated mitigation.
- Impact is quantified: duration, number of affected users, error rates, and
  financial impact where measurable.
- Action items are concrete, assigned to owners, and have deadlines. "Improve
  monitoring" is not an action item; "Add latency alert for checkout service
  at p99 > 2s, owner: @platform, due: 2024-03-15" is.
- The review is blameless: focus on system and process improvements, not
  individual mistakes.
- Follow-up is tracked: action items are linked to the tracking system and
  reviewed in subsequent operational reviews.

**Downstream Consumers:** Team Lead (for prioritizing reliability improvements),
Architect (for system design lessons), Developer (for code-level fixes),
Compliance / Risk Analyst (for incident audit records).

---

## 5. Chaos Experiment Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Chaos Experiment Plan                              |
| **Cadence**        | As needed; typically before major releases or quarterly resilience validation |
| **Template**       | `personas/platform-sre-engineer/templates/chaos-experiment-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A controlled experiment designed to validate that the system
behaves as expected under failure conditions. The chaos experiment plan
defines the hypothesis, the failure to inject, the expected system response,
the blast radius controls, and the rollback procedure -- ensuring that
resilience claims are tested, not assumed.

**Quality Bar:**
- The hypothesis is specific and falsifiable: "When the primary database fails
  over, the application continues serving read requests from the replica with
  latency increase < 500ms and zero write errors surfaced to users."
- The failure injection method is documented: what tool, what failure mode, and
  the exact parameters.
- Blast radius is bounded: the experiment affects a defined scope (single
  service, single availability zone, percentage of traffic) with documented
  limits.
- Abort criteria are defined: what conditions trigger immediate experiment
  termination and rollback.
- Observability is in place before the experiment starts: dashboards and alerts
  that will capture the system's response.
- Results are documented: did the system behave as hypothesized? What was
  learned? What action items emerged?

**Downstream Consumers:** Architect (for system resilience validation), Team
Lead (for reliability confidence), Developer (for understanding failure modes),
DevOps / Release Engineer (for deployment resilience).

---

## 6. Reliability Risk Assessment

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Reliability Risk Assessment                        |
| **Cadence**        | At system design; updated when architecture changes significantly |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** An analysis of the system's reliability posture that identifies
single points of failure, failure domains, cascading failure risks, and recovery
gaps. The assessment provides a prioritized list of reliability risks with
recommended mitigations.

**Required Sections:**
1. **System Overview** -- Architecture summary, critical paths, and dependency
   graph.
2. **Single Points of Failure** -- Components where a single failure causes
   user-facing impact, with severity and likelihood ratings.
3. **Failure Domain Analysis** -- How failures propagate: blast radius of each
   component failure, cascading failure risks, and dependency chain analysis.
4. **Recovery Capabilities** -- Current failover mechanisms, recovery time
   estimates, and gaps in automated recovery.
5. **Observability Gaps** -- Areas where monitoring, alerting, or tracing is
   insufficient to detect or diagnose failures.
6. **Risk Prioritization** -- Ranked list of reliability risks by impact and
   likelihood, with recommended mitigations and estimated effort.

**Quality Bar:**
- Every critical path through the system is analyzed for failure modes.
- Risk ratings are based on data (incident history, load test results, dependency
  SLAs) not intuition.
- Mitigations are specific and actionable, not generic recommendations.
- The assessment is reviewed with the Architect and service owners.

**Downstream Consumers:** Architect (for system design improvements), Team Lead
(for reliability investment prioritization), Security Engineer (for overlapping
infrastructure risks).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository under `docs/sre/` or `docs/reliability/`.
- SLO definitions are living documents updated in place when targets or SLIs
  change, with version history tracked by the repository.
- Incident response runbooks are versioned alongside the services they cover.
  An outdated runbook is worse than no runbook because it creates false
  confidence during an incident.
- Post-incident reviews are immutable once finalized -- they are historical
  records, not living documents. Action items are tracked separately.
- Capacity plans include the date of the underlying measurements so reviewers
  can assess data freshness.
- Chaos experiment plans reference the specific system version and configuration
  tested, so results can be tied to a known state.
- Use parameterized placeholders (e.g., `${SERVICE}`, `${ENVIRONMENT}`) in
  runbook commands rather than hardcoded values.
