# Document Control and Records Management

Standards for controlling documented information within the QMS. ISO 9001:2015
Clause 7.5 requires organizations to control the creation, update, and
disposition of documented information needed for QMS effectiveness.

---

## Defaults

- **Documented information:** Includes both documents (procedures, policies,
  work instructions) and records (evidence of activities performed).
- **Control:** Ensure documents are available where needed, adequately
  protected, and that obsolete versions are prevented from unintended use.
- **Retention:** Records are retained for the period required by regulatory,
  contractual, and organizational requirements.
- **Medium:** Electronic preferred. Git-based version control is acceptable
  for technical documentation.

---

## Document vs. Record

| Aspect | Document | Record |
|--------|----------|--------|
| **Purpose** | Prescribes how to do something | Provides evidence that something was done |
| **Examples** | Procedures, work instructions, policies, forms (blank) | Completed forms, test results, audit reports, meeting minutes |
| **Revision** | Updated when processes change | Not revised — records are immutable evidence |
| **Control** | Version control, approval, distribution | Identification, storage, protection, retrieval, retention, disposition |

---

## Document Control Requirements (ISO 9001:2015 Clause 7.5)

### Creation and Update

- Documents must be appropriately **identified** (title, date, author,
  version/revision number)
- Documents must be **reviewed and approved** for adequacy before issue
- Format and media must be appropriate for the intended use

### Control of Documented Information

| Requirement | Implementation |
|-------------|---------------|
| **Availability** | Documents accessible to those who need them, when they need them |
| **Protection** | Adequate protection from loss of confidentiality, improper use, or loss of integrity |
| **Distribution and access** | Controlled — only current versions available at points of use |
| **Storage and preservation** | Protected from deterioration or damage |
| **Retention and disposition** | Retained for required periods, then disposed of appropriately |
| **Change control** | Changes identified, reviewed, and approved. Revision history maintained. |
| **External documents** | Identified and their distribution controlled |

---

## Document Control for Software Teams

Git-based workflows naturally satisfy many document control requirements:

| ISO Requirement | Git Implementation |
|-----------------|-------------------|
| Version identification | Git commits, tags, branch names |
| Change history | `git log`, commit messages, PR descriptions |
| Review and approval | Pull request reviews, required approvals |
| Access control | Repository permissions, branch protection rules |
| Distribution | `git clone`, `git pull` — always get the current version |
| Obsolete version prevention | `main` branch is the current approved version |
| Audit trail | Full commit history with author, date, and changes |

### What Git Does NOT Cover

- **Retention policies** — Git retains everything by default. Define explicit
  retention policies for records that must be archived or destroyed.
- **Training records** — Track who has been trained on which procedures
  separately from the procedure documents.
- **External document control** — Third-party standards, regulatory documents,
  and customer specifications need separate tracking.
- **Non-technical records** — Meeting minutes, management review records,
  calibration certificates may not belong in a code repository.

---

## Do / Don't

- **Do** establish a document numbering or naming convention and enforce it.
- **Do** define who can approve documents and ensure approvals are recorded.
- **Do** make the current version of every document easy to find.
- **Do** maintain a master list (or index) of all controlled documents.
- **Do** review documents periodically for continued adequacy.
- **Do** protect records from alteration — records are evidence, not drafts.
- **Don't** let "convenience copies" proliferate. Uncontrolled copies lead to
  people working from outdated procedures.
- **Don't** skip the approval step. An unapproved document is not controlled.
- **Don't** retain records longer than required without justification — excess
  retention creates liability.
- **Don't** assume electronic storage is inherently safe. Backups, access
  controls, and integrity checks are still required.

---

## Common Pitfalls

1. **Too many approval layers.** Documents take weeks to approve because five
   people must sign off. Solution: define minimum approval authority per
   document type. Not everything needs executive approval.
2. **Outdated master list.** The document index does not match reality. New
   documents are created without being registered. Solution: automate the
   index where possible (e.g., scan the repository structure).
3. **Records scattered across systems.** Test results in one tool, meeting
   notes in another, audit reports in email. Solution: define a records
   management system and migrate records to it.
4. **No retention schedule.** Records accumulate indefinitely with no plan for
   review or disposal. Solution: create a retention schedule aligned with
   regulatory and business requirements.

---

## Document Hierarchy

```
Level 1: Quality Policy
         (What we stand for)
              │
Level 2: Quality Manual / QMS Overview
         (How our system works)
              │
Level 3: Procedures
         (How we do specific processes)
              │
Level 4: Work Instructions / Forms
         (Step-by-step details and data capture)
              │
Level 5: Records
         (Evidence of activities performed)
```

---

## Checklist

- [ ] Document naming/numbering convention is defined and followed
- [ ] All controlled documents have version identification
- [ ] Review and approval process is defined for each document type
- [ ] Current versions are available at all points of use
- [ ] Obsolete versions are identified and prevented from unintended use
- [ ] Changes are tracked with revision history
- [ ] External documents are identified and controlled
- [ ] Records are identified, stored, protected, and retrievable
- [ ] Retention periods are defined and followed
- [ ] Master document list/index is maintained and current
