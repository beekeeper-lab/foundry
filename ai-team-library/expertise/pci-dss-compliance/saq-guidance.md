# SAQ Guidance

Self-Assessment Questionnaire (SAQ) guidance for organizations validating PCI
DSS compliance. SAQs are validation tools for merchants and service providers
that are not required to undergo a full on-site assessment (Report on
Compliance). The correct SAQ type depends on how cardholder data is handled.

---

## Defaults

- **Validation method:** Merchants determine SAQ eligibility based on payment
  brand rules and their acquirer's requirements.
- **Assessment frequency:** Annual SAQ submission, supplemented by quarterly
  ASV scans (for SAQ types that require them).
- **Attestation:** Each SAQ is accompanied by an Attestation of Compliance
  (AOC) signed by an authorized officer of the organization.
- **Remediation:** Any "No" or "N/A" response that is not legitimately
  not applicable must be remediated before the SAQ is considered compliant.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| SAQ (self-assessment) | Report on Compliance (ROC) with QSA | Required for Level 1 merchants (>6M transactions/year) and any entity required by payment brands or acquirer |
| Annual SAQ cycle | Continuous compliance validation | Organizations with high change velocity where annual snapshots are insufficient |
| Internal assessment | QSA-assisted SAQ | When the organization lacks internal PCI DSS expertise to accurately complete the SAQ |

---

## SAQ Types

| SAQ | Description | Applies To | Quarterly ASV Scan Required |
|-----|-------------|------------|----------------------------|
| **A** | Card-not-present merchants that have fully outsourced all account data functions to PCI DSS compliant third parties | E-commerce or mail/telephone-order merchants with no electronic cardholder data storage, processing, or transmission on their systems | No |
| **A-EP** | E-commerce merchants that partially outsource payment processing to a PCI DSS validated third party | E-commerce merchants whose website does not receive cardholder data but affects the security of the payment transaction (e.g., redirect or iFrame) | Yes |
| **B** | Merchants using only imprint machines or standalone dial-out terminals | Brick-and-mortar merchants with no electronic cardholder data storage; terminals are not connected to the internet | No |
| **B-IP** | Merchants using only standalone PTS-approved payment terminals with IP connectivity | Brick-and-mortar merchants with IP-connected terminals; no electronic cardholder data storage | Yes |
| **C** | Merchants with payment application systems connected to the internet | Merchants with a payment application connected to the internet; no electronic cardholder data storage | Yes |
| **C-VT** | Merchants using only web-based virtual terminals | Merchants who manually enter one transaction at a time via a virtual terminal provided by a PCI DSS compliant service provider; no electronic cardholder data storage | No |
| **D (Merchants)** | All other merchants | Merchants that do not fit into any other SAQ type, including those that store cardholder data electronically | Yes |
| **D (Service Providers)** | Service providers eligible to complete an SAQ | Service providers validated by a payment brand as eligible for SAQ (not required to complete a ROC) | Yes |
| **P2PE** | Merchants using a validated P2PE solution | Merchants that use hardware payment terminals included in a PCI SSC listed P2PE solution; no access to clear-text cardholder data | No |

---

## SAQ Selection Decision Tree

```
Start: How does your organization handle cardholder data?

  ├─ All card data functions fully outsourced (card-not-present)?
  │   └─ Yes → SAQ A
  │
  ├─ E-commerce with redirect/iFrame (no direct CHD handling)?
  │   └─ Yes → SAQ A-EP
  │
  ├─ Imprint machine or standalone dial-out terminal only?
  │   └─ Yes → SAQ B
  │
  ├─ Standalone IP-connected PTS payment terminal only?
  │   └─ Yes → SAQ B-IP
  │
  ├─ PCI SSC validated P2PE solution with hardware terminals?
  │   └─ Yes → SAQ P2PE
  │
  ├─ Web-based virtual terminal (manual, one-at-a-time entry)?
  │   └─ Yes → SAQ C-VT
  │
  ├─ Payment application connected to the internet (no CHD storage)?
  │   └─ Yes → SAQ C
  │
  └─ None of the above?
      └─ SAQ D (Merchant) or SAQ D (Service Provider)
```

---

## Merchant Levels and Validation Requirements

Merchant levels are defined by individual payment brands. The following is
representative (Visa classification):

| Level | Annual Transactions | Validation Requirement |
|-------|--------------------|-----------------------|
| **1** | Over 6 million | Annual ROC by QSA (or ISA), quarterly ASV scan |
| **2** | 1–6 million | Annual SAQ, quarterly ASV scan |
| **3** | 20,000–1 million (e-commerce) | Annual SAQ, quarterly ASV scan |
| **4** | Fewer than 20,000 (e-commerce) or up to 1 million (other) | Annual SAQ, quarterly ASV scan (recommended) |

> **Note:** Transaction thresholds and requirements vary by payment brand.
> Always confirm specific requirements with your acquirer and each payment
> brand.

---

## Completing an SAQ

| Step | Description |
|------|-------------|
| **1. Determine scope** | Identify all system components, people, and processes that store, process, or transmit CHD (see `fundamentals.md`) |
| **2. Select SAQ type** | Use the decision tree above; confirm eligibility with your acquirer |
| **3. Assess each requirement** | For each question in the SAQ, evaluate your environment and select Yes, No, N/A, or Compensating Control |
| **4. Document compensating controls** | For requirements met via compensating controls, complete Appendix B and C of the SAQ |
| **5. Complete the AOC** | Sign the Attestation of Compliance — this is a formal declaration of compliance status |
| **6. Submit** | Provide the completed SAQ and AOC to your acquirer and/or payment brand as required |
| **7. Remediate gaps** | Address any "No" responses with a remediation plan and timeline |

---

## Compensating Controls

When an organization cannot meet a PCI DSS requirement as stated due to a
legitimate technical or business constraint, a compensating control may be
implemented. Compensating controls must:

1. Meet the intent and rigor of the original requirement
2. Provide a similar level of defense as the original requirement
3. Be above and beyond other PCI DSS requirements (not simply using another
   existing requirement as compensating)
4. Be commensurate with the additional risk imposed by not adhering to the
   original requirement
5. Be documented in the Compensating Controls Worksheet (Appendix B and C)

---

## Do / Don't

- **Do** confirm your SAQ eligibility with your acquirer before beginning the
  self-assessment. Using the wrong SAQ type invalidates your compliance
  validation.
- **Do** scope your environment accurately before starting the SAQ. An
  incorrect scope leads to an inaccurate assessment.
- **Do** complete the SAQ honestly. A "Yes" response means the requirement is
  fully implemented, tested, and maintained — not planned or partially done.
- **Do** document compensating controls thoroughly. Include the constraint,
  the control objective, the compensating control implemented, and evidence
  of its effectiveness.
- **Do** engage a QSA for guidance if your team lacks PCI DSS expertise.
  QSA-assisted SAQs are permitted for all SAQ types.
- **Don't** select a simpler SAQ type than your environment warrants. If your
  payment flow does not match the SAQ description exactly, use SAQ D.
- **Don't** mark requirements as "N/A" without verifying they truly do not
  apply to your environment. Improper N/A responses are a common audit finding.
- **Don't** treat the SAQ as a one-time event. PCI DSS compliance must be
  maintained continuously, not just at assessment time.
- **Don't** forget that quarterly ASV scans are required for most SAQ types.
  An SAQ without passing ASV scans is incomplete.

---

## Common Pitfalls

1. **Wrong SAQ type.** Organizations select a simpler SAQ than their payment
   flow warrants. Solution: map your exact data flow — where CHD is captured,
   transmitted, processed, and stored — then match to the SAQ type definitions.
2. **Scope underestimation.** Systems connected to the CDE are excluded from
   the SAQ scope. Solution: include all connected-to and security-impacting
   systems when scoping (see `fundamentals.md` scoping guidance).
3. **Compensating controls without documentation.** Organizations implement
   alternative measures but do not complete the Compensating Controls Worksheet.
   Solution: document every compensating control in Appendix B and C before
   submitting the SAQ.
4. **Stale SAQ responses.** The environment has changed since the last SAQ
   but responses are carried forward without re-evaluation. Solution: re-assess
   every requirement against the current environment each year.
5. **Ignoring payment brand differences.** Each payment brand (Visa,
   Mastercard, etc.) has its own merchant level definitions and requirements.
   Solution: check each brand's compliance program documentation and confirm
   with your acquirer.

---

## Checklist

- [ ] SAQ eligibility confirmed with acquirer
- [ ] Correct SAQ type selected based on cardholder data flow
- [ ] CDE scope documented and validated before assessment
- [ ] All SAQ requirements assessed against current environment
- [ ] Compensating controls documented in Appendix B and C (if applicable)
- [ ] Attestation of Compliance (AOC) signed by authorized officer
- [ ] Quarterly ASV scans completed and passing (if required by SAQ type)
- [ ] SAQ and AOC submitted to acquirer and/or payment brands
- [ ] Remediation plan created for any "No" responses with target dates
- [ ] SAQ reassessment scheduled for next annual cycle
