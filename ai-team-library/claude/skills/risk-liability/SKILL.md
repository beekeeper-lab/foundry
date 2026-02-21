# Skill: Risk Assessment & Liability Analysis

## Description

Performs a structured legal risk assessment and liability analysis for a software
project, evaluating legal exposure across six domains: contractual liability,
indemnification obligations, limitation of liability provisions, insurance
requirements, incident response legal obligations, and breach notification duties.
The skill reads project context, contracts, and regulatory landscape to produce
a comprehensive risk-liability report with scored risks, mitigation strategies,
and actionable recommendations. This is a core analytical tool for the Legal
Counsel persona, complementing the existing legal risk assessment template with
a process-driven, repeatable methodology.

## Trigger

- Invoked by the `/risk-liability` slash command.
- Called by the Legal Counsel persona during project onboarding or when the
  risk landscape changes (new contracts, new jurisdictions, regulatory updates).
- Should be re-run when contracts are signed, renewed, or materially amended.
- Should be re-run after a security incident or data breach.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| project_context | File path | Yes | `ai/context/project.md` or equivalent project brief with business context, data types, and target jurisdictions |
| contracts | File list | No | Paths to contracts, service agreements, or vendor terms under review |
| architecture_doc | File path | No | Architecture spec or design doc describing system components and data flows |
| regulatory_scope | String | No | Comma-separated list of applicable regulations (e.g., "GDPR, CCPA, HIPAA") |
| existing_assessment | File path | No | Previous risk-liability assessment to update incrementally |
| insurance_policies | File list | No | Paths to current insurance policy summaries (cyber liability, E&O, general liability) |

## Process

1. **Establish assessment scope** -- Parse the project context to identify the
   business domain, data types processed (PII, PHI, financial, etc.), target
   jurisdictions, and contractual relationships. Define the boundaries of the
   assessment.

2. **Evaluate legal exposure** -- Analyze the project's legal exposure across
   each category:
   - What data is collected, processed, stored, or transmitted?
   - What contractual obligations govern data handling?
   - What regulatory regimes apply based on jurisdiction and data types?
   - What third-party dependencies create legal exposure?

3. **Analyze indemnification clauses** -- For each contract in scope, identify
   and evaluate indemnification provisions:
   - Scope of indemnification (IP infringement, data breach, negligence, willful misconduct)
   - Direction (mutual vs. one-way)
   - Caps and carve-outs
   - Trigger conditions and notice requirements
   - Defense and settlement control
   - Survival provisions post-termination

4. **Assess limitation of liability** -- For each contract in scope, evaluate
   liability limitation provisions:
   - Cap amounts (fixed, fee-based, or uncapped)
   - Exclusion of consequential, incidental, and indirect damages
   - Carve-outs from liability caps (IP indemnity, confidentiality breach, willful misconduct)
   - Aggregate vs. per-incident caps
   - Whether caps are mutual or asymmetric
   - Super-cap provisions for data breach or security incidents

5. **Determine insurance requirements** -- Assess insurance adequacy:
   - Required insurance types (cyber liability, E&O, general liability, umbrella)
   - Minimum coverage amounts required by contracts
   - Gap analysis between contractual requirements and current coverage
   - First-party vs. third-party coverage assessment
   - Sub-limits and exclusions relevant to the project's risk profile
   - Certificate of insurance obligations

6. **Map incident response legal obligations** -- Document legal obligations
   triggered by a security incident or data breach:
   - Contractual notification obligations (timing, recipients, content)
   - Regulatory notification requirements by jurisdiction
   - Forensic investigation and evidence preservation duties
   - Cooperation obligations with affected parties
   - Remediation and credit monitoring obligations
   - Legal privilege considerations for incident response
   - Documentation and record-keeping requirements

7. **Analyze breach notification duties** -- For each applicable jurisdiction
   and regulation, document:
   - Definition of "breach" or "security incident" triggering notification
   - Notification timing requirements (e.g., 72 hours under GDPR Art. 33)
   - Required notification recipients (supervisory authority, data subjects, business partners)
   - Required notification content
   - Exceptions and safe harbors (encryption, de-identification)
   - Penalties for non-compliance or delayed notification
   - Cross-border notification coordination requirements

8. **Score and prioritize risks** -- For each identified risk, assign
   probability (1-5) and impact (1-5) ratings with documented rationale.
   Calculate risk score (P x I). Classify as Low (1-5), Medium (6-12),
   High (13-19), or Critical (20-25).

9. **Develop mitigation strategies** -- For each Medium+ risk, propose specific
   mitigation actions:
   - Contract negotiation points (specific alternative language)
   - Insurance procurement or adjustment recommendations
   - Process and procedure implementations
   - Technical controls with legal significance
   - Policy development requirements

10. **Produce the risk-liability report** -- Write the complete assessment
    following the Legal Counsel's risk assessment template structure, with
    additional sections for indemnification analysis, liability caps,
    insurance adequacy, incident response obligations, and breach
    notification duties.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| risk_liability_report | Markdown file | Complete risk assessment covering all six analysis domains with scored risks and mitigations |
| indemnification_matrix | Section in report | Comparative analysis of indemnification provisions across all contracts in scope |
| liability_cap_summary | Section in report | Summary of liability limitations across contracts with gap analysis |
| insurance_gap_analysis | Section in report | Coverage adequacy assessment against contractual and operational requirements |
| incident_response_playbook | Section in report | Legal obligations checklist triggered by security incidents, organized by timeline |
| breach_notification_matrix | Section in report | Jurisdiction-by-jurisdiction notification requirements with timelines and recipients |
| priority_actions | Section in report | Ranked mitigation actions by risk severity and urgency |

## Quality Criteria

- Every risk references a specific legal basis: statute, regulation, contract
  clause, or established legal principle.
- Indemnification analysis covers scope, direction, caps, carve-outs, triggers,
  and survival for each contract -- not just "indemnification exists."
- Limitation of liability analysis distinguishes between direct damage caps,
  consequential damage exclusions, and carve-outs -- not just "liability is
  capped at $X."
- Insurance requirements are traced to specific contractual provisions or
  regulatory mandates, with gap analysis against current coverage.
- Incident response obligations include specific timelines, not vague
  references to "prompt notification."
- Breach notification duties cite the specific statutory provision and its
  requirements (timing, recipients, content, exceptions).
- Probability and impact ratings include documented rationale, not arbitrary
  labels.
- Mitigation strategies are actionable: they specify contract language changes,
  insurance coverage amounts, or process steps -- not "reduce risk."
- The assessment distinguishes between legal requirements (compliance is
  mandatory), legal risks (exposure is manageable), and best practices
  (proactive posture improvement).
- Cross-references between domains are explicit: e.g., if a liability cap
  carve-out for data breach affects the insurance adequacy analysis, this
  connection is documented.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoProjectContext` | No project context file provided or found | Create a project context document with business domain, data types, and jurisdictions |
| `NoJurisdiction` | Project context does not specify target jurisdictions | Add jurisdiction information to the project context; breach notification analysis requires specific jurisdictions |
| `NoContracts` | No contracts provided for contractual risk analysis | Provide contracts for review or note that contractual analysis is out of scope for this assessment |
| `IncompleteRegScope` | Regulatory scope specified but missing key regulations for the jurisdiction/data type combination | Review applicable regulations for the project's jurisdictions and data types |
| `StaleAssessment` | Existing assessment references contracts or regulations that have been superseded | Obtain current versions of contracts and verify regulatory citations before updating |

## Dependencies

- Project context document with business domain, data types, and jurisdictions
- Legal Counsel persona's legal risk assessment template (`personas/legal-counsel/templates/legal-risk-assessment.md`)
- Contract review outputs from the Legal Counsel persona (if contracts have been previously reviewed)
- Architecture documentation from the Architect persona (for data flow and technical risk context)
- Compliance / Risk Analyst outputs (for regulatory landscape mapping)
- Applicable regulatory texts for breach notification analysis
