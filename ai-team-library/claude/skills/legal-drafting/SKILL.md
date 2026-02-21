# Skill: Legal Drafting

## Description

Drafts and reviews legal documents for software products and services: Terms of
Service (ToS), Privacy Policies, End-User License Agreements (EULAs), Data
Processing Agreements (DPAs), and cookie consent notices. The skill produces
structured, plain-language documents that address regulatory requirements (GDPR,
CCPA, CAN-SPAM, COPPA, ePrivacy Directive) while remaining understandable to
non-lawyers. Each document type follows a specific process tailored to its
regulatory context and audience, with built-in compliance checklists. This is the
Legal Counsel persona's primary drafting tool.

## Trigger

- Invoked by the `/legal-drafting` slash command.
- Called by the Legal Counsel persona when a project requires legal documentation.
- Should be invoked when a new product launches, a feature changes data collection practices, or when existing legal documents need review or update.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| document_type | Enum: `tos`, `privacy-policy`, `eula`, `dpa`, `cookie-consent` | Yes | The type of legal document to draft |
| product_name | String | Yes | Name of the product or service the document covers |
| product_description | Text | No | Brief description of what the product does; used to tailor clauses |
| project_context | File path | No | `ai/context/project.md` for stack, domain, and deployment context |
| jurisdiction | String | No | Primary legal jurisdiction (e.g., "US", "EU", "global"); defaults to "global" |
| data_practices | Text | No | Description of data collection, processing, storage, and sharing practices |
| existing_document | File path | No | Previous version of the document to update incrementally |
| audience | Enum: `consumer`, `enterprise`, `developer` | No | Target audience; defaults to `consumer` |

## Process

1. **Gather context** -- Read the project context file and any existing legal documents. Identify the product's domain (SaaS, mobile app, marketplace, API, etc.), tech stack, data handling patterns, and target user base. If `data_practices` is not provided, infer data collection patterns from the project context and architecture documentation.

2. **Determine regulatory scope** -- Based on jurisdiction and product type, identify applicable regulations:
   - **GDPR** (EU): Data subject rights, lawful basis, DPO requirements, cross-border transfers
   - **CCPA/CPRA** (California): Consumer rights, sale of data, opt-out requirements
   - **COPPA** (US): Children's data protections if applicable
   - **CAN-SPAM** (US): Email communication rules if applicable
   - **ePrivacy Directive** (EU): Cookie and tracking consent requirements
   - **LGPD** (Brazil), **PIPA** (South Korea), **PIPEDA** (Canada): If jurisdiction requires
   Document which regulations apply and which sections of the document they affect.

3. **Select document template** -- Based on `document_type`, apply the appropriate structure:

   **Terms of Service (ToS):**
   - Acceptance of terms and eligibility
   - Account registration and responsibilities
   - Permitted and prohibited use
   - Intellectual property rights
   - User-generated content (if applicable)
   - Payment terms and billing (if applicable)
   - Service availability and SLA (if applicable)
   - Limitation of liability and disclaimers
   - Indemnification
   - Termination and suspension
   - Dispute resolution and governing law
   - Modification of terms and notice
   - Contact information

   **Privacy Policy:**
   - Information collected (categories and specific data points)
   - How information is collected (direct, automatic, third-party)
   - Purpose and legal basis for processing
   - Data sharing and third-party disclosure
   - Data retention periods
   - User rights (access, correction, deletion, portability, objection)
   - Cookie and tracking technologies
   - Children's privacy
   - International data transfers
   - Security measures
   - Policy updates and notification
   - Contact information and DPO details

   **EULA:**
   - License grant and scope
   - Restrictions on use
   - Intellectual property ownership
   - Updates and maintenance
   - Data collection by the software
   - Warranty disclaimers
   - Limitation of liability
   - Term and termination
   - Export compliance
   - Governing law

   **Data Processing Agreement (DPA):**
   - Definitions (controller, processor, data subject, personal data)
   - Subject matter and duration of processing
   - Nature and purpose of processing
   - Categories of data subjects and personal data
   - Obligations of the processor
   - Obligations of the controller
   - Sub-processors and consent mechanism
   - Data subject rights assistance
   - Security measures (Article 32 GDPR)
   - Data breach notification procedures
   - Data transfer mechanisms (SCCs, adequacy decisions)
   - Audit rights
   - Return and deletion of data
   - Liability and indemnification

   **Cookie Consent Notice:**
   - What cookies are used (strictly necessary, functional, analytics, advertising)
   - Purpose of each cookie category
   - Cookie providers (first-party vs. third-party)
   - Duration of each cookie
   - How to accept, reject, or manage cookie preferences
   - Link to full privacy policy
   - Consent mechanism description (banner, preference center)
   - Updates to cookie practices

4. **Draft in plain language** -- Write each section using plain-language principles:
   - Use short sentences (average 15-20 words)
   - Avoid legal jargon; when legal terms are necessary, define them on first use
   - Use active voice ("We collect" not "Data is collected")
   - Use "you" for the user and "we" for the company
   - Use headers and bullet points for scannability
   - Place the most important information first in each section
   - Include concrete examples where abstract concepts appear (e.g., "personal data such as your name, email address, and payment information")

5. **Apply regulatory requirements** -- For each applicable regulation identified in step 2, ensure the document contains the required disclosures:
   - GDPR: Lawful basis for each processing purpose, data subject rights enumerated, DPO contact, transfer mechanisms
   - CCPA: "Do Not Sell My Personal Information" right, categories of data sold/shared, financial incentive disclosures
   - COPPA: Parental consent mechanism, teacher consent for school context, limited data collection
   - ePrivacy: Cookie categories with opt-in consent for non-essential cookies, granular consent controls

6. **Add compliance metadata** -- Include metadata at the top of the document:
   - Document type and version number
   - Effective date
   - Last reviewed date
   - Applicable jurisdictions
   - Applicable regulations
   - Product/service covered
   - Document owner (role, not individual)

7. **Generate compliance checklist** -- Produce a checklist verifying each regulatory requirement is addressed in the document. Format as a table: Regulation | Requirement | Section | Status (Addressed / N/A / Needs Review).

8. **Produce the document** -- Write the complete legal document and compliance checklist to the Legal Counsel persona's output directory: `ai/outputs/legal-counsel/`.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| legal_document | Markdown file | Complete legal document (ToS, Privacy Policy, EULA, DPA, or Cookie Consent) in plain language |
| compliance_checklist | Markdown section | Regulation-by-requirement verification table appended to the document |
| document_summary | Section in document | Executive summary with document scope, key rights, and regulatory coverage |

## Quality Criteria

- The document covers every section required by the selected template for that document type.
- Plain-language standards are met: average sentence length under 20 words, no undefined legal jargon, active voice throughout.
- Every applicable regulation identified in step 2 has corresponding disclosures in the document.
- The compliance checklist has an entry for every regulatory requirement, with a section reference for each.
- Data practices described in the document match the project's actual data collection and processing patterns.
- User rights are enumerated concretely with instructions on how to exercise them (not just "you have certain rights").
- Cookie consent notices list every cookie by name, provider, purpose, and duration -- not generic categories.
- DPAs include specific technical and organizational security measures, not vague references to "appropriate measures."
- The document includes a version number, effective date, and last-reviewed date.
- If jurisdiction is "global," the document addresses the most restrictive applicable requirements (GDPR as baseline).

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `InvalidDocumentType` | The `document_type` input is not one of the five supported types | Use one of: `tos`, `privacy-policy`, `eula`, `dpa`, `cookie-consent` |
| `NoProductName` | Product name is empty | Provide the name of the product or service |
| `NoDataPractices` | Cannot determine data collection practices from context or input | Provide `data_practices` input or ensure project context describes data handling |
| `UnknownJurisdiction` | Jurisdiction string does not match a recognized region | Use a recognized jurisdiction code (e.g., "US", "EU", "UK", "global") |
| `OutputDirNotWritable` | Cannot write to `ai/outputs/legal-counsel/` | Check permissions or scaffold the project with the Legal Counsel persona |
| `ConflictingRequirements` | Jurisdiction requirements conflict (e.g., data retention minimization vs. mandatory retention) | Document the conflict explicitly and recommend legal review for resolution |

## Dependencies

- Project context (`ai/context/project.md`) for product and data handling details
- Architecture documentation for understanding data flows and storage
- Legal Counsel persona's output directory (`ai/outputs/legal-counsel/`)
- Existing legal documents (if updating rather than creating from scratch)
- Cookie/tracking inventory from the technical team (for cookie consent notices)
