# A/B Test Plan: [Experiment Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Analyst       | [Data Analyst name]            |
| Requested by  | [Product owner / stakeholder]  |
| Related links | [Feature spec / task links]    |
| Status        | Design / Running / Complete    |

*Experiment design document. All parameters must be pre-specified before the test launches. Do not modify after launch unless stopping the test.*

---

## Hypothesis

**Statement:** [If we (change), then (metric) will (direction) by (magnitude) because (rationale).]

**Example:** If we simplify the checkout flow from 4 steps to 2, then checkout completion rate will increase by at least 5 percentage points because the current drop-off analysis shows 30% abandonment between steps 2 and 3.

---

## Metrics

### Primary Metric

| Field              | Value                                    |
|--------------------|------------------------------------------|
| Metric name        | [e.g., Checkout completion rate]         |
| Definition         | [Exact calculation -- link to metric catalog] |
| Current baseline   | [e.g., 62%]                              |
| Minimum detectable effect | [e.g., 5 percentage points]        |

### Secondary Metrics

| Metric             | Definition                    | Purpose                    |
|--------------------|-------------------------------|----------------------------|
| [e.g., Revenue per user] | [Calculation]            | [Ensure no revenue impact] |
| [e.g., Support tickets]  | [Calculation]            | [Monitor for confusion]    |

### Guard-Rail Metrics

| Metric             | Threshold          | Action if Breached          |
|--------------------|--------------------|-----------------------------|
| [e.g., Error rate] | [e.g., >2% increase] | [Stop test immediately]   |
| [e.g., Page load time] | [e.g., >500ms increase] | [Investigate and decide] |

---

## Test Design

| Parameter               | Value                                   |
|-------------------------|-----------------------------------------|
| Randomization unit      | [e.g., User ID]                         |
| Variants                | [e.g., Control (current) vs Treatment (2-step checkout)] |
| Traffic allocation      | [e.g., 50/50]                           |
| Targeting criteria      | [e.g., New users on web platform only]  |
| Significance level (α)  | [e.g., 0.05]                            |
| Statistical power (1-β) | [e.g., 0.80]                            |
| Required sample size    | [e.g., 4,200 per variant]               |
| Estimated duration      | [e.g., 14 days at current traffic]      |
| Test type               | [e.g., Two-sided t-test / Chi-squared]  |

---

## Implementation Requirements

- [ ] [e.g., Feature flag `checkout_v2` created and configured]
- [ ] [e.g., Event tracking added for new checkout flow steps]
- [ ] [e.g., Randomization verified: no selection bias in variant assignment]
- [ ] [e.g., Monitoring dashboard live before test launch]

---

## Monitoring Plan

| Check              | Frequency    | Owner         | Action if Anomaly           |
|--------------------|-------------|---------------|-----------------------------|
| Sample ratio mismatch | [Daily] | [Analyst]     | [Stop test, investigate]    |
| Guard-rail metrics | [Daily]     | [Analyst]     | [Stop test if breached]     |
| Data quality       | [Daily]     | [Analyst]     | [Pause test, fix data]      |

---

## Decision Criteria

| Outcome            | Criteria                           | Action                      |
|--------------------|------------------------------------|-----------------------------|
| **Ship treatment** | Primary metric significant at α=0.05, positive direction, guard rails clean | [Roll out to 100%] |
| **Iterate**        | Directionally positive but not significant | [Extend test or redesign variant] |
| **Revert**         | Negative or neutral result         | [Keep control, document learnings] |
| **Stop early**     | Guard-rail metric breached         | [Revert immediately, investigate] |

---

## Results (Post-Experiment)

### Summary

| Metric             | Control   | Treatment | Difference | 95% CI        | p-value |
|--------------------|-----------|-----------|------------|---------------|---------|
| [Primary metric]   | [value]   | [value]   | [value]    | [low, high]   | [value] |
| [Secondary metric] | [value]   | [value]   | [value]    | [low, high]   | [value] |

### Guard-Rail Outcomes

| Metric             | Control   | Treatment | Status              |
|--------------------|-----------|-----------|---------------------|
| [Guard-rail 1]     | [value]   | [value]   | [Clean / Breached]  |

### Decision

**Outcome:** [Ship / Iterate / Revert]

**Rationale:** [Why this decision was made based on the data]

### Learnings

- [Key learning 1]
- [Key learning 2]
- [Follow-up experiment or analysis needed]
