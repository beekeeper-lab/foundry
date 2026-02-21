# Cloud Cost Optimization Report

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [Name / role responsible for optimization]  |
| Related links | [Billing exports, usage reports, prior optimization reports] |
| Status        | Draft / Reviewed / Approved                 |

## Scope

- **Cloud provider(s)**: [AWS / Azure / GCP / Multi-cloud]
- **Accounts / subscriptions**: [List of accounts in scope]
- **Analysis period**: [Start date] to [End date]
- **Current monthly spend**: [$X]

## Executive Summary

*Top-line findings: total addressable savings, number of recommendations, and quick wins.*

| Metric | Value |
|--------|-------|
| Total current monthly spend | [$X] |
| Total addressable monthly savings | [$X] |
| Total addressable annual savings | [$X] |
| Number of recommendations | [N] |
| Quick wins (high savings, low effort) | [N] |

## Recommendations

### Quick Wins

*High savings, low implementation effort. Can be implemented immediately.*

| # | Resource / Service | Current State | Proposed Change | Monthly Savings | Annual Savings | Effort | Risk |
|---|-------------------|---------------|----------------|----------------|---------------|--------|------|
| 1 | [e.g., prod-api-01] | [m5.2xlarge, p95 CPU 23%] | [Rightsize to m5.xlarge] | [$234] | [$2,803] | [1 hour] | [Low -- rollback is instance type change] |
| 2 | [Resource] | [Current] | [Proposed] | [$X] | [$X] | [Effort] | [Risk] |

### Medium-Term Optimizations

*Significant savings, moderate effort. Plan for next sprint or quarter.*

| # | Resource / Service | Current State | Proposed Change | Monthly Savings | Annual Savings | Effort | Risk |
|---|-------------------|---------------|----------------|----------------|---------------|--------|------|
| 1 | [Resource] | [Current] | [Proposed] | [$X] | [$X] | [Effort] | [Risk] |

### Strategic Optimizations

*Require architectural or commitment changes. Plan for next quarter or beyond.*

| # | Resource / Service | Current State | Proposed Change | Monthly Savings | Annual Savings | Effort | Risk |
|---|-------------------|---------------|----------------|----------------|---------------|--------|------|
| 1 | [e.g., All compute] | [On-demand pricing] | [1-year Savings Plan at $X/hr] | [$X] | [$X] | [Procurement process] | [Commitment lock-in] |

## Previously Identified — Not Yet Implemented

*Track recommendations from prior reports that remain open.*

| # | Recommendation | First Identified | Estimated Savings | Status | Blocker |
|---|---------------|-----------------|-------------------|--------|---------|
| 1 | [Description] | [YYYY-MM-DD] | [$X/yr] | [Open / In Progress / Blocked] | [Reason if blocked] |

## Notes

- [Data sources and methodology for utilization analysis]
- [Exclusions or limitations of the analysis]

## Definition of Done

- [ ] Each recommendation includes current state, proposed change, and estimated savings
- [ ] Savings estimates are based on actual usage data with documented methodology
- [ ] Recommendations are prioritized by net benefit
- [ ] Quick wins are flagged for immediate action
- [ ] Previously identified recommendations are tracked
- [ ] Report reviewed by a second party
