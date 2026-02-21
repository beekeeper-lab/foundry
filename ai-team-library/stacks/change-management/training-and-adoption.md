# Training and Adoption

Frameworks for designing training curricula, measuring adoption, and sustaining
behavioral change. Training builds Knowledge and Ability (ADKAR stages 3 and 4),
while adoption tracking ensures change sticks beyond go-live.

---

## Defaults

| Aspect | Default | Alternatives |
|--------|---------|-------------|
| **Training Approach** | Blended learning (instructor-led + self-paced + hands-on practice) | Fully self-paced for minor changes; immersive bootcamp for transformational changes |
| **Timing** | Just-in-time — train close to when skills are needed | Pre-training weeks in advance (increases forgetting) |
| **Assessment** | Pre/post competency assessment to measure learning | No formal assessment for low-impact changes |
| **Adoption Metrics** | Usage data + proficiency measures + satisfaction surveys | Usage data only for simple tool changes |
| **Reinforcement** | 90-day post-go-live support with graduated reduction | Extended support for transformational changes |

---

## Training Curricula Design

### Learning Path Template

```
Change Initiative: ____________________
Target Audience:   ____________________

Role-Based Learning Path:
┌─────────────────────────────────────────────────────┐
│ Phase 1: Foundation (Awareness + Context)            │
│ ├── What is changing and why (30 min)                │
│ ├── Impact on your role (15 min)                     │
│ └── Overview of new process/tool (30 min)            │
├─────────────────────────────────────────────────────┤
│ Phase 2: Skill Building (Knowledge)                  │
│ ├── Core workflow walkthrough (60 min, instructor)    │
│ ├── Hands-on practice exercises (90 min, lab)        │
│ └── Edge cases and troubleshooting (30 min)          │
├─────────────────────────────────────────────────────┤
│ Phase 3: Application (Ability)                       │
│ ├── Supervised practice in real environment (1 week)  │
│ ├── Peer buddy system activation                     │
│ └── Support resources walkthrough (15 min)           │
├─────────────────────────────────────────────────────┤
│ Phase 4: Mastery (Reinforcement)                     │
│ ├── Advanced scenarios workshop (60 min)             │
│ ├── Knowledge check / certification (30 min)         │
│ └── Ongoing micro-learning modules (5 min each)      │
└─────────────────────────────────────────────────────┘
```

### Training Format Selection

| Format | Best For | Group Size | Duration | Cost |
|--------|---------|-----------|----------|------|
| **Instructor-led (in-person)** | Complex processes, hands-on systems, high-impact groups | 10–25 | 2–8 hours | High |
| **Virtual instructor-led** | Geographically distributed teams, moderate complexity | 10–50 | 1–4 hours | Medium |
| **Self-paced e-learning** | Simple tool changes, broad audiences, compliance topics | Unlimited | 15–60 min | Low |
| **Job aids / quick reference** | Task-specific guidance, just-in-time support | Unlimited | 2–5 min | Very Low |
| **Peer coaching / buddy system** | On-the-job application, cultural change | 1:1 or 1:3 | Ongoing | Low |
| **Sandbox / simulation** | System changes requiring safe practice | 5–20 | 1–4 hours | Medium |
| **Video / screen recording** | Demonstrations, refresher content | Unlimited | 5–20 min | Low |

### Content Design Principles

1. **Role-based** — Tailor content to what each role needs to do differently, not a
   generic overview of the entire change.
2. **Task-oriented** — Structure around tasks people perform, not system features.
   "How to submit a purchase request" not "The Procurement Module."
3. **Progressive** — Layer complexity. Start with the 80% case, then address exceptions.
4. **Practice-heavy** — Adults learn by doing. Minimum 50% of training time should be
   hands-on practice.
5. **Supported** — Every training session should end with "here's where to get help."

---

## Adoption KPI Framework

### Adoption Metrics by Category

| Category | Metric | Measurement Method | Target Example |
|----------|--------|--------------------|---------------|
| **Usage** | Active users / total target users | System analytics | 90% within 30 days |
| **Usage** | Feature utilization rate | System analytics | 70% using core features by week 4 |
| **Usage** | Login frequency / session duration | System analytics | Daily active use |
| **Proficiency** | Task completion time (new vs. old) | Time studies, system logs | Within 120% of old process by day 30 |
| **Proficiency** | Error rate | System logs, support tickets | Below baseline by day 60 |
| **Proficiency** | Help desk ticket volume | ITSM data | Declining trend after week 2 |
| **Satisfaction** | User satisfaction score | Survey (Likert scale) | 3.5/5 minimum |
| **Satisfaction** | Net Promoter Score (NPS) | Survey | Positive NPS by day 90 |
| **Compliance** | Process adherence rate | Audit / spot checks | 95% by day 60 |
| **Business** | Target business outcome | Business metrics | Achieved within 6 months |

### Adoption Curve Tracking

```
Adoption %
100│                                          ──────── Target
   │                                   ●───●
 80│                              ●───●
   │                         ●───●
 60│                    ●───●
   │               ●───●
 40│          ●───●
   │     ●───●
 20│●───●
   │
  0├──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──
   W1 W2 W3 W4 W5 W6 W7 W8 W9 W10 W11 W12
                 Weeks Post Go-Live

Adoption Thresholds:
  < 40% by Week 4:  ⚠ Intervention required
  < 60% by Week 8:  ⚠ Review training and support
  < 80% by Week 12: ⚠ Escalate to sponsor
```

---

## Reinforcement Strategies

| Strategy | Description | Timing |
|----------|-------------|--------|
| **Floor walkers** | Roaming support during first days/weeks of go-live | Week 1–2 |
| **Super users** | Trained power users embedded in teams for ongoing peer support | Weeks 1–12+ |
| **Micro-learning** | Short (2–5 min) refresher modules on specific tasks | Weekly for first 90 days |
| **Recognition** | Public acknowledgment of adoption milestones and champions | Ongoing |
| **Gamification** | Leaderboards, badges, or team challenges for adoption targets | Weeks 2–8 |
| **Manager check-ins** | Structured 1:1 questions about the change | Weekly for 4 weeks, then bi-weekly |
| **Feedback loops** | Collect and act on user feedback; communicate improvements made | Bi-weekly |
| **Refresher training** | Targeted sessions addressing common gaps identified post-launch | Weeks 4, 8, 12 |

---

## Do / Don't

- **Do** train just-in-time — as close to when skills will be used as practical.
- **Do** provide job aids (cheat sheets, quick reference cards) for every training session.
- **Do** measure adoption with leading indicators (usage, proficiency), not just
  lagging indicators (business outcomes).
- **Do** establish a super-user network before go-live and equip them to coach peers.
- **Do** plan for the "valley of despair" — the productivity dip that occurs as people
  learn new ways of working.
- **Do** differentiate training by role and impact level. Not everyone needs the same depth.
- **Don't** rely on a single training event. One session does not create lasting behavior change.
- **Don't** train too early. Skills decay rapidly without practice — train within 1–2 weeks
  of needing the skill.
- **Don't** measure only training completion. Completion means attendance, not competence.
- **Don't** end support at go-live. The highest support need is in the first 2–4 weeks
  post-launch.
- **Don't** ignore training for managers. They need to know how to coach their teams,
  not just use the system themselves.
- **Don't** assume online training works for everyone. Offer multiple formats and
  accommodate different learning styles.

---

## Common Pitfalls

1. **Training as checkbox.** Training is treated as a compliance event rather than a
   capability-building program. Solution: measure outcomes (proficiency, adoption),
   not just attendance.

2. **Premature training withdrawal.** Support and training resources are removed before
   adoption stabilizes. Solution: maintain graduated support for at least 90 days
   post-go-live; use data to determine when to scale down.

3. **Ignoring the forgetting curve.** People forget 70% of new information within 24 hours
   without reinforcement. Solution: spaced repetition — follow up initial training with
   micro-learning at increasing intervals (1 day, 3 days, 1 week, 2 weeks).

4. **Generic training content.** The same material for all roles regardless of impact.
   Solution: create role-based learning paths that focus on what each role does differently.

5. **No adoption baseline.** Adoption metrics are tracked without establishing a baseline,
   making it impossible to demonstrate improvement. Solution: measure current-state
   performance before go-live.

---

## Checklist

- [ ] Role-based learning paths are designed for each target audience
- [ ] Training formats are selected based on content type and audience needs
- [ ] Training schedule is aligned with go-live timeline (just-in-time)
- [ ] Job aids and quick reference materials are created for all core tasks
- [ ] Super-user network is identified and trained before go-live
- [ ] Adoption KPIs are defined with baselines, targets, and measurement methods
- [ ] Adoption tracking dashboard is set up before go-live
- [ ] Reinforcement plan spans at least 90 days post-go-live
- [ ] Manager coaching guide is developed and distributed
- [ ] Feedback mechanisms are in place to capture and act on learner input
- [ ] Contingency plan exists for low-adoption scenarios (additional training, support)
- [ ] Training materials are versioned and owned for ongoing maintenance
