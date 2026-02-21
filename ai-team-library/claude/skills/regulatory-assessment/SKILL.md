# Skill: Regulatory Compliance Assessment

## Description

Performs a structured regulatory compliance assessment for software products,
mapping applicable regulations (GDPR, CCPA, HIPAA, SOX, ADA, and others) to
the product's data practices, user base, and operational jurisdictions. The
skill conducts jurisdiction analysis, identifies compliance gaps against each
applicable regulation, and produces a prioritized remediation roadmap. This is
the Legal Counsel persona's primary regulatory analysis tool.

## Trigger

- Invoked by the `/regulatory-assessment` slash command.
- Called by the Legal Counsel persona when a product enters a new market, handles
  new data categories, or when regulatory landscape changes.
- Should be re-run when the product's jurisdictional footprint, data processing
  activities, or user demographics change materially.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| product_description | File path or text | Yes | Description of the software product including features, data collected, user types, and deployment model |
| jurisdictions | String or list | No | Target jurisdictions for the assessment (e.g., "US, EU, California"); auto-detected from product description if not provided |
| data_inventory | File path | No | Inventory of data types collected, processed, and stored by the product |
| architecture_doc | File path | No | Architecture documentation showing data flows, storage locations, and third-party integrations |
| existing_compliance | File path | No | Existing compliance documentation, certifications, or prior assessment results |
| industry | String | No | Industry vertical for sector-specific regulations (e.g., "healthcare", "finance", "education"); auto-detected if not provided |
| assessment_scope | String | No | Limit to specific regulation(s): `gdpr`, `ccpa`, `hipaa`, `sox`, `ada`, `all`; defaults to `all` applicable |

## Process

### Phase 1: Product and Jurisdiction Analysis

1. **Profile the product** -- Classify the software product by type (SaaS, mobile
   app, embedded system, internal tool), deployment model (cloud, on-premises,
   hybrid), data processing role (controller, processor, sub-processor), and user
   base (consumer, enterprise, government, mixed). Identify all categories of
   data collected, processed, and stored.

2. **Map jurisdictional exposure** -- Determine which jurisdictions apply based on
   where users are located, where data is stored and processed, where the
   organization is incorporated, and where the product is marketed or accessible.
   Consider both direct jurisdiction (operating in a territory) and long-arm
   jurisdiction (processing data of residents in a territory).

3. **Identify applicable regulations** -- For each jurisdiction, enumerate the
   regulations that apply based on the product profile. Include:
   - **Data protection and privacy:** GDPR (EU/EEA), CCPA/CPRA (California),
     PIPEDA (Canada), LGPD (Brazil), POPIA (South Africa), state-level US
     privacy laws (Virginia VCDPA, Colorado CPA, Connecticut CTDPA, etc.)
   - **Health data:** HIPAA (US health data), HITECH Act, state health privacy
     laws, EU health data provisions under GDPR Article 9
   - **Financial data:** SOX (US public companies), GLBA (US financial
     institutions), PCI DSS (payment card data), PSD2/PSD3 (EU payment services),
     state money transmitter laws
   - **Accessibility:** ADA Title III (US), Section 508 (US federal), WCAG 2.1
     (international standard), EAA (EU European Accessibility Act), EN 301 549
     (EU standard)
   - **Sector-specific:** FERPA (US education), COPPA (US children's data),
     FISMA (US federal systems), FedRAMP (US federal cloud), ITAR/EAR (US
     export controls)
   - **Cross-cutting:** CAN-SPAM/CASL (email marketing), TCPA (US
     telecommunications), e-Privacy Directive/Regulation (EU), cookie laws

4. **Determine regulatory priority** -- Rank applicable regulations by enforcement
   risk (penalty severity and enforcement activity), operational impact (scope of
   required changes), and timeline (compliance deadlines or effective dates).

### Phase 2: Compliance Gap Analysis

5. **Assess GDPR compliance** (if applicable) -- Evaluate against key GDPR
   requirements:
   - Lawful basis for processing (Article 6) for each data processing activity
   - Consent mechanisms and management (Articles 7-8)
   - Data subject rights implementation: access, rectification, erasure,
     portability, restriction, objection (Articles 15-22)
   - Privacy by design and default (Article 25)
   - Data Protection Impact Assessments for high-risk processing (Article 35)
   - Data Processing Agreements with all processors (Article 28)
   - Cross-border transfer mechanisms: adequacy decisions, SCCs, BCRs (Chapter V)
   - Data breach notification procedures -- 72-hour supervisory authority
     notification, undue delay data subject notification (Articles 33-34)
   - Records of processing activities (Article 30)
   - Data Protection Officer appointment if required (Articles 37-39)

6. **Assess CCPA/CPRA compliance** (if applicable) -- Evaluate against key
   California requirements:
   - Notice at collection with categories, purposes, retention periods
   - Right to know, delete, correct, and opt-out of sale/sharing
   - "Do Not Sell or Share My Personal Information" link
   - Service provider and contractor agreements
   - Financial incentive disclosures for data-for-discount programs
   - Sensitive personal information processing limitations
   - CPRA-specific: purpose limitation, data minimization, storage limitation
   - Privacy policy disclosures meeting all statutory requirements

7. **Assess HIPAA compliance** (if applicable) -- Evaluate against key HIPAA
   requirements:
   - Covered entity or business associate determination
   - Business Associate Agreements with all downstream processors
   - Privacy Rule: minimum necessary standard, use and disclosure limitations,
     individual rights (access, amendment, accounting of disclosures)
   - Security Rule: administrative safeguards (risk analysis, workforce training,
     contingency planning), physical safeguards (facility access, workstation
     security), technical safeguards (access control, audit controls, integrity
     controls, transmission security)
   - Breach notification: 60-day individual notification, HHS notification,
     media notification for breaches affecting 500+ individuals
   - HITECH Act: enhanced penalties, breach notification requirements, business
     associate direct liability

8. **Assess SOX compliance** (if applicable) -- Evaluate against key SOX
   requirements:
   - Section 302: CEO/CFO certification of financial reports
   - Section 404: Internal controls over financial reporting (ICFR) with
     management assessment and (for accelerated filers) auditor attestation
   - IT General Controls (ITGCs): access controls, change management, computer
     operations, program development
   - Application controls: input validation, processing controls, output controls
     for financial systems
   - Audit trail and logging requirements for financial data access and
     modification
   - Document retention requirements (Section 802)

9. **Assess ADA/accessibility compliance** (if applicable) -- Evaluate against
   key accessibility requirements:
   - WCAG 2.1 Level AA conformance across all product interfaces
   - Perceivable: text alternatives, captions, adaptable content, distinguishable
     content (contrast, resize, audio control)
   - Operable: keyboard accessible, sufficient time, seizure prevention,
     navigable, input modalities
   - Understandable: readable, predictable, input assistance
   - Robust: compatible with assistive technologies, proper markup
   - Section 508 refresh (aligned with WCAG 2.0 Level AA) for federal procurement
   - Voluntary Product Accessibility Template (VPAT) availability
   - Accessibility statement and feedback mechanism

10. **Assess additional applicable regulations** -- For each additional regulation
    identified in Phase 1, evaluate the product's current compliance posture
    against the regulation's key requirements. Document specific provisions and
    the product's status for each.

### Phase 3: Remediation Roadmap

11. **Classify each gap** -- For every compliance gap identified, assign:
    - **Severity:** Critical (active violation with enforcement exposure), High
      (material gap likely to be identified in an audit or complaint), Medium
      (partial compliance requiring enhancement), Low (best practice gap or
      optional improvement)
    - **Effort:** High (architectural change, new system, or major process
      redesign), Medium (significant feature development or process update), Low
      (configuration change, policy update, or documentation)
    - **Regulatory risk:** Specific penalty exposure citing the relevant
      enforcement provision and historical enforcement precedents

12. **Build the remediation roadmap** -- Organize gaps into a phased
    implementation plan:
    - **Immediate (0-30 days):** Critical gaps with active enforcement exposure.
      Quick wins that reduce risk without major engineering effort.
    - **Short-term (30-90 days):** High-severity gaps and medium-effort items
      that address the most significant compliance risks.
    - **Medium-term (90-180 days):** Medium-severity gaps requiring feature
      development or process redesign.
    - **Long-term (180+ days):** Low-severity gaps, continuous improvement items,
      and preparation for upcoming regulatory changes.

13. **Estimate resource requirements** -- For each roadmap phase, estimate the
    types of resources needed (engineering, legal, operations, training),
    external dependencies (vendor agreements, third-party audits, legal counsel),
    and ongoing maintenance obligations.

14. **Produce the assessment report** -- Write the complete regulatory compliance
    assessment following the structured output format.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| regulatory_assessment | Markdown file | Complete regulatory compliance assessment with jurisdiction analysis, gap findings, and roadmap |
| jurisdiction_matrix | Section in report | Matrix mapping jurisdictions to applicable regulations with applicability rationale |
| gap_analysis | Section in report | Detailed compliance gap findings organized by regulation with severity and evidence |
| remediation_roadmap | Section in report | Phased remediation plan with priorities, effort estimates, and timelines |
| executive_summary | Section in report | High-level overview with critical finding count, overall compliance posture, and top priorities |
| regulation_profiles | Section in report | Summary of each applicable regulation's key requirements, penalties, and enforcement trends |

## Quality Criteria

- Every applicable regulation is identified with a specific rationale for why it
  applies -- jurisdiction, data type, industry, or user demographic.
- Gap findings reference specific regulatory provisions (article, section,
  subsection) -- not vague references like "GDPR compliance."
- Each gap includes the current state, the required state, and the specific delta
  between them.
- Severity ratings are justified with reference to enforcement history, penalty
  ranges, and the specific risk to the product.
- The remediation roadmap is actionable: each item identifies what needs to be
  done, who is responsible, dependencies, and a realistic timeline.
- The assessment distinguishes between legal requirements (mandatory compliance),
  regulatory risk (likely enforcement focus), and best practices (recommended but
  not legally required).
- Jurisdiction analysis accounts for both direct presence and long-arm
  jurisdiction (e.g., GDPR applies to non-EU companies processing EU residents'
  data).
- Penalty exposure is quantified where possible using the relevant enforcement
  provision (e.g., "GDPR: up to 4% of global annual turnover or EUR 20M" per
  Article 83(5)).
- Cross-regulatory interactions are identified where compliance with one
  regulation partially satisfies another (e.g., GDPR compliance substantially
  addresses CCPA requirements).
- The assessment notes upcoming regulatory changes or proposed legislation that
  may affect the product's compliance posture.

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoProductDescription` | No product description or context provided | Provide a product description including features, data types, users, and deployment model |
| `InsufficientContext` | Product description lacks detail needed for jurisdiction or regulation mapping | Provide additional detail on data types collected, user locations, and deployment geography |
| `NoJurisdictionDetermined` | Unable to determine applicable jurisdictions from the product description | Specify target jurisdictions explicitly using the `jurisdictions` input |
| `RegulationOutOfScope` | A requested regulation is not covered by this skill's analysis framework | Note the limitation and recommend specialized counsel for the uncovered regulation |
| `StaleAssessment` | The assessment is based on regulatory provisions that may have been amended | Verify current regulatory text before relying on the assessment; note the assessment date |
| `JurisdictionUnsupported` | The specified jurisdiction has regulatory frameworks outside the skill's coverage | Flag the limitation and recommend local counsel for jurisdiction-specific analysis |

## Dependencies

- Legal Counsel persona context for legal analysis framing
- Product description or project documentation for product profiling
- Architecture documentation for data flow and storage analysis (optional but
  recommended)
- Data inventory for comprehensive data mapping (optional but recommended)
- Existing compliance documentation for delta analysis (optional)
- Compliance / Risk Analyst outputs for integration with control frameworks
