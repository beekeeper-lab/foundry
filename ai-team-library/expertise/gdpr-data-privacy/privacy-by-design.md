# Privacy by Design & Data Protection Impact Assessments

Standards for embedding data protection into system design and conducting
Data Protection Impact Assessments (DPIAs) as required by Articles 25 and 35
of the GDPR. Privacy by design is not optional — it is a legal obligation.

---

## Defaults

- **Principle:** Data protection by design and by default (Article 25).
  Appropriate technical and organisational measures must be implemented at
  the time of determining the means for processing and at the time of
  processing itself.
- **Default Setting:** Only personal data necessary for each specific purpose
  is processed by default. This applies to the amount of data collected,
  the extent of processing, the period of storage, and accessibility.
- **DPIA Trigger:** A DPIA is mandatory when processing is likely to result
  in a high risk to the rights and freedoms of natural persons (Article 35).
- **Supervisory Authority Consultation:** If a DPIA indicates high risk that
  cannot be mitigated, the controller must consult the supervisory authority
  before processing (Article 36).

---

## Privacy by Design Principles

| # | Principle | Application |
|---|-----------|-------------|
| 1 | **Proactive not Reactive** | Anticipate and prevent privacy risks before they materialise. Do not wait for breaches or complaints. |
| 2 | **Privacy as the Default** | No action required from the individual to protect their privacy. The system must protect data automatically. |
| 3 | **Privacy Embedded into Design** | Privacy is integral to system architecture, not bolted on as an add-on or afterthought. |
| 4 | **Full Functionality** | Avoid false trade-offs between privacy and functionality. Both are achievable with proper design. |
| 5 | **End-to-End Security** | Data is protected throughout its entire lifecycle — from collection through processing, storage, and deletion. |
| 6 | **Visibility and Transparency** | Processing operations are visible and verifiable. Stakeholders can confirm that privacy promises are kept. |
| 7 | **Respect for User Privacy** | Keep the interests of the individual paramount. Offer strong defaults, appropriate notice, and user-friendly options. |

---

## Technical Measures for Privacy by Design

| Measure | Description | Example |
|---------|-------------|---------|
| **Pseudonymisation** | Replace direct identifiers with tokens or keys so data cannot be attributed to a subject without additional information (stored separately). | Hash email addresses in analytics tables; store the mapping separately with restricted access. |
| **Encryption** | Encrypt personal data at rest and in transit to protect against unauthorised access. | TLS for data in transit; AES-256 for data at rest; envelope encryption for key management. |
| **Access Controls** | Enforce least-privilege access. Only authorised personnel can access personal data, and only for authorised purposes. | Role-based access control (RBAC); attribute-based access control (ABAC); just-in-time access. |
| **Data Minimisation in Schema** | Design database schemas and APIs to collect and store only the fields necessary for the stated purpose. | Separate tables for required vs. optional data; avoid catch-all "notes" fields. |
| **Automated Retention Enforcement** | Implement automated deletion, anonymisation, or archival based on defined retention periods. | Scheduled jobs that purge or anonymise records past their retention date. |
| **Audit Logging** | Log access to and changes of personal data to maintain accountability and support DSAR responses. | Immutable audit trail recording who accessed what data, when, and for what purpose. |
| **Purpose Separation** | Process data collected for different purposes in separate systems or with strict logical separation. | Separate analytics data from transactional data; use distinct processing pipelines per purpose. |

---

## Data Protection Impact Assessment (DPIA)

### When a DPIA Is Required (Article 35)

A DPIA is mandatory when processing is likely to result in a high risk.
The GDPR specifies three cases where a DPIA is always required:

| Trigger | Description |
|---------|-------------|
| **Systematic and extensive profiling** | Automated processing, including profiling, that produces legal effects or similarly significant effects on individuals. |
| **Large-scale special category data** | Processing of special categories of data (Article 9) or criminal conviction data (Article 10) on a large scale. |
| **Systematic monitoring of public areas** | Large-scale, systematic monitoring of a publicly accessible area (e.g., CCTV with facial recognition). |

Supervisory authorities publish additional lists of processing operations
requiring a DPIA (Article 35(4)).

### DPIA Process

| Step | Activity | Output |
|------|----------|--------|
| 1 | **Describe the processing** | Systematic description of processing operations, purposes, and lawful basis. Include data flows and recipients. |
| 2 | **Assess necessity and proportionality** | Evaluate whether the processing is necessary for the stated purpose and proportionate to the risk. |
| 3 | **Identify and assess risks** | Identify risks to data subjects' rights and freedoms. Assess likelihood and severity. |
| 4 | **Identify mitigation measures** | Define technical and organisational measures to address identified risks. |
| 5 | **Document and record** | Record the DPIA, including the assessment, decisions, and measures adopted. |
| 6 | **Consult the DPO** | Seek the DPO's advice on the DPIA (Article 35(2)). Document the DPO's input. |
| 7 | **Review and update** | Revisit the DPIA when processing changes or new risks emerge. A DPIA is not a one-time exercise. |

---

## Do / Don't

- **Do** integrate privacy considerations at the requirements and design
  phases of every project, not after development is complete.
- **Do** conduct a DPIA before beginning any processing likely to result in
  high risk. "Before" means before processing starts, not after launch.
- **Do** involve the DPO in DPIAs from the beginning. Their advice is
  required under Article 35(2).
- **Do** design systems so that the most privacy-protective setting is the
  default. Users should opt in to less privacy, not opt out.
- **Do** document all privacy design decisions and their rationale for
  accountability purposes.
- **Don't** treat privacy by design as a checkbox exercise. It must be
  reflected in actual system architecture and configuration.
- **Don't** skip the DPIA because the project is "low risk." If in doubt,
  conduct a threshold assessment to determine whether a full DPIA is needed.
- **Don't** conduct the DPIA in isolation from the engineering team. Privacy
  engineers and developers must be involved.
- **Don't** treat the DPIA as a one-time document. It must be reviewed when
  processing changes, new data types are added, or new technologies are adopted.

---

## Common Pitfalls

1. **Privacy bolted on at the end.** The system is designed and built first,
   then a privacy review is conducted. Solution: include privacy requirements
   in the project brief and design review gates.
2. **DPIA as a paper exercise.** The DPIA is completed to satisfy a process
   requirement but does not influence actual design decisions. Solution: link
   DPIA findings to engineering tickets and track mitigation implementation.
3. **Default settings expose data.** User profiles, sharing settings, or data
   visibility default to "public" or "everyone." Solution: default to the
   most restrictive setting; let users explicitly choose to broaden access.
4. **No retention automation.** Retention periods are defined in policy but
   not enforced technically. Data accumulates indefinitely. Solution: implement
   automated deletion or anonymisation pipelines with monitoring.
5. **Ignoring DPO advice.** The DPO is consulted but their recommendations
   are not acted upon or documented. Solution: record DPO input and the
   controller's response. If recommendations are not followed, document why.

---

## Checklist

- [ ] Privacy requirements included in project brief and design documents
- [ ] Privacy by design review conducted at architecture and design phases
- [ ] Default settings are the most privacy-protective option
- [ ] DPIA threshold assessment performed for all new processing activities
- [ ] Full DPIA conducted where required, before processing begins
- [ ] DPO consulted and advice documented in all DPIAs
- [ ] Technical measures implemented: pseudonymisation, encryption, access controls
- [ ] Automated retention enforcement in place for all data stores
- [ ] Audit logging covers access to and modification of personal data
- [ ] DPIAs reviewed and updated when processing changes
