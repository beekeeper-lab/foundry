---
id: hipaa-compliance
category: Compliance & Governance
entry: true
last-reviewed: 2026-07
---

# HIPAA Compliance Conventions

## Category
Compliance & Governance

Non-negotiable defaults for handling protected health information (PHI) under
HIPAA, as amended by the HITECH Act (2009) and the Omnibus Rule (2013). These
conventions cover the Privacy and Security Rules, safeguards for ePHI,
business associate agreements, and breach notification. Deviations require a
documented risk assessment and sign-off.

---

## Defaults

| Concern | Default |
|---------|---------|
| Scope | Covered entities and business associates; PHI in any form — electronic, paper, or oral |
| Use/disclosure standard | Minimum necessary for every use, disclosure, and request (treatment purposes exempt) |
| Encryption at rest | AES-256 for ePHI (AES-128 acceptable; 256 preferred) |
| Encryption in transit | TLS 1.2+ (VPN tunnel when point-to-point encryption is impractical) |
| Access control | Role-based access control (RBAC); unique user ID per person, no shared accounts |
| Remote access | Multi-factor authentication (single-factor only with documented compensating controls) |
| Addressable specs | Not optional — implement, implement an alternative, or document why not reasonable |
| De-identification | Expert Determination (§ 164.514(b)(1)) or Safe Harbor: remove all 18 identifiers (§ 164.514(b)(2)) |
| Individual access requests | Respond within 30 days (one 30-day extension with written notice) |
| Breach presumption | Impermissible use/disclosure is presumed a breach unless the four-factor risk assessment shows low probability of compromise |
| Breach notification | Individuals within 60 days of discovery; HHS + media within 60 days for 500+ affected; small breaches logged annually to HHS |
| Vendors handling PHI | Executed BAA before PHI is shared; BA-to-CE breach notice window (default 30 days, shorter when needed) |
| Documentation retention | 6 years for all HIPAA policies, procedures, and actions |
| Enforcement exposure | Four penalty tiers, ~$137–$68,928 per violation, ~$2.07M annual cap per category; criminal penalties for knowing violations |

---

## 1. Privacy Rule

- Provide a Notice of Privacy Practices (NPP) describing how PHI may be used
  and disclosed.
- Honor individual rights: access, amendment, restriction, and accounting of
  disclosures. Access requests get a response within 30 days.
- Permitted uses without authorization: treatment, payment, healthcare
  operations, plus specific public-health and law-enforcement conditions.
  Marketing uses require written authorization (limited face-to-face and
  nominal-gift exceptions).
- Apply the minimum necessary standard to every use, disclosure, and request
  except treatment. Implement it via role-based access policies.
- De-identified data is only non-PHI after Safe Harbor (all 18 identifiers
  removed) or Expert Determination — never by assumption.

Full detail: `privacy-security-rules.md` (including the 18-identifier table).

---

## 2. Security Rule Safeguards

The Security Rule (45 CFR § 164.308, § 164.310, § 164.312) requires three
families of safeguards for ePHI, each with Required (R) and Addressable (A)
specifications:

- **Administrative (§ 164.308):** security management process, risk analysis
  and risk management (both R), sanction policy, activity review, a designated
  security official, workforce training, incident procedures, contingency
  plan, periodic evaluation.
- **Physical (§ 164.310):** facility access controls, workstation use and
  security, device/media controls including disposal and re-use procedures.
- **Technical (§ 164.312):** access control with unique user identification,
  emergency access, automatic logoff, encryption, audit controls, integrity,
  authentication, transmission security.

Rules:
- Risk analysis is the foundation: inventory and assess every system,
  application, and device that creates, receives, maintains, or transmits ePHI.
- Encrypt ePHI at rest and in transit. Encryption is addressable, but failing
  to encrypt is a leading cause of enforcement actions — and encrypted PHI
  that is breached does not require notification.
- Audit controls must include regular log review; logging without review is
  insufficient.
- Test the contingency plan (backups, disaster recovery, emergency mode) at
  least annually.

Full detail: `safeguards.md`.

---

## 3. Business Associate Agreements

- Execute a BAA with every person or entity that creates, receives,
  maintains, or transmits PHI on your behalf — before sharing PHI. A cloud
  provider's standard terms of service are not a BAA.
- Required provisions: permitted uses/disclosures, safeguards, breach
  reporting, subcontractor flow-down, individual access and amendment,
  accounting of disclosures, HHS access, return-or-destroy at termination,
  and termination for material violation (45 CFR § 164.502(e), § 164.504(e),
  § 164.314).
- Business associates are directly liable under the Omnibus Rule and must
  obtain BAAs from their own subcontractors.
- Maintain a BAA inventory (execution dates, renewals, compliance status);
  review compliance at least annually via audits or SOC 2 report review.
- Set BA-to-CE breach notification windows that leave room for your own
  60-day obligation.

Full detail: `business-associate-agreements.md`.

---

## 4. Breach Notification

- A breach is an impermissible acquisition, access, use, or disclosure of
  unsecured PHI that compromises its security or privacy (45 CFR
  §§ 164.400–164.414). It is presumed a breach unless a documented
  **four-factor risk assessment** demonstrates low probability of compromise:
  (1) nature and extent of the PHI, (2) the unauthorized person, (3) whether
  PHI was actually acquired or viewed, (4) extent of mitigation.
- Exceptions: good-faith unintentional workforce acquisition, inadvertent
  disclosure between authorized persons, and good-faith belief the recipient
  could not retain the information.
- Notify individuals within 60 days of discovery by first-class mail (email
  only if previously agreed), including: what happened, PHI types involved,
  protective steps, entity remediation, and contact information.
- 500+ individuals: notify HHS within 60 days and prominent media serving any
  state with 500+ affected. Under 500: log and report annually to HHS.
- The 60-day clock starts when the breach is known **or reasonably should
  have been known** — check state laws, which may impose shorter timelines.

Full detail: `breach-notification.md` (including penalty tiers).

---

## Do / Don't

**Do:**
- Conduct a thorough risk analysis before designing the security program —
  it is the foundation of HIPAA compliance.
- Encrypt ePHI at rest and in transit; encrypted PHI is "secured" and exempt
  from breach notification.
- Document everything — safeguard decisions, addressable-spec assessments,
  risk assessments for incidents that did **not** require notification — and
  retain for 6 years.
- Train all workforce members on role-relevant HIPAA policies, including
  recognizing and immediately reporting potential breaches.
- Track state breach notification laws and apply the most restrictive
  timeline.

**Don't:**
- Treat addressable specifications as optional — assess, implement or
  substitute, and document.
- Use shared accounts for ePHI access; unique user IDs are required for
  audit trails.
- Assume cloud providers handle safeguards or that their terms of service
  constitute a BAA — verify via signed BAAs and independent assessments.
- Ignore oral and paper PHI; the Privacy Rule covers all forms.
- Delay breach investigation to avoid starting the 60-day clock — willful
  delay increases penalty exposure.

---

## Common Pitfalls

1. **Incomplete risk analysis.** Superficial assessments miss systems holding
   ePHI. Inventory every system, application, and device — including mobile.
2. **Addressable confusion.** Skipping addressable specifications as
   "optional." Each requires a documented assessment.
3. **Encryption gaps.** ePHI encrypted in transit but not at rest (or vice
   versa). Cover all states and document the standards used.
4. **Audit log neglect.** Logs enabled but never reviewed. Assign review
   responsibility and escalation procedures.
5. **Missing or boilerplate BAAs.** Vendors handle PHI with no executed BAA,
   or generic templates that don't match actual PHI flows and lack
   subcontractor flow-down.
6. **State law conflicts.** Following HIPAA's 60-day breach timeline while a
   state law requires 30. Maintain a state-law matrix.
7. **Stale policies and untested plans.** Policies written once and never
   updated; contingency plans never exercised. Review annually and test.

---

## Checklist

- [ ] Risk analysis covers all systems, applications, and devices with ePHI
- [ ] Security official designated; risk management plan documented
- [ ] Administrative, physical, and technical safeguards implemented
- [ ] ePHI encrypted at rest (AES-256) and in transit (TLS 1.2+)
- [ ] Unique user IDs enforced; RBAC aligned to minimum necessary
- [ ] Audit logs enabled, reviewed regularly, retained per policy
- [ ] Contingency plan documented and tested annually
- [ ] Addressable specifications assessed and documented
- [ ] Notice of Privacy Practices published; individual rights procedures live
- [ ] Workforce HIPAA training completed and documented
- [ ] BAA inventory current; BAAs executed before PHI is shared
- [ ] Incident response plan includes four-factor risk assessment template
- [ ] HHS breach portal access established; breach log maintained
- [ ] State breach notification laws inventoried; strictest timeline applied
- [ ] All HIPAA documentation retained for 6+ years
