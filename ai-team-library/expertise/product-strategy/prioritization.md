# Prioritization Frameworks

Structured methods for deciding what to build next. Prioritization replaces
opinion-driven roadmaps with evidence-based ranking. Every framework trades off
precision against effort — pick the lightest one that gives your team enough
signal to act with confidence.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Primary framework** | RICE scoring | MoSCoW for fixed-scope releases; Weighted Scoring for complex multi-criteria decisions |
| **Scoring frequency** | Every planning cycle (quarterly or per-sprint) | Continuous re-scoring for fast-moving backlogs |
| **Who scores** | Product manager with input from engineering and design | Cross-functional scoring committee for high-stakes decisions |
| **Tie-breaking** | Strategic alignment with current OKRs | Customer urgency; revenue impact; technical risk reduction |
| **Backlog grooming** | Monthly review of bottom-quartile items | Quarterly purge of items untouched for 2+ cycles |
| **Confidence calibration** | Three-point scale (low/medium/high) | Percentage-based confidence for data-rich teams |
| **Stakeholder input** | Async scoring with sync calibration meeting | Fully async for distributed teams; live workshop for alignment-critical decisions |

---

## RICE Framework

RICE scores each initiative on four factors to produce a single comparable number.

| Factor | Definition | Scale |
|--------|-----------|-------|
| **R**each | How many users/customers will this affect per quarter? | Absolute number (e.g., 5,000 users) |
| **I**mpact | How much will this move the target metric per user? | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| **C**onfidence | How sure are we about reach, impact, and effort estimates? | 100% = high, 80% = medium, 50% = low |
| **E**ffort | How many person-months will this take? | Person-months (e.g., 2) |

**Formula:** `RICE Score = (Reach × Impact × Confidence) / Effort`

### RICE Example

| Initiative | Reach | Impact | Confidence | Effort | RICE Score |
|------------|-------|--------|------------|--------|------------|
| Onboarding redesign | 8,000 | 2 | 80% | 3 | 4,267 |
| Bulk CSV import | 1,200 | 3 | 90% | 1 | 3,240 |
| Dashboard dark mode | 15,000 | 0.5 | 100% | 2 | 3,750 |
| API rate limit upgrade | 500 | 2 | 50% | 0.5 | 1,000 |

**Decision:** Onboarding redesign ranks highest. Dashboard dark mode is close but
lower impact per user. Bulk CSV import wins on effort efficiency.

---

## MoSCoW Framework

MoSCoW categorizes features into four buckets for a given release or timebox.
It does not rank within buckets — items in the same bucket have equal priority.

| Category | Meaning | Rule of Thumb |
|----------|---------|---------------|
| **Must have** | Non-negotiable for this release. Without these, the release has no value or violates a constraint. | ≤60% of available capacity |
| **Should have** | Important but the release is viable without them. Deliver if capacity allows. | ~20% of capacity |
| **Could have** | Desirable. Nice-to-have features that improve polish or UX. First to be cut. | ~20% of capacity |
| **Won't have (this time)** | Explicitly out of scope for this release. Acknowledged, not forgotten. Revisited next cycle. | Unlimited — clarity over false hope |

### MoSCoW Example (Q2 Release)

| Feature | Category | Rationale |
|---------|----------|-----------|
| Payment processing | Must | Core revenue path — release is unusable without it |
| Email notifications | Should | Important for engagement but manual workaround exists |
| Custom themes | Could | User-requested but not blocking adoption |
| Mobile app | Won't | Deferred to Q3 — needs dedicated team capacity |

---

## Weighted Scoring

For decisions with multiple evaluation criteria that vary in importance. Each
criterion gets a weight; each option gets a score per criterion.

**Steps:**
1. Define criteria (e.g., revenue impact, strategic alignment, user demand, effort)
2. Assign weights (must sum to 100%)
3. Score each option per criterion (1–5 or 1–10)
4. Multiply scores by weights and sum for a total

### Weighted Scoring Example

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Revenue impact | 35% | 4 (1.40) | 5 (1.75) | 2 (0.70) |
| Strategic alignment | 25% | 5 (1.25) | 3 (0.75) | 4 (1.00) |
| User demand | 25% | 3 (0.75) | 4 (1.00) | 5 (1.25) |
| Implementation effort (inverse) | 15% | 4 (0.60) | 2 (0.30) | 3 (0.45) |
| **Total** | **100%** | **4.00** | **3.80** | **3.40** |

---

## Opportunity Scoring (Outcome-Driven Innovation)

Ranks features by the gap between importance and satisfaction for a given user job.

**Formula:** `Opportunity Score = Importance + max(Importance - Satisfaction, 0)`

| User Job | Importance (1–10) | Satisfaction (1–10) | Opportunity Score |
|----------|-------------------|---------------------|-------------------|
| Find relevant reports quickly | 9 | 4 | 14 |
| Share dashboards with clients | 7 | 6 | 8 |
| Export data to CSV | 8 | 8 | 8 |
| Customize notification settings | 5 | 3 | 7 |

**Decision:** "Find relevant reports quickly" has the highest unmet need (high
importance, low satisfaction). Prioritize features that close this gap.

---

## Do / Don't

- **Do** pick one primary framework and use it consistently. Switching frameworks
  every sprint undermines comparability.
- **Do** recalibrate scores when new data arrives (user research, analytics, market
  shifts). Stale scores produce stale roadmaps.
- **Do** make the scoring visible. Publish the ranked backlog so stakeholders can
  see *why* their request ranks where it does.
- **Do** account for dependencies. A high-RICE feature blocked by a low-RICE
  prerequisite means both need to be prioritized together.
- **Do** use MoSCoW for fixed-scope, deadline-driven releases where the question
  is "what fits?" not "what ranks highest?"
- **Do** timebox scoring sessions. Spending 2 hours debating a 0.5-point difference
  defeats the purpose.
- **Don't** treat scores as absolute truth. Frameworks provide signal, not answers.
  Product judgment still matters.
- **Don't** let the HiPPO (Highest Paid Person's Opinion) override the framework
  without documented rationale.
- **Don't** score effort without engineering input. Product managers consistently
  underestimate complexity.
- **Don't** skip the "Won't have" bucket in MoSCoW. Explicit exclusion prevents
  scope creep and manages stakeholder expectations.
- **Don't** rank 50 items with RICE. Prioritize the top 15–20 candidates;
  everything else stays in the unscored backlog until it rises.

---

## Common Pitfalls

1. **Precision theater.** Debating whether a RICE Impact score should be 2 or 2.5
   when both produce the same relative ranking. Solution: use coarse scales and
   focus on rank order, not absolute scores.
2. **Effort amnesia.** Scoring reach and impact enthusiastically but hand-waving
   effort as "medium." Solution: require engineering estimates before scoring.
3. **Anchoring bias.** The first scorer's number anchors everyone else. Solution:
   collect scores independently before the calibration discussion.
4. **MoSCoW inflation.** Every feature is a "Must have" because stakeholders fear
   their items will be cut. Solution: enforce the 60% capacity cap on Must-haves.
   If everything is Must, nothing fits.
5. **Ignoring opportunity cost.** Scoring a feature highly without asking "what
   can't we build if we build this?" Solution: always present the top N items as
   a package that fits within capacity, not as an infinite ranked list.
6. **Stale backlog.** Items scored 6 months ago still sitting in the ranked list
   with outdated assumptions. Solution: expire scores after 2 cycles. Re-score
   or archive.

---

## Checklist

- [ ] A primary prioritization framework is selected and documented
- [ ] Scoring criteria and scales are defined and shared with the team
- [ ] Engineering provides effort estimates before scoring
- [ ] Scores are collected independently before group calibration
- [ ] The ranked backlog is visible to all stakeholders
- [ ] MoSCoW capacity caps are enforced (≤60% Must, ~20% Should, ~20% Could)
- [ ] "Won't have" items are explicitly listed, not silently dropped
- [ ] Scores are recalibrated at least once per planning cycle
- [ ] Bottom-quartile backlog items are reviewed and pruned monthly
- [ ] Dependencies between items are identified and co-prioritized
