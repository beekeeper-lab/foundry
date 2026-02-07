# Evidence Attachments

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | [YYYY-MM-DD]                   |
| Owner         | [evidence collector]           |
| Related links | [issue/PR/ADR URLs]            |
| Status        | Draft / Reviewed / Approved    |

## Purpose

*Catalog evidence artifacts that support audits, compliance checks, reviews, or incident investigations. Each entry should be traceable to a specific requirement or control.*

## Evidence Register

| Evidence ID | Description                     | Type              | Source                  | Date Collected | Collected By | Storage Location        | Related Control / Requirement |
|-------------|---------------------------------|-------------------|-------------------------|----------------|-------------- |-------------------------|-------------------------------|
| E-001       | [what this evidence shows]      | [type]            | [where it came from]    | [YYYY-MM-DD]   | [person]      | [path, URL, or system]  | [control ID or requirement]   |
| E-002       | [what this evidence shows]      | [type]            | [where it came from]    | [YYYY-MM-DD]   | [person]      | [path, URL, or system]  | [control ID or requirement]   |
| E-003       | [what this evidence shows]      | [type]            | [where it came from]    | [YYYY-MM-DD]   | [person]      | [path, URL, or system]  | [control ID or requirement]   |

## Type Reference

*Use consistent type labels for filtering and reporting.*

- **Screenshot** -- visual capture of a UI, dashboard, or configuration screen
- **Log** -- system log, audit log, or access log extract
- **Config** -- configuration file, environment settings, or policy document
- **Test result** -- test execution report, coverage summary, or scan output
- **Approval** -- sign-off record, review comment, or approval email
- **Report** -- generated report from a tool (security scan, performance test, etc.)
- **Other** -- any evidence that does not fit the above categories

## Collection Guidelines

*Follow these practices when gathering evidence.*

- Capture evidence at the time of the activity, not retroactively when possible.
- Include enough context to understand the evidence without additional explanation (timestamps, environment, user).
- Redact any secrets, credentials, or personally identifiable information before storing.
- Store evidence in a durable, access-controlled location referenced in the Storage Location column.
- Link each piece of evidence to the specific control, requirement, or decision it supports.

## Definition of Done

- [ ] All required evidence collected and catalogued in the register
- [ ] Each entry has a valid storage location that is accessible to reviewers
- [ ] Sensitive data redacted from all artifacts
- [ ] Evidence linked to corresponding controls or requirements
- [ ] Register reviewed by compliance or audit lead
