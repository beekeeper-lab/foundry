# Segregation of Duties (SoD)

Standards for implementing segregation of duties as a fundamental internal
control principle under SOX compliance. SoD prevents any single individual
from having the ability to both commit and conceal errors or fraud.

---

## Defaults

- **Principle:** No single person should control all phases of a transaction
  or process.
- **Scope:** All financially significant processes and supporting IT systems.
- **Minimum separation:** Authorization, custody, and record-keeping functions
  must be performed by different individuals.
- **Review frequency:** SoD matrices reviewed quarterly; access-level SoD
  monitored continuously where possible.

---

## Core SoD Functions

| Function | Description | Example |
|----------|-------------|---------|
| **Authorization** | Approving transactions or access | Manager approves purchase order |
| **Custody** | Physical or logical control of assets | Warehouse receives goods |
| **Record-keeping** | Recording transactions in the books | Accountant records the payable |
| **Reconciliation** | Verifying records against independent data | Controller reconciles bank statement |

A single person performing two or more of these functions for the same
process creates a **SoD conflict**.

---

## SoD in IT Systems

| Area | Conflict | Required Separation |
|------|----------|-------------------|
| **Application development** | Developer deploys own code | Developer, approver, and deployer must be different people |
| **Database administration** | DBA modifies financial data | DBA access to production data is logged and reviewed; DBAs should not process transactions |
| **System administration** | Sysadmin creates own access | Access provisioning requires independent approval |
| **Security administration** | Security admin exempts own account | Security policy changes require separate approval |

---

## SoD Matrix

A SoD matrix maps roles against conflicting activities. Cells are marked:

| | Create PO | Approve PO | Receive Goods | Record Invoice | Approve Payment |
|---|:-:|:-:|:-:|:-:|:-:|
| **Buyer** | X | | | | |
| **Purchasing Manager** | | X | | | |
| **Warehouse Clerk** | | | X | | |
| **AP Clerk** | | | | X | |
| **AP Manager** | | | | | X |

**X** = Permitted role. Any role with two or more X marks in a single row
indicates a potential SoD conflict that must be evaluated.

---

## Compensating Controls

When SoD cannot be fully achieved (common in small organizations), document
compensating controls:

| Situation | Compensating Control | Evidence |
|-----------|---------------------|----------|
| Small IT team — developer must deploy | Management reviews all deployment logs within 24 hours | Signed review log |
| Single AP clerk handles invoices and payments | Controller reviews and approves all payments above threshold | Approval documentation |
| DBA has production data access | All DBA queries logged; monthly review by IT management | Query log review report |
| Owner/operator approves own expenses | Board or audit committee reviews owner expenses quarterly | Meeting minutes |

Compensating controls must be:
- **Documented** — written policy describing the control
- **Tested** — auditors verify the control actually operates
- **Proportionate** — the compensating control addresses the specific risk

---

## Do / Don't

- **Do** build a formal SoD matrix for all financially significant processes.
- **Do** implement system-enforced SoD where possible (role-based access
  controls that prevent conflicting access).
- **Do** document all SoD exceptions with compensating controls and review
  them quarterly.
- **Do** include SoD in the user access review process — reviewers should
  check for conflicting role combinations, not just individual access.
- **Don't** rely solely on manual SoD reviews. Automated SoD monitoring tools
  can detect conflicts in real time.
- **Don't** assume SoD is only about financial transactions. IT SoD (dev vs.
  deploy vs. approve) is equally critical for SOX.
- **Don't** grant temporary SoD exceptions without an expiration date and
  follow-up review.

---

## Common Pitfalls

1. **Role accumulation.** Users accumulate access over time through role
   changes. Each new role adds permissions but old ones are never removed.
   Solution: conduct quarterly access reviews that specifically check for
   conflicting role combinations.
2. **Emergency access abuse.** Break-glass or emergency access bypasses SoD
   controls and is never reviewed. Solution: all emergency access events
   trigger a review within 24-48 hours with documented justification.
3. **SoD in name only.** Roles are separated on paper but the same person
   effectively controls both sides (e.g., the approver rubber-stamps
   everything the requestor submits). Solution: test operating effectiveness,
   not just design.
4. **IT SoD ignored.** Focus on financial process SoD while ignoring that
   developers can push directly to production. Solution: enforce CI/CD
   pipeline controls with required approvals.

---

## Checklist

- [ ] SoD matrix created for all financially significant processes
- [ ] IT SoD enforced (develop/approve/deploy separation)
- [ ] SoD conflicts identified and documented
- [ ] Compensating controls documented for all accepted SoD exceptions
- [ ] Compensating controls tested for operating effectiveness
- [ ] Quarterly review of SoD matrix and exceptions
- [ ] System-enforced role-based access prevents known SoD conflicts
- [ ] User access reviews include SoD conflict checks
