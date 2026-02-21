# Customer Health Scoring

A composite metric that predicts customer retention, expansion, and churn risk
by combining product usage, engagement, support, and financial signals. Health
scores replace gut feel with a consistent, data-driven view of account status.

---

## Defaults

| Setting | Default | Alternatives |
|---------|---------|--------------|
| **Score range** | 0–100 | Letter grades (A–F), traffic light (R/Y/G) |
| **Update frequency** | Weekly automated refresh | Daily, monthly, event-triggered |
| **Scoring model** | Weighted average of signal categories | ML-based predictive model |
| **Threshold: healthy** | 75–100 | Adjust per segment after baseline period |
| **Threshold: at-risk** | 40–74 | Adjust per segment after baseline period |
| **Threshold: critical** | 0–39 | Adjust per segment after baseline period |
| **Review cadence** | Weekly for at-risk, monthly for healthy | Daily for critical |

---

## Health Signal Categories

### Product Usage (Weight: 35%)

Measures how deeply and frequently the customer uses the product. Tracks login
frequency, feature adoption breadth, core workflow completion, and usage trends
(growing, stable, declining). Declining usage is the strongest leading indicator
of churn.

### Engagement (Weight: 25%)

Measures the customer's relationship engagement beyond product usage. Tracks
meeting attendance, email responsiveness, executive sponsor accessibility,
training participation, and community involvement. Disengaged customers churn
silently.

### Support Experience (Weight: 20%)

Measures the quality of the support relationship. Tracks ticket volume trends,
resolution satisfaction (CSAT), escalation frequency, and open issue age. A spike
in tickets or a pattern of escalations signals trouble.

### Financial Health (Weight: 20%)

Measures the commercial relationship. Tracks payment timeliness, contract
renewal proximity, expansion/contraction signals, and discount dependency.
Late payments and renewal hesitation are direct churn precursors.

---

## Do / Don't

- **Do** calibrate score weights using historical churn data. Validate that your
  scoring model actually predicts outcomes before trusting it.
- **Do** make health scores visible to the entire customer-facing organization
  (CS, sales, support, product). Shared visibility drives coordinated action.
- **Do** pair the numeric score with a human-readable summary that explains why
  the score is what it is. A number without context does not drive action.
- **Do** review and adjust thresholds quarterly. As the customer base evolves,
  the definition of "healthy" changes.
- **Do** define specific playbooks for each health zone (healthy, at-risk,
  critical) so CSMs know exactly what actions to take.
- **Don't** treat the health score as a single source of truth. It is a signal
  aggregator, not a replacement for customer conversations.
- **Don't** let scores go stale. A weekly refresh is the minimum. Outdated
  scores are worse than no scores.
- **Don't** use a single metric as a health score proxy (e.g., just NPS or just
  login frequency). Single metrics miss too much context.
- **Don't** penalize new customers for low usage during onboarding. Adjust
  scoring expectations for account tenure.
- **Don't** hide declining scores from leadership. Transparency enables early
  intervention.

---

## Common Pitfalls

1. **Scoring without action playbooks.** The dashboard shows a score of 32 but
   nobody knows what to do about it. Solution: define specific intervention
   playbooks for each health zone with clear owners, timelines, and success
   criteria.
2. **Over-indexing on usage data.** A customer logs in daily but is deeply
   frustrated with the product. Usage alone misses sentiment. Solution: include
   engagement and support signals alongside usage. Always combine quantitative
   data with qualitative input.
3. **One-size-fits-all scoring.** Enterprise and SMB customers are scored
   identically despite different usage patterns and engagement expectations.
   Solution: build segment-specific scoring models or adjust weight distributions
   by segment.
4. **Score manipulation by CSMs.** CSMs schedule unnecessary check-ins to boost
   engagement scores. Solution: weight objective signals (product telemetry,
   support data, payment history) more heavily than subjective ones (meeting
   notes, relationship rating).
5. **No baseline period.** New customers immediately receive low health scores
   because they have not had time to adopt. Solution: exclude accounts in their
   first 30–60 days from health scoring or use an onboarding-specific scoring
   model.

---

## Health Score Calculation

```yaml
# Customer Health Score Configuration
health_score:
  range: 0-100
  update_frequency: weekly

  categories:
    - name: product_usage
      weight: 0.35
      signals:
        - metric: login_frequency
          weight: 0.25
          scoring:
            daily: 100
            weekly: 75
            biweekly: 50
            monthly: 25
            inactive_30d: 0

        - metric: feature_adoption
          weight: 0.30
          scoring:
            method: percentage_of_core_features_used
            # core features defined per product/plan tier

        - metric: usage_trend
          weight: 0.25
          scoring:
            growing: 100       # 10%+ increase MoM
            stable: 75         # within +/- 10%
            declining: 30      # 10%+ decrease MoM
            sharply_declining: 0  # 25%+ decrease MoM

        - metric: depth_of_use
          weight: 0.20
          scoring:
            method: actions_per_session_vs_benchmark

    - name: engagement
      weight: 0.25
      signals:
        - metric: meeting_attendance
          weight: 0.30
          scoring:
            attends_all: 100
            attends_most: 75
            misses_frequently: 40
            no_meetings_scheduled: 20

        - metric: email_responsiveness
          weight: 0.25
          scoring:
            responds_within_24h: 100
            responds_within_72h: 70
            responds_within_week: 40
            unresponsive: 10

        - metric: executive_sponsor_access
          weight: 0.25
          scoring:
            active_sponsor: 100
            sponsor_identified: 60
            no_sponsor: 20

        - metric: training_participation
          weight: 0.20
          scoring:
            completed_all: 100
            completed_some: 60
            none_completed: 20

    - name: support_experience
      weight: 0.20
      signals:
        - metric: ticket_volume_trend
          weight: 0.30
          scoring:
            decreasing: 100
            stable_low: 80
            stable_high: 40
            increasing: 10

        - metric: csat_average
          weight: 0.30
          scoring:
            method: linear_scale
            min: 1              # maps to 0
            max: 5              # maps to 100

        - metric: escalation_frequency
          weight: 0.20
          scoring:
            none_90d: 100
            one_90d: 60
            multiple_90d: 20

        - metric: open_issue_age
          weight: 0.20
          scoring:
            none_open: 100
            all_under_7d: 80
            some_over_14d: 40
            any_over_30d: 10

    - name: financial_health
      weight: 0.20
      signals:
        - metric: payment_timeliness
          weight: 0.30
          scoring:
            on_time: 100
            late_1_14d: 60
            late_15_30d: 30
            late_30d_plus: 0

        - metric: renewal_proximity
          weight: 0.25
          scoring:
            renewed: 100
            renewal_confirmed: 90
            renewal_6mo_plus: 80
            renewal_3_6mo: 60
            renewal_under_3mo_no_signal: 30

        - metric: expansion_signals
          weight: 0.25
          scoring:
            actively_expanding: 100
            exploring_expansion: 70
            stable: 50
            contracting: 10

        - metric: discount_dependency
          weight: 0.20
          scoring:
            no_discount: 100
            standard_discount: 70
            heavy_discount: 40
            unsustainable_discount: 10
```

---

## Health Zone Playbooks

```yaml
# Action Playbooks by Health Zone
playbooks:
  healthy:               # score 75-100
    cadence: monthly_check_in
    actions:
      - "Identify expansion opportunities"
      - "Request referrals and case studies"
      - "Invite to beta programs and advisory board"
      - "Share product roadmap updates"
    owner: csm
    review: monthly

  at_risk:               # score 40-74
    cadence: biweekly_check_in
    actions:
      - "Schedule executive business review"
      - "Identify top 3 pain points and create resolution plan"
      - "Increase product training and enablement"
      - "Review open support tickets and accelerate resolution"
      - "Engage executive sponsor"
    owner: csm
    review: weekly
    escalate_to: cs_manager

  critical:              # score 0-39
    cadence: weekly_check_in
    actions:
      - "Immediate executive-to-executive outreach"
      - "Create 30-day recovery plan with measurable milestones"
      - "Assign dedicated support engineer"
      - "Review contract terms and identify retention options"
      - "Daily internal stand-up until score improves"
    owner: cs_manager
    review: daily
    escalate_to: vp_customer_success
```

---

## Alternatives

| Approach | When to consider |
|----------|-----------------|
| ML-based churn prediction | Large customer base with sufficient historical churn data |
| Traffic light (R/Y/G) | Simpler organizations that need a less granular view |
| Product-qualified accounts | Product-led growth models where usage is the primary signal |
| Composite scoring with NPS | When NPS data is reliable and collected consistently |
| Account-level sentiment analysis | When support and communication data is rich enough for NLP |

---

## Checklist

- [ ] Health signal categories defined with weights validated against churn data
- [ ] Scoring model configured with segment-specific adjustments
- [ ] Automated weekly refresh pipeline operational
- [ ] Health dashboard accessible to all customer-facing teams
- [ ] Thresholds calibrated (healthy, at-risk, critical) with quarterly review
- [ ] Action playbooks defined for each health zone
- [ ] New-customer exclusion period configured (first 30–60 days)
- [ ] Health score alerts configured for rapid declines (drop of 15+ points)
- [ ] CSM review cadence aligned with health zones
- [ ] Quarterly model validation against actual churn and expansion outcomes
