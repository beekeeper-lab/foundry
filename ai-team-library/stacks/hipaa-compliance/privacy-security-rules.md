# Privacy and Security Rules

Standards for complying with the HIPAA Privacy Rule (45 CFR Part 160 and
Subparts A and E of Part 164) and the HIPAA Security Rule (45 CFR Part 160
and Subparts A and C of Part 164). The Privacy Rule governs the use and
disclosure of protected health information (PHI). The Security Rule
establishes safeguards for electronic PHI (ePHI).

---

## Defaults

- **Regulation:** Health Insurance Portability and Accountability Act of
  1996, as amended by the HITECH Act (2009) and the Omnibus Rule (2013).
- **Scope:** All covered entities (health plans, healthcare clearinghouses,
  healthcare providers who transmit health information electronically) and
  their business associates.
- **Protected health information (PHI):** Individually identifiable health
  information transmitted or maintained in any form — electronic, paper, or
  oral.
- **Minimum necessary standard:** Use, disclose, and request only the
  minimum amount of PHI needed to accomplish the intended purpose.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| Minimum necessary disclosure | Full dataset access | Only for treatment purposes, which are exempt from minimum necessary |
| Individual authorization required for marketing uses | No authorization | Only when the communication is face-to-face or involves promotional gifts of nominal value |
| 30-day response window for individual access requests | Extended to 60 days | Only when the entity cannot meet the 30-day deadline and provides written notice |
| De-identification via Expert Determination (§ 164.514(b)(1)) | Safe Harbor method (§ 164.514(b)(2)) | When statistical expertise is unavailable; remove all 18 identifiers |

---

## Privacy Rule — Key Requirements

| Requirement | Description |
|-------------|-------------|
| **Notice of Privacy Practices (NPP)** | Covered entities must provide individuals with a clear description of how their PHI may be used and disclosed |
| **Individual rights** | Right to access, amend, restrict, and receive an accounting of disclosures of their PHI |
| **Minimum necessary** | Limit PHI use, disclosure, and requests to the minimum necessary for the purpose |
| **Permitted uses and disclosures** | Treatment, payment, healthcare operations, public health, law enforcement (under specific conditions) |
| **Authorization** | Uses beyond permitted purposes require written individual authorization |
| **De-identification** | PHI from which all 18 identifiers have been removed (Safe Harbor) or that an expert certifies carries very small re-identification risk |

---

## Security Rule — Key Requirements

| Requirement | Description |
|-------------|-------------|
| **Risk analysis** | Conduct an accurate and thorough assessment of potential risks and vulnerabilities to ePHI (§ 164.308(a)(1)(ii)(A)) |
| **Risk management** | Implement security measures to reduce risks to a reasonable and appropriate level (§ 164.308(a)(1)(ii)(B)) |
| **Administrative safeguards** | Security management, workforce security, information access management, security awareness training, contingency planning (see `safeguards.md`) |
| **Physical safeguards** | Facility access controls, workstation use and security, device and media controls (see `safeguards.md`) |
| **Technical safeguards** | Access control, audit controls, integrity controls, transmission security (see `safeguards.md`) |
| **Organizational requirements** | Business associate agreements, policies and procedures, documentation retention (6 years) |

---

## The 18 PHI Identifiers (Safe Harbor)

| # | Identifier |
|---|-----------|
| 1 | Names |
| 2 | Geographic data smaller than a state |
| 3 | Dates (except year) related to an individual |
| 4 | Phone numbers |
| 5 | Fax numbers |
| 6 | Email addresses |
| 7 | Social Security numbers |
| 8 | Medical record numbers |
| 9 | Health plan beneficiary numbers |
| 10 | Account numbers |
| 11 | Certificate/license numbers |
| 12 | Vehicle identifiers and serial numbers |
| 13 | Device identifiers and serial numbers |
| 14 | Web URLs |
| 15 | IP addresses |
| 16 | Biometric identifiers |
| 17 | Full-face photographs and comparable images |
| 18 | Any other unique identifying number, characteristic, or code |

---

## Do / Don't

- **Do** conduct a thorough risk analysis before designing your security
  program. The risk analysis is the foundation of HIPAA compliance.
- **Do** apply the minimum necessary standard to every use, disclosure,
  and request for PHI — except for treatment purposes.
- **Do** provide individuals with access to their PHI within 30 days
  of request (extendable once by 30 days with written notice).
- **Do** maintain documentation of all HIPAA policies, procedures, and
  actions for a minimum of 6 years.
- **Do** train all workforce members on HIPAA policies and procedures
  relevant to their role.
- **Don't** assume de-identified data is safe by default. Verify
  de-identification using either Expert Determination or Safe Harbor
  before treating data as non-PHI.
- **Don't** disclose PHI for marketing purposes without individual
  authorization (limited exceptions for face-to-face and nominal gifts).
- **Don't** ignore the oral and paper dimensions of PHI. The Privacy Rule
  covers all forms, not just electronic data.
- **Don't** treat the Security Rule as a one-time project. Risk analysis
  and risk management are ongoing obligations.

---

## Common Pitfalls

1. **Incomplete risk analysis.** Organizations perform a superficial risk
   analysis that does not cover all systems containing ePHI. Solution:
   inventory every system, application, and device that creates, receives,
   maintains, or transmits ePHI, and assess each one.
2. **Confusing privacy and security.** Teams address technical controls
   (Security Rule) but neglect use-and-disclosure policies (Privacy Rule),
   or vice versa. Solution: treat Privacy and Security as complementary
   programs that must be coordinated.
3. **Overlooking oral PHI.** Security controls focus on electronic systems
   but staff discuss patient information in public areas. Solution: include
   physical and administrative controls for oral disclosures (private
   offices, lowered voices, need-to-know conversations).
4. **Missing minimum necessary analysis.** The organization has not defined
   role-based access policies that limit PHI access to what is necessary
   for each job function. Solution: implement role-based access controls
   and review them periodically.
5. **Stale policies.** HIPAA policies were written once and never updated.
   Solution: review and update policies annually or whenever there is a
   significant change in operations, technology, or regulations.

---

## Checklist

- [ ] Risk analysis conducted covering all systems with ePHI
- [ ] Risk management plan documented with prioritized remediation actions
- [ ] Notice of Privacy Practices published and distributed
- [ ] Individual rights procedures in place (access, amendment, restriction, accounting)
- [ ] Minimum necessary policies defined for each role
- [ ] Workforce training completed and documented
- [ ] HIPAA policies and procedures documented and retained (6-year minimum)
- [ ] De-identification procedures verified (Safe Harbor or Expert Determination)
- [ ] Security Rule safeguards implemented (administrative, physical, technical)
- [ ] Sanctions policy established for workforce violations
