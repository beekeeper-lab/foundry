# Compliance / Risk Analyst -- Outputs

This document enumerates every artifact the Compliance / Risk Analyst is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Control Mapping Document

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Control Mapping Document                           |
| **Cadence**        | One per regulatory framework; updated as controls change |
| **Template**       | `personas/compliance-risk/templates/control-mapping.md` |
| **Format**         | Markdown                                           |

**Description.** A traceability matrix that links each regulatory requirement to
the specific control that addresses it, the technical implementation of that
control, and the evidence that proves it is operating effectively. The control
mapping is the backbone of compliance -- it answers the auditor's fundamental
question: "Show me how you meet this requirement."

**Quality Bar:**
- Every applicable requirement from the in-scope framework is listed, with its
  official identifier (e.g., SOC 2 CC6.1, GDPR Article 32(1)(a)).
- Each requirement maps to at least one control. If no control exists, the row
  is marked as a gap with a remediation reference.
- Controls reference specific implementations: "Role-based access enforced in
  API gateway via `auth-policy.yaml`" not "access controls exist."
- Evidence locations are concrete and navigable: file paths, URLs, or system
  names -- not "available upon request."
- The mapping distinguishes between controls that are implemented, partially
  implemented, and planned.
- The document is version-controlled with a change log noting what changed and
  when.

**Downstream Consumers:** Security Engineer (for control implementation
verification), Architect (for design constraints), Team Lead (for compliance
status reporting), external auditors (for audit evidence).

---

## 2. Risk Register

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Risk Register                                      |
| **Cadence**        | Created at project start; reviewed and updated per cycle |
| **Template**       | `personas/compliance-risk/templates/risk-register.md` |
| **Format**         | Markdown                                           |

**Description.** A living inventory of identified risks to the project, rated by
likelihood and impact, with assigned owners and tracked mitigation status. The
risk register transforms vague concerns into structured, prioritized items that
the team can act on and stakeholders can accept or escalate.

**Quality Bar:**
- Each risk has a unique identifier, a concise title, and a description that
  explains the threat scenario in concrete terms.
- Likelihood is rated on a defined scale (e.g., Rare / Unlikely / Possible /
  Likely / Almost Certain) with documented rationale for the rating.
- Impact is rated on a defined scale (e.g., Negligible / Minor / Moderate /
  Major / Severe) with rationale tied to business consequences.
- Every risk has an assigned owner -- a specific persona or role, not "the
  team."
- Mitigation status is one of: Open, In Progress, Mitigated, Accepted, or
  Transferred, with the date of last status change.
- Accepted risks include a documented acceptance decision with the name of the
  stakeholder who accepted and an expiration date for re-evaluation.
- The register is sorted or filterable by risk score (likelihood x impact) so
  the highest risks are immediately visible.

**Downstream Consumers:** Team Lead (for prioritization and resource allocation),
Architect (for design risk awareness), Security Engineer (for security-related
risks), stakeholders (for risk acceptance decisions).

---

## 3. Evidence Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Evidence Plan                                      |
| **Cadence**        | One per audit cycle or regulatory engagement       |
| **Template**       | `personas/compliance-risk/templates/evidence-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A structured plan that defines what evidence must be collected
for each control, who is responsible for producing it, where it will be stored,
and when it must be refreshed. The evidence plan ensures that audit readiness is
a continuous process, not a last-minute scramble.

**Quality Bar:**
- Every control in the control mapping has a corresponding evidence entry in
  the plan.
- Each entry specifies the evidence type: configuration file, log export,
  screenshot, test result, signed approval, or access review report.
- Collection responsibility is assigned to a specific persona or role, not left
  unassigned.
- Storage location is specified: repository path, document management system, or
  audit evidence folder.
- Refresh cadence is defined for each evidence item: one-time, quarterly,
  annually, or on-change.
- The plan identifies evidence that does not yet exist and includes a task
  reference or deadline for producing it.
- Evidence naming conventions are standardized so auditors can locate items
  without assistance.

**Downstream Consumers:** DevOps / Release Engineer (for infrastructure
evidence), Developer (for code-level evidence), Security Engineer (for security
control evidence), external auditors (for evidence retrieval).

---

## 4. Policy / Procedure Document

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Policy / Procedure Document                        |
| **Cadence**        | As needed for new controls or regulatory requirements |
| **Template**       | `personas/compliance-risk/templates/policy-procedure.md` |
| **Format**         | Markdown                                           |

**Description.** A formal document that defines an organizational policy or
operational procedure required by a regulatory framework. Policies state what
must be done; procedures state how to do it. These documents translate regulatory
obligations into executable instructions that team members can follow.

**Quality Bar:**
- The document clearly identifies the regulatory requirement(s) it satisfies,
  with official identifiers.
- Policies are stated as declarative rules: "All production access requires
  multi-factor authentication" not "We should consider MFA."
- Procedures include numbered steps that are specific enough for a new team
  member to execute without additional guidance.
- Roles and responsibilities are explicitly assigned for each procedure step.
- The document includes an effective date, a review schedule, and a version
  history.
- Exception handling is documented: what to do when the standard procedure
  cannot be followed, and who must approve the exception.
- The document is reviewed and approved by at least one stakeholder with
  authority over the policy area.

**Downstream Consumers:** Developer (for implementation procedures), DevOps /
Release Engineer (for operational procedures), Security Engineer (for security
policies), Team Lead (for enforcement and compliance tracking).

---

## 5. Compliance Gap Analysis

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Compliance Gap Analysis                            |
| **Cadence**        | At project start; updated when scope or regulations change |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** An assessment that compares the project's current compliance
posture against the requirements of applicable regulatory frameworks. The gap
analysis identifies where controls are missing, insufficient, or untested, and
provides a prioritized remediation roadmap.

**Required Sections:**
1. **Scope** -- Regulatory frameworks assessed, components in scope, and data
   classifications covered.
2. **Current State Summary** -- High-level overview of existing controls and
   compliance maturity.
3. **Gap Inventory** -- Each gap with: the unmet requirement (with official
   identifier), the current state, the desired state, and the severity
   (Critical / High / Medium / Low).
4. **Remediation Roadmap** -- Prioritized list of remediation actions with
   owners, effort estimates, and target completion dates.
5. **Dependencies** -- External dependencies that block remediation (e.g.,
   infrastructure provisioning, vendor contracts, stakeholder approvals).
6. **Residual Risk** -- Gaps that cannot be fully closed within the current
   scope, with risk acceptance recommendations.

**Quality Bar:**
- Every gap references a specific regulatory requirement, not a vague compliance
  area.
- Severity ratings are justified: Critical means "audit failure or regulatory
  penalty if unaddressed," not "important to fix."
- Remediation actions are concrete: "Implement automated access review using
  tool X, assign to Security Engineer, target March 15" not "address access
  review gap."
- The analysis covers all in-scope frameworks, not just the most familiar one.
- Residual risks include a recommended risk acceptance owner and an expiration
  date for reassessment.

**Downstream Consumers:** Team Lead (for roadmap planning), Architect (for
design changes required by gaps), Security Engineer (for security control
gaps), stakeholders (for risk acceptance and resource allocation).

---

## 6. Audit Notes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Audit Notes                                        |
| **Cadence**        | During and immediately after each audit engagement |
| **Template**       | `personas/compliance-risk/templates/audit-notes.md` |
| **Format**         | Markdown                                           |

**Description.** A record of observations, questions, findings, and action items
captured during an audit or compliance review engagement. Audit notes serve as
the team's working memory during the audit and as a reference for tracking
remediation of any findings afterward.

**Quality Bar:**
- Each note is timestamped and attributed to the audit session or auditor
  interaction where it was captured.
- Auditor questions are recorded verbatim or paraphrased with enough fidelity
  to reconstruct the intent.
- Findings are categorized by severity and mapped back to the relevant control
  in the control mapping.
- Action items include an owner, a deadline, and a clear description of what
  must be delivered.
- The notes distinguish between formal findings (will appear in the audit
  report) and informal observations (auditor suggestions that are not
  findings).
- Follow-up commitments made to the auditor are tracked to completion.

**Downstream Consumers:** Team Lead (for action item tracking), Security
Engineer (for security-related findings), Developer (for code-related
remediation), stakeholders (for audit outcome awareness).

---

## Output Format Guidelines

- All deliverables are written in Markdown and stored in the project repository
  under `docs/compliance/` or a dedicated compliance evidence folder.
- Control mappings and risk registers are living documents -- they are updated
  in place with version history, not replaced with new files each cycle.
- Evidence plans reference specific storage locations so that evidence can be
  retrieved without the Compliance / Risk Analyst's assistance.
- Policy documents use a formal tone appropriate for external audit consumption.
  Internal working documents (gap analyses, audit notes) may use a more
  concise operational tone.
- Regulatory requirement identifiers (e.g., SOC 2 CC6.1, GDPR Art. 32) are
  used consistently across all documents. Define abbreviations once in the
  control mapping and reference them everywhere else.
- Audit notes are treated as confidential working documents and are not shared
  outside the project team without explicit approval.
