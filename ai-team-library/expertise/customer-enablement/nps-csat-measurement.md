# NPS / CSAT Measurement

Standardized frameworks for measuring customer satisfaction (CSAT) and loyalty
(NPS). These metrics quantify the customer experience, establish baselines, and
signal when intervention is needed — but only when measured consistently and
acted upon.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **NPS cadence** | Quarterly relational survey | Semi-annual, continuous (transactional) |
| **CSAT trigger** | Post-interaction (support, onboarding) | Post-feature-use, periodic |
| **NPS scale** | 0–10 (standard) | — (do not modify the standard scale) |
| **CSAT scale** | 1–5 stars | 1–7 Likert, thumbs up/down, emoji |
| **Response rate target** | 25%+ for NPS, 40%+ for CSAT | Adjust by segment and channel |
| **Follow-up** | Open text for all, call for detractors | Text only, no follow-up |

---

## NPS Framework

### How NPS Works

Net Promoter Score asks: "How likely are you to recommend [product] to a
colleague?" on a 0–10 scale. Responses are grouped:

- **Promoters (9–10):** Loyal, will recommend and expand.
- **Passives (7–8):** Satisfied but not enthusiastic. Vulnerable to competitors.
- **Detractors (0–6):** Unhappy. Risk of churn and negative word-of-mouth.

**NPS = % Promoters − % Detractors** (range: −100 to +100).

### Relational vs. Transactional NPS

Relational NPS measures overall loyalty. Send quarterly to a representative
sample. Transactional NPS measures satisfaction with a specific interaction
(onboarding, support resolution). Send immediately after the event.

Use both: relational NPS for trend tracking, transactional NPS for operational
improvement.

---

## CSAT Framework

### How CSAT Works

Customer Satisfaction Score asks: "How satisfied were you with [specific
experience]?" Measured on a 1–5 scale immediately after the interaction.

**CSAT = (Satisfied responses ÷ Total responses) × 100**

Where "satisfied" = ratings of 4 or 5 on a 5-point scale.

### When to Use CSAT vs. NPS

CSAT measures satisfaction with a specific moment. NPS measures overall
relationship health. A customer can rate a support interaction 5/5 (high CSAT)
while giving an NPS of 3 (detractor) because the product has unresolved issues.
Both metrics are needed.

---

## Do / Don't

- **Do** include an open-text follow-up question ("What is the primary reason for
  your score?"). The score tells you what, the text tells you why.
- **Do** segment results by customer tier, tenure, product usage, and geography.
  Aggregate NPS hides actionable patterns.
- **Do** track trends over time, not individual snapshots. A single quarter's NPS
  is noisy. Three-quarter trends are signal.
- **Do** contact every detractor within 48 hours. Detractor follow-up is the
  highest-ROI activity in any NPS program.
- **Do** share results transparently with product, engineering, and leadership.
  Metrics that stay in the CS team do not drive change.
- **Don't** game the score by surveying only happy customers or timing surveys
  after positive interactions.
- **Don't** use NPS as a performance metric for individual CSMs. It incentivizes
  score manipulation, not customer outcomes.
- **Don't** compare your NPS to other companies' published scores. Benchmarks
  vary wildly by industry, segment, and methodology.
- **Don't** survey the same customer more than once per quarter for NPS. Survey
  fatigue suppresses response rates and skews results.
- **Don't** ignore passives. They are the largest conversion opportunity — a
  small improvement can shift them to promoters.

---

## Common Pitfalls

1. **Measuring without acting.** NPS becomes a vanity metric reported in
   quarterly reviews but never tied to specific actions. Solution: every NPS
   cycle must produce a prioritized list of improvement actions with owners and
   deadlines.
2. **Low response rates skew results.** Only 8% of customers respond, and they
   are disproportionately very happy or very unhappy. Solution: optimize survey
   delivery (in-app > email), keep it short (2 questions max), and A/B test
   timing and messaging.
3. **No detractor follow-up process.** Detractors submit their score and hear
   nothing back. Solution: trigger a CSM outreach workflow for every detractor
   response within 48 hours. Log the outcome.
4. **Aggregating across segments.** Enterprise NPS is 60, SMB NPS is 10, and the
   blended score of 35 looks "okay." Solution: always report NPS by segment.
   Investigate segment-level trends independently.
5. **Confusing CSAT and NPS.** Teams use CSAT and NPS interchangeably, surveying
   randomly. Solution: use CSAT for transactional touchpoints, NPS for
   relational health. Define which metric applies to each customer touchpoint.

---

## NPS Survey Configuration

```yaml
# NPS Survey Configuration
nps:
  type: relational
  cadence: quarterly
  channel: in_app         # in_app | email | both
  sample:
    method: stratified    # stratified by segment to ensure representation
    segments:
      - enterprise
      - mid_market
      - smb
    min_per_segment: 50

  questions:
    - id: nps_score
      text: "How likely are you to recommend {{ product_name }} to a colleague?"
      type: scale
      min: 0
      max: 10
      labels:
        0: "Not at all likely"
        10: "Extremely likely"

    - id: nps_reason
      text: "What is the primary reason for your score?"
      type: open_text
      max_length: 1000
      required: false

  follow_up:
    detractor:              # score 0-6
      action: create_task
      owner: assigned_csm
      sla: 48_hours
      template: "detractor-outreach"
    passive:                # score 7-8
      action: log_for_review
      review_cadence: monthly
    promoter:               # score 9-10
      action: request_referral
      delay_days: 7
```

---

## CSAT Survey Configuration

```yaml
# CSAT Survey Configuration
csat:
  type: transactional
  triggers:
    - event: support_ticket_resolved
      delay_minutes: 30
    - event: onboarding_completed
      delay_hours: 24
    - event: training_session_completed
      delay_hours: 2

  throttle:
    per_customer: once_per_14_days
    across_triggers: true     # don't stack surveys from multiple triggers

  questions:
    - id: csat_score
      text: "How satisfied were you with your {{ interaction_type }} experience?"
      type: rating
      scale: 1-5
      labels:
        1: "Very dissatisfied"
        2: "Dissatisfied"
        3: "Neutral"
        4: "Satisfied"
        5: "Very satisfied"

    - id: csat_comment
      text: "Any additional feedback?"
      type: open_text
      max_length: 500
      required: false
      show_if: "csat_score <= 3"

  scoring:
    satisfied_threshold: 4    # scores >= 4 count as "satisfied"
    target_csat: 85           # percentage
```

---

## Reporting Dashboard Metrics

```yaml
# NPS/CSAT Reporting Structure
reporting:
  nps:
    metrics:
      - name: overall_nps
        calculation: "promoter_pct - detractor_pct"
        display: score_with_trend
      - name: nps_by_segment
        breakdown: [enterprise, mid_market, smb]
      - name: response_rate
        target: 0.25
      - name: detractor_followup_rate
        target: 1.0          # 100% of detractors contacted
      - name: detractor_recovery_rate
        description: "Detractors who become passive/promoter next cycle"

  csat:
    metrics:
      - name: overall_csat
        calculation: "satisfied_count / total_responses * 100"
        display: percentage_with_trend
      - name: csat_by_touchpoint
        breakdown: [support, onboarding, training]
      - name: response_rate
        target: 0.40
      - name: low_score_followup_rate
        target: 1.0

  cadence:
    nps_report: quarterly
    csat_report: monthly
    executive_summary: quarterly
```

---

## Alternatives

| Metric | When to consider |
|--------|-----------------|
| Customer Effort Score (CES) | Measuring ease of completing specific tasks (support, setup) |
| Product-Market Fit score | Early-stage products validating core value proposition |
| Customer Health Score | Composite metric combining usage, sentiment, and engagement |
| Churn prediction model | When NPS alone is insufficient to predict retention |
| Qualitative interviews | When scores need deeper context than open-text provides |

---

## Checklist

- [ ] NPS survey configured with standard 0–10 scale and open-text follow-up
- [ ] CSAT surveys configured for key transactional touchpoints
- [ ] Survey throttling in place (NPS: quarterly max, CSAT: once per 14 days)
- [ ] Detractor follow-up workflow defined with 48-hour SLA
- [ ] Results segmented by customer tier, tenure, and product usage
- [ ] Response rate targets set and monitored (NPS: 25%+, CSAT: 40%+)
- [ ] Trend reporting configured (3+ quarters for NPS, monthly for CSAT)
- [ ] Results shared cross-functionally (product, engineering, leadership)
- [ ] Improvement actions documented and tracked after each NPS cycle
- [ ] Passive-to-promoter conversion strategy defined
