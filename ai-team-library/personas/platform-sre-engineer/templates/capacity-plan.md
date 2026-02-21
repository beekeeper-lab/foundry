# Capacity Plan: [Service / System Name]

## Metadata

| Field          | Value                                    |
|----------------|------------------------------------------|
| Date           | [YYYY-MM-DD]                             |
| Owner          | [SRE / Platform Engineer name/role]      |
| Related Links  | [Architecture doc, SLO definition, load test results] |
| Status         | Draft / Reviewed / Approved              |

---

**Planning Horizon:** [e.g., Next quarter / Next 6 months / Next 12 months]
**Last Load Test:** [Date and link to results]
**Next Review Date:** [YYYY-MM-DD]

---

## 1. Current Utilization

*Measured values as of [YYYY-MM-DD]. Source: [monitoring system].*

### Compute

| Component              | Metric         | Current (avg) | Current (peak) | Capacity Limit | Headroom |
|------------------------|----------------|---------------|----------------|----------------|----------|
| [Service A]            | CPU            | [X%]          | [X%]           | [X cores]      | [X%]     |
| [Service A]            | Memory         | [X GB]        | [X GB]         | [X GB]         | [X%]     |
| [Service B]            | CPU            | [X%]          | [X%]           | [X cores]      | [X%]     |
| [Service B]            | Memory         | [X GB]        | [X GB]         | [X GB]         | [X%]     |

### Storage

| Component              | Current Usage  | Growth Rate    | Capacity Limit | Time to Full |
|------------------------|----------------|----------------|----------------|--------------|
| [Primary database]     | [X GB]         | [X GB/month]   | [X GB]         | [X months]   |
| [Object storage]       | [X TB]         | [X GB/month]   | [Unlimited*]   | [N/A]        |
| [Log storage]          | [X GB]         | [X GB/day]     | [X GB]         | [X days]     |

### Network & Connections

| Component              | Metric              | Current (peak) | Capacity Limit | Headroom |
|------------------------|---------------------|----------------|----------------|----------|
| [Database]             | Connections          | [X]            | [X max]        | [X%]     |
| [Load balancer]        | Requests/sec         | [X]            | [X max]        | [X%]     |
| [Message queue]        | Messages/sec         | [X]            | [X max]        | [X%]     |

---

## 2. Traffic Analysis

### Current Traffic Patterns

| Metric                | Value               | Measurement Period |
|-----------------------|---------------------|--------------------|
| Average requests/sec  | [X]                 | [Last 30 days]     |
| Peak requests/sec     | [X]                 | [Last 30 days]     |
| Peak-to-average ratio | [X]                 | [Last 30 days]     |
| Daily traffic pattern | [Description]       | [Time zones, peaks] |
| Weekly pattern        | [Description]       | [Weekday vs weekend] |
| Seasonal pattern      | [Description]       | [Monthly/quarterly trends] |

### Growth Trends

| Metric                | 3 months ago | Current    | Growth Rate     |
|-----------------------|--------------|------------|-----------------|
| Daily active users    | [X]          | [X]        | [X% / month]    |
| Requests/sec (avg)    | [X]          | [X]        | [X% / month]    |
| Data volume           | [X GB]       | [X GB]     | [X GB / month]  |

---

## 3. Demand Projections

### Organic Growth

| Metric                | Current    | +3 months  | +6 months  | +12 months |
|-----------------------|------------|------------|------------|------------|
| Requests/sec (avg)    | [X]        | [X]        | [X]        | [X]        |
| Requests/sec (peak)   | [X]        | [X]        | [X]        | [X]        |
| Storage               | [X GB]     | [X GB]     | [X GB]     | [X GB]     |
| Database connections   | [X]        | [X]        | [X]        | [X]        |

### Planned Events

| Event                 | Date       | Expected Impact          | Preparation Required |
|-----------------------|------------|--------------------------|----------------------|
| [Product launch]      | [Date]     | [Xn traffic increase]    | [Scaling actions]    |
| [Marketing campaign]  | [Date]     | [Xn traffic increase]    | [Scaling actions]    |
| [Seasonal peak]       | [Date]     | [Xn traffic increase]    | [Scaling actions]    |

---

## 4. Bottlenecks & Single Points of Failure

| Component              | Risk                           | Current Headroom | Threshold | Action Required |
|------------------------|--------------------------------|------------------|-----------|-----------------|
| [Database connections] | [Connection exhaustion]        | [X%]             | [< 20%]   | [Add pooling]   |
| [Single AZ deployment] | [AZ failure = full outage]     | [N/A]            | [N/A]     | [Multi-AZ]      |

---

## 5. Scaling Recommendations

### Recommendation 1: [Title]

| Field              | Value                                       |
|--------------------|---------------------------------------------|
| Component          | [What to scale]                             |
| Trigger            | [When to scale -- specific metric threshold] |
| Action             | [How to scale -- specific steps]            |
| Type               | [Horizontal / Vertical / Architectural]     |
| Lead Time          | [How long to implement]                     |
| Estimated Cost     | [Monthly cost delta]                        |
| Priority           | [Critical / High / Medium / Low]            |

*Add additional recommendations as needed.*

---

## 6. Load Test Validation

| Test Scenario          | Target Load    | Result         | Pass/Fail | Notes          |
|------------------------|----------------|----------------|-----------|----------------|
| [Steady state]         | [X rps]        | [p99: X ms]    | [ ]       |                |
| [Peak projected]       | [X rps]        | [p99: X ms]    | [ ]       |                |
| [2x peak]              | [X rps]        | [p99: X ms]    | [ ]       |                |
| [Failure mode: DB]     | [X rps, 1 DB]  | [p99: X ms]    | [ ]       |                |

---

## Definition of Done

- [ ] Current utilization measured from monitoring (not estimated)
- [ ] Growth projections based on historical data and planned events
- [ ] Bottlenecks and single points of failure identified
- [ ] Scaling recommendations with cost estimates and timelines
- [ ] Load test results validate projections
- [ ] Plan reviewed by Architect and service owners
