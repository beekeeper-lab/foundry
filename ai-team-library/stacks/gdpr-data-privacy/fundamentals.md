# GDPR Fundamentals & Data Subject Rights

Standards and principles for complying with the General Data Protection
Regulation (EU) 2016/679 (GDPR). The GDPR governs the processing of personal
data of individuals in the European Economic Area (EEA) and applies to any
organization that processes such data, regardless of where the organization
is established.

---

## Defaults

- **Regulation:** General Data Protection Regulation (EU) 2016/679, effective
  25 May 2018. Directly applicable in all EU/EEA member states.
- **Scope:** Any processing of personal data of individuals in the EEA, whether
  the controller or processor is established in the EEA or not (Article 3).
- **Lawful Bases:** Every processing activity requires a lawful basis under
  Article 6: consent, contract, legal obligation, vital interests, public task,
  or legitimate interests.
- **Accountability:** The controller must demonstrate compliance — it is not
  enough to simply comply. Records, policies, and evidence are required
  (Article 5(2)).

---

## Key Principles (Article 5)

| # | Principle | Description |
|---|-----------|-------------|
| 1 | **Lawfulness, Fairness, Transparency** | Data must be processed lawfully, fairly, and in a transparent manner. Data subjects must be informed of processing activities. |
| 2 | **Purpose Limitation** | Data must be collected for specified, explicit, and legitimate purposes and not further processed in a manner incompatible with those purposes. |
| 3 | **Data Minimisation** | Data collected must be adequate, relevant, and limited to what is necessary for the processing purpose. |
| 4 | **Accuracy** | Personal data must be accurate and, where necessary, kept up to date. Inaccurate data must be erased or rectified without delay. |
| 5 | **Storage Limitation** | Data must be kept in a form that permits identification of data subjects for no longer than is necessary. |
| 6 | **Integrity and Confidentiality** | Data must be processed with appropriate security measures, including protection against unauthorized processing, accidental loss, destruction, or damage. |
| 7 | **Accountability** | The controller is responsible for, and must be able to demonstrate, compliance with all principles. |

---

## Lawful Bases for Processing (Article 6)

| Lawful Basis | When to Use | Key Requirement |
|-------------|-------------|-----------------|
| **Consent** (Art. 6(1)(a)) | Data subject has given clear, affirmative consent for a specific purpose | Must be freely given, specific, informed, unambiguous. Must be as easy to withdraw as to give. |
| **Contract** (Art. 6(1)(b)) | Processing is necessary to perform or enter into a contract with the data subject | Must be genuinely necessary for the contract, not just useful or convenient. |
| **Legal Obligation** (Art. 6(1)(c)) | Processing is necessary to comply with a legal obligation on the controller | Must be a specific legal requirement, not a vague or general obligation. |
| **Vital Interests** (Art. 6(1)(d)) | Processing is necessary to protect someone's life | Narrow scope — only when no other lawful basis applies and it is genuinely life-or-death. |
| **Public Task** (Art. 6(1)(e)) | Processing is necessary for a task in the public interest or official authority | Primarily for public authorities and bodies. |
| **Legitimate Interests** (Art. 6(1)(f)) | Processing is necessary for legitimate interests of the controller or third party, balanced against data subject rights | Requires a three-part test: purpose, necessity, and balancing. Document the assessment. |

---

## Data Subject Rights

| Right | Article | Description | Response Deadline |
|-------|---------|-------------|-------------------|
| **Right to be Informed** | Art. 13, 14 | Data subjects must be told how their data is processed at the point of collection (Art. 13) or within one month if not collected directly (Art. 14). | At collection or within 1 month |
| **Right of Access** | Art. 15 | Data subjects can request confirmation of processing and a copy of their personal data. | 1 month |
| **Right to Rectification** | Art. 16 | Data subjects can request correction of inaccurate or incomplete personal data. | 1 month |
| **Right to Erasure** | Art. 17 | Data subjects can request deletion when data is no longer necessary, consent is withdrawn, or processing is unlawful. Not absolute — legal obligations and public interest can override. | 1 month |
| **Right to Restrict Processing** | Art. 18 | Data subjects can request limitation of processing while accuracy is contested, processing is unlawful, or the controller no longer needs the data but the subject requires it for legal claims. | 1 month |
| **Right to Data Portability** | Art. 20 | Data subjects can receive their data in a structured, commonly used, machine-readable format and transmit it to another controller. Applies only to data provided by the subject and processed by automated means based on consent or contract. | 1 month |
| **Right to Object** | Art. 21 | Data subjects can object to processing based on legitimate interests or public task. For direct marketing, the right to object is absolute. | Without undue delay |
| **Automated Decision-Making** | Art. 22 | Data subjects have the right not to be subject to decisions based solely on automated processing, including profiling, that produce legal or similarly significant effects. Exceptions: contract, explicit consent, or law. | 1 month |

---

## Do / Don't

- **Do** identify and document a lawful basis for every processing activity
  before processing begins.
- **Do** provide clear, concise, and accessible privacy notices. Use plain
  language, not legal jargon.
- **Do** maintain a Record of Processing Activities (ROPA) under Article 30,
  covering purposes, categories of data, recipients, transfers, and retention.
- **Do** respond to data subject requests within one calendar month. The
  deadline can be extended by two further months for complex requests, but
  the data subject must be informed within the first month.
- **Do** appoint a Data Protection Officer (DPO) when required (public
  authority, large-scale monitoring, or large-scale special category processing).
- **Don't** treat consent as the default lawful basis. Consent must be freely
  given — if there is a power imbalance (e.g., employer-employee), consent
  is unlikely to be valid.
- **Don't** bundle consent with terms and conditions. Consent must be
  separate, specific, and granular.
- **Don't** collect data "just in case." Data minimisation is a legal
  requirement, not a suggestion.
- **Don't** ignore the right to erasure because it is inconvenient. Design
  systems to support deletion from the start.
- **Don't** assume legitimate interests is a catch-all. It requires a
  documented balancing test — the data subject's rights may override.

---

## Common Pitfalls

1. **No lawful basis documented.** Processing activities exist without a clear,
   documented lawful basis. Solution: create a processing register mapping each
   activity to its Article 6 basis before processing begins.
2. **Dark patterns in consent.** Pre-ticked boxes, confusing wording, or
   making it harder to refuse than to accept. Solution: design consent flows
   that meet the GDPR standard — freely given, specific, informed, unambiguous.
3. **Ignoring subject access requests.** Requests are lost, delayed, or
   handled inconsistently. Solution: implement a formal DSAR handling process
   with tracking, templates, and escalation paths.
4. **Over-retention of data.** Data is stored indefinitely with no retention
   policy. Solution: define retention periods for each processing purpose and
   automate deletion or anonymisation where possible.
5. **Privacy notice as an afterthought.** A generic, copy-pasted privacy
   policy that does not reflect actual processing activities. Solution: write
   privacy notices that are specific, accurate, and updated when processing
   changes.

---

## Checklist

- [ ] Lawful basis identified and documented for every processing activity
- [ ] Record of Processing Activities (ROPA) maintained under Article 30
- [ ] Privacy notices provided at all points of data collection
- [ ] Data subject request handling process in place with tracking
- [ ] Response to DSARs within one calendar month (with documented extension process)
- [ ] Consent mechanisms meet GDPR standard (freely given, specific, informed, unambiguous)
- [ ] Consent withdrawal is as easy as consent giving
- [ ] Data Protection Officer appointed (if required under Article 37)
- [ ] Data retention periods defined and enforced for all processing purposes
- [ ] Regular review of lawful bases and processing activities
