---
id: iso-9000
category: Compliance & Governance
entry: true
last-reviewed: 2026-07
---

# ISO 9000 Conventions

## Category
Compliance & Governance

Standards for implementing and maintaining a Quality Management System (QMS)
aligned with the ISO 9000 family: ISO 9001:2015 (requirements), ISO 9000:2015
(fundamentals and vocabulary), and ISO 19011:2018 (audit guidelines). The QMS
must drive actual quality improvement — it is not a documentation exercise.

---

## Defaults

| Concern | Default |
|---------|---------|
| Standard | ISO 9001:2015 (requirements), backed by ISO 9000:2015 (vocabulary) |
| Approach | Process-based, applying the Plan-Do-Check-Act (PDCA) cycle |
| QMS scope | All processes affecting product/service quality, design through post-delivery |
| Management commitment | Top management demonstrates leadership and commitment — not optional |
| Internal audits | At planned intervals per Clause 9.2; at minimum annually per process area |
| Audit standard | ISO 19011:2018; auditors trained, competent, independent of the area audited |
| Certification audits | Stage 1 (documentation) + Stage 2 (implementation); surveillance annual; recertification every 3 years |
| CAPA trigger | Any nonconformity — audit findings, complaints, process failures, defects, near-misses |
| Root cause analysis | Required for all corrective actions; every action verified for effectiveness |
| CAPA timeline | Containment 24–48 h; root cause within 2 weeks; implementation within 30 days |
| Document control | ISO 9001:2015 Clause 7.5; electronic preferred, Git acceptable for technical docs |
| Records retention | Per regulatory, contractual, and organizational requirements |

---

## 1. QMS Fundamentals

- Apply the seven quality management principles: customer focus, leadership,
  engagement of people, process approach, improvement, evidence-based decision
  making, relationship management.
- Run every process through PDCA: Plan (objectives, criteria, standards),
  Do (implement), Check (measure against objectives), Act (improve).
- Define a quality policy understood at all levels; tie measurable quality
  objectives to customer satisfaction.
- Assign process owners accountable for process performance; conduct
  management reviews at planned intervals with documented outcomes.
- Apply risk-based thinking throughout (Clause 6.1): identify risks to QMS
  objectives, assess impact/likelihood, plan and monitor treatments. A formal
  framework (ISO 31000) is not required, but the thinking must be demonstrable.
- Know the clause structure: 4 Context, 5 Leadership, 6 Planning, 7 Support,
  8 Operation, 9 Performance Evaluation, 10 Improvement.

Full detail: `qms-fundamentals.md`

---

## 2. Audit Procedures

- Three audit types: internal (1st party, own trained auditors), supplier
  (2nd party), certification (3rd party, accredited body).
- Process: plan the annual program → prepare (docs review, checklist,
  communicate plan) → conduct (opening meeting, gather evidence, record
  findings, closing meeting) → report → follow up to verified closure.
- Classify findings as conformity, nonconformity (major/minor), or
  opportunity for improvement (OFI).
- Every finding must include the clause, the requirement, the evidence, and
  the gap — never "procedure not followed" with no specifics.
- Plan audits based on risk — high-risk processes get more frequent audits.
- Never audit your own work; rotate auditors for independence and fresh
  perspectives. Report audit results to management review.

Full detail: `audit-procedures.md`

---

## 3. Corrective and Preventive Action (CAPA)

- CAPA is the backbone of continual improvement (Clause 10.2). Workflow:
  containment → investigation → root cause analysis → corrective action →
  verification of effectiveness → preventive action (extend the fix).
- Pick the RCA technique for the problem: 5 Whys (simple, single cause),
  Fishbone/Ishikawa (multiple potential causes), Fault Tree (safety-critical),
  Pareto (recurring problems needing prioritization).
- The root cause must point to a process, system, or design flaw — "operator
  error" is not a root cause; ask why the process allowed the error.
- "We fixed it" is not evidence — "we verified it stays fixed" is. Every
  corrective action needs a verification plan with objective evidence.
- Track metrics: time to close (< 30 days minor, < 60 major), overdue CAPAs
  (target 0), effectiveness rate (> 90%), recurrence rate (< 5%); review CAPA
  data quarterly for trends.

Full detail: `capa.md`

---

## 4. Document Control and Records

- Documents prescribe how to do something and are version-controlled and
  approved; records are immutable evidence that something was done and are
  never revised.
- Clause 7.5 requirements: identification (title, date, author, version),
  review and approval before issue, availability at points of use, protection,
  change control with revision history, control of external documents,
  prevention of obsolete-version use, defined retention and disposition.
- Git satisfies much of this for software teams (versioning, PR review/
  approval, access control, audit trail, `main` as the current approved
  version) — but Git does NOT cover retention policies, training records,
  external document control, or non-technical records.
- Maintain a master list/index of controlled documents; review documents
  periodically for continued adequacy.

Full detail: `document-control.md`

---

## 5. Standards and References

- Primary: ISO 9000:2015, ISO 9001:2015 (the certifiable standard),
  ISO 9004:2018 (sustained success), ISO 19011:2018 (auditing).
- Related Annex SL standards integrate with 9001: ISO 14001, ISO 45001,
  ISO 27001. Industry derivatives: AS9100 (aerospace), IATF 16949
  (automotive), ISO 13485 (medical devices), ISO/IEC 90003 (software).
- Full texts require purchase (iso.org, ANSI); free guidance is available
  from ISO TC 176 and the ISO 9001 Auditing Practices Group.

Full detail: `references.md`

---

## Do / Don't

**Do:**
- Define a clear quality policy with measurable objectives tied to customer satisfaction.
- Document processes at the level needed for consistency — not more, not less.
- Plan audits by risk, use objective evidence, and frame findings constructively.
- Investigate root causes, not symptoms; contain immediate impact quickly.
- Verify corrective action effectiveness and look for systemic patterns.
- Record approvals, maintain a master document list, and protect records from alteration.

**Don't:**
- Treat the QMS as a documentation exercise or delegate quality to a "quality department."
- Audit your own work, or limit audits to documentation review without observing practice.
- Accept "operator error" as a root cause or use "retrain" as the default fix.
- Skip follow-up — an unverified corrective action is an open nonconformity.
- Let uncontrolled "convenience copies" of documents proliferate.
- Retain records longer than required without justification — excess retention creates liability.

---

## Common Pitfalls

1. **Documentation overload.** Excessive documentation nobody reads. Document
   what adds value — ISO 9001:2015 reduced mandatory documentation vs. 2008.
2. **Management lip service.** Leadership endorses the QMS without resources or
   participation. Make management review a calendar event with documented actions.
3. **Checklist-only auditing.** Mechanical box-checking. Train auditors to probe,
   ask "why," and follow the process end-to-end.
4. **Shallow root cause analysis.** Ask at least 5 levels deep; the root cause
   should point to a process, system, or design flaw.
5. **Effectiveness not verified.** The fix was implemented but nobody checked the
   problem stopped. Build verification into the CAPA record as a mandatory step.
6. **CAPA backlog and no trending.** Hundreds of stale CAPAs, patterns unseen.
   Limit WIP, prioritize by severity, chart CAPA data quarterly.
7. **Outdated master list / scattered records.** The index doesn't match reality
   and records live across tools. Automate the index; define one records system.

---

## Checklist

- [ ] Quality policy defined, documented, communicated; objectives measurable
- [ ] Process approach applied — processes identified, sequenced, managed with owners
- [ ] Risks and opportunities identified and addressed (Clause 6.1)
- [ ] Management reviews conducted at planned intervals with documented outcomes
- [ ] Annual audit program covers all QMS processes; auditors independent
- [ ] Findings classified (conformity, minor/major NC, OFI) with clause, requirement, evidence, gap
- [ ] Corrective actions have owners, due dates, and verified effectiveness
- [ ] Root cause analysis performed with a recognized technique for every NC
- [ ] CAPA data reviewed periodically for trends
- [ ] Documents version-identified, approved, current at points of use
- [ ] Obsolete versions prevented from unintended use; external documents controlled
- [ ] Records identified, protected, retrievable, retained per schedule
- [ ] Team has access to ISO 9001:2015, ISO 9000:2015, and ISO 19011:2018 texts
