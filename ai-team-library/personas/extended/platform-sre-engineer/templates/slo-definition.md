# SLO Definition: [Service Name]

## Metadata

| Field          | Value                                    |
|----------------|------------------------------------------|
| Date           | [YYYY-MM-DD]                             |
| Owner          | [SRE / Platform Engineer name/role]      |
| Related Links  | [Architecture doc, dashboard, monitoring links] |
| Status         | Draft / Reviewed / Approved              |

---

**Service:** [Service name and brief description]
**Measurement Window:** [Rolling 30 days / Calendar month / Other]
**Review Cadence:** [Quarterly / After significant changes]

---

## 1. Service Level Indicators (SLIs)

### SLI 1: [Name, e.g., Availability]

| Field              | Value                                       |
|--------------------|---------------------------------------------|
| Description        | [What user-facing behavior is measured]      |
| Numerator          | [Count of successful events]                |
| Denominator        | [Count of total valid events]               |
| Data Source         | [Monitoring system, metric name, query]     |
| Measurement Method | [Request logs / Synthetic probes / Client instrumentation] |
| Exclusions         | [What is excluded from measurement, e.g., planned maintenance] |

### SLI 2: [Name, e.g., Latency]

| Field              | Value                                       |
|--------------------|---------------------------------------------|
| Description        | [What user-facing behavior is measured]      |
| Percentile         | [p50 / p95 / p99]                           |
| Threshold          | [Requests completing within X ms]           |
| Data Source         | [Monitoring system, metric name, query]     |
| Measurement Method | [Server-side / Client-side / Edge measurement] |
| Exclusions         | [What is excluded from measurement]         |

*Add additional SLIs as needed.*

---

## 2. SLO Targets

| SLI                        | Target          | Measurement Window |
|----------------------------|-----------------|--------------------|
| [Availability]             | [99.9%]         | [Rolling 30 days]  |
| [Latency p99]              | [< 2000ms]      | [Rolling 30 days]  |

**Rationale:** [Why these targets were chosen. Reference historical performance
data, user expectations, and business requirements.]

---

## 3. Error Budget

| SLI              | Target   | Budget (per window)              |
|------------------|----------|----------------------------------|
| [Availability]   | [99.9%]  | [43.2 minutes / 0.1% of requests] |
| [Latency p99]    | [< 2s]   | [0.1% of requests may exceed]    |

**Current Budget Status:**
- Budget consumed this window: [X%]
- Burn rate (last 1h / 6h / 24h): [X]
- Projected exhaustion: [Date or "within budget"]

---

## 4. Error Budget Policy

**When error budget is healthy (> 50% remaining):**
- Feature development proceeds normally.
- Reliability improvements are scheduled in regular sprint planning.

**When error budget is at risk (25-50% remaining):**
- Reliability work is prioritized alongside feature work.
- New deployments require explicit SRE review.
- Increased monitoring frequency.

**When error budget is exhausted (< 25% remaining or depleted):**
- Feature releases are frozen until budget recovers.
- All engineering effort redirected to reliability improvements.
- Post-incident review required for contributing incidents.
- Escalation to Team Lead for resource allocation.

---

## 5. Alerting

### Burn-Rate Alerts

| Alert Name             | Window   | Burn Rate | Severity | Action              |
|------------------------|----------|-----------|----------|---------------------|
| [SLO budget burn 1h]   | 1 hour   | [14.4x]   | Critical | Page on-call        |
| [SLO budget burn 6h]   | 6 hours  | [6x]      | Warning  | Notify team channel |
| [SLO budget burn 24h]  | 24 hours | [3x]      | Info     | Review in standup   |

**Alert Routing:**
- Critical: [PagerDuty service / On-call rotation]
- Warning: [Team Slack channel / Email]
- Info: [Dashboard / Daily report]

---

## 6. Dashboard

**Dashboard Link:** [URL to SLO dashboard]

**Required Panels:**
- [ ] SLI current value vs target
- [ ] Error budget remaining (percentage and absolute)
- [ ] Burn rate trend (1h, 6h, 24h, 7d)
- [ ] SLI time series over measurement window
- [ ] Top error contributors (error codes, endpoints, regions)

---

## 7. Review History

| Date       | Reviewer    | Changes Made                           |
|------------|-------------|----------------------------------------|
| [Date]     | [Name]      | [Initial SLO definition]               |

---

## Definition of Done

- [ ] SLIs are precisely defined with data source and query
- [ ] Targets are validated against historical data
- [ ] Error budget policy is agreed upon by stakeholders
- [ ] Burn-rate alerts are configured and tested
- [ ] Dashboard is live and accessible to the team
- [ ] SLO reviewed and approved by service owner and platform team
