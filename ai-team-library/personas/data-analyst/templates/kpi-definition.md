# KPI Definition: [Metric Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Metric owner name]            |
| Related links | [Task / strategy doc links]    |
| Status        | Draft / Reviewed / Approved    |

*Precise definition of a key performance indicator or business metric. Write this to establish the single source of truth for how this metric is calculated.*

---

## Metric Overview

- **Name:** [Unique metric name, e.g., Monthly Active Users (MAU)]
- **Category:** [e.g., Engagement / Revenue / Retention / Acquisition]
- **Business question:** [What decision does this metric inform?]
- **Owner:** [Team or individual responsible for this metric]

---

## Definition

**Plain language:** [One-sentence description understandable by any stakeholder]

**Calculation formula:**
```
[Exact formula, e.g., COUNT(DISTINCT user_id) WHERE event_type IN ('core_action_1', 'core_action_2') AND event_date BETWEEN (current_date - 30) AND current_date]
```

---

## Data Source

| Field            | Value                                    |
|------------------|------------------------------------------|
| Database/Schema  | [e.g., analytics.core]                   |
| Table(s)         | [e.g., events, users]                    |
| Key columns      | [e.g., user_id, event_type, event_date]  |
| Refresh cadence  | [e.g., Daily at 06:00 UTC]               |
| Expected latency | [e.g., T+1 day]                          |

---

## Inclusions & Exclusions

| Rule         | Description                                           |
|--------------|-------------------------------------------------------|
| **Include**  | [e.g., All users who completed at least one core action] |
| **Exclude**  | [e.g., Internal test accounts (is_internal = true)]   |
| **Exclude**  | [e.g., Bot traffic (flagged by fraud detection)]      |

---

## Segmentation

| Segment      | Definition                        | Purpose                    |
|--------------|-----------------------------------|----------------------------|
| [e.g., Platform] | [e.g., iOS / Android / Web]  | [e.g., Platform comparison] |
| [e.g., Cohort]   | [e.g., Sign-up month]        | [e.g., Retention analysis]  |

---

## Targets & Thresholds

| Threshold    | Value        | Action                                  |
|--------------|--------------|-----------------------------------------|
| **Target**   | [e.g., 50K]  | [On track]                              |
| **Warning**  | [e.g., <40K] | [Investigate root cause]                |
| **Critical** | [e.g., <30K] | [Escalate to Team Lead]                 |

---

## Change History

| Date       | Change Description                       | Changed By |
|------------|------------------------------------------|------------|
| YYYY-MM-DD | [e.g., Initial definition]               | [Name]     |
