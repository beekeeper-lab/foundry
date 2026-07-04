---
id: product-strategy
category: Business Practices
entry: true
last-reviewed: 2026-07
---

# Product Strategy Conventions

## Category
Business Practices

Evidence-based practices for deciding what to build, aligning teams around
measurable goals, and taking products to market. These conventions replace
opinion-driven roadmaps with structured frameworks — prioritization scoring,
OKRs, story mapping, lifecycle management, GTM planning, and competitive
analysis — applied consistently across planning cycles.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Prioritization framework** | RICE scoring: `(Reach × Impact × Confidence) / Effort` | MoSCoW for fixed-scope releases; Weighted Scoring for multi-criteria decisions |
| **Goal-setting** | Quarterly OKRs, 3–5 objectives per team, 2–4 measurable KRs each | Annual OKRs for slow-moving orgs; 6-week cycles for fast iteration |
| **OKR scoring** | 0.0–1.0 scale, 0.7 = on target; 70% stretch / 30% committed | Binary pass/fail for compliance KRs |
| **Scope discovery** | User story mapping workshop (cross-functional, 2–4 hours) | PM-led draft with async review for distributed teams |
| **Release slicing** | Walking skeleton first (thinnest end-to-end path), then sophistication | Effort-based slicing for execution-focused teams |
| **Feature lifecycle** | Discovery → Definition → Delivery → Launch → Growth → Maturity → Sunset | Simplified 4-stage (Ideate → Build → Run → Retire) for small teams |
| **Sunset trigger** | <5% monthly active usage AND declining 2+ quarters | Cost-based trigger when maintenance exceeds value |
| **GTM motion** | Product-led growth (PLG) with self-serve onboarding | Sales-led for enterprise; community-led for developer tools |
| **Launch tiers** | 3-tier: T1 major (6–8 wk lead), T2 minor (2–4 wk), T3 ship-and-announce | 2-tier for small teams; 4-tier for platform orgs |
| **Competitive analysis** | Quarterly refresh; 3–5 direct competitors + 2–3 adjacent threats | Event-driven updates on competitor launches, pivots, funding |
| **Success metrics** | Outcomes (adoption, retention, revenue), never output counts | Revenue attribution for monetized features; NPS delta for experience features |

---

## 1. Prioritization

- Pick one primary framework and use it consistently across cycles. Default is
  RICE: Reach (users/quarter), Impact (3/2/1/0.5/0.25), Confidence
  (100/80/50%), Effort (person-months).
- Require engineering estimates before scoring effort — PMs consistently
  underestimate complexity.
- Collect scores independently before group calibration to avoid anchoring.
- Use MoSCoW for fixed-scope, deadline-driven releases: cap Must-haves at
  ≤60% of capacity, ~20% Should, ~20% Could, and always list "Won't have
  (this time)" explicitly.
- Score only the top 15–20 candidates; expire scores after 2 cycles.
- Frameworks provide signal, not answers — no HiPPO overrides without
  documented rationale.

Full detail: `prioritization.md`

---

## 2. OKRs

- Objectives are inspirational and qualitative; key results are measurable
  (number, percentage, or binary milestone). "Launch feature X" is a task,
  not a KR — KRs measure outcomes like "activation rate 30% → 45%".
- Cascade top-down objectives with bottom-up key results; every team objective
  traces to a company objective. Orphan OKRs signal misalignment.
- Set stretch targets: 60–70% achievement on stretch OKRs is success.
  Consistent 100% means sandbagging.
- Monthly check-ins with traffic-light status; formal 0.0–1.0 grading at
  end of quarter. Ungraded OKRs teach nothing.
- Keep OKRs separate from KPIs (steady-state health) and from performance
  reviews (punishing missed stretch goals kills ambition).

Full detail: `okrs.md`

---

## 3. User Story Mapping

- Build the backbone first: 5–7 user activities left-to-right in chronological
  order, then tasks vertically under each activity ranked by necessity.
- "Checkout" is an activity (a goal); "Enter shipping address" is a task.
  Map user tasks, never system features ("Admin panel" is not a user task).
- Slice releases with horizontal lines. Release 1 is the walking skeleton —
  the minimum set that lets the user complete their goal end-to-end. Every
  extra card in Release 1 delays learning.
- Map with the whole cross-functional team (PM, design, engineering, QA);
  timebox the workshop to 2–4 hours.
- The map is the primary planning artifact — post it, reference it in sprint
  planning, and update it as scope evolves.

Full detail: `user-story-mapping.md`

---

## 4. Feature Lifecycle

- Every feature moves through Discovery → Definition → Delivery → Launch →
  Growth → Maturity → Sunset, with exit criteria at each gate.
- Timebox discovery (2–4 weeks) with a go/no-go gate; define success metrics
  (baseline + target) before delivery begins.
- Feature-flag every new feature for gradual rollout (1% → 10% → 50% → 100%),
  with a flag expiration date set at creation; clean up flags within one
  sprint of 100% rollout.
- Review the feature health scorecard quarterly (MAU trend, 30-day retention,
  support volume, error rate, maintenance cost, revenue attribution). Features
  below threshold get a mandatory sunset-or-justify decision.
- Sunset with notice: 6 months for paid features, 3 months for free, with a
  documented migration path before any announcement. Remove dead code after.

Full detail: `feature-lifecycle.md`

---

## 5. Go-to-Market

- Tier every launch: T1 (new product/market, full cross-functional GTM),
  T2 (significant feature, product + marketing + sales), T3 (incremental,
  changelog + docs). Scale effort to impact — launch fatigue is real.
- Run the four phases: Strategy (segment, value prop, measurable launch goals,
  motion, pricing) → Preparation (enablement, assets, docs, training,
  tracking) → Launch (staggered channel sequence, real-time monitoring) →
  Post-Launch (measure against goals, 30-day retrospective).
- Define the target segment narrowly — "10–50 person SaaS companies that
  manage invoicing manually", not "small businesses".
- Set measurable launch goals *before* launch; research willingness to pay
  (Van Westendorp / Gabor-Granger) rather than anchoring price to cost.
- Stagger rollout: beta group → existing customers → public. Don't launch
  on a Friday.

Full detail: `go-to-market.md`

---

## 6. Competitive Analysis

- Maintain a quarterly-refreshed analysis of 3–5 direct competitors plus
  2–3 adjacent/emerging threats, owned by the PM with sales/marketing/CS input.
- Core artifacts: feature comparison matrix (buyer-relevant capabilities only,
  weighted by importance), SWOT per competitor, and a positioning map on the
  two dimensions target buyers care most about.
- Use win/loss interviews as a primary data source; verify competitor claims
  against public documentation, not marketing copy.
- Monitor ongoing signals: changelogs, hiring patterns, funding/M&A, review
  sentiment (G2, Capterra), messaging shifts.
- Size non-consumption (spreadsheets, manual processes) as a competitor —
  the real competition is often "do nothing".

Full detail: `competitive-analysis.md`

---

## Do / Don't

**Do:**
- Tie every key result and success metric to outcomes, not outputs.
- Require engineering input on effort before any prioritization score.
- Keep the walking skeleton ruthlessly thin — prove end-to-end first.
- Define success metrics and launch goals before building or shipping.
- Plan for sunset from day one; document the trigger for every feature.
- Publish the ranked backlog so stakeholders see why items rank where they do.
- Share competitive intelligence with sales and marketing.

**Don't:**
- Confuse KRs with tasks, or OKRs with steady-state KPIs.
- Let every stakeholder item become a MoSCoW "Must have" — enforce the 60% cap.
- Treat launch as the finish line; growth and maturity determine payoff.
- Keep zombie features alive because "someone might use it".
- Copy competitor features without understanding their strategy and context.
- Change OKRs mid-quarter unless business context has fundamentally shifted.
- Rank 50 backlog items — score the top 15–20 and let the rest wait.

---

## Common Pitfalls

1. **Precision theater.** Debating a RICE score of 2 vs 2.5 when the rank
   order is unchanged. Use coarse scales; focus on rank, not absolutes.
2. **Sandbagging OKRs.** Easy targets to guarantee 100%. Calibrate so 70% on
   stretch goals is success, and decouple from performance reviews.
3. **Release 1 bloat.** "Must-haves" pile in until the MVP isn't minimum.
   Apply the walking skeleton test: can the user complete their goal?
4. **Launch-and-forget.** Shipping and moving on without monitoring adoption.
   Block the next initiative until the 30-day post-launch review is done.
5. **Zombie features.** Negligible-usage features nobody dares remove.
   Quarterly scorecard review with mandatory sunset-or-justify.
6. **Build-it-and-they-will-come.** No launch plan, low adoption. Every
   feature above T3 gets a GTM plan.
7. **Reactive positioning.** Re-planning the roadmap every time a competitor
   ships. Maintain a strategic thesis; evaluate competitor moves against it.

---

## Checklist

- [ ] A primary prioritization framework is documented and applied every cycle
- [ ] Engineering provides effort estimates before scoring; scores collected independently
- [ ] Each team has 3–5 quarterly objectives with 2–4 measurable, outcome-based KRs
- [ ] OKRs cascade to company objectives; KPIs tracked separately
- [ ] Story map exists per major initiative with a validated walking skeleton
- [ ] Success metrics (baseline + target) defined before delivery begins
- [ ] Feature flags used for gradual rollout, with expiration dates
- [ ] Feature health scorecard reviewed quarterly; sunset triggers documented
- [ ] Every launch is tiered (T1/T2/T3) with measurable goals set pre-launch
- [ ] 30-day launch retrospective completed with learnings fed back to roadmap
- [ ] Competitive analysis refreshed quarterly and shared with sales/marketing
- [ ] Non-consumption sized as a competitive alternative
