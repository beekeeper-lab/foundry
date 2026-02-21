# PCI-DSS Fundamentals

Overview of the Payment Card Industry Data Security Standard (PCI DSS v4.0).
PCI DSS applies to all entities that store, process, or transmit cardholder data
(CHD) or sensitive authentication data (SAD). The standard is maintained by the
PCI Security Standards Council (PCI SSC) and enforced by payment brands
(Visa, Mastercard, American Express, Discover, JCB).

---

## Defaults

- **Standard:** PCI DSS v4.0.1 (published June 2024, mandatory after
  March 31, 2025).
- **Scope:** All system components included in or connected to the cardholder
  data environment (CDE) — people, processes, and technology.
- **Cardholder data (CHD):** Primary account number (PAN), cardholder name,
  expiration date, service code.
- **Sensitive authentication data (SAD):** Full track data, CAV2/CVC2/CVV2/CID,
  PINs and PIN blocks. SAD must never be stored after authorization.
- **Compliance validation:** Annual assessment (SAQ or ROC) plus quarterly
  network vulnerability scans by an Approved Scanning Vendor (ASV).

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| Full PCI DSS assessment (ROC) | Self-Assessment Questionnaire (SAQ) | Merchants with lower transaction volumes; specific SAQ type depends on how card data is handled (see `saq-guidance.md`) |
| Quarterly ASV scans | Continuous scanning | High-risk environments or where real-time vulnerability awareness is required |
| Network segmentation of CDE | Flat network (entire network in scope) | Only if the entire network meets all PCI DSS requirements — segmentation significantly reduces scope and effort |
| Tokenization for stored PAN | Format-preserving encryption (FPE) | When downstream systems require a value that resembles a PAN; ensure token provider is PCI DSS compliant |
| Point-to-point encryption (P2PE) | End-to-end encryption (E2EE) | P2PE validated solutions reduce PCI scope at the point of interaction; E2EE when P2PE validation is not available |

---

## The 12 PCI DSS Requirements

PCI DSS v4.0 organizes requirements under six goals:

| Goal | Requirement | Description |
|------|-------------|-------------|
| **Build and Maintain a Secure Network and Systems** | 1 | Install and maintain network security controls |
| | 2 | Apply secure configurations to all system components |
| **Protect Account Data** | 3 | Protect stored account data |
| | 4 | Protect cardholder data with strong cryptography during transmission over open, public networks |
| **Maintain a Vulnerability Management Program** | 5 | Protect all systems and networks from malicious software |
| | 6 | Develop and maintain secure systems and software |
| **Implement Strong Access Control Measures** | 7 | Restrict access to system components and cardholder data by business need to know |
| | 8 | Identify users and authenticate access to system components |
| | 9 | Restrict physical access to cardholder data |
| **Regularly Monitor and Test Networks** | 10 | Log and monitor all access to system components and cardholder data |
| | 11 | Test security of systems and networks regularly |
| **Maintain an Information Security Policy** | 12 | Support information security with organizational policies and programs |

---

## Cardholder Data Elements

| Element | Storage Permitted | Protection Required | Render Unreadable |
|---------|-------------------|--------------------|--------------------|
| Primary Account Number (PAN) | Yes | Yes | Yes (Req. 3.5) |
| Cardholder Name | Yes | Yes | No |
| Service Code | Yes | Yes | No |
| Expiration Date | Yes | Yes | No |
| Full Track Data (magnetic stripe, chip) | **No** — never after authorization | N/A | N/A |
| CAV2/CVC2/CVV2/CID | **No** — never after authorization | N/A | N/A |
| PIN / PIN Block | **No** — never after authorization | N/A | N/A |

Methods to render PAN unreadable (Requirement 3.5):
- One-way hashes based on strong cryptography (of the entire PAN)
- Truncation (first six and last four digits is the maximum displayable)
- Index tokens and pads (pads must be securely stored)
- Strong cryptography with associated key-management processes

---

## Scoping the CDE

```
┌─────────────────────────────────────────────────┐
│                 Out of Scope                     │
│  Systems with no connectivity to the CDE         │
│  and no impact on security of CHD                │
│                                                  │
│  ┌───────────────────────────────────────────┐   │
│  │          Connected-to / Security-          │   │
│  │          Impacting Systems                 │   │
│  │  Systems that connect to or could impact   │   │
│  │  the security of the CDE                   │   │
│  │                                            │   │
│  │  ┌─────────────────────────────────────┐   │   │
│  │  │     Cardholder Data Environment     │   │   │
│  │  │  Systems that store, process, or    │   │   │
│  │  │  transmit CHD or SAD                │   │   │
│  │  └─────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

Steps to define scope:
1. Identify all locations where CHD is stored, processed, or transmitted
2. Identify all system components in the CDE
3. Identify connected-to and security-impacting systems
4. Apply network segmentation to minimize scope (see `network-segmentation.md`)
5. Document and validate scope annually and after significant changes

---

## Do / Don't

- **Do** scope your CDE before starting any compliance work. Accurate scoping
  determines which systems, processes, and people are subject to PCI DSS.
- **Do** use network segmentation to isolate the CDE from the rest of the
  network. Segmentation is not required but dramatically reduces scope and cost.
- **Do** eliminate SAD (track data, CVV, PIN) immediately after authorization.
  There is no business justification for retaining SAD post-authorization.
- **Do** implement tokenization or truncation to minimize the amount of stored
  PAN. Less stored data means less exposure.
- **Do** assign a dedicated PCI DSS compliance owner responsible for the
  compliance program, assessments, and remediation tracking.
- **Don't** store SAD after authorization — ever. This is the single most
  critical rule in PCI DSS. Violations result in severe penalties.
- **Don't** assume that outsourcing card processing eliminates PCI DSS
  obligations. You must still validate compliance for your environment and
  manage third-party risks.
- **Don't** use the same cryptographic keys for test/development and production
  environments.
- **Don't** rely solely on compliance checklists. PCI DSS v4.0 emphasizes a
  customized approach — understand the security objective behind each
  requirement.

---

## Common Pitfalls

1. **Scope creep from flat networks.** Without segmentation, every system on
   the network is in scope for PCI DSS. Solution: implement and validate
   network segmentation (see `network-segmentation.md`) to isolate the CDE.
2. **Storing SAD after authorization.** Developers log full track data or CVV
   for debugging. Solution: never log SAD, implement automated scanning for
   PAN/SAD in logs and databases, and train developers on data handling rules.
3. **Incomplete data discovery.** Organizations miss cardholder data in
   unexpected locations (spreadsheets, email, backups, legacy systems).
   Solution: run regular data discovery scans across all systems and storage.
4. **Treating compliance as annual.** PCI DSS requires continuous compliance,
   not just passing an annual assessment. Solution: implement continuous
   monitoring, regular internal scans, and ongoing security awareness training.
5. **Ignoring third-party risk.** Service providers handling CHD are not
   assessed or monitored. Solution: maintain an inventory of all third-party
   service providers with access to CHD, verify their PCI DSS compliance
   status, and include PCI DSS requirements in contracts.

---

## Checklist

- [ ] Cardholder data environment (CDE) identified and documented
- [ ] All data flows involving CHD and SAD mapped
- [ ] Network segmentation implemented to isolate the CDE
- [ ] SAD is not stored after authorization (verified by scanning)
- [ ] PAN rendered unreadable wherever stored (encryption, truncation, tokenization, or hashing)
- [ ] All 12 PCI DSS requirements assessed against the current environment
- [ ] Compliance validation method determined (SAQ type or ROC)
- [ ] Approved Scanning Vendor (ASV) engaged for quarterly external scans
- [ ] Internal vulnerability scans conducted quarterly
- [ ] Penetration testing performed annually and after significant changes
- [ ] PCI DSS compliance owner assigned with documented responsibilities
- [ ] Third-party service providers inventoried and compliance verified
- [ ] Incident response plan includes payment card breach procedures
- [ ] Annual PCI DSS scope validation documented
