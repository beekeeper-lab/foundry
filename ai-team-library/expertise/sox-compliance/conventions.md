---
id: sox-compliance
category: Compliance & Governance
entry: true
last-reviewed: 2026-07
---

# SOX Compliance Conventions

## Category
Compliance & Governance

Standards for complying with the Sarbanes-Oxley Act of 2002: internal controls
over financial reporting (ICFR), IT general controls, segregation of duties,
and audit trails. Section 404 requires management to assess and report on ICFR
effectiveness annually; these conventions define the defaults that make that
assessment defensible.

---

## Defaults

| Concern | Default |
|---------|---------|
| Controls framework | COSO Internal Control — Integrated Framework (2013) |
| ITGC framework | COBIT or COSO IT controls guidance |
| Scope | All controls and IT systems that could materially affect financial reporting |
| Assessment cadence | Annual management assessment (SOX 404(a)); external auditor attestation for accelerated filers (404(b)) |
| Control documentation | Every control: objective, description, frequency, owner, evidence, test results |
| SoD minimum | Authorization, custody, and record-keeping performed by different individuals |
| SoD review | Matrix reviewed quarterly; access-level SoD monitored continuously where possible |
| Access reviews | Quarterly, signed off by application/data owners |
| Deprovisioning | Access removed within 24–48 hours of role change or termination |
| Change management | Developer ≠ approver ≠ deployer for all in-scope systems |
| Audit log retention | Minimum 7 years for financial records |
| Audit log integrity | Tamper-evident, append-only, centralized; real-time or near-real-time capture |

---

## 1. Internal Controls over Financial Reporting

- Adopt the COSO framework's five components: Control Environment, Risk
  Assessment, Control Activities, Information & Communication, Monitoring.
- Identify **key controls** — the critical few that, if they fail, could
  result in a material misstatement. Maintain a risk-control matrix mapping
  financial statement assertions to specific controls.
- Prefer preventive controls (SoD, access controls, approval workflows) over
  detective controls (reconciliations, exception reports); preventive is more
  cost-effective. Automated controls are only as reliable as the ITGCs
  (access, change management) beneath them.
- Test controls throughout the year, not just at year-end, and remediate
  deficiencies promptly. Classification escalates: control deficiency
  (internal reporting) → significant deficiency (audit committee) → material
  weakness (disclosed in the 10-K).

Full detail: `internal-controls.md`

---

## 2. IT General Controls (ITGC)

- Four domains: access to programs and data, program changes, program
  development, computer operations. ITGC failures undermine every automated
  control that depends on them.
- Access management: documented approval for all access requests, least
  privilege, quarterly owner-signed access reviews, deprovisioning within
  24–48 hours. Privileged access requires extra approval, is logged and
  reviewed; shared/generic accounts are prohibited or tightly controlled.
- Change management: change request → development (code review) → testing
  (documented results) → approval (business owner + IT management) →
  deployment by operations (never the developer) → post-deployment
  validation with rollback plan.
- Emergency changes get retroactive documentation and approval within 24–48
  hours; frequent emergency use indicates process breakdown.
- Test restores, not just backups.

Full detail: `itgc.md`

---

## 3. Segregation of Duties

- No single person controls all phases of a transaction. Separate the four
  core functions: authorization, custody, record-keeping, reconciliation.
  Two or more for the same process is a SoD conflict.
- Build a formal SoD matrix for all financially significant processes and
  enforce it with role-based access controls where possible.
- IT SoD is equally critical: developer/approver/deployer separation, DBA
  production access logged and reviewed, access provisioning independently
  approved.
- Where SoD cannot be achieved (small teams), document compensating controls
  that are written, tested for operating effectiveness, and proportionate to
  the risk — e.g., management review of all deployment logs within 24 hours.
- SoD exceptions require an expiration date and quarterly review.

Full detail: `segregation-of-duties.md`

---

## 4. Audit Trail

- Log at both the application layer (business context: who approved what) and
  the database layer (before/after values), plus system/access events, all
  feeding a centralized, tamper-evident log store.
- Log financial transactions (create/modify/delete/approve/post with approval
  chain), access events, data changes on financial tables, system and
  configuration changes, and access-management events.
- Evidence must be sufficient, appropriate, reliable (system-generated, not
  manually created after the fact), timely, and complete.
- Logs are append-only; no application user or administrator may modify or
  delete them. Never log secrets (passwords, full card numbers) — log the
  event, not the secret.
- Retain at least 7 years; automate retention enforcement; assign owners to
  review logs (detective controls require active review).

Full detail: `audit-trail.md`

---

## 5. Certifications and Key SOX Sections

- **Section 302** — CEO/CFO certify accuracy of financial reports and
  effectiveness of disclosure controls.
- **Section 404(a)/(b)** — management assessment of ICFR / external auditor
  attestation (accelerated filers, audited under PCAOB AS 2201).
- **Section 409** — rapid disclosure of material changes in financial
  condition.
- **Sections 802/906** — criminal penalties for document destruction and
  false certification.

Full detail: `references.md`

---

## Do / Don't

**Do:**
- Document controls in enough detail for a third party to understand and test.
- Enforce dev/approve/deploy separation — the most scrutinized ITGC control.
- Ship logs in real time to a separate, restricted, tamper-evident system.
- Conduct quarterly access reviews that check for conflicting role
  combinations, not just individual access.
- Document and test compensating controls for every accepted SoD exception.
- Include audit trail requirements in vendor and system selection criteria.

**Don't:**
- Treat SOX compliance as a standalone project — integrate controls into
  daily operations.
- Let developers deploy their own code or hold write access to production.
- Assume automated controls are inherently reliable; they depend on ITGCs.
- Document controls that don't actually operate — paper controls provide
  zero assurance.
- Keep critical financial data in uncontrolled spreadsheets.
- Skip change management for "low-risk" changes, config changes, or data fixes.

---

## Common Pitfalls

1. **Over-documentation.** Every process documented as a "control" when only
   a subset are key controls. Focus on risks of material misstatement.
2. **Deficiencies found in Q4.** No time to remediate before year-end. Test
   throughout the year.
3. **Stale access / role accumulation.** Old permissions never removed after
   role changes; terminated users retain access. Automate deprovisioning tied
   to HR events.
4. **Missing log context.** Database logs show a row changed but not who or
   why (service accounts). Add application-level logging tied to individual
   users and business transactions.
5. **SoD in name only.** Approver rubber-stamps everything; emergency access
   bypasses SoD unreviewed. Test operating effectiveness, not just design.
6. **Backup without recovery testing.** Restores untested for years. Test
   restores quarterly and document recovery time and completeness.

---

## Checklist

- [ ] COSO framework adopted; risk assessment performed for financial reporting risks
- [ ] Key controls identified and mapped to financial statement assertions
- [ ] Each key control documented: objective, description, frequency, owner, evidence
- [ ] SoD matrix built; IT dev/approve/deploy separation enforced
- [ ] Compensating controls documented and tested for all SoD exceptions
- [ ] Access provisioning approved; deprovisioning within 24–48 hours; quarterly reviews
- [ ] All changes to in-scope systems follow change management, with emergency-change procedure
- [ ] Audit logging at application and database layers, shipped to tamper-evident central store
- [ ] Log retention (7+ years) enforced; log review owners assigned
- [ ] Control testing calendar in place; deficiencies tracked with escalation criteria
- [ ] Annual 404(a) management assessment completed; 404(b) attestation if required
