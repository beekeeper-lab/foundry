# IT General Controls (ITGC)

Standards for IT General Controls that support the reliability of automated
controls and IT-dependent manual controls within the scope of SOX compliance.
ITGC failures can undermine the entire control environment because automated
controls depend on IT systems operating with integrity.

---

## Defaults

- **Scope:** All IT systems that process, store, or transmit data relevant
  to financial reporting.
- **Framework:** COBIT (Control Objectives for Information and Related
  Technologies) or COSO IT controls guidance.
- **Assessment:** ITGCs are tested annually as part of the SOX 404 assessment.
- **Key areas:** Access management, change management, IT operations
  (backup/recovery), and program development.

---

## ITGC Domains

| Domain | Objective | Key Controls |
|--------|-----------|-------------|
| **Access to Programs and Data** | Only authorized users can access systems and data | User provisioning/deprovisioning, role-based access, privileged access management, periodic access reviews |
| **Program Changes** | Changes to applications are authorized, tested, and approved before deployment | Change request, development, testing, approval, deployment procedures |
| **Program Development** | New systems are designed, developed, and implemented with adequate controls | Requirements, design review, testing, user acceptance, data migration |
| **Computer Operations** | IT operations support the continued proper functioning of the IT environment | Job scheduling, backup and recovery, incident management, monitoring |

---

## Access Management Controls

### User Provisioning and Deprovisioning

| Control | Description | Frequency |
|---------|-------------|-----------|
| **Access request and approval** | All access requests documented and approved by data/application owner | Per event |
| **Principle of least privilege** | Users granted minimum access necessary to perform their role | Per event, verified quarterly |
| **Segregation of duties (SoD)** | Conflicting access combinations prevented or monitored | Continuous monitoring or quarterly review |
| **Timely deprovisioning** | Access removed within 24-48 hours of role change or termination | Per event |
| **Periodic access review** | Application and data owners review user access lists | Quarterly |

### Privileged Access

- Administrative and elevated access requires additional approval
- Privileged account usage is logged and reviewed
- Shared/generic accounts are prohibited or tightly controlled
- Service accounts have defined owners and are reviewed periodically
- Emergency/break-glass access procedures are documented and tested

---

## Change Management Controls

```
  Change Request
       │
       ▼
  ┌──────────────┐
  │  Development  │  Changes coded in non-production environment
  │               │  Code review required
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   Testing     │  Unit testing, integration testing, regression testing
  │               │  Test results documented
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   Approval    │  Business owner and IT management approve
  │               │  Segregation: developer ≠ approver ≠ deployer
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Deployment   │  Deployed to production by operations (not developer)
  │               │  Deployment evidence retained
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Validation   │  Post-deployment verification
  │               │  Rollback plan available
  └──────────────┘
```

### Key Segregation Requirements

| Role | Can Develop | Can Approve | Can Deploy |
|------|------------|-------------|------------|
| Developer | Yes | No | No |
| Business Owner | No | Yes | No |
| IT Operations | No | No | Yes |

### Emergency Changes

- Documented procedure for urgent changes that bypass normal process
- Retroactive documentation and approval required within 24-48 hours
- Emergency change usage tracked and reviewed — frequent use indicates
  process breakdown

---

## Do / Don't

- **Do** enforce segregation of duties between development, approval, and
  deployment. This is the most scrutinized ITGC control.
- **Do** log all access changes and system modifications. Logs are evidence.
- **Do** conduct quarterly access reviews with application/data owners signing
  off on user lists.
- **Do** test backup and recovery procedures regularly — not just backups,
  but actual restores.
- **Do** maintain an inventory of in-scope systems and applications.
- **Don't** allow developers to deploy their own code to production. This is
  a segregation of duties failure.
- **Don't** share credentials or use generic accounts for production access.
  Individual accountability requires individual accounts.
- **Don't** skip testing for "low-risk" changes. All changes to in-scope
  systems must follow the change management process.
- **Don't** treat ITGC testing as an annual event. Monitor controls
  continuously where possible.

---

## Common Pitfalls

1. **Developer access to production.** Developers have direct write access to
   production databases or can deploy without approval. Solution: enforce
   deployment pipelines that require separate approval and deployment roles.
2. **Stale access.** Terminated employees or role-changed users retain access
   for months. Solution: automate deprovisioning tied to HR events; review
   access quarterly.
3. **Undocumented changes.** Changes deployed without going through change
   management (especially "configuration changes" or "data fixes"). Solution:
   all changes to in-scope systems, regardless of type, must follow the process.
4. **Backup without recovery testing.** Backups run daily but nobody has tested
   a restore in years. Solution: conduct restore tests quarterly; document
   recovery time and completeness.
5. **SoD violations accepted without compensating controls.** Small teams may
   have inherent SoD conflicts. Solution: document compensating controls
   (e.g., management review of all changes) and test their effectiveness.

---

## Checklist

- [ ] In-scope IT systems and applications are inventoried
- [ ] User access provisioning requires documented approval
- [ ] User deprovisioning occurs within policy timeframe (24-48 hours)
- [ ] Quarterly access reviews are performed and documented
- [ ] Privileged access is restricted and monitored
- [ ] Segregation of duties is enforced (dev/approve/deploy separation)
- [ ] Change management process is documented and followed
- [ ] All changes are tested before production deployment
- [ ] Emergency change procedures exist with retroactive documentation
- [ ] Backup procedures are defined and recovery tests are performed
- [ ] Incident management process is documented
- [ ] ITGC testing is performed and deficiencies are tracked
