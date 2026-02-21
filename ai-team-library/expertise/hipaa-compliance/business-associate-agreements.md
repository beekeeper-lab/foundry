# Business Associate Agreements

Standards for establishing and managing Business Associate Agreements (BAAs)
as required by HIPAA (45 CFR § 164.502(e), § 164.504(e), and § 164.314).
A BAA is a contract between a covered entity and a business associate that
establishes permitted uses and disclosures of PHI and requires the business
associate to implement appropriate safeguards.

---

## Defaults

- **Requirement:** A covered entity must obtain satisfactory assurances from
  its business associates that they will appropriately safeguard PHI. These
  assurances must be documented in a BAA.
- **Scope:** Any person or entity that creates, receives, maintains, or
  transmits PHI on behalf of a covered entity (excluding members of the
  covered entity's own workforce).
- **Liability:** Under the Omnibus Rule (2013), business associates are
  directly liable for HIPAA Security Rule compliance and certain Privacy
  Rule provisions.
- **Subcontractors:** Business associates must obtain BAAs from their own
  subcontractors that create, receive, maintain, or transmit PHI.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| Full BAA with all required provisions | Addendum to existing master services agreement | When an MSA already exists and the BAA provisions can be cleanly incorporated |
| Annual BAA compliance review | Biennial review | Only for low-risk associates with stable operations — annual is strongly recommended |
| Right to audit business associate | Reliance on SOC 2 report | When the business associate is a large vendor with independently audited security programs |
| 30-day breach notification from BA to CE | Shorter window (e.g., 5-10 days) | When the covered entity needs more time for its own 60-day notification obligation |

---

## Required BAA Provisions

| Provision | Description |
|-----------|-------------|
| **Permitted uses and disclosures** | Specify the permitted and required uses and disclosures of PHI by the business associate |
| **Safeguards** | Require the business associate to use appropriate safeguards to prevent unauthorized use or disclosure |
| **Reporting** | Require the business associate to report any use or disclosure not provided for in the agreement, including breaches of unsecured PHI |
| **Subcontractor assurances** | Require the business associate to obtain satisfactory assurances from subcontractors that create, receive, maintain, or transmit PHI |
| **Individual access** | Require the business associate to make PHI available to individuals to satisfy the right of access |
| **Amendment** | Require the business associate to make PHI available for amendment and incorporate amendments |
| **Accounting of disclosures** | Require the business associate to make information available to provide an accounting of disclosures |
| **HHS access** | Require the business associate to make its practices, books, and records available to HHS for compliance determination |
| **Return or destruction** | Require the business associate to return or destroy all PHI at termination, if feasible |
| **Termination** | Authorize the covered entity to terminate the agreement if the business associate violates a material term |

---

## Common Business Associates

| Type | Examples | Key PHI Risks |
|------|----------|---------------|
| **Cloud service providers** | AWS, Azure, GCP hosting ePHI workloads | Data storage, backup, multi-tenancy isolation |
| **EHR/EMR vendors** | Epic, Cerner, Athenahealth | Full patient records, clinical data, billing |
| **Billing and claims processors** | Third-party billing services, clearinghouses | Patient demographics, diagnosis codes, financial data |
| **IT service providers** | Managed service providers, consultants with system access | Remote access to ePHI systems, potential for broad exposure |
| **Data analytics and research** | Population health platforms, de-identification services | Aggregated patient data, re-identification risk |
| **Legal and accounting firms** | Firms that receive PHI for professional services | Medical records used in legal proceedings, audit evidence |
| **Destruction services** | Shredding companies, e-waste recyclers | Paper records, hard drives, media containing PHI |

---

## Do / Don't

- **Do** maintain an inventory of all business associates and their BAAs.
  Track execution dates, renewal dates, and compliance status.
- **Do** include breach notification timelines in the BAA that give the
  covered entity sufficient time to meet its own 60-day obligation.
- **Do** require business associates to obtain BAAs from their
  subcontractors. The chain of protection must extend downstream.
- **Do** include a right to audit or require independent security
  assessments (e.g., SOC 2 Type II) to verify safeguard implementation.
- **Do** address BAA obligations during vendor selection, not after
  contract execution.
- **Don't** use a BAA as a substitute for due diligence. Signing a BAA
  does not absolve the covered entity of responsibility if it knew or
  should have known the business associate was non-compliant.
- **Don't** allow BAAs to auto-renew without periodic review. Business
  associate relationships and risk profiles change over time.
- **Don't** overlook the return-or-destroy provision at contract
  termination. PHI left with a former business associate is an ongoing
  compliance risk.
- **Don't** assume that a cloud provider's standard terms of service
  constitute a BAA. Obtain an explicit, signed BAA.

---

## Common Pitfalls

1. **Missing BAAs.** The organization works with vendors who handle PHI but
   has no executed BAA in place. Solution: inventory all vendors, identify
   those that meet the definition of business associate, and execute BAAs
   before sharing PHI.
2. **Boilerplate BAAs.** The organization uses a generic BAA template that
   does not reflect the actual services or PHI flows. Solution: tailor each
   BAA to the specific relationship, data types, and services involved.
3. **No subcontractor flow-down.** The BAA does not require the business
   associate to extend protections to its subcontractors. Solution: include
   explicit subcontractor provisions and verify compliance.
4. **Termination gaps.** When a business associate relationship ends, PHI
   is not returned or destroyed. Solution: include specific return-or-destroy
   procedures and timelines in the BAA, and verify completion.
5. **Unmonitored compliance.** The BAA is signed and filed but the covered
   entity never verifies the business associate's safeguards. Solution:
   implement ongoing monitoring through audits, security assessments, or
   SOC 2 report reviews.

---

## Checklist

- [ ] Business associate inventory maintained and current
- [ ] BAAs executed with all business associates before PHI is shared
- [ ] Each BAA includes all required provisions (uses, safeguards, reporting, subcontractors, individual rights, HHS access, return/destroy, termination)
- [ ] Breach notification timelines in BAAs support the covered entity's 60-day obligation
- [ ] BAA compliance reviewed at least annually
- [ ] Subcontractor flow-down requirements included and verified
- [ ] Right to audit or independent assessment requirement included
- [ ] BAA provisions addressed during vendor selection and procurement
- [ ] Return-or-destroy procedures defined and executed at termination
- [ ] BAA inventory tracks execution dates, renewal dates, and compliance status
