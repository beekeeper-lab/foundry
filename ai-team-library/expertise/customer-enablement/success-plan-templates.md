# Success Plan Templates

Structured documents that align the vendor and customer on desired outcomes,
milestones, and accountability. A success plan turns a vague relationship into a
managed engagement with measurable progress. Without one, "success" means
whatever the last person in the room said.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Plan format** | Outcome-based (goals → milestones → actions) | Timeline-based, OKR-style |
| **Creation timing** | End of onboarding / start of steady-state | Pre-sale, at contract renewal |
| **Review cadence** | Quarterly business review (QBR) | Monthly, semi-annual |
| **Ownership** | CSM owns the document, customer co-owns the goals | Customer-led, joint ownership |
| **Plan scope** | 12-month rolling | 6-month, contract-term aligned |
| **Success metric** | Goal attainment rate | Value realization score, ROI |

---

## Success Plan Structure

### Section 1 — Customer Context

Who the customer is, what they bought, and why. Captures the business context
that anchors every goal. Includes company overview, key stakeholders, contract
details, and the original business case for purchasing.

### Section 2 — Desired Outcomes

The 3–5 business outcomes the customer expects to achieve. Outcomes are written
from the customer's perspective, not the vendor's. "Reduce support ticket volume
by 30%" not "Customer adopts self-service portal."

### Section 3 — Milestones and Actions

Each outcome breaks down into measurable milestones with specific actions, owners,
and target dates. Milestones are the checkpoints; actions are the work that gets
you there.

### Section 4 — Risk and Mitigation

Known risks to achieving the outcomes and the planned mitigations. Updated at
every review. Risks include technical blockers, stakeholder changes, competing
priorities, and adoption challenges.

### Section 5 — Review History

Log of every success plan review meeting, decisions made, and plan adjustments.
Provides continuity when stakeholders change on either side.

---

## Do / Don't

- **Do** co-create the success plan with the customer. A plan written
  unilaterally by the vendor is a sales document, not a partnership tool.
- **Do** tie every outcome to a measurable metric. "Improve efficiency" is not
  an outcome. "Reduce report generation time from 4 hours to 30 minutes" is.
- **Do** review and update the plan at every QBR. A plan that is not reviewed
  becomes a forgotten artifact.
- **Do** connect success plan outcomes to the customer's renewal and expansion
  decisions. If the customer achieves their goals, renewal is the natural next
  step.
- **Do** document stakeholder changes immediately. A new VP may have different
  priorities than the one who signed the contract.
- **Don't** list product features as outcomes. Features are means, not ends.
  The customer does not care about feature adoption — they care about the
  business result it produces.
- **Don't** create a success plan and never share it with the customer. It must
  be a living, jointly owned document.
- **Don't** set goals the customer cannot influence. If a goal depends entirely
  on your engineering team shipping a feature, it is your commitment, not the
  customer's success criterion.
- **Don't** overload the plan with 15 goals. Three to five focused outcomes
  drive more progress than a comprehensive wishlist.
- **Don't** skip the risk section. Every plan has risks. Acknowledging them
  builds trust and enables proactive mitigation.

---

## Common Pitfalls

1. **Success plan as a checkbox exercise.** The CSM creates the plan because
   the process requires it, but neither side references it again. Solution: tie
   QBR agendas directly to the success plan. Every review starts with plan
   progress.
2. **Goals set without baselines.** "Improve NPS" with no starting measurement.
   There is no way to evaluate progress. Solution: establish baseline
   measurements for every metric before setting targets. If no baseline exists,
   the first milestone is to measure it.
3. **Vendor-centric outcomes.** The plan lists "Achieve 80% feature adoption"
   instead of what that adoption enables for the customer. Solution: rewrite
   every outcome to answer "So that the customer can..."
4. **Single-threaded stakeholder.** The success plan depends on one champion. If
   they leave, the plan dies. Solution: involve at least two customer
   stakeholders. Document the executive sponsor's priorities separately from the
   day-to-day contact's.
5. **No connection to renewal.** The success plan and the commercial relationship
   are managed as separate tracks. Solution: explicitly map success plan
   outcomes to the renewal conversation. "We agreed you wanted X. Here is the
   evidence of X achieved."

---

## Success Plan Template

```yaml
# Customer Success Plan
plan:
  version: "1.0"
  created: "2026-02-01"
  last_reviewed: "2026-02-01"
  next_review: "2026-05-01"
  status: active              # active | completed | at_risk | archived

customer:
  company: "Acme Corp"
  industry: "Financial Services"
  segment: enterprise
  contract:
    start_date: "2025-08-01"
    renewal_date: "2026-08-01"
    arr: "$150,000"
    plan_tier: "Enterprise"

stakeholders:
  customer:
    - name: "Sarah Chen"
      role: "VP Operations"
      type: executive_sponsor
      engagement: active
    - name: "Mike Torres"
      role: "Operations Manager"
      type: day_to_day_contact
      engagement: active
    - name: "Lisa Park"
      role: "IT Director"
      type: technical_contact
      engagement: moderate
  vendor:
    - name: "Jane Smith"
      role: "Customer Success Manager"
      type: primary_owner
    - name: "Tom Brown"
      role: "Solutions Engineer"
      type: technical_resource

outcomes:
  - id: O1
    description: >
      Reduce monthly report generation time from 4 hours to 30 minutes
      by automating the three core operational reports.
    business_value: "Frees 42 hours/year of analyst time ($5,000+/year)"
    baseline:
      metric: "Report generation time"
      current: "4 hours per report"
      measured_on: "2025-08-15"
    target:
      metric: "Report generation time"
      goal: "30 minutes per report"
      target_date: "2026-04-01"
    status: in_progress
    milestones:
      - name: "Report templates configured"
        target_date: "2025-10-01"
        actual_date: "2025-10-05"
        status: complete
        owner: "Mike Torres"
      - name: "Data sources connected"
        target_date: "2025-11-15"
        actual_date: "2025-11-12"
        status: complete
        owner: "Lisa Park"
      - name: "Automated scheduling enabled"
        target_date: "2026-01-15"
        actual_date: null
        status: in_progress
        owner: "Mike Torres"
        blockers:
          - "Requires API access approval from IT security"
      - name: "Target achieved and validated"
        target_date: "2026-04-01"
        actual_date: null
        status: pending
        owner: "Jane Smith"

  - id: O2
    description: >
      Achieve 80% team adoption across the 25-person operations team
      within 6 months of launch.
    business_value: "Consistent processes, reduced training overhead"
    baseline:
      metric: "Monthly active users"
      current: "8 of 25 (32%)"
      measured_on: "2025-10-01"
    target:
      metric: "Monthly active users"
      goal: "20 of 25 (80%)"
      target_date: "2026-04-01"
    status: in_progress
    milestones:
      - name: "Training program delivered"
        target_date: "2025-11-01"
        actual_date: "2025-11-03"
        status: complete
        owner: "Jane Smith"
      - name: "50% adoption reached"
        target_date: "2026-01-01"
        actual_date: "2025-12-18"
        status: complete
        owner: "Mike Torres"
      - name: "80% adoption reached"
        target_date: "2026-04-01"
        actual_date: null
        status: in_progress
        owner: "Mike Torres"

risks:
  - id: R1
    description: "IT security approval for API access may delay automation milestone"
    impact: high
    likelihood: medium
    mitigation: "CSM to schedule call with IT Director and security team by Feb 15"
    status: open
    owner: "Jane Smith"

  - id: R2
    description: "Two team members resistant to adopting new tool"
    impact: medium
    likelihood: high
    mitigation: "Schedule 1:1 training sessions focused on their specific workflows"
    status: mitigated
    owner: "Mike Torres"

review_history:
  - date: "2025-11-01"
    attendees: ["Sarah Chen", "Mike Torres", "Jane Smith"]
    summary: >
      Q1 review. Report templates complete, data sources on track.
      Adoption at 40% — ahead of schedule. No new risks identified.
    decisions:
      - "Accelerate training for remaining team members"
    plan_changes: none

  - date: "2026-02-01"
    attendees: ["Sarah Chen", "Mike Torres", "Lisa Park", "Jane Smith"]
    summary: >
      Q2 review. Adoption at 64%, on track for 80% target. API access
      blocker identified — added as R1. Report automation delayed.
    decisions:
      - "CSM to facilitate meeting between vendor engineering and Acme IT security"
      - "Extend automation milestone to April 1"
    plan_changes:
      - "O1 milestone 3 target date moved from Jan 15 to Mar 1"
```

---

## QBR Agenda Template

```yaml
# Quarterly Business Review Agenda
qbr:
  duration: 60 minutes
  attendees:
    customer: [executive_sponsor, day_to_day_contact]
    vendor: [csm, account_executive]

  agenda:
    - topic: "Success Plan Progress Review"
      duration: 20 min
      content:
        - "Review each outcome: status, milestones completed, blockers"
        - "Update baseline metrics with current measurements"
        - "Discuss any goal adjustments needed"

    - topic: "Health and Engagement Summary"
      duration: 10 min
      content:
        - "Product usage trends"
        - "Support experience summary"
        - "Team adoption metrics"

    - topic: "Risk Review and Mitigation"
      duration: 10 min
      content:
        - "Review open risks and mitigation progress"
        - "Identify new risks"
        - "Assign mitigation owners"

    - topic: "Product Roadmap and Opportunities"
      duration: 10 min
      content:
        - "Relevant upcoming product capabilities"
        - "Expansion opportunities aligned to customer goals"
        - "Beta program invitations"

    - topic: "Action Items and Next Steps"
      duration: 10 min
      content:
        - "Summarize decisions made"
        - "Assign action items with owners and dates"
        - "Confirm next review date"
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| OKR-style success plans | Companies already using OKR frameworks internally |
| Joint accountability plan | High-touch strategic accounts with shared commitments |
| Value realization tracker | ROI-focused customers who need quantified business impact |
| Mutual action plan (pre-sale) | Complex sales cycles requiring joint implementation planning |
| Lightweight goal card | SMB accounts where a full success plan is disproportionate |

---

## Checklist

- [ ] Success plan co-created with customer (not vendor-only)
- [ ] 3–5 measurable business outcomes defined with baselines and targets
- [ ] Each outcome has milestones with owners and target dates
- [ ] Stakeholders documented (at least two customer contacts)
- [ ] Executive sponsor identified and engaged
- [ ] Risk register populated with mitigations and owners
- [ ] QBR cadence established and first review scheduled
- [ ] Success plan linked to renewal timeline and commercial strategy
- [ ] Review history maintained with decisions and plan changes logged
- [ ] Plan shared in a format accessible to both customer and vendor teams
