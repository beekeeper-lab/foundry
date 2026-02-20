# Corrective and Preventive Action (CAPA)

Standards for identifying, investigating, and resolving quality issues through
systematic corrective and preventive action. CAPA is the backbone of continual
improvement in ISO 9001 (Clause 10.2 — Nonconformity and corrective action).

---

## Defaults

- **Trigger:** Any nonconformity — audit findings, customer complaints, process
  failures, product defects, near-misses.
- **Root cause analysis:** Required for all corrective actions. No corrective
  action is complete without understanding why the problem occurred.
- **Verification:** Every corrective action must be verified for effectiveness.
  "We fixed it" is not evidence — "we verified it stays fixed" is.
- **Timeline:** Corrective actions should have defined due dates. Typical
  targets: containment within 24-48 hours, root cause within 2 weeks,
  corrective action implementation within 30 days.

---

## CAPA Workflow

```
  Nonconformity Detected
         │
         ▼
  ┌──────────────┐
  │  Containment  │  Immediate action to prevent further impact
  │   Action      │  (quarantine, stop shipment, disable feature)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Investigation │  Gather facts, data, evidence
  │              │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Root Cause   │  Determine why the problem occurred
  │  Analysis     │  (not just what happened)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Corrective   │  Eliminate the root cause to prevent recurrence
  │  Action       │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Verification  │  Confirm the corrective action is effective
  │              │  and the problem does not recur
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Preventive   │  Extend the fix to prevent similar problems
  │  Action       │  in other areas (optional but valuable)
  └──────────────┘
```

---

## Root Cause Analysis Techniques

| Technique | When to Use | How It Works |
|-----------|-------------|-------------|
| **5 Whys** | Simple problems with a single root cause | Ask "Why?" repeatedly until the fundamental cause is reached. Typically 5 iterations. |
| **Fishbone (Ishikawa)** | Complex problems with multiple potential causes | Categorize causes: People, Process, Equipment, Materials, Environment, Measurement |
| **Fault Tree Analysis** | Safety-critical or high-severity issues | Top-down deductive analysis using Boolean logic to trace failure paths |
| **Pareto Analysis** | Recurring problems needing prioritization | Identify the 20% of causes responsible for 80% of occurrences |

### 5 Whys Example (Software Context)

```
Problem: Production deployment failed at 2:00 AM

Why 1: The deployment script timed out.
Why 2: The database migration took 45 minutes instead of the expected 2.
Why 3: The migration performed a full table scan on a 50M row table.
Why 4: The migration added an index without using CONCURRENTLY.
Why 5: The migration review checklist does not include a performance check
       for large tables.

Root Cause: Migration review process lacks a performance gate for large tables.
Corrective Action: Add a mandatory performance review step for migrations
                   affecting tables over 1M rows.
```

---

## CAPA Record Template

```markdown
# CAPA Record

| Field | Value |
|-------|-------|
| **CAPA ID** | CAPA-2026-007 |
| **Date Opened** | YYYY-MM-DD |
| **Source** | [Audit / Customer Complaint / Internal / Supplier / Other] |
| **Nonconformity** | [Clear description of what went wrong] |
| **Affected Process** | [Process name and clause reference] |
| **Severity** | [Critical / Major / Minor] |

## Containment Action
- **Action:** [What was done immediately]
- **Date:** YYYY-MM-DD
- **Responsible:** [Name]

## Investigation
- **Evidence gathered:** [List of data, records, interviews]
- **Timeline of events:** [Sequence of what happened]

## Root Cause Analysis
- **Method used:** [5 Whys / Fishbone / Fault Tree / Other]
- **Root cause:** [The fundamental reason the problem occurred]
- **Contributing factors:** [Other factors that enabled the problem]

## Corrective Action
- **Action:** [What will be done to eliminate the root cause]
- **Responsible:** [Name]
- **Due date:** YYYY-MM-DD
- **Completion date:** YYYY-MM-DD

## Verification of Effectiveness
- **Method:** [How effectiveness will be verified]
- **Date verified:** YYYY-MM-DD
- **Result:** [Effective / Not effective — if not, reopen]
- **Verified by:** [Name]

## Preventive Action (if applicable)
- **Action:** [Extension to other areas to prevent similar issues]
- **Scope:** [Which other processes/products are affected]

## CAPA Status: [Open / In Progress / Closed]
```

---

## Do / Don't

- **Do** investigate the root cause, not just the symptom. Fixing the symptom
  guarantees recurrence.
- **Do** contain the immediate impact quickly. Root cause analysis takes time;
  containment is urgent.
- **Do** verify corrective action effectiveness with objective evidence (data,
  test results, audit findings).
- **Do** look for systemic patterns. If the same type of problem recurs in
  different areas, the root cause may be organizational.
- **Do** close CAPAs promptly. Open CAPAs that linger lose urgency and credibility.
- **Don't** accept "operator error" as a root cause. Ask why the process
  allowed the error to occur.
- **Don't** implement corrective actions without a verification plan. How will
  you know it worked?
- **Don't** treat CAPA as paperwork. The value is in the investigation and
  the fix, not the form.
- **Don't** skip preventive action. Corrective action fixes one instance;
  preventive action fixes the class of problems.

---

## Common Pitfalls

1. **Shallow root cause analysis.** "The operator made a mistake" is not a root
   cause. Solution: always ask at least 5 levels deep. The root cause should
   point to a process, system, or design flaw.
2. **CAPA backlog.** Hundreds of open CAPAs that nobody is working on. Solution:
   limit work in progress, prioritize by severity, set realistic due dates.
3. **Effectiveness not verified.** The corrective action was implemented but
   nobody checked if the problem actually stopped. Solution: build verification
   into the CAPA record as a mandatory step.
4. **Corrective action is "retrain."** Retraining addresses knowledge gaps but
   does not fix process deficiencies. If the process allowed the error, fix the
   process. Solution: require process changes alongside training.
5. **No trending.** Individual CAPAs are closed but nobody looks for patterns.
   Solution: review CAPA data quarterly — chart by type, source, process area,
   and recurrence rate.

---

## CAPA Metrics

| Metric | Target | Why It Matters |
|--------|--------|---------------|
| **Average time to close** | < 30 days (minor), < 60 days (major) | Measures responsiveness |
| **Overdue CAPAs** | 0 | Overdue CAPAs indicate resource or priority problems |
| **Effectiveness rate** | > 90% | Percentage of CAPAs verified effective on first attempt |
| **Recurrence rate** | < 5% | Problems that come back indicate ineffective root cause analysis |
| **CAPAs by source** | Trending | Identifies where most quality issues originate |

---

## Checklist

- [ ] Nonconformity is clearly described with objective evidence
- [ ] Containment action is implemented immediately
- [ ] Root cause analysis is performed using a recognized technique
- [ ] Root cause identifies a process/system flaw, not just human error
- [ ] Corrective action addresses the root cause, not just the symptom
- [ ] Corrective action has an owner and due date
- [ ] Effectiveness verification is planned and executed
- [ ] Preventive action is considered for broader application
- [ ] CAPA record is complete and retained
- [ ] CAPA data is reviewed periodically for trends
