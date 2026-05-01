# Cost Estimate / Budget Forecast

## Metadata

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Date          | [YYYY-MM-DD]                               |
| Owner         | [Name / role responsible for this estimate] |
| Related links | [Project brief, architecture spec, pricing pages] |
| Status        | Draft / Reviewed / Approved                |

## Scope

*Identify what is being estimated and the time horizon.*

- **Project / Feature**: [Name and brief description]
- **Environment(s)**: [Production / Staging / Dev / All]
- **Estimate period**: [Start date] to [End date]
- **Currency**: [USD / EUR / etc.]

## Assumptions

*List every assumption that affects the estimate. If an assumption changes, the estimate must be revised.*

| # | Assumption | Impact if Wrong |
|---|-----------|-----------------|
| 1 | [e.g., Traffic: 500K requests/day average, 2M peak] | [Higher traffic increases compute and API costs] |
| 2 | [e.g., Data growth: 50GB/month] | [Higher growth increases storage and transfer costs] |
| 3 | [e.g., Pricing tier: On-demand, no commitments] | [Commitments would reduce cost by 20-40%] |

## Cost Breakdown

*Break down costs by category. Provide unit price, quantity, and subtotal for each line item.*

### Compute

| Resource | Type / SKU | Unit Price | Quantity | Monthly Cost | Annual Cost | Notes |
|----------|-----------|------------|----------|-------------|-------------|-------|
| [e.g., API servers] | [m5.xlarge] | [$0.192/hr] | [3 instances x 730 hrs] | [$420.48] | [$5,045.76] | [On-demand pricing] |

### Storage

| Resource | Type / SKU | Unit Price | Quantity | Monthly Cost | Annual Cost | Notes |
|----------|-----------|------------|----------|-------------|-------------|-------|
| [e.g., Database] | [gp3 EBS] | [$0.08/GB-mo] | [500 GB] | [$40.00] | [$480.00] | [Plus IOPS charges] |

### Networking

| Resource | Type / SKU | Unit Price | Quantity | Monthly Cost | Annual Cost | Notes |
|----------|-----------|------------|----------|-------------|-------------|-------|
| [e.g., Data transfer] | [AWS egress] | [$0.09/GB] | [200 GB/mo] | [$18.00] | [$216.00] | [First 1GB free] |

### Licensing

| Product | License Type | Unit Price | Quantity | Monthly Cost | Annual Cost | Notes |
|---------|-------------|------------|----------|-------------|-------------|-------|
| [e.g., Datadog] | [Per host] | [$23/host/mo] | [5 hosts] | [$115.00] | [$1,380.00] | [Pro tier] |

### Other / One-Time

| Item | Cost | Frequency | Notes |
|------|------|-----------|-------|
| [e.g., Migration labor] | [$5,000] | One-time | [20 hours at $250/hr] |

## Summary

| Category | Monthly (Low) | Monthly (Expected) | Monthly (High) | Annual (Expected) |
|----------|--------------|-------------------|----------------|-------------------|
| Compute  | [$X] | [$X] | [$X] | [$X] |
| Storage  | [$X] | [$X] | [$X] | [$X] |
| Networking | [$X] | [$X] | [$X] | [$X] |
| Licensing | [$X] | [$X] | [$X] | [$X] |
| Other    | [$X] | [$X] | [$X] | [$X] |
| **Total** | **[$X]** | **[$X]** | **[$X]** | **[$X]** |

## Range Drivers

*Explain what drives the difference between low, expected, and high estimates.*

| Range Boundary | Driven By |
|---------------|-----------|
| Low | [e.g., Traffic stays flat, no new features, spot instances available] |
| Expected | [e.g., 20% traffic growth, planned feature launches, on-demand pricing] |
| High | [e.g., 50% traffic spike, unplanned scaling, premium support tier] |

## Notes

- [Any caveats, exclusions, or dependencies]
- [Pricing source and date for reproducibility]

## Definition of Done

- [ ] Every cost line item has a specific resource type and unit price
- [ ] Assumptions are documented and reviewable
- [ ] Low, expected, and high ranges are provided
- [ ] One-time vs. recurring costs are distinguished
- [ ] Monthly and annual totals are calculated
- [ ] Pricing source and date are documented
