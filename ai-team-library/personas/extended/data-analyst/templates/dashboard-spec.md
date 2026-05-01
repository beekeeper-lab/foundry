# Dashboard Specification: [Dashboard Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Analyst name]            |
| Related links | [Task / requirements links]    |
| Status        | Draft / Reviewed / Approved    |

*Specification for a dashboard or automated report. Write this before building to align on purpose, audience, and metrics with stakeholders.*

---

## Dashboard Overview

- **Purpose:** [What decisions does this dashboard support?]
- **Target audience:** [Who will use this dashboard and how often?]
- **Tool:** [e.g., Metabase, Looker, Tableau, Grafana]
- **Refresh cadence:** [e.g., Real-time / Hourly / Daily]
- **Access:** [Who has access? Any row-level security requirements?]

---

## Metrics & Visualizations

| # | Metric | Definition Reference | Visualization Type | Filters | Position |
|---|--------|---------------------|--------------------|---------|----------|
| 1 | [e.g., Daily Active Users] | [Link to metric catalog] | [e.g., Line chart] | [e.g., Date range, Platform] | [e.g., Top row, left] |
| 2 | [e.g., Conversion Rate] | [Link to metric catalog] | [e.g., Scorecard with trend] | [e.g., Date range, Channel] | [e.g., Top row, right] |
| 3 | [e.g., Revenue by Channel] | [Link to metric catalog] | [e.g., Stacked bar chart] | [e.g., Date range] | [e.g., Middle row] |

---

## Filters & Interactivity

| Filter     | Type       | Default Value       | Applies To         |
|------------|------------|---------------------|--------------------|
| [e.g., Date range] | [Date picker] | [Last 30 days] | [All charts]    |
| [e.g., Platform]   | [Dropdown]    | [All]          | [Charts 1, 2]   |

---

## Layout

```
[ASCII layout sketch or description of dashboard sections]

+---------------------------+---------------------------+
|   DAU (line chart)        |   Conversion (scorecard)  |
+---------------------------+---------------------------+
|   Revenue by Channel (stacked bar)                    |
+-------------------------------------------------------+
|   Top Pages (table)       |   Funnel (funnel chart)   |
+---------------------------+---------------------------+
```

---

## Data Sources

| Metric          | Source Table             | Key Joins               |
|-----------------|-------------------------|-------------------------|
| [e.g., DAU]     | [e.g., analytics.events] | [e.g., users on user_id] |

---

## Performance Requirements

- **Load time:** [e.g., <3 seconds for default view]
- **Caching strategy:** [e.g., Query cache with 1-hour TTL]
- **Data freshness indicator:** [e.g., "Last updated" timestamp in header]

---

## Stakeholder Review

| Reviewer   | Role        | Review Date | Feedback Status |
|------------|-------------|-------------|-----------------|
| [Name]     | [e.g., PM]  | YYYY-MM-DD  | [Pending / Approved] |
