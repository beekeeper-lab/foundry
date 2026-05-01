# Legal Counsel / Lawyer -- Outputs

This document enumerates every artifact the Legal Counsel is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Contract Review Memo

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Contract Review Memo                               |
| **Cadence**        | One per contract or agreement under review         |
| **Template**       | `personas/legal-counsel/templates/contract-review.md` |
| **Format**         | Markdown                                           |

**Description.** A structured analysis of a contract, service agreement, or vendor
terms that identifies key obligations, rights, restrictions, and risk areas. The
memo highlights clauses that create material legal exposure and provides
recommendations for modification, acceptance, or rejection. Each finding
references the specific contract section under review.

**Quality Bar:**
- Every material clause is identified with its section reference.
- Risk findings include the specific legal exposure created by the clause:
  "Section 8.2 indemnification is uncapped and covers third-party IP claims" not
  "indemnification clause is broad."
- Recommendations are specific: accept, reject, or propose alternative language.
- Obligations extracted from the contract are listed in a structured format with
  responsible parties and deadlines.
- The memo distinguishes between standard commercial terms and terms that deviate
  from market norms.
- Missing provisions that should be present (e.g., limitation of liability, data
  protection addendum) are flagged.

**Downstream Consumers:** Team Lead (for vendor decision-making), Architect (for
technical obligations in the agreement), Compliance / Risk Analyst (for
compliance-related obligations), stakeholders (for approval decisions).

---

## 2. IP & Licensing Analysis

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | IP & Licensing Analysis                            |
| **Cadence**        | At project start; updated when dependencies change |
| **Template**       | `personas/legal-counsel/templates/license-analysis.md` |
| **Format**         | Markdown                                           |

**Description.** An analysis of intellectual property and licensing considerations
for the project, covering open-source dependency licenses, proprietary license
terms, copyright ownership, and license compatibility. The analysis ensures the
project's licensing model is compatible with all third-party components and that
IP obligations are understood and met.

**Quality Bar:**
- Every third-party dependency is listed with its license identifier (SPDX where
  available).
- License compatibility is assessed against the project's outbound license.
  Conflicts are flagged with specific incompatibility references.
- Copyleft obligations (source disclosure, derivative work provisions) are
  documented for each applicable license.
- Attribution requirements are compiled into a single actionable list.
- Proprietary license restrictions (field-of-use, redistribution, modification)
  are documented.
- The analysis distinguishes between permissive, weak copyleft, and strong
  copyleft licenses and their implications.

**Downstream Consumers:** Developer (for license compliance in dependency
selection), Architect (for design constraints from licensing), DevOps / Release
Engineer (for attribution and notice file generation), Team Lead (for dependency
approval decisions).

---

## 3. Legal Risk Assessment

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Legal Risk Assessment                              |
| **Cadence**        | At project start; updated when risk landscape changes |
| **Template**       | `personas/legal-counsel/templates/legal-risk-assessment.md` |
| **Format**         | Markdown                                           |

**Description.** A structured assessment of legal risks facing the project,
covering contractual, regulatory, IP, data protection, and operational legal
exposures. Each risk is documented with its legal basis, probability, impact,
current mitigation, and recommended actions. The assessment enables stakeholders
to make informed risk acceptance decisions.

**Quality Bar:**
- Each risk references a specific legal basis: statute, regulation, contract
  clause, or established legal principle.
- Probability and impact are assessed with documented rationale, not arbitrary
  labels.
- Current mitigations are described with an honest assessment of their
  effectiveness.
- Recommendations are actionable and prioritized by risk severity.
- The assessment distinguishes between legal requirements (compliance is
  mandatory), legal risks (exposure exists but is manageable), and legal
  opportunities (proactive measures that improve posture).
- Residual risk after mitigation is documented for each item.

**Downstream Consumers:** Team Lead (for prioritization), Compliance / Risk
Analyst (for risk register integration), Architect (for design risk awareness),
stakeholders (for risk acceptance decisions).

---

## 4. Legal Document Draft

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Legal Document Draft                               |
| **Cadence**        | As needed for project legal requirements           |
| **Template**       | `personas/legal-counsel/templates/legal-document.md` |
| **Format**         | Markdown                                           |

**Description.** A drafted or reviewed legal document required by the project,
such as terms of service, privacy policy, data processing agreement, acceptable
use policy, or license header. The document is written in enforceable legal
language appropriate to the target jurisdiction while remaining as clear as
possible for non-legal readers.

**Quality Bar:**
- The document identifies the governing jurisdiction and applicable law.
- Definitions are clear and used consistently throughout.
- Obligations and rights are stated in specific, enforceable language.
- The document addresses all required topics for its type (e.g., a privacy
  policy covers all required disclosures under applicable law).
- Version history and effective date are included.
- The document has been reviewed against applicable regulatory requirements.
- Plain-language summaries are provided where the audience includes non-legal
  readers.

**Downstream Consumers:** Stakeholders (for approval), Technical Writer (for
user-facing presentation), Developer (for in-product legal content integration),
Compliance / Risk Analyst (for regulatory alignment verification).

---

## 5. Regulatory Interpretation Memo

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Regulatory Interpretation Memo                     |
| **Cadence**        | As needed when regulatory questions arise          |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A legal analysis that interprets a specific regulation, statute,
or legal requirement in the context of the project. The memo explains what the
law requires, how it applies to the project's specific circumstances, and what
the team must do to comply. This bridges the gap between raw regulatory text and
the actionable guidance the Compliance / Risk Analyst needs for control mapping.

**Required Sections:**
1. **Question Presented** -- The specific legal question being analyzed.
2. **Applicable Law** -- The statutes, regulations, or legal authorities that
   govern the question, with citations.
3. **Analysis** -- How the law applies to the project's specific facts and
   circumstances.
4. **Conclusion** -- The legal interpretation and its practical implications.
5. **Recommended Actions** -- Specific steps the team should take based on the
   analysis.
6. **Limitations** -- Jurisdictional scope, areas of legal uncertainty, and
   conditions that could change the analysis.

**Quality Bar:**
- The question presented is specific enough to produce a useful answer.
- Legal authorities are cited with sufficient specificity (article, section,
  subsection).
- The analysis applies the law to the project's facts, not generic hypotheticals.
- The conclusion is clear and unambiguous where the law permits.
- Where the law is unsettled, the memo identifies the uncertainty and recommends
  a conservative approach.
- Recommended actions are concrete and assignable.

**Downstream Consumers:** Compliance / Risk Analyst (for control mapping and gap
analysis), Architect (for design decisions with legal implications), Team Lead
(for planning), stakeholders (for strategic decisions).

---

## 6. License Compliance Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | License Compliance Report                          |
| **Cadence**        | Per release or when dependency changes are significant |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A report documenting the project's compliance with all
applicable open-source and proprietary license obligations. The report
inventories all third-party components, their licenses, the obligations arising
from each license, and the project's compliance status for each obligation.

**Required Sections:**
1. **Dependency Inventory** -- All third-party components with license
   identifiers, versions, and usage context (linked, bundled, modified, SaaS).
2. **License Obligation Summary** -- For each license type in use, the
   obligations it imposes (attribution, source disclosure, derivative work
   provisions, patent grants).
3. **Compliance Status** -- For each obligation, whether it is met, partially
   met, or unmet, with evidence of compliance.
4. **Action Items** -- Required actions to achieve or maintain full compliance.
5. **Compatibility Matrix** -- Confirmation that all dependency licenses are
   compatible with the project's outbound license.

**Quality Bar:**
- Every dependency is accounted for, including transitive dependencies.
- License identifiers use SPDX notation where available.
- Obligations are traced to specific license text, not assumptions.
- Compliance evidence is concrete: attribution file locations, source
  availability mechanisms, notice files.
- Incompatibilities are flagged with remediation options (replace dependency,
  change project license, obtain commercial license).

**Downstream Consumers:** Developer (for dependency management), DevOps /
Release Engineer (for release compliance), Team Lead (for dependency approval),
stakeholders (for legal risk awareness).

---

## Output Format Guidelines

- All deliverables are written in Markdown and stored in the project repository
  under `docs/legal/` or a dedicated legal documentation folder.
- Contract review memos and legal opinions are treated as confidential by default
  and should be stored with appropriate access controls.
- Legal documents intended for external use (terms of service, privacy policies)
  should be reviewed by stakeholders before publication.
- Regulatory interpretation memos reference specific legal provisions using
  standard citation formats.
- License analysis uses SPDX license identifiers for consistency and
  machine-readability.
- All legal deliverables include a date, author, and scope limitation to ensure
  the advice is not applied beyond its intended context.
- Legal risk assessments use consistent severity scales aligned with the project's
  risk register format used by the Compliance / Risk Analyst.
