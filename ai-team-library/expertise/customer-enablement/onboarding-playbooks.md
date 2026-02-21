# Customer Onboarding Playbooks

Structured playbooks that guide new customers from contract signing through first
value realization. Onboarding is the highest-leverage moment in the customer
lifecycle — a poor experience here compounds into churn.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Onboarding model** | High-touch (dedicated CSM) | Tech-touch (automated), hybrid |
| **Kickoff timing** | Within 3 business days of contract close | Same-day, within 1 week |
| **Time to first value** | 14 days | 7 days (simple products), 30 days (complex) |
| **Playbook format** | Phase-based checklist | Milestone-based, outcome-based |
| **Handoff trigger** | All onboarding milestones complete | Time-based (30/60/90 days) |
| **Success metric** | Feature adoption rate at day 14 | Time to first value, login frequency |

---

## Onboarding Phases

### Phase 1 — Welcome & Kickoff (Days 1–3)

Send a welcome email within 24 hours of contract close. Schedule the kickoff call.
Confirm stakeholders, success criteria, and integration requirements. Set
expectations for the onboarding timeline.

### Phase 2 — Technical Setup (Days 3–7)

Provision accounts, configure integrations, and import data. Assign a technical
onboarding specialist if the setup requires API integration or SSO configuration.
Validate the environment before inviting end users.

### Phase 3 — Training & Adoption (Days 7–14)

Deliver role-based training sessions. Provide self-service resources (videos,
docs, in-app guides). Track feature activation to identify adoption gaps early.

### Phase 4 — First Value & Handoff (Days 14–21)

Confirm the customer has achieved their defined success milestone. Conduct a
review call to celebrate progress and introduce the ongoing CSM. Document lessons
learned and update the customer health record.

---

## Do / Don't

- **Do** define "first value" with the customer during the kickoff call, not
  internally.
- **Do** send a pre-kickoff questionnaire to gather technical and business
  context before the first meeting.
- **Do** assign a single owner for each onboarding engagement — avoid diffusing
  responsibility across teams.
- **Do** track onboarding milestones in a shared system visible to both the
  customer and internal teams.
- **Don't** treat onboarding as a one-size-fits-all process. Segment by customer
  tier, complexity, and use case.
- **Don't** wait until the end of onboarding to check adoption metrics. Monitor
  weekly from day one.
- **Don't** skip the handoff meeting between onboarding and the ongoing CSM.
  Context loss causes customer frustration.
- **Don't** let onboarding drag beyond the agreed timeline without escalating.

---

## Common Pitfalls

1. **No defined "done" criteria.** Onboarding continues indefinitely because
   nobody defined completion milestones. Solution: agree on 3–5 measurable
   milestones at kickoff and track them in a shared checklist.
2. **Sales-to-CS handoff gap.** Sales closes the deal and disappears. The CSM
   starts from scratch. Solution: structured handoff document covering goals,
   stakeholders, technical requirements, and any promises made during the sales
   cycle.
3. **Training without context.** Generic training sessions that do not map to the
   customer's actual use case. Solution: customize training agendas based on the
   pre-kickoff questionnaire and the customer's stated goals.
4. **Champion leaves mid-onboarding.** The primary contact changes and momentum
   stalls. Solution: identify at least two stakeholders during kickoff. Document
   all decisions in a shared space, not in email threads.
5. **Ignoring low-engagement signals.** The customer stops logging in during week
   two but nobody notices. Solution: automated engagement alerts tied to login
   frequency and feature usage thresholds.

---

## Kickoff Agenda Template

```yaml
# Customer Onboarding Kickoff Agenda
meeting:
  duration: 45 minutes
  attendees:
    customer:
      - executive_sponsor
      - project_lead
      - technical_contact
    internal:
      - csm
      - onboarding_specialist
      - solutions_engineer  # if integration required

agenda:
  - topic: Introductions and Roles
    duration: 5 min
    notes: "Clarify who owns what on both sides"

  - topic: Goals and Success Criteria
    duration: 10 min
    notes: "Define what 'first value' means for this customer"

  - topic: Technical Requirements Review
    duration: 10 min
    notes: "SSO, integrations, data migration, environment setup"

  - topic: Onboarding Timeline and Milestones
    duration: 10 min
    notes: "Walk through the phase-based plan, agree on dates"

  - topic: Communication and Escalation
    duration: 5 min
    notes: "Preferred channels, meeting cadence, escalation path"

  - topic: Next Steps
    duration: 5 min
    notes: "Assign action items with owners and due dates"
```

---

## Onboarding Tracker Example

```yaml
# Customer Onboarding Tracker
customer:
  name: "Acme Corp"
  tier: enterprise
  csm: "Jane Smith"
  start_date: "2026-01-15"
  target_first_value: "2026-01-29"

milestones:
  - name: "Kickoff completed"
    target_date: "2026-01-17"
    actual_date: "2026-01-16"
    status: complete

  - name: "Accounts provisioned"
    target_date: "2026-01-20"
    actual_date: "2026-01-20"
    status: complete

  - name: "Integration configured"
    target_date: "2026-01-22"
    actual_date: null
    status: in_progress
    blockers:
      - "Waiting on customer SSO metadata"

  - name: "Training delivered"
    target_date: "2026-01-27"
    actual_date: null
    status: pending

  - name: "First value achieved"
    target_date: "2026-01-29"
    actual_date: null
    status: pending
    criteria: "Customer has created 3 automated workflows"

health:
  engagement: high      # login frequency, support tickets
  sentiment: positive   # from kickoff and check-in calls
  risk_level: low       # no blockers, on schedule
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| Fully automated (tech-touch) | High-volume, low-ACV products with simple setup |
| Hybrid onboarding | Mid-market accounts with moderate complexity |
| White-glove onboarding | Enterprise accounts with custom integrations |
| Partner-led onboarding | Channel sales model where partners own implementation |
| Self-service with checkpoints | Developer-focused products with strong documentation |

---

## Checklist

- [ ] Onboarding kickoff scheduled within 3 business days of contract close
- [ ] Pre-kickoff questionnaire sent and responses reviewed
- [ ] Success criteria and first-value definition agreed with customer
- [ ] Accounts provisioned and environment validated
- [ ] Role-based training sessions scheduled and delivered
- [ ] Adoption metrics tracked weekly from day one
- [ ] Engagement alerts configured for low-activity thresholds
- [ ] Handoff meeting completed between onboarding specialist and ongoing CSM
- [ ] Customer health record updated with onboarding outcomes
- [ ] Post-onboarding survey sent to capture experience feedback
