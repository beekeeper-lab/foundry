# Control Mapping

## Metadata

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Date          | [YYYY-MM-DD]                               |
| Owner         | [Name / role responsible for this mapping]  |
| Related links | [Regulation URL, framework docs, ADRs]     |
| Status        | Draft / Reviewed / Approved                |

## Scope

*Identify the regulation, standard, or framework being mapped and which system boundary this covers.*

- **Standard / Regulation**: [e.g., SOC 2 Type II, ISO 27001, HIPAA, PCI-DSS]
- **System boundary**: [e.g., production SaaS platform, internal tooling]
- **Assessment period**: [Start date] to [End date]

## Control Mapping Table

*For each requirement in the standard, map it to the control that satisfies it, the component that implements it, and the evidence that proves it.*

| Req ID | Requirement Description | Control ID | Control Description | Implementation | Component / Service | Evidence Type | Verification Method | Status | Owner |
|--------|------------------------|------------|--------------------|--------------------|---------------------|---------------|---------------------|--------|-------|
| [R-001] | [Requirement text from standard] | [C-001] | [What the control does] | [How the system implements this] | [Service or module name] | [Log / Config / Test result / Policy doc] | [Automated test / Manual review / Audit scan] | Implemented / Partial / Planned / Gap | [Name] |
| [R-002] | [Requirement text] | [C-002] | [Control description] | [Implementation details] | [Component] | [Evidence type] | [Verification method] | [Status] | [Name] |
| [R-003] | [Requirement text] | [C-003] | [Control description] | [Implementation details] | [Component] | [Evidence type] | [Verification method] | [Status] | [Name] |

## Gap Summary

*List any requirements with Status = Gap or Partial. For each, note the remediation plan.*

| Req ID | Gap Description | Remediation Plan | Target Date | Owner |
|--------|----------------|-----------------|-------------|-------|
| [R-00X] | [What is missing] | [Steps to close the gap] | [YYYY-MM-DD] | [Name] |

## Notes

- [Any assumptions, exclusions, or caveats about this mapping]
- [Cross-references to related control mappings for other standards]

## Definition of Done

- [ ] Every requirement in the standard has a corresponding row
- [ ] Each control has an identified owner
- [ ] Gaps are documented with remediation plans and target dates
- [ ] Evidence types are specified and evidence is collectible
- [ ] Mapping reviewed by a second party
- [ ] Status reflects current state, not aspirational state
