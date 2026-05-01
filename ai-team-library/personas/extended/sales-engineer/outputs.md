# Sales Engineer -- Outputs

This document enumerates every artifact the Sales Engineer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Technical Demo Script & Environment

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technical Demonstration Package                    |
| **Cadence**        | Per opportunity or prospect engagement             |
| **Template**       | `demo-script.md`                                   |
| **Format**         | Markdown script + configured demo environment      |

**Description.** A tailored demonstration script and pre-configured environment
that showcases product capabilities mapped to the prospect's specific
requirements. Includes talking points, transition cues, objection-handling
notes, and a reliable environment that reproduces the demo flow consistently.

**Quality Bar:**
- Demo script maps each section to a stated customer requirement.
- Environment setup is documented and reproducible by any team member.
- All demo flows have been rehearsed with no errors or workarounds.
- Talking points lead with business outcomes, not feature names.
- Fallback paths are documented for known fragile points.
- No internal credentials, test data with PII, or production connections.

**Downstream Consumers:** Account Executive (for meeting coordination),
Tech-QA (for environment validation), Product Management (for feature
feedback).

---

## 2. Proof-of-Concept Build

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | POC Package (environment + results report)         |
| **Cadence**        | Per qualified opportunity requiring evaluation     |
| **Template**       | `poc-plan.md`                                      |
| **Format**         | Markdown plan + working environment + results doc  |

**Description.** A scoped proof-of-concept implementation that allows the
prospect to evaluate the product against their specific use case. Includes
a POC plan with success criteria, a working environment, and a results
document summarizing outcomes against the agreed criteria.

**Quality Bar:**
- Success criteria are defined and agreed upon before POC begins.
- Timeline and scope boundaries are documented and communicated.
- Environment is isolated, repeatable, and can be rebuilt from documentation.
- Results are measured against pre-defined criteria with supporting evidence.
- Product gaps discovered during POC are documented in the gap report.
- Customer data handling follows security and privacy policies.
- Exit criteria and decision framework are stated upfront.

**Downstream Consumers:** Account Executive (for deal progression),
Architect (for integration patterns), Product Management (for gap feedback),
Customer Success (for implementation handoff).

---

## 3. RFP/RFI Response Document

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technical Response Document                        |
| **Cadence**        | Per RFP/RFI/RFQ received                          |
| **Template**       | `rfp-response.md`                                  |
| **Format**         | Markdown or customer-specified format              |

**Description.** Technical sections of formal response documents addressing
the prospect's requirements, questions, and evaluation criteria. Each
response directly answers the question asked with accurate, verifiable
technical detail.

**Quality Bar:**
- Every question receives a direct, specific answer -- no generic filler.
- Technical claims are verified against current product capabilities.
- Gaps are disclosed honestly with workaround descriptions where available.
- Compliance and certification claims are verified with Security/Legal.
- Response follows the customer's required format and numbering.
- All responses are reviewed by a subject matter expert before submission.
- Version-controlled with clear change tracking between drafts.

**Downstream Consumers:** Account Executive (for submission), Legal Counsel
(for contractual review), Security Engineer (for compliance validation).

---

## 4. Competitive Analysis & Battlecard

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Competitive Analysis Report or Battlecard          |
| **Cadence**        | Per competitor encounter or quarterly refresh      |
| **Template**       | `competitive-analysis.md`                          |
| **Format**         | Markdown                                           |

**Description.** Factual comparison of the product against specific
competitors, including feature-by-feature analysis, differentiation
strategies, common objections with responses, and win/loss pattern
analysis. Battlecards provide quick-reference competitive positioning
for use during active engagements.

**Quality Bar:**
- All competitive claims are factual and cite verifiable sources.
- Feature comparisons reference specific versions and release dates.
- Differentiation points are framed as customer benefits, not abstract advantages.
- Common objections include tested, effective responses.
- Analysis is current -- reviewed within the last quarter.
- No FUD, unverifiable claims, or disparaging language.
- Win/loss patterns include sample size and confidence level.

**Downstream Consumers:** Account Executive (for positioning), Product
Management (for competitive strategy), Marketing (for messaging alignment).

---

## 5. Technical Win Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technical Win Plan                                 |
| **Cadence**        | Per qualified opportunity                          |
| **Template**       | `technical-win-plan.md`                            |
| **Format**         | Markdown                                           |

**Description.** A strategy document defining the technical win criteria for
a specific opportunity, including success metrics, risk assessment,
competitive positioning, and an execution plan. The win plan aligns the
account team on what "winning technically" looks like and how to get there.

**Quality Bar:**
- Win criteria are specific, measurable, and tied to customer evaluation priorities.
- Risks are identified with likelihood, impact, and mitigation strategies.
- Competitive threats are assessed with planned counter-positioning.
- Key stakeholders and their technical priorities are mapped.
- Milestones and timeline align with the customer's evaluation process.
- Plan is reviewed and agreed upon by Account Executive and Sales leadership.

**Downstream Consumers:** Account Executive (for deal strategy), Sales
leadership (for pipeline review), Product Management (for strategic deals).

---

## 6. Customer-Facing Architecture Diagram

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Architecture Diagram and Integration Guide         |
| **Cadence**        | Per engagement requiring integration assessment    |
| **Template**       | `architecture-review.md`                           |
| **Format**         | Markdown with embedded diagrams                    |

**Description.** Architecture diagrams and integration guides that show how
the product fits into the customer's existing environment. Includes data
flow, integration points, authentication mechanisms, and deployment
topology tailored to the customer's infrastructure.

**Quality Bar:**
- Diagrams use standard notation understandable by the customer's team.
- Integration points specify protocols, authentication, and data formats.
- Customer's existing systems are accurately represented.
- Security boundaries and data flow directions are clearly marked.
- Assumptions and prerequisites are explicitly stated.
- No internal infrastructure details or proprietary architecture exposed.

**Downstream Consumers:** Architect (for integration validation), Security
Engineer (for security review), Customer Success (for implementation
planning).

---

## 7. Product Gap Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Product Gap Report                                 |
| **Cadence**        | Ongoing per engagement; consolidated monthly       |
| **Template**       | `gap-report.md`                                    |
| **Format**         | Markdown                                           |

**Description.** Documented product gaps surfaced during pre-sales
engagements, including customer context, business impact, workaround
availability, and frequency of occurrence across deals. Gap reports feed
the product roadmap and prevent over-promising on capabilities that do
not yet exist.

**Quality Bar:**
- Each gap is tied to a specific customer requirement with business context.
- Severity and deal impact are assessed (deal-blocker, nice-to-have, etc.).
- Available workarounds are documented with their limitations.
- Frequency across engagements is tracked to identify patterns.
- Gaps are de-duplicated against previously reported items.
- No customer-identifying information in shared gap reports (use deal IDs).

**Downstream Consumers:** Product Management (for roadmap input), Developer
(for implementation awareness), Account Executive (for customer
expectation setting).

---

## Output Format Guidelines

- All customer-facing artifacts are written as if the prospect's technical
  leadership is the audience. Avoid internal jargon and acronyms.
- Technical claims are precise and verifiable. State specific numbers,
  versions, and configurations rather than vague qualitative statements.
- Artifacts follow the stack-specific conventions document
  (`stacks/<stack>/conventions.md`) where applicable.
- All outputs are version-controlled. No deliverables live in personal
  folders or email threads only.
- Customer-specific materials are stored in the designated deal folder
  structure, never in shared/public repositories.
