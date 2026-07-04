---
id: customer-enablement
category: Business Practices
entry: true
last-reviewed: 2026-07
---

# Customer Enablement Conventions

## Category
Business Practices

Customer enablement covers the full post-sale lifecycle: onboarding, health
scoring, success planning, satisfaction measurement, feedback, support
escalation, and self-service knowledge. The unifying rule is that every signal
must drive a defined action — scores without playbooks, surveys without
follow-up, and feedback without a review loop are worse than nothing.

---

## Defaults

| Concern | Default | Notes |
|---------|---------|-------|
| Health score | 0–100, weighted average, weekly refresh | Zones: healthy 75–100, at-risk 40–74, critical 0–39 |
| Health signal weights | Usage 35% / Engagement 25% / Support 20% / Financial 20% | Calibrate against historical churn data |
| Onboarding model | High-touch (dedicated CSM), kickoff within 3 business days | Time to first value: 14 days |
| Success plan | Outcome-based, 3–5 outcomes, 12-month rolling | Reviewed at every QBR (quarterly) |
| NPS | Quarterly relational, standard 0–10 scale | Detractor follow-up within 48 hours |
| CSAT | Post-interaction, 1–5 scale, satisfied = 4+ | Target 85%; throttle once per 14 days |
| Feedback prioritization | Impact × frequency matrix, segment-weighted | Enterprise 2.0×, mid-market 1.5×, SMB 1.0× |
| Escalation | 3 tiers (L1 → L2 → L3), SLA-based + manual triggers | P0/P1 bypass straight to L3 |
| Knowledge base | Product-area hierarchy, 5 content tiers | Quarterly accuracy audit |

---

## 1. Customer Health Scoring

- Composite 0–100 score from four weighted categories: **product usage (35%)**,
  **engagement (25%)**, **support experience (20%)**, **financial health (20%)**.
  Declining usage is the strongest leading churn indicator.
- Refresh weekly at minimum; stale scores are worse than no scores.
- Every health zone has an action playbook with owner and cadence: healthy →
  monthly check-in (CSM), at-risk → biweekly with weekly review (escalate to CS
  manager), critical → weekly check-in, daily review, 30-day recovery plan
  (escalate to VP Customer Success).
- Weight objective signals (telemetry, support data, payment history) more
  heavily than subjective ones to prevent CSM score manipulation.
- Exclude accounts in their first 30–60 days, or use an onboarding-specific
  model. Validate weights quarterly against actual churn and expansion.

Full detail: `customer-health-scoring.md`

---

## 2. Onboarding Playbooks

Four phases from contract close to steady state:

1. **Welcome & Kickoff (days 1–3)** — welcome email within 24h; confirm
   stakeholders, success criteria, integration requirements.
2. **Technical Setup (days 3–7)** — provision, integrate, validate before
   inviting end users.
3. **Training & Adoption (days 7–14)** — role-based training; track feature
   activation weekly from day one.
4. **First Value & Handoff (days 14–21)** — confirm the success milestone, hold
   a handoff meeting to the ongoing CSM.

- Define "first value" **with the customer** at kickoff, not internally.
- Agree on 3–5 measurable completion milestones at kickoff — otherwise
  onboarding never ends.
- Require a structured sales-to-CS handoff document (goals, stakeholders,
  technical requirements, promises made in the sales cycle).
- Identify at least two customer stakeholders so a departing champion does not
  stall momentum.

Full detail: `onboarding-playbooks.md`

---

## 3. Success Plans and QBRs

- Structure: customer context → 3–5 desired outcomes → milestones and actions →
  risk and mitigation → review history.
- Outcomes are written from the customer's perspective with a metric, baseline,
  and target date ("Reduce report generation time from 4 hours to 30 minutes"),
  never product features ("adopt the self-service portal"). If no baseline
  exists, the first milestone is to measure one.
- Co-create the plan with the customer; the CSM owns the document, the customer
  co-owns the goals. Every QBR agenda starts with success plan progress.
- Map outcomes explicitly to the renewal conversation: "We agreed you wanted X.
  Here is the evidence of X achieved."
- Never skip the risk section — every plan has risks, and acknowledging them
  builds trust.

Full detail: `success-plan-templates.md`

---

## 4. NPS / CSAT Measurement

- **NPS** = % Promoters (9–10) − % Detractors (0–6); Passives are 7–8. Use
  relational NPS quarterly for trend tracking and transactional NPS for
  operational improvement. Never modify the 0–10 scale.
- **CSAT** = satisfied responses (4–5 on a 5-point scale) ÷ total × 100,
  triggered immediately post-interaction. CSAT measures a moment; NPS measures
  the relationship — a customer can rate support 5/5 and still be a detractor.
- Always pair the score with an open-text "primary reason" question.
- Contact every detractor within 48 hours — the highest-ROI activity in any NPS
  program. Track detractor recovery rate the next cycle.
- Report by segment (enterprise / mid-market / SMB); blended scores hide
  actionable patterns. Trends over 3+ quarters are signal; single quarters are
  noise.
- Throttle: NPS once per quarter per customer, CSAT once per 14 days across all
  triggers. Never use NPS as an individual CSM performance metric.

Full detail: `nps-csat-measurement.md`

---

## 5. Feedback Collection

- Five feedback types with distinct routing: feature requests (capture the job
  to be done, not the requested solution), bug reports (route to engineering
  triage), usability feedback, praise (protect it during redesigns), and churn
  signals (route to CS for immediate intervention).
- Collect at the moment of experience — post-action surveys get 3–5× the
  response rate of periodic email. Max 3 questions per in-app survey.
- Prioritize with an impact × frequency matrix weighted by segment; tie the
  review to a recurring product ceremony with documented outcomes.
- Close the loop with every submitter; ignored feedback programs erode trust
  faster than having none.
- Include exit surveys in the cancellation flow to avoid survivorship bias.
  Centralize all channels in one system with consistent tagging.

Full detail: `feedback-collection.md`

---

## 6. Escalation and Knowledge Base

**Escalation** (`escalation-workflows.md`):
- Three tiers: L1 front-line (4h first response), L2 specialist (2h), L3
  engineering/executive (1h). Severity overrides route P0/P1 directly to L3.
- Every escalation carries a structured note: symptom, steps tried, customer
  impact, account context. The receiving tier owns the ticket — no ping-pong,
  no shadow escalations outside the ticketing system.
- Define de-escalation criteria so resolved-critical issues return to lower
  tiers. Track SLA compliance on original creation time to prevent clock games.

**Knowledge base** (`knowledge-base.md`):
- Five content tiers: getting started, how-to, reference, conceptual,
  troubleshooting (symptom → cause → resolution → prevention). One tier per
  article; one template per tier.
- Organize by customer task, never internal org chart. Titles are task
  statements ("How to configure SSO").
- Review failed searches weekly and fill the top unanswered queries. Tie
  content audits to the product release cycle; archive articles with zero views
  in 90 days.

---

## Do / Don't

**Do:**
- Define an action playbook for every health zone before shipping the score.
- Co-create success plans and first-value definitions with the customer.
- Contact every NPS detractor within 48 hours and log the outcome.
- Segment every metric (health, NPS, CSAT, feedback) by customer tier.
- Transfer full context on every escalation and support handoff.
- Close the feedback loop — acknowledge, act, and notify the submitter.
- Track adoption weekly from onboarding day one, not at the end.

**Don't:**
- Use a single metric (NPS alone, logins alone) as a health proxy.
- Penalize new customers with health scores during their first 30–60 days.
- List product features as success plan outcomes — features are means, not ends.
- Survey the same customer more than once per quarter (NPS) or per 14 days (CSAT).
- Let one loud customer dictate priorities — use the impact × frequency matrix.
- Allow escalations to bypass the ticketing system via Slack DMs or email.
- Organize the knowledge base by internal team structure.

---

## Common Pitfalls

1. **Scoring without action playbooks.** The dashboard shows 32 and nobody
   knows what to do. Define interventions per zone with owners and timelines.
2. **Measuring without acting.** NPS becomes a vanity metric. Every cycle must
   produce a prioritized action list with owners and deadlines.
3. **Sales-to-CS handoff gap.** The CSM starts from scratch after close.
   Require a structured handoff document including promises made during sales.
4. **Single-threaded stakeholder.** Champion leaves, plan dies. Always involve
   at least two customer stakeholders and document decisions in shared space.
5. **Survey fatigue and survivorship bias.** Over-surveyed customers stop
   responding; churned customers are never asked. Throttle per customer and add
   exit surveys.
6. **No context transfer on escalation.** The customer repeats their story at
   every tier. Enforce the structured escalation note.
7. **Vendor-centric outcomes.** "80% feature adoption" instead of the business
   result it enables. Rewrite every outcome to answer "so that the customer
   can…".

---

## Checklist

- [ ] Health score configured (0–100, four weighted categories, weekly refresh)
- [ ] Zone playbooks defined with owners, cadences, and escalation paths
- [ ] New-customer scoring exclusion (first 30–60 days) in place
- [ ] Onboarding kickoff within 3 business days; first-value criteria agreed with customer
- [ ] Sales-to-CS handoff document required and reviewed
- [ ] Success plan with 3–5 baselined, measurable outcomes, co-created with customer
- [ ] QBR cadence set; every review starts with success plan progress
- [ ] NPS quarterly (0–10 standard scale) with 48-hour detractor follow-up
- [ ] CSAT on key transactional touchpoints, throttled once per 14 days
- [ ] All satisfaction metrics segmented by customer tier
- [ ] Feedback prioritized via impact × frequency matrix with closed-loop process
- [ ] Escalation tiers, SLAs, severity overrides, and note template enforced
- [ ] Knowledge base tiered, task-organized, with weekly failed-search review
