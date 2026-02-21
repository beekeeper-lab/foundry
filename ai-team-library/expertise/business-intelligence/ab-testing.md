# A/B Testing Methodology

Standards for designing, running, and analyzing controlled experiments. A/B
testing is the primary method for making data-driven product decisions. A poorly
designed experiment is worse than no experiment — it gives false confidence.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Experiment platform** | Feature flag service with built-in assignment and analysis (LaunchDarkly, Statsig, Eppo) | In-house randomization service; warehouse-native experimentation (Eppo, internal) for teams with strong data eng |
| **Randomization unit** | User ID (consistent hashing) | Session ID for anonymous users; organization/account ID for B2B; device ID for multi-device products |
| **Statistical method** | Frequentist two-sample t-test or z-test with fixed-horizon analysis | Sequential testing (CUPED-adjusted) for continuous monitoring; Bayesian analysis for business-friendly credible intervals |
| **Significance level (α)** | 0.05 (5% false positive rate) | 0.01 for high-stakes decisions (pricing, payments); 0.10 for exploratory experiments |
| **Power (1 − β)** | 0.80 (80% probability of detecting true effect) | 0.90 for critical experiments where missing a real effect is costly |
| **Minimum Detectable Effect (MDE)** | Defined per experiment based on business impact analysis | Default MDE by metric type: conversion ±1pp, revenue ±2%, engagement ±5% |
| **Experiment duration** | Run until pre-computed sample size is reached AND at least 1 full business cycle (7 days) | Minimum 14 days for metrics with weekly seasonality; 30 days for subscription/retention metrics |
| **Guardrail metrics** | Page load time, error rate, crash rate — monitored on every experiment | Revenue per user, customer support tickets — added for experiments affecting monetization or UX |

---

## Do / Don't

- **Do** define the hypothesis, primary metric, and sample size calculation before launching the experiment. Document these in the experiment brief.
- **Do** run a power analysis to determine the required sample size. Do not eyeball it or "run it for a week and see."
- **Do** use a single primary metric per experiment. Secondary metrics and guardrails are tracked but do not determine the ship decision.
- **Do** account for multiple comparisons if testing more than one variant. Apply Bonferroni correction or use a method designed for multiple testing.
- **Do** check for Sample Ratio Mismatch (SRM) within the first 24 hours. An SRM > 1% indicates a randomization or logging bug — pause the experiment.
- **Do** run the experiment for at least one full business cycle (typically 7 days) to capture day-of-week effects, even if sample size is reached sooner.
- **Do** document the experiment result (ship, no-ship, or inconclusive) with the observed effect size, confidence interval, and business interpretation.
- **Don't** peek at results before the pre-committed sample size is reached and make ship decisions. Peeking inflates the false positive rate. Use sequential testing if continuous monitoring is required.
- **Don't** run experiments on overlapping populations without an isolation framework. Traffic collisions between experiments corrupt both results.
- **Don't** use ratio metrics (e.g., revenue per user) without delta-method variance estimation. Naive t-tests on ratios underestimate variance.
- **Don't** extend an experiment past the planned end date to "wait for significance." This is p-hacking. If the result is inconclusive, document it and plan a follow-up with a larger sample.
- **Don't** skip guardrail metric monitoring. A variant that improves conversion but doubles page load time should not ship.
- **Don't** exclude outliers post-hoc without a pre-registered rule. Define winsorization or trimming thresholds in the experiment brief before launch.

---

## Experiment Lifecycle

### 1. Design

```
Hypothesis:    "Adding urgency messaging to the cart page will increase
                checkout completion rate by ≥ 2 percentage points."
Primary metric: Checkout completion rate (orders / carts)
Secondary:     Average order value, items per order
Guardrails:    Page load time (p95), error rate, support ticket rate
Variants:      Control (no message), Treatment (urgency banner)
Unit:          User ID
Traffic split: 50/50
MDE:           2 percentage points
α:             0.05
Power:         0.80
Sample size:   ~12,400 users per variant (from power analysis)
Duration:      14 days minimum (2 full business cycles)
```

### 2. Validation

- [ ] Randomization is deterministic and consistent (same user always sees same variant)
- [ ] Logging captures assignment event, exposure event, and metric events
- [ ] SRM check is automated for the first 24 hours
- [ ] Guardrail alerts are configured

### 3. Execution

- Launch to the planned traffic allocation. Do not ramp up gradually unless the feature has safety risk.
- Monitor guardrails daily. If a guardrail breaches its threshold, pause and investigate.
- Do not change traffic split, variant behavior, or targeting mid-experiment.

### 4. Analysis

- Wait for the pre-committed sample size and minimum duration.
- Run the statistical test on the primary metric.
- Report: observed effect, confidence interval, p-value, sample size achieved, SRM check result.
- Interpret the result in business terms: "The treatment increased checkout completion by 2.3pp (95% CI: [0.8pp, 3.8pp]). At current traffic, this represents ~$140K annual incremental revenue."

### 5. Decision

| Result | Action |
|--------|--------|
| Statistically significant, positive, guardrails clear | Ship the treatment |
| Statistically significant, positive, guardrail breach | Investigate guardrail; ship only after resolution |
| Not statistically significant | Document as inconclusive; plan follow-up with larger MDE or higher traffic |
| Statistically significant, negative | Do not ship; document learnings |

---

## Common Pitfalls

1. **Peeking and early stopping.** Checking results daily and stopping when p < 0.05 inflates false positives to 20–30%. Commit to a fixed sample size or use a sequential testing method with proper stopping boundaries.
2. **Underpowered experiments.** Running an experiment with too little traffic to detect the expected effect. The result is almost always "inconclusive," wasting time. Run the power analysis before launch.
3. **Network effects and spillover.** In marketplace or social products, treatment users affect control users (e.g., a supply-side change affects all buyers). Use cluster randomization (by market, geography, or time) to isolate effects.
4. **Novelty and primacy effects.** A new UI element gets more clicks initially because it is novel, not because it is better. Run experiments long enough to pass the novelty window (typically 2–4 weeks).
5. **Survivorship bias in retention experiments.** Measuring 30-day retention only on users who were still active at day 7 excludes early churners and biases the result upward. Define the cohort at the point of randomization, not at a later event.
6. **Multiple primary metrics.** Declaring three metrics as "co-primary" and shipping if any one is significant is a form of multiple testing. Pick one primary metric; use the others as secondary evidence.

---

## Checklist

- [ ] Hypothesis, primary metric, and MDE are documented in the experiment brief
- [ ] Power analysis determines required sample size before launch
- [ ] Single primary metric is declared; secondary and guardrails are listed separately
- [ ] Randomization unit is specified and consistent (same user → same variant)
- [ ] Traffic split is documented and will not change mid-experiment
- [ ] SRM check is automated for the first 24 hours
- [ ] Guardrail metrics are defined with breach thresholds
- [ ] Minimum duration covers at least 1 full business cycle (7 days)
- [ ] Multiple comparison correction is applied if > 1 variant
- [ ] Outlier handling rules are pre-registered (not decided post-hoc)
- [ ] Results are documented with effect size, confidence interval, and business interpretation
- [ ] Ship/no-ship decision is recorded with rationale
