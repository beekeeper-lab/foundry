# Audit Notes

## Metadata

| Field         | Value                                    |
|---------------|------------------------------------------|
| Date          | [YYYY-MM-DD]                             |
| Owner         | [Auditor name / Compliance Analyst]      |
| Related Links | [Control mapping, policy docs, evidence] |
| Status        | Draft / Reviewed / Approved              |

## Audit Scope

*Define the boundaries of this audit -- what is being examined and why.*

- **Audit type:** [Internal / External / Regulatory / Certification]
- **Framework / Standard:** [SOC 2, ISO 27001, HIPAA, PCI-DSS, or project-specific]
- **Period under review:** [YYYY-MM-DD] to [YYYY-MM-DD]
- **Systems in scope:** [List systems, services, or components being audited]
- **Areas excluded:** [Anything explicitly out of scope and the reason]

## Auditor Information

| Role          | Name     | Organization         |
|---------------|----------|----------------------|
| Lead Auditor  | [Name]   | [Internal / Firm]    |
| Audit Support | [Name]   | [Internal / Firm]    |
| Auditee POC   | [Name]   | [Team / Department]  |

## Observations

*Record each observation as a separate row. Assign a unique finding ID for traceability.*

| Finding ID | Observation                              | Control Reference | Severity           | Evidence Status       |
|------------|------------------------------------------|-------------------|--------------------|-----------------------|
| AUD-001    | [Describe what was observed]             | [CTL-XXX]         | Critical / High / Medium / Low / Info | Collected / Pending / Missing |
| AUD-002    | [Describe what was observed]             | [CTL-XXX]         | [Severity]         | [Evidence status]     |
| AUD-003    | [Describe what was observed]             | [CTL-XXX]         | [Severity]         | [Evidence status]     |

*Add rows as needed. Every observation should map to at least one control reference.*

## Findings Detail

*For each finding rated Medium or above, provide a detailed write-up below.*

### AUD-001: [Finding Title]

- **Observation:** [Detailed description of what was found]
- **Expected control:** [What should have been in place per the control framework]
- **Actual state:** [What was actually observed]
- **Root cause:** [Why the gap exists, if known]
- **Evidence:** [References to collected evidence -- screenshots, logs, config exports]
- **Risk implication:** [What could go wrong if this is not addressed]

### AUD-002: [Finding Title]

- **Observation:** [Detailed description]
- **Expected control:** [Expected state]
- **Actual state:** [Observed state]
- **Root cause:** [Cause if known]
- **Evidence:** [Evidence references]
- **Risk implication:** [Risk if unaddressed]

## Remediation Actions

| Finding ID | Action                                   | Owner    | Target Date  | Status                          |
|------------|------------------------------------------|----------|--------------|---------------------------------|
| AUD-001    | [Specific corrective action]             | [Name]   | [YYYY-MM-DD] | Not Started / In Progress / Done |
| AUD-002    | [Specific corrective action]             | [Name]   | [YYYY-MM-DD] | [Status]                        |
| AUD-003    | [Specific corrective action]             | [Name]   | [YYYY-MM-DD] | [Status]                        |

## Follow-Up Schedule

| Milestone                     | Date         | Owner    |
|-------------------------------|--------------|----------|
| Draft audit notes delivered   | [YYYY-MM-DD] | [Name]  |
| Auditee response due          | [YYYY-MM-DD] | [Name]  |
| Remediation progress check    | [YYYY-MM-DD] | [Name]  |
| Remediation verification      | [YYYY-MM-DD] | [Name]  |
| Final audit report issued     | [YYYY-MM-DD] | [Name]  |

## Definition of Done

- [ ] All observations recorded with finding IDs and control references
- [ ] Severity assigned to every observation using a consistent scale
- [ ] Evidence status documented for each finding
- [ ] Detailed write-ups provided for all Medium-and-above findings
- [ ] Remediation actions assigned with owners and target dates
- [ ] Follow-up schedule established and communicated to auditee
- [ ] Audit notes reviewed by a second auditor or compliance lead
