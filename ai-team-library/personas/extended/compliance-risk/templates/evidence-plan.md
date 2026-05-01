# Evidence Collection Plan

## Metadata

| Field         | Value                                          |
|---------------|-------------------------------------------------|
| Date          | [YYYY-MM-DD]                                    |
| Owner         | [Name / role responsible for evidence program]   |
| Related links | [Control mapping doc, audit schedule, ADRs]      |
| Status        | Draft / Reviewed / Approved                     |

## Audit Scope

*Define which standard, regulation, or audit this evidence plan supports.*

- **Standard / Regulation**: [e.g., SOC 2 Type II, ISO 27001, HIPAA]
- **Audit period**: [Start date] to [End date]
- **Auditor / Assessor**: [Firm or internal team]
- **Scope boundary**: [Systems, services, and teams in scope]

## Evidence Collection Schedule

*Define the cadence for gathering each category of evidence.*

| Collection Phase | Date Range | Activities | Responsible Party |
|-----------------|------------|------------|-------------------|
| Pre-audit prep  | [Start] - [End] | [Gather artifacts, verify freshness] | [Name / role] |
| Ongoing collection | [Start] - [End] | [Automated log exports, periodic screenshots] | [Name / role] |
| Final assembly  | [Start] - [End] | [Package evidence, fill gaps, peer review] | [Name / role] |

## Evidence Inventory

*List every piece of evidence needed, tied back to control IDs from the control mapping.*

| Control ID | Evidence Type | Source System | Collection Method | Frequency | Retention Period | Owner |
|-----------|---------------|---------------|-------------------|-----------|-----------------|-------|
| [C-001] | [Audit log export] | [Logging platform] | [Automated export / API pull] | [Daily / Weekly / On-demand] | [12 months] | [Name] |
| [C-002] | [Configuration snapshot] | [Infrastructure-as-code repo] | [Git commit history] | [On change] | [Duration of audit period + 1 year] | [Name] |
| [C-003] | [Test results] | [CI/CD pipeline] | [Automated test report export] | [Per build] | [6 months] | [Name] |
| [C-004] | [Policy document] | [Document management system] | [Manual retrieval] | [On revision] | [Current + 2 prior versions] | [Name] |

## Storage and Access

*Where evidence is stored and who can access it.*

- **Storage location**: [Shared drive path, document management system, evidence vault]
- **Backup**: [How and where backups are maintained]
- **Access controls**:
  - Read access: [Roles / individuals]
  - Write access: [Roles / individuals]
  - Admin access: [Roles / individuals]
- **Encryption**: [At rest and in transit requirements]

## Review and Freshness

*How to ensure evidence stays current and complete.*

- **Review cadence**: [Monthly / Quarterly review of evidence completeness]
- **Staleness threshold**: [Evidence older than X days must be refreshed]
- **Reviewer**: [Name / role who validates evidence quality]
- **Escalation**: [What happens when evidence cannot be collected on schedule]

## Definition of Done

- [ ] Every control in the control mapping has at least one evidence item
- [ ] Collection methods are tested and producing output
- [ ] Storage location is provisioned with appropriate access controls
- [ ] Retention periods comply with regulatory requirements
- [ ] Evidence owners are assigned and acknowledged
- [ ] Review cadence is scheduled on team calendar
