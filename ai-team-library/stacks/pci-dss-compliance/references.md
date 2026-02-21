# References

Primary sources, guidance documents, and supplementary materials for PCI DSS
compliance.

---

## Primary Standards

| Reference | Description |
|-----------|-------------|
| **PCI DSS v4.0.1** | Payment Card Industry Data Security Standard, version 4.0.1 (June 2024). Defines the 12 requirements for protecting cardholder data. |
| **PCI DSS v4.0 Summary of Changes** | Document describing all changes from v3.2.1 to v4.0, including new requirements and revised guidance. |
| **PCI DSS ROC Reporting Template** | Template for Qualified Security Assessors conducting on-site assessments. |
| **PCI DSS SAQ Documents** | Self-Assessment Questionnaires for each SAQ type (A, A-EP, B, B-IP, C, C-VT, D, P2PE). |
| **PCI DSS AOC Templates** | Attestation of Compliance templates for merchants and service providers. |

---

## PCI SSC Guidance Documents

| Document | Description |
|----------|-------------|
| **Information Supplement: Penetration Testing** | Guidance on penetration testing methodology, scope, and reporting for PCI DSS. |
| **Information Supplement: Best Practices for Maintaining PCI DSS Compliance** | Ongoing compliance maintenance, including monitoring, testing, and change management. |
| **Information Supplement: Scoping and Segmentation** | Guidance on accurately defining the CDE scope and validating segmentation controls. |
| **Information Supplement: Cloud Computing** | PCI DSS applicability in cloud environments, shared responsibility models, and IaaS/PaaS/SaaS considerations. |
| **Information Supplement: Third-Party Security Assurance** | Managing third-party service provider risk, due diligence, and ongoing monitoring. |
| **Information Supplement: Tokenization** | Guidelines for tokenization solutions, deployment models, and risk reduction. |
| **Information Supplement: E-commerce Security** | Securing e-commerce payment channels, including redirects, iFrames, and JavaScript-based integrations. |
| **PCI P2PE Standard** | Point-to-Point Encryption standard for validated encryption solutions at the point of interaction. |
| **PA-DSS / PCI Secure Software Standard** | Requirements for payment application security (PA-DSS replaced by PCI Secure Software Standard). |

---

## NIST Publications (Relevant to PCI DSS)

| Publication | Description |
|-------------|-------------|
| **NIST SP 800-53 Rev. 5** | Security and Privacy Controls for Information Systems — comprehensive control catalog mappable to PCI DSS requirements. |
| **NIST Cybersecurity Framework (CSF) 2.0** | Voluntary framework with functions (Identify, Protect, Detect, Respond, Recover) aligned to PCI DSS goals. |
| **NIST SP 800-57 Part 1 Rev. 5** | Recommendation for Key Management — key lifecycle, crypto-periods, and algorithm selection relevant to PCI DSS Requirements 3 and 4. |
| **NIST SP 800-52 Rev. 2** | Guidelines for TLS Implementations — cipher suite selection and protocol configuration for PCI DSS Requirement 4. |
| **NIST SP 800-115** | Technical Guide to Information Security Testing and Assessment — relevant to PCI DSS Requirement 11 (penetration testing and vulnerability scanning). |
| **NIST SP 800-92** | Guide to Computer Security Log Management — relevant to PCI DSS Requirement 10 (audit logging). |

---

## Payment Brand Programs

| Brand | Program | Description |
|-------|---------|-------------|
| **Visa** | Visa Global Registry / CISP | Cardholder Information Security Program — merchant levels, compliance validation, and registered service providers. |
| **Mastercard** | Site Data Protection (SDP) | Compliance program for merchants and service providers, including merchant level definitions and validation requirements. |
| **American Express** | Data Security Operating Policy (DSOP) | Compliance requirements for merchants accepting American Express. |
| **Discover** | Discover Information Security Compliance (DISC) | Compliance program for Discover merchants and service providers. |
| **JCB** | JCB Data Security Program | Compliance requirements for JCB card acceptance. |

---

## Related Stack Files

| File | Description |
|------|-------------|
| `fundamentals.md` | PCI DSS overview, 12 requirements, cardholder data elements, CDE scoping. |
| `network-segmentation.md` | Network security controls, segmentation architecture, firewall rule management. |
| `encryption-and-key-management.md` | Encryption at rest and in transit, key lifecycle, code examples. |
| `audit-logging.md` | Audit logging, monitoring, vulnerability scanning, penetration testing. |
| `saq-guidance.md` | Self-Assessment Questionnaire types, selection, merchant levels, compensating controls. |

---

## Key Concepts Glossary

| Term | Definition |
|------|-----------|
| **Cardholder Data (CHD)** | At minimum, the full PAN. May also include cardholder name, expiration date, and service code. |
| **Sensitive Authentication Data (SAD)** | Full track data, CAV2/CVC2/CVV2/CID, PINs, and PIN blocks. Must never be stored after authorization. |
| **Primary Account Number (PAN)** | The unique payment card number (up to 19 digits) that identifies the issuer and the cardholder account. |
| **Cardholder Data Environment (CDE)** | The people, processes, and technology that store, process, or transmit cardholder data or sensitive authentication data. |
| **Network Security Control (NSC)** | Firewall, router ACL, cloud security group, or similar control that manages network traffic between segments. |
| **Tokenization** | Process of replacing a PAN with a surrogate value (token) that cannot be used to retrieve the original PAN without access to the token vault. |
| **Point-to-Point Encryption (P2PE)** | PCI SSC validated encryption solution that encrypts cardholder data from the point of interaction to the decryption environment. |
| **Qualified Security Assessor (QSA)** | Independent security organization qualified by the PCI SSC to validate an entity's compliance with PCI DSS. |
| **Approved Scanning Vendor (ASV)** | Organization approved by the PCI SSC to conduct external vulnerability scans for PCI DSS compliance. |
| **Internal Security Assessor (ISA)** | Individual within an organization who has been qualified by the PCI SSC to conduct internal PCI DSS assessments. |
| **Report on Compliance (ROC)** | Formal assessment report completed by a QSA or ISA documenting an entity's compliance with all PCI DSS requirements. |
| **Self-Assessment Questionnaire (SAQ)** | Validation tool for merchants and service providers not required to undergo a full ROC. |
| **Attestation of Compliance (AOC)** | Declaration signed by the assessed entity and (for ROC) the QSA, attesting to the entity's PCI DSS compliance status. |
| **Compensating Control** | Alternative security control implemented when an entity cannot meet a PCI DSS requirement as stated due to a legitimate constraint. |
| **Crypto-period** | The time span during which a specific cryptographic key is authorized for use. Key rotation occurs at the end of a crypto-period. |
| **File Integrity Monitoring (FIM)** | Technology that monitors and alerts on changes to critical system files, configuration files, and content files. |
