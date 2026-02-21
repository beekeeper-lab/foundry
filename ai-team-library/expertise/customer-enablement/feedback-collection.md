# Feedback Collection Frameworks

Systematic approaches to gathering, categorizing, and acting on customer feedback.
Feedback is signal — without a framework, it becomes noise that teams ignore or
misinterpret.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Collection method** | In-app surveys + support ticket tagging | Email surveys, interview programs |
| **Survey timing** | Event-triggered (post-action) | Time-based (monthly), milestone-based |
| **Categorization** | Product area + feedback type taxonomy | Free-text with AI classification |
| **Prioritization** | Impact × frequency matrix | Revenue-weighted, segment-weighted |
| **Feedback loop** | Quarterly product review | Monthly, continuous backlog integration |
| **Tooling** | Integrated feedback widget | Standalone survey platform |

---

## Feedback Types

### Feature Requests

Customers asking for capabilities that do not exist. Capture the underlying job
to be done, not just the requested solution. "We need a CSV export" might mean
"I need to share data with my finance team."

### Bug Reports

Something is broken or behaving unexpectedly. Capture reproduction steps,
expected behavior, actual behavior, and environment details. Route to engineering
triage, not the general feedback backlog.

### Usability Feedback

The feature exists but is confusing, slow, or hard to find. Often surfaces as
support tickets that begin with "How do I...?" Track alongside product analytics
to identify UX friction points.

### Praise / Positive Feedback

What is working well. Easy to dismiss but critical for understanding what to
protect during redesigns. Tag and surface during product planning.

### Churn Signals

Feedback that indicates dissatisfaction or intent to leave. Cancellation reasons,
negative survey responses, and declining engagement patterns. Route to customer
success for immediate intervention.

---

## Do / Don't

- **Do** ask for feedback at the moment of experience, not days later. Post-action
  surveys have 3–5x higher response rates than periodic email surveys.
- **Do** separate the collection channel from the analysis process. Collect
  broadly, analyze centrally.
- **Do** close the loop with customers who provide feedback. Even a brief
  acknowledgment increases future participation.
- **Do** combine quantitative scores (ratings, NPS) with qualitative context
  (open-text responses) for complete signal.
- **Do** tag feedback by customer segment, plan tier, and account health to
  enable weighted prioritization.
- **Don't** ask more than 3 questions in an in-app survey. Completion rates drop
  sharply after the third question.
- **Don't** treat all feedback equally. A feature request from a churning
  enterprise account carries different weight than one from a free trial user.
- **Don't** collect feedback without a process to review and act on it. Ignored
  feedback programs erode customer trust faster than having no program at all.
- **Don't** route all feedback to a single inbox. Categorize and route
  automatically to reduce response time.

---

## Common Pitfalls

1. **Collecting feedback but never acting on it.** The survey exists, responses
   accumulate, and nothing changes. Customers stop responding. Solution: tie
   feedback review to a recurring product planning ceremony with documented
   outcomes.
2. **Survivorship bias.** Only satisfied customers respond to surveys. Churned
   customers are never asked. Solution: include exit surveys in the cancellation
   flow and conduct win/loss interviews for sales outcomes.
3. **Anecdote-driven prioritization.** A single loud customer dictates the
   roadmap. Solution: use an impact × frequency matrix to prioritize
   systematically. Weight by segment and revenue.
4. **Survey fatigue.** Customers are surveyed after every interaction and stop
   responding entirely. Solution: throttle survey frequency per customer (no more
   than once per 30 days). Coordinate across teams to prevent overlap.
5. **Feedback silos.** Sales hears one thing, support hears another, product
   hears a third. Nobody sees the full picture. Solution: centralize all feedback
   in a single system with consistent tagging and cross-team visibility.

---

## In-App Feedback Widget Configuration

```yaml
# Feedback Widget Configuration
widget:
  trigger: event          # event | time | manual
  event_name: "task_completed"
  delay_seconds: 5        # wait before showing
  throttle:
    per_user: once_per_30_days
    per_session: once

  survey:
    - question: "How easy was it to complete this task?"
      type: rating
      scale: 1-5
      labels:
        1: "Very difficult"
        5: "Very easy"
      required: true

    - question: "What would you improve?"
      type: open_text
      max_length: 500
      required: false
      show_if: "rating <= 3"   # only ask for low scores

  routing:
    - condition: "rating <= 2"
      action: create_support_ticket
      priority: high
      tags: ["ux-friction", "auto-escalated"]

    - condition: "rating >= 4"
      action: log_to_feedback_db
      tags: ["positive-signal"]

  metadata:
    customer_id: "{{ user.account_id }}"
    plan_tier: "{{ user.plan }}"
    feature_area: "task-management"
```

---

## Feedback Prioritization Matrix

```yaml
# Impact x Frequency Prioritization
prioritization:
  method: impact_frequency_matrix
  review_cadence: monthly

  scoring:
    impact:
      high: 3     # blocks core workflow or causes churn risk
      medium: 2   # workaround exists but painful
      low: 1      # nice to have, minimal workflow disruption
    frequency:
      high: 3     # reported by 20%+ of active accounts
      medium: 2   # reported by 5-20% of active accounts
      low: 1      # reported by < 5% of active accounts

  weighting:
    enterprise: 2.0   # enterprise feedback weighted 2x
    mid_market: 1.5
    smb: 1.0
    free_trial: 0.5

  example_items:
    - id: FB-101
      summary: "CSV export for billing reports"
      impact: high
      frequency: high
      weighted_score: 18.0   # 3 * 3 * 2.0 (mostly enterprise requests)
      decision: build_next_quarter

    - id: FB-102
      summary: "Dark mode support"
      impact: low
      frequency: medium
      weighted_score: 3.0    # 1 * 2 * 1.5 (mid-market requests)
      decision: backlog

    - id: FB-103
      summary: "Login page loads slowly"
      impact: medium
      frequency: high
      weighted_score: 9.0    # 2 * 3 * 1.5
      decision: investigate_this_sprint
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| Customer advisory board | Strategic feedback from key accounts on roadmap direction |
| Beta program feedback | Validating new features before general availability |
| Community forums | High-volume products with engaged user communities |
| Social media monitoring | B2C products where customers discuss publicly |
| Sales call recording analysis | Capturing feedback from prospects during the sales cycle |

---

## Checklist

- [ ] Feedback collection channels defined (in-app, email, support, sales)
- [ ] Survey throttling configured to prevent fatigue (max once per 30 days)
- [ ] Feedback categorization taxonomy established (type, product area, segment)
- [ ] Routing rules configured to direct feedback to appropriate teams
- [ ] Prioritization framework documented (impact × frequency with weighting)
- [ ] Feedback review ceremony scheduled (monthly or quarterly)
- [ ] Closed-loop process defined (acknowledge, update, resolve, notify)
- [ ] Exit survey integrated into cancellation flow
- [ ] Cross-team visibility enabled (single system, consistent tagging)
- [ ] Feedback-to-roadmap traceability documented
