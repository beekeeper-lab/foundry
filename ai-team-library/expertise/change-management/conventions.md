---
id: change-management
category: Business Practices
entry: true
last-reviewed: 2026-07
---

# Change Management Conventions

## Category
Business Practices

Defaults and frameworks for managing the people-side of organizational change —
adoption, engagement, and resistance management. The pack is anchored on ADKAR:
every affected person must progress through Awareness, Desire, Knowledge,
Ability, and Reinforcement, and interventions target the lowest-scored stage
(the barrier point).

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| Framework | ADKAR (Awareness, Desire, Knowledge, Ability, Reinforcement) | Kotter 8-Step, Lewin 3-Stage, Bridges Transition Model, McKinsey 7-S |
| Scope | People-side of change — adoption, engagement, resistance | Technical change management (ITIL) for system changes |
| Governance | Change Advisory Board (CAB) with defined escalation paths | Lightweight peer-review for low-risk changes |
| Readiness | Organizational readiness assessment before launch | Skip only for trivial, low-impact changes |
| Stakeholder mapping | Power/Interest Grid (Mendelow) with disposition tracking | Salience Model, RACI, Influence/Impact Matrix |
| Communication | Cadenced, multi-channel (push + pull), bi-directional | Single channel only for low-impact changes |
| Training | Blended, just-in-time, role-based, ≥50% hands-on practice | Fully self-paced (minor) or bootcamp (transformational) |
| Risk | Likelihood × Impact matrix (1–25) with defined thresholds | Qualitative ranking for small changes |
| Rollback | Pre-defined, measurable triggers agreed by CAB before go-live | No rollback plan only for irreversible changes |
| Reinforcement | 90-day post-go-live support with graduated reduction | Extended support for transformational changes |

---

## 1. ADKAR and Readiness

- Score each target group 1–5 on all five ADKAR dimensions; the lowest score
  is the **barrier point** — focus intervention there. Pushing past an
  unaddressed barrier produces failed adoption.
- Assess organizational readiness (leadership alignment, culture, capacity,
  capability, communication infrastructure, stakeholder disposition) before
  committing to timelines. Score 25–30 = proceed; 18–24 = close gaps first;
  12–17 = phased approach; 6–11 = do not proceed.
- Match approach to change type: incremental (lightweight, days–weeks),
  transitional (formal plan + training, weeks–months), transformational (full
  program + executive sponsorship, months–years).
- Don't skip the Desire phase — awareness without motivation produces informed
  resisters.

Full detail: `fundamentals.md`

---

## 2. Stakeholder Management

- Map stakeholders on the Power/Interest Grid **before** the first
  announcement: High/High = Manage Closely (partner, co-design); High
  power/Low interest = Keep Satisfied; Low/High = Keep Informed; Low/Low =
  Monitor.
- Track disposition per group on the Champion → Advocate → Neutral →
  Resistant → Blocker scale, with current and target states, in a living
  stakeholder register reviewed at every phase gate.
- Run impact analysis across six dimensions (process, technology, skills,
  reporting, culture, job security); 4+ affected dimensions = critical
  severity requiring dedicated transition support.
- Treat middle managers as the most critical stakeholder group — equip them
  with talking points, FAQs, and coaching skills before broader communication.
- Handle resistance with the response framework: Listen → Acknowledge →
  Diagnose (which ADKAR element is blocked) → Address → Follow up. Resistance
  is information about gaps in the plan, not "the problem."

Full detail: `stakeholder-management.md`

---

## 3. Communication

- Right message, right audience, right channel, right time. Build a message
  matrix (phase × audience × message × channel × sender × timing × feedback
  mechanism) aligned to ADKAR phases.
- Every key message answers five questions: what is changing, why, who is
  affected and how, when, and how people will be supported.
- Deliver every key message through at least two channels — one push (town
  hall, email, manager cascade) and one pull (intranet, FAQ, recordings).
- Match sender authority to message type: sponsors deliver vision and
  commitment (non-delegable), managers deliver team impact, experts deliver
  how-to.
- Brief managers before broader announcements; include a feedback path with
  every communication; maintain cadence even when there's "nothing new."

Full detail: `communication-plans.md`

---

## 4. Training and Adoption

- Train just-in-time (within 1–2 weeks of skill need), role-based and
  task-oriented ("how to submit a purchase request," not "the Procurement
  Module"), progressive (80% case first), with ≥50% hands-on practice.
- Follow the four-phase learning path: Foundation (awareness + context) →
  Skill Building (knowledge) → Application (ability) → Mastery
  (reinforcement).
- Measure adoption, not activity: usage (active users, feature utilization),
  proficiency (task completion time, error rate, ticket volume), satisfaction
  (survey scores, NPS), and compliance — against a pre-go-live baseline.
- Intervention thresholds on the adoption curve: <40% by week 4 = intervene;
  <60% by week 8 = review training/support; <80% by week 12 = escalate to
  sponsor.
- Sustain with super users, floor walkers, micro-learning (spaced repetition
  to beat the forgetting curve), manager check-ins, and refresher training at
  weeks 4/8/12 — for at least 90 days post-go-live.

Full detail: `training-and-adoption.md`

---

## 5. Risk and Rollback

- Maintain a risk register (likelihood × impact, 1–25) covering people,
  process, technology, timeline, external, and organizational categories.
  Thresholds: 1–4 accept/monitor; 5–9 mitigate; 10–15 escalate with active
  mitigation; 16–25 escalate to sponsor, consider delay or rollback.
- Define rollback triggers **before** go-live with specific, measurable
  thresholds (e.g., >4h unplanned downtime, any confirmed data loss, <25%
  adoption after 2 weeks, >300% baseline error rate), agreed by the CAB, with
  named decision-makers and backups.
- Severity drives response: CRITICAL = immediate rollback (Change Lead
  authority); HIGH = convene CAB within 4 hours (rollback, fix-forward, or
  pause); MEDIUM = monitor 24 hours.
- Test the rollback procedure before it's needed — an untested rollback plan
  is a hope, not a plan.
- Gate go-live on explicit Go/No-Go criteria (training ≥85% complete, UAT
  passed, support staffed, rollback tested, sponsor sign-off, compliance
  verified); any failing criterion blocks go-live absent CAB exception.

Full detail: `risk-and-rollback.md`

---

## Do / Don't

**Do:**
- Start with a clear change vision answering "why now" and "what's in it for me."
- Identify and activate a sponsor coalition; define non-delegable sponsor actions.
- Assess readiness and map stakeholders before announcing anything.
- Address resistance early as a signal, not an obstacle.
- Measure adoption throughout the lifecycle against a baseline, not just at go-live.
- Plan reinforcement from day one — changes revert without sustained support.
- Define and test rollback triggers before go-live.

**Don't:**
- Assume a good technical solution sells itself — people adopt changes, not systems.
- Skip the Desire phase or the manager cascade.
- Rely solely on email; use multiple channels and formats.
- Measure activity (emails sent, sessions held) instead of adoption outcomes.
- Declare victory at go-live — the highest support need is weeks 1–4 after launch.
- Treat "fix-forward" as always better than rollback, or hide rollback events from stakeholders.

---

## Common Pitfalls

1. **Absent sponsorship.** No visible executive champion, or the sponsor
   delegates everything downward. Define explicit sponsor actions and hold
   sponsors accountable.
2. **Change saturation.** Too many concurrent changes hit the same groups.
   Maintain a change portfolio view; stagger or consolidate initiatives.
3. **Ignoring middle management.** Frontline managers are the most critical
   change agents yet often the last informed. Equip them first.
4. **Communication vacuum.** Gaps between updates let rumors fill the void.
   Keep a regular cadence even with nothing new to report.
5. **Training as checkbox.** Attendance is measured instead of competence.
   Measure proficiency and adoption outcomes against a pre-go-live baseline.
6. **Ambiguous rollback triggers.** "If things go wrong" delays crisis
   decisions. Define measurable thresholds with named decision-makers.
7. **Static artifacts.** Stakeholder register and risk register created once
   and never updated. Review both at every phase gate.

---

## Checklist

- [ ] Change vision and objectives documented and approved by sponsors
- [ ] Organizational readiness assessment completed; plan calibrated to findings
- [ ] ADKAR assessment identifies the barrier point per target group
- [ ] Sponsor coalition identified with explicit, tracked sponsor actions
- [ ] Stakeholder register with Power/Interest mapping, dispositions, and engagement strategies
- [ ] Impact analysis completed for high/critical stakeholder groups
- [ ] Communication plan with message matrix, push + pull channels, and feedback mechanisms
- [ ] Manager cascade scheduled before broader announcements
- [ ] Role-based, just-in-time training paths with job aids and super-user network
- [ ] Adoption KPIs defined with baselines, targets, and a tracking dashboard
- [ ] Risk register maintained with owners, mitigations, and review cadence
- [ ] Rollback triggers defined, procedure documented and tested, Go/No-Go criteria agreed by CAB
- [ ] Reinforcement plan spans at least 90 days post-go-live
- [ ] Post-implementation review scheduled
