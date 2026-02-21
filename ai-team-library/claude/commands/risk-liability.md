# /risk-liability Command

Claude Code slash command that performs a risk assessment and liability analysis for a software project.

## Purpose

Systematically evaluate legal exposure across six domains: contractual liability, indemnification obligations, limitation of liability provisions, insurance requirements, incident response legal obligations, and breach notification duties. Produces a scored risk register with mitigation strategies and actionable recommendations. Essential for any project handling regulated data, operating under vendor contracts, or deploying across multiple jurisdictions.

## Usage

```
/risk-liability <project-context> [--contracts <paths>] [--regulations <list>] [--update <existing>]
```

- `project-context` -- Path to the project context or brief describing business domain, data types, and jurisdictions.

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| Project context | Positional argument | Yes |
| Contracts | `--contracts` flag (comma-separated paths) | No |
| Architecture doc | `--architecture` flag | No |
| Regulatory scope | `--regulations` flag (comma-separated) | No |
| Insurance policies | `--insurance` flag (comma-separated paths) | No |
| Existing assessment | `--update` flag | No |

## Process

1. **Establish scope** -- Parse project context for business domain, data types, jurisdictions, and contractual relationships.
2. **Evaluate legal exposure** -- Analyze data handling, contractual obligations, regulatory applicability, and third-party dependencies.
3. **Analyze indemnification** -- Review indemnification provisions across contracts for scope, direction, caps, and triggers.
4. **Assess liability limits** -- Evaluate limitation of liability clauses for caps, exclusions, carve-outs, and symmetry.
5. **Review insurance** -- Assess insurance adequacy against contractual requirements and operational risk profile.
6. **Map incident response** -- Document legal obligations triggered by security incidents with timelines.
7. **Analyze breach notification** -- Map jurisdiction-specific notification requirements with timing, recipients, and content.
8. **Score and prioritize** -- Rate each risk by probability and impact; classify and rank by severity.
9. **Develop mitigations** -- Propose specific actions for each Medium+ risk.
10. **Write output** -- Save the complete risk-liability report.

## Output

| Artifact | Path | Description |
|----------|------|-------------|
| Risk-liability report | `ai/outputs/legal-counsel/risk-liability-report.md` | Complete assessment with scored risks across all six domains |

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--contracts <paths>` | None | Comma-separated paths to contracts and agreements for review |
| `--architecture <path>` | None | Path to architecture doc for data flow and technical context |
| `--regulations <list>` | Auto-detected | Comma-separated regulatory identifiers (e.g., "GDPR,CCPA,HIPAA") |
| `--insurance <paths>` | None | Comma-separated paths to insurance policy summaries |
| `--update <path>` | None | Update an existing risk-liability assessment incrementally |
| `--output <dir>` | `ai/outputs/legal-counsel/` | Override the output directory |
| `--severity <level>` | `medium` | Only include risks at or above this severity in priority actions |

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoProjectContext` | File not found | Provide a valid path to a project context document |
| `NoJurisdiction` | Project context missing jurisdiction info | Add target jurisdictions to the project context |
| `NoContracts` | No contracts provided | Provide contract paths via `--contracts` or note contractual analysis is out of scope |
| `StaleAssessment` | Existing assessment references superseded contracts | Obtain current contract versions before updating |

## Examples

**Full assessment with contracts:**
```
/risk-liability ai/context/project.md --contracts "contracts/vendor-a.md,contracts/saas-agreement.md"
```
Analyzes the project's legal exposure and reviews the specified contracts for indemnification, liability, and insurance provisions.

**Regulatory-focused assessment:**
```
/risk-liability ai/context/project.md --regulations "GDPR,HIPAA"
```
Focuses on breach notification duties and incident response obligations under GDPR and HIPAA.

**Update existing assessment:**
```
/risk-liability ai/context/project.md --update ai/outputs/legal-counsel/risk-liability-report.md --contracts "contracts/new-vendor.md"
```
Incrementally updates the existing risk-liability report with analysis of a new vendor contract.

**Scoped assessment with insurance review:**
```
/risk-liability ai/context/project.md --contracts "contracts/enterprise-client.md" --insurance "insurance/cyber-policy.md,insurance/eo-policy.md"
```
Assesses contractual liability and compares insurance coverage against contractual requirements.
