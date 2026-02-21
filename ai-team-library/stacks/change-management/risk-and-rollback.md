# Risk and Rollback

Frameworks for identifying change risks, defining rollback triggers, and managing
change failures. Proactive risk management and clear rollback criteria prevent
small problems from becoming organizational crises.

---

## Defaults

| Aspect | Default | Alternatives |
|--------|---------|-------------|
| **Risk Framework** | Likelihood x Impact matrix with defined thresholds | Qualitative risk ranking for small changes |
| **Rollback Strategy** | Pre-defined triggers with automated or manual rollback procedures | No rollback plan only for irreversible changes (e.g., org restructures) |
| **Monitoring** | Daily risk review during transition, weekly post-go-live | Continuous monitoring for high-risk changes |
| **Escalation** | Three-tier: Change Lead → CAB → Executive Sponsor | Two-tier for small changes |
| **Review Cadence** | Risk register reviewed at every phase gate and weekly during transition | Monthly for low-risk, long-duration changes |

---

## Change Risk Assessment

### Risk Categories

| Category | Examples | Typical Impact |
|----------|---------|---------------|
| **People** | Resistance, skill gaps, key person dependency, change fatigue | Adoption failure, productivity loss |
| **Process** | Workflow disruption, compliance gaps, handoff failures | Operational errors, regulatory exposure |
| **Technology** | System failures, integration issues, data migration errors | Downtime, data loss |
| **Timeline** | Compressed schedule, dependency delays, resource conflicts | Rushed rollout, inadequate training |
| **External** | Regulatory changes, market shifts, vendor failures | Scope change, forced acceleration |
| **Organizational** | Sponsor turnover, restructuring, competing priorities | Loss of momentum, defunding |

### Risk Assessment Matrix

```
              │ Negligible │   Minor    │  Moderate  │   Major    │  Critical  │
              │     1      │     2      │     3      │     4      │     5      │
──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
Almost        │            │            │            │            │            │
Certain (5)   │     5      │    10      │    15      │    20      │    25      │
──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
Likely (4)    │     4      │     8      │    12      │    16      │    20      │
──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
Possible (3)  │     3      │     6      │     9      │    12      │    15      │
──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
Unlikely (2)  │     2      │     4      │     6      │     8      │    10      │
──────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤
Rare (1)      │     1      │     2      │     3      │     4      │     5      │
──────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘

Risk Score Thresholds:
  1–4:   LOW       → Accept and monitor
  5–9:   MEDIUM    → Mitigate with defined actions
  10–15: HIGH      → Escalate; active mitigation required
  16–25: CRITICAL  → Escalate to sponsor; consider delay or rollback
```

### Risk Register Template

| ID | Risk Description | Category | Likelihood (1–5) | Impact (1–5) | Score | Mitigation | Owner | Status |
|----|-----------------|----------|------------------|--------------|-------|------------|-------|--------|
| R1 | Key sponsor leaves mid-initiative | Organizational | 2 | 5 | 10 | Identify backup sponsor, document sponsor commitments | Change Lead | Open |
| R2 | Training completion below 80% by go-live | People | 3 | 4 | 12 | Mandatory completion policy, manager accountability | Training Lead | Open |
| R3 | Integration with legacy system fails | Technology | 2 | 5 | 10 | Parallel run period, manual fallback procedure | Tech Lead | Open |
| R4 | Change fatigue from concurrent initiatives | People | 4 | 3 | 12 | Coordinate with change portfolio, stagger timelines | Change Lead | Open |

---

## Rollback Triggers

### Defining Rollback Triggers

A rollback trigger is a pre-agreed condition that, when met, initiates a return to
the previous state. Triggers must be defined **before** go-live and agreed by the
Change Advisory Board.

### Trigger Categories

| Category | Trigger Example | Measurement | Threshold |
|----------|----------------|-------------|-----------|
| **System Health** | Critical system outage post-deployment | Uptime monitoring | >4 hours unplanned downtime |
| **Data Integrity** | Data corruption or loss detected | Data validation checks | Any confirmed data loss |
| **Adoption** | Active user adoption critically below target | Usage analytics | <25% adoption after 2 weeks |
| **Error Rate** | Error rate exceeds acceptable threshold | Error logs, support tickets | >300% of baseline error rate |
| **Business Impact** | Revenue or service-level impact | Business metrics | Defined per initiative |
| **Safety/Compliance** | Regulatory non-compliance detected | Audit / compliance review | Any confirmed violation |
| **User Sentiment** | Severe user pushback or safety concerns | Surveys, escalations | Defined per initiative |

### Rollback Decision Framework

```
Trigger Detected
      │
      ▼
Is it a defined rollback trigger?
      │
  ┌───┴───┐
  │ YES   │ NO
  │       │
  ▼       ▼
Severity? Escalate to Change Lead
  │       for assessment
  │
  ├── CRITICAL → Immediate rollback
  │              (Change Lead authority)
  │
  ├── HIGH → Convene CAB within 4 hours
  │          Decision: rollback, fix-forward, or pause
  │
  └── MEDIUM → Monitor for 24 hours
               Escalate if worsening
```

### Rollback Procedure Template

```
Rollback Plan: ____________________
Change Initiative: ____________________
Effective Date: ____________________

1. TRIGGER CONFIRMATION
   - Trigger condition: ____________________
   - Confirmed by: ____________________
   - Time of detection: ____________________

2. DECISION
   - Decision maker: ____________________
   - Decision: [ ] Rollback  [ ] Fix-forward  [ ] Pause and assess
   - Rationale: ____________________

3. ROLLBACK STEPS
   Step 1: ____________________
   Step 2: ____________________
   Step 3: ____________________

4. COMMUNICATION
   - Internal notification: ____________________
   - External notification (if applicable): ____________________
   - Talking points for managers: ____________________

5. VERIFICATION
   - How to confirm rollback is complete: ____________________
   - Who verifies: ____________________

6. POST-ROLLBACK
   - Root cause analysis scheduled: [ ] Yes (date: _____)
   - Revised go-live criteria: ____________________
   - Stakeholder debrief scheduled: [ ] Yes (date: _____)
```

---

## Go/No-Go Criteria

Define explicit criteria that must be met before proceeding with go-live:

| Category | Criterion | Target | Actual | Status |
|----------|----------|--------|--------|--------|
| **Training** | Completion rate for target users | ≥85% | | |
| **Testing** | User acceptance testing passed | 100% critical, 90% overall | | |
| **Infrastructure** | System load testing completed | Pass all scenarios | | |
| **Support** | Help desk staffed and trained | 100% coverage for go-live period | | |
| **Communication** | All stakeholders notified of go-live | 100% | | |
| **Rollback** | Rollback procedure tested and documented | Complete | | |
| **Sponsor** | Executive sponsor sign-off | Obtained | | |
| **Compliance** | Regulatory requirements verified | All met | | |

**Decision rule:** Any criterion with "Fail" status blocks go-live. The CAB must
approve any exceptions.

---

## Do / Don't

- **Do** define rollback triggers before go-live, not during a crisis.
- **Do** test the rollback procedure before it's needed. A rollback plan that
  hasn't been tested is a hope, not a plan.
- **Do** maintain a living risk register that is reviewed at every phase gate.
- **Do** define clear escalation paths and decision-making authority for each
  severity level.
- **Do** include people-side risks (resistance, change fatigue, skill gaps) alongside
  technical risks.
- **Do** document lessons learned from every rollback or risk event.
- **Don't** treat risk assessment as a one-time activity. Risks evolve as the change
  progresses.
- **Don't** set rollback triggers so loose that the organization endures significant
  damage before acting, or so tight that minor hiccups trigger unnecessary rollbacks.
- **Don't** assume "fix-forward" is always better than rollback. Sometimes the fastest
  path to stability is reverting.
- **Don't** skip the post-rollback root cause analysis. Rollback buys time; it
  doesn't solve the underlying issue.
- **Don't** hide rollback events from stakeholders. Transparent communication about
  setbacks builds more trust than spin.
- **Don't** rely on a single person to authorize rollbacks. Define backup decision-makers.

---

## Common Pitfalls

1. **No rollback plan.** The team assumes everything will go smoothly and has no
   reversion strategy. Solution: every change with a go-live event must have a
   documented, tested rollback procedure.

2. **Ambiguous triggers.** Rollback conditions are vaguely defined ("if things go
   wrong"), leading to delayed or disputed decisions during a crisis. Solution: define
   specific, measurable thresholds with named decision-makers.

3. **Optimism bias in risk assessment.** Teams consistently rate likelihood and impact
   too low. Solution: use historical data from similar changes, involve skeptics in
   the assessment, and stress-test assumptions.

4. **Risk register as shelfware.** The register is created at the start and never
   updated. Solution: make risk review a standing agenda item in weekly change
   meetings; assign owners with update deadlines.

5. **Rollback shame.** Teams view rollback as failure and resist triggering it even when
   criteria are met. Solution: normalize rollback as a responsible decision; frame it
   as protecting users and the organization.

---

## Checklist

- [ ] Risk assessment completed with likelihood and impact scores for all identified risks
- [ ] Risk register is maintained with owners, mitigations, and status
- [ ] Rollback triggers are defined with specific, measurable thresholds
- [ ] Rollback procedure is documented step-by-step
- [ ] Rollback procedure has been tested (dry run or simulation)
- [ ] Go/No-Go criteria are documented and agreed by CAB
- [ ] Escalation paths are defined for each severity level
- [ ] Decision-making authority for rollback is clearly assigned (with backup)
- [ ] Communication plan for rollback scenario is prepared
- [ ] Post-rollback root cause analysis process is defined
- [ ] Risk review is scheduled as a recurring activity
- [ ] Lessons learned repository is maintained and consulted for new initiatives
