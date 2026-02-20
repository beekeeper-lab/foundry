# Internal Controls

Standards for designing, implementing, and evaluating internal controls over
financial reporting (ICFR) as required by the Sarbanes-Oxley Act of 2002.
Section 404 requires management to assess and report on the effectiveness
of ICFR annually.

---

## Defaults

- **Framework:** COSO Internal Control — Integrated Framework (2013) is the
  de facto standard for SOX compliance.
- **Scope:** All controls that could materially affect financial reporting.
- **Assessment:** Annual management assessment of ICFR effectiveness
  (SOX Section 404(a)). External auditor attestation for accelerated filers
  (SOX Section 404(b)).
- **Documentation:** Every control must be documented with: objective,
  description, frequency, owner, evidence, and test results.

---

## COSO Framework Components

| Component | Description | SOX Application |
|-----------|-------------|-----------------|
| **Control Environment** | Tone at the top, organizational values, governance structure | Board oversight, management integrity, ethical values |
| **Risk Assessment** | Identifying and analyzing risks to achieving objectives | Financial reporting risks, fraud risk assessment |
| **Control Activities** | Policies and procedures that mitigate identified risks | Approvals, authorizations, reconciliations, reviews |
| **Information & Communication** | Relevant information is identified, captured, and communicated | Financial reporting systems, IT controls, disclosure |
| **Monitoring Activities** | Ongoing evaluations and separate evaluations of controls | Internal audit, management testing, deficiency tracking |

---

## Control Types

| Type | Description | Examples |
|------|-------------|---------|
| **Preventive** | Designed to prevent errors or irregularities before they occur | Segregation of duties, access controls, approval workflows |
| **Detective** | Designed to detect errors or irregularities after they occur | Reconciliations, variance analysis, exception reports |
| **Manual** | Performed by people | Manager review and approval of journal entries |
| **Automated** | Performed by IT systems | System-enforced approval thresholds, automated three-way match |
| **IT-Dependent Manual** | Manual control that relies on IT-generated data | Review of system-generated aging report |

---

## Key Control Areas for Software Companies

| Area | Key Controls |
|------|-------------|
| **Revenue recognition** | Contract review and approval, milestone documentation, revenue cutoff procedures |
| **Accounts payable** | Purchase order matching, vendor master file changes, payment authorization |
| **Financial close** | Journal entry review, account reconciliation, period-end cutoff |
| **IT general controls** | Access management, change management, backup and recovery (see `itgc.md`) |
| **Equity and stock compensation** | Grant approvals, fair value calculations, vesting schedules |
| **Expense management** | Expense report approval, credit card reconciliation, travel policy compliance |

---

## Do / Don't

- **Do** document controls at a level of detail sufficient for a third party
  to understand and test them.
- **Do** identify key controls — the critical few that, if they fail, could
  result in a material misstatement.
- **Do** test controls regularly, not just at year-end.
- **Do** remediate deficiencies promptly. A control deficiency left unaddressed
  can escalate to a material weakness.
- **Do** maintain a risk-control matrix mapping financial statement assertions
  to specific controls.
- **Don't** treat SOX compliance as a standalone project. Integrate controls
  into daily business operations.
- **Don't** rely solely on detective controls. Preventive controls are more
  cost-effective and reduce risk of errors reaching financial statements.
- **Don't** assume automated controls are inherently reliable. They depend
  on IT general controls (access, change management) being effective.
- **Don't** document controls that don't actually operate. If the control
  exists on paper but is not performed, it provides zero assurance.

---

## Common Pitfalls

1. **Over-documentation.** Documenting every process as a "control" when only
   a subset are key controls. Solution: focus on controls that address risks
   of material misstatement.
2. **Control owner confusion.** Nobody knows who is responsible for performing
   or monitoring the control. Solution: assign a single accountable owner to
   each key control.
3. **Untested controls.** Controls are documented but never tested for operating
   effectiveness. Solution: establish a testing calendar with clear ownership.
4. **Deficiency escalation.** A control deficiency is discovered in Q4 with no
   time to remediate before year-end. Solution: test throughout the year to
   catch issues early.
5. **Excessive reliance on spreadsheets.** Critical financial data lives in
   uncontrolled spreadsheets with no access controls or version management.
   Solution: migrate key financial processes to controlled systems.

---

## Deficiency Classification

| Classification | Definition | Reporting |
|---------------|------------|-----------|
| **Control Deficiency** | A control does not allow management or employees to prevent or detect misstatements on a timely basis | Internal reporting |
| **Significant Deficiency** | A deficiency, or combination of deficiencies, that is less severe than a material weakness but important enough to merit attention | Reported to audit committee |
| **Material Weakness** | A deficiency, or combination of deficiencies, such that there is a reasonable possibility that a material misstatement will not be prevented or detected on a timely basis | Disclosed in annual report (10-K) |

---

## Checklist

- [ ] COSO framework adopted and documented
- [ ] Risk assessment performed for financial reporting risks
- [ ] Key controls identified and mapped to financial statement assertions
- [ ] Each key control has: objective, description, frequency, owner, evidence
- [ ] Segregation of duties evaluated and enforced
- [ ] Control testing plan established with calendar and ownership
- [ ] Deficiency tracking process in place with escalation criteria
- [ ] Management assessment of ICFR effectiveness completed annually
- [ ] External auditor attestation obtained (if required — accelerated filers)
- [ ] Remediation actions tracked and verified
