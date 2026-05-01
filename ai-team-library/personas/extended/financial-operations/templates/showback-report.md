# Showback / Chargeback Report

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [Name / role responsible for cost allocation] |
| Related links | [Billing exports, tagging policy, allocation methodology] |
| Status        | Draft / Reviewed / Approved                 |

## Reporting Period

- **Period**: [Month] [YYYY]
- **Total spend**: [$X]
- **Allocation method**: [Direct attribution + proportional shared cost allocation]
- **Billing data source**: [Cloud provider billing export, cost management tool]

## Allocation Summary

| Team / Business Unit | Direct Costs | Shared Costs (Allocated) | Total Cost | % of Total | vs. Prior Period | Unit Economics |
|---------------------|-------------|------------------------|-----------|------------|-----------------|---------------|
| [Team A] | [$X] | [$X] | [$X] | [X%] | [+/- X%] | [$X per user] |
| [Team B] | [$X] | [$X] | [$X] | [X%] | [+/- X%] | [$X per transaction] |
| [Team C] | [$X] | [$X] | [$X] | [X%] | [+/- X%] | [$X per environment] |
| Unattributed | [$X] | [—] | [$X] | [X%] | [+/- X%] | [—] |
| **Total** | **[$X]** | **[$X]** | **[$X]** | **100%** | **[+/- X%]** | |

## Shared Cost Allocation Methodology

*Document how shared costs are divided among teams.*

| Shared Cost Category | Total Cost | Allocation Method | Allocation Key |
|---------------------|-----------|-------------------|---------------|
| [e.g., Networking] | [$X] | [Proportional to data transfer] | [GB transferred per team] |
| [e.g., Monitoring] | [$X] | [Equal split] | [N teams] |
| [e.g., Platform overhead] | [$X] | [Weighted by compute usage] | [vCPU-hours per team] |

## Team Detail: [Team A]

| Service / Resource | Cost | % of Team Total | Notes |
|-------------------|------|----------------|-------|
| [e.g., EC2 compute] | [$X] | [X%] | [3x m5.xlarge production] |
| [e.g., RDS database] | [$X] | [X%] | [db.r5.large multi-AZ] |
| [e.g., S3 storage] | [$X] | [X%] | [1.2 TB stored] |
| [Allocated shared] | [$X] | [X%] | [Networking + monitoring] |
| **Total** | **[$X]** | **100%** | |

<!-- Repeat Team Detail section for each team -->

## Unattributed Costs

*Costs that could not be allocated due to missing tags or shared resources without a clear allocation key.*

| Resource / Service | Cost | Reason Unattributed | Remediation Plan |
|-------------------|------|--------------------|--------------------|
| [e.g., Orphaned EBS volumes] | [$X] | [No tags, no attached instance] | [Identify owner or delete by YYYY-MM-DD] |

## Trend

| Team / BU | [Month-3] | [Month-2] | [Month-1] | Current | Trend |
|-----------|-----------|-----------|-----------|---------|-------|
| [Team A]  | [$X]      | [$X]      | [$X]      | [$X]    | [Up / Down / Flat] |
| [Team B]  | [$X]      | [$X]      | [$X]      | [$X]    | [Trend] |

## Notes

- [Changes to allocation methodology since last report]
- [Teams added or removed from the report]

## Definition of Done

- [ ] All costs are allocated or explicitly marked as unattributed
- [ ] Allocation methodology is documented and consistent
- [ ] Shared cost allocation uses a defensible method
- [ ] Unit economics are included where applicable
- [ ] Unattributed costs have remediation plans
- [ ] Report is understandable by non-technical stakeholders
