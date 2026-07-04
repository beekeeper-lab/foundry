---
name: contract-review
description: "- Invoked by the /contract-review slash command. - Called by the Legal Counsel persona when a new contract or renewal is under consideration. - Should be re-run when contract amendments or addenda are proposed."
---

# Skill: Contract Review

## Description

Performs a structured review of software contracts, SLAs, vendor agreements,
and Master Service Agreements (MSAs). The skill systematically analyzes each
clause for risk exposure, identifies unfavorable terms, evaluates liability
caps and indemnification provisions, flags auto-renewal traps and termination
restrictions, and produces a redline-ready report with recommended changes.
This is the Legal Counsel persona's primary contract analysis tool.

## Trigger

- Invoked by the `/contract-review` slash command.
- Called by the Legal Counsel persona when a new contract or renewal is under consideration.
- Should be re-run when contract amendments or addenda are proposed.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| contract_doc | File path or text | Yes | The contract, SLA, MSA, or vendor agreement to review |
| contract_type | String | No | Type of agreement: `msa`, `sla`, `sow`, `nda`, `license`, `vendor`, `saas`; auto-detected if not provided |
| party_role | String | No | Whether the client is the `buyer` or `seller`/`provider`; defaults to `buyer` |
| risk_tolerance | String | No | Risk posture: `conservative`, `moderate`, `aggressive`; defaults to `moderate` |
| comparison_doc | File path | No | A preferred-terms template or previous contract version for delta comparison |
| jurisdiction | String | No | Governing law jurisdiction for jurisdiction-specific analysis (e.g., "Delaware", "England and Wales") |

## Process

### Phase 1: Contract Parsing and Classification

1. **Identify contract type** -- Classify the agreement (MSA, SLA, SOW, NDA, license agreement, SaaS subscription, vendor agreement) and determine the applicable review framework.
2. **Extract parties and roles** -- Identify the contracting parties, determine which party the review is being conducted for, and establish the power dynamic (enterprise vs. startup, buyer vs. seller).
3. **Map contract structure** -- Build an outline of all sections, schedules, exhibits, and annexes. Identify cross-references between clauses.

### Phase 2: Clause-by-Clause Analysis

4. **Review liability and indemnification** -- Analyze liability caps (per-incident, aggregate, and exclusions), indemnification obligations (mutual vs. one-sided, carve-outs), and consequential damages waivers. Flag uncapped liability, one-sided indemnification, or missing liability floors.
5. **Review termination and exit** -- Evaluate termination for convenience vs. cause provisions, notice periods, cure periods, transition assistance obligations, and data return/destruction clauses. Flag lock-in mechanisms, excessive notice periods, or missing transition rights.
6. **Review renewal and pricing** -- Analyze auto-renewal mechanisms, price escalation clauses, benchmark rights, and volume commitment traps. Flag silent auto-renewals, uncapped price increases, and minimum commitment penalties.
7. **Review SLA and performance** -- Evaluate uptime commitments, response time guarantees, measurement methodology, service credit calculations, and termination triggers for chronic underperformance. Flag SLAs measured over excessively long periods, credits capped too low, or missing termination rights for repeated failures.
8. **Review data and IP provisions** -- Analyze data ownership, data processing terms, data portability, data breach notification, intellectual property assignment vs. license, and work-product ownership. Flag broad IP assignments, missing data portability, or inadequate breach notification timelines.
9. **Review warranty and representations** -- Evaluate warranty scope, warranty disclaimers, representation accuracy, and remedy limitations. Flag excessive warranty disclaimers or remedies limited to "re-performance only."
10. **Review confidentiality** -- Analyze confidentiality obligations (mutual vs. one-sided), duration, exceptions, and compelled disclosure procedures. Flag perpetual confidentiality obligations or missing standard exceptions.
11. **Review dispute resolution** -- Evaluate governing law, dispute resolution mechanism (litigation vs. arbitration vs. mediation), venue selection, jury waiver, and class action waiver. Flag unfavorable venue selection or mandatory binding arbitration without appeal rights.
12. **Review force majeure and risk allocation** -- Analyze force majeure definitions, notice requirements, mitigation obligations, and termination rights during extended force majeure. Flag overly broad or overly narrow definitions.
13. **Review assignment and change of control** -- Evaluate assignment restrictions, change-of-control triggers, and consent requirements. Flag provisions that allow counterparty assignment without consent while restricting your own.

### Phase 3: Risk Assessment and Redlining

14. **Rate each finding** -- Assign risk level (Critical/High/Medium/Low) based on financial exposure, operational impact, and likelihood of the clause being invoked. Calibrate to the stated risk tolerance.
15. **Generate redline recommendations** -- For each Medium+ finding, draft specific alternative language that rebalances the clause. Provide both the ideal position and a fallback compromise position.
16. **Identify missing clauses** -- Flag standard protective clauses that are absent from the contract (e.g., missing limitation of liability, no data breach notification, no transition assistance).
17. **Produce the contract review report** -- Write the complete analysis following the structured output format.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| contract_review | Markdown file | Complete clause-by-clause analysis with risk ratings and findings |
| redline_summary | Section in report | Recommended contract changes with proposed alternative language |
| risk_matrix | Section in report | Summary table of all findings rated by risk level and category |
| executive_summary | Section in report | High-level overview with critical/high finding count and negotiation priorities |
| missing_clauses | Section in report | Standard protective clauses absent from the contract |

## Quality Criteria

- Every material clause category (liability, termination, renewal, SLA, data/IP, warranty, confidentiality, dispute resolution, force majeure, assignment) is evaluated -- none are skipped.
- Every finding has a risk rating with stated rationale explaining the financial or operational exposure.
- Every Medium, High, or Critical finding includes specific redline language -- not vague advice like "negotiate better terms."
- Redline recommendations include both an ideal position and a fallback compromise, giving the negotiator flexibility.
- Missing clauses are identified with an explanation of why the clause matters and sample language to propose.
- The analysis accounts for the party's role (buyer vs. seller) and adjusts risk ratings accordingly -- a clause favorable to sellers is a risk for buyers and vice versa.
- The executive summary accurately reflects the overall risk posture and prioritizes the most impactful negotiation items.
- If a comparison document is provided, the report highlights material differences between the two versions.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoContractProvided` | No contract document or text supplied | Provide the contract to review as a file path or pasted text |
| `UnrecognizedFormat` | The document does not appear to be a contract or agreement | Verify the correct file was provided; the skill expects legal agreements, not general business documents |
| `IncompleteContract` | The contract is missing signature blocks, schedules, or referenced exhibits | Note which sections are missing in the report; request the complete document for a full review |
| `MultipleContracts` | The input contains multiple separate agreements | Split into individual contracts and review each separately, or specify which agreement to analyze |
| `JurisdictionUnsupported` | The specified jurisdiction has legal nuances outside the skill's coverage | Flag jurisdiction-specific clauses that require local legal counsel review |

## Dependencies

- Legal Counsel persona's contract review template (`personas/legal-counsel/templates/contract-review.md`) if available
- Comparison document or preferred-terms template for delta analysis (optional)
- Project context for industry-specific risk calibration (e.g., regulated industries have stricter data handling requirements)
- Jurisdiction reference for governing law analysis (optional)
