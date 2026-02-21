# Safeguards

Standards for implementing the administrative, physical, and technical
safeguards required by the HIPAA Security Rule (45 CFR § 164.308, § 164.310,
§ 164.312). Safeguards protect the confidentiality, integrity, and
availability of electronic protected health information (ePHI).

---

## Defaults

- **Framework:** NIST Cybersecurity Framework (CSF) mapped to HIPAA Security
  Rule requirements. HHS crosswalk available for alignment.
- **Classification:** All safeguard specifications are either Required (R)
  or Addressable (A). Addressable does not mean optional — it means the
  entity must assess whether the specification is reasonable and appropriate.
- **Documentation:** All safeguard implementations must be documented,
  including rationale for any addressable specifications not implemented.
- **Review cycle:** Security measures must be reviewed periodically and
  updated in response to environmental or operational changes.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| AES-256 encryption for ePHI at rest | AES-128 | Acceptable but AES-256 is preferred for long-term protection |
| TLS 1.2+ for ePHI in transit | VPN tunnel | When point-to-point encryption is impractical; VPN provides network-level protection |
| Role-based access control (RBAC) | Attribute-based access control (ABAC) | When access decisions require context beyond role (e.g., location, time, patient relationship) |
| Multi-factor authentication for remote access | Single-factor with compensating controls | Only when MFA is technically infeasible and compensating controls are documented |

---

## Administrative Safeguards (§ 164.308)

| Specification | Type | Description |
|---------------|------|-------------|
| **Security management process** | R | Implement policies and procedures to prevent, detect, contain, and correct security violations |
| **Risk analysis** | R | Conduct an accurate and thorough assessment of risks to ePHI |
| **Risk management** | R | Implement measures to reduce risk to reasonable and appropriate levels |
| **Sanction policy** | R | Apply appropriate sanctions against workforce members who violate security policies |
| **Information system activity review** | R | Regularly review records of information system activity (audit logs, access reports, security incident tracking) |
| **Assigned security responsibility** | R | Designate a security official responsible for developing and implementing security policies |
| **Workforce security** | A | Implement procedures to ensure workforce members have appropriate access to ePHI |
| **Security awareness and training** | A | Implement a security awareness and training program for all workforce members |
| **Security incident procedures** | R | Implement policies and procedures to address security incidents |
| **Contingency plan** | R | Establish policies and procedures for responding to emergencies or other occurrences that damage systems containing ePHI |
| **Evaluation** | R | Perform periodic technical and non-technical evaluation of security policies and procedures |

---

## Physical Safeguards (§ 164.310)

| Specification | Type | Description |
|---------------|------|-------------|
| **Facility access controls** | A | Implement policies and procedures to limit physical access to ePHI systems while ensuring authorized access |
| **Workstation use** | R | Implement policies and procedures for proper workstation use to protect ePHI |
| **Workstation security** | R | Implement physical safeguards for workstations that access ePHI |
| **Device and media controls** | R | Implement policies governing receipt, removal, and disposal of hardware and electronic media containing ePHI |
| **Media disposal** | R | Implement procedures for final disposition of ePHI and/or hardware/media on which it is stored |
| **Media re-use** | R | Implement procedures for removal of ePHI from electronic media before re-use |
| **Accountability** | A | Maintain records of hardware and media movements, and the persons responsible |

---

## Technical Safeguards (§ 164.312)

| Specification | Type | Description |
|---------------|------|-------------|
| **Access control** | R | Implement technical policies and procedures to allow access only to authorized persons or software programs |
| **Unique user identification** | R | Assign a unique name and/or number to each user for tracking and identification |
| **Emergency access procedure** | R | Establish procedures for obtaining necessary ePHI during an emergency |
| **Automatic logoff** | A | Implement electronic procedures that terminate sessions after a predetermined period of inactivity |
| **Encryption and decryption** | A | Implement a mechanism to encrypt and decrypt ePHI |
| **Audit controls** | R | Implement hardware, software, and/or procedural mechanisms to record and examine activity in systems containing ePHI |
| **Integrity** | R | Implement policies and procedures to protect ePHI from improper alteration or destruction |
| **Authentication** | R | Implement procedures to verify that a person or entity seeking access to ePHI is who they claim to be |
| **Transmission security** | R | Implement technical security measures to guard against unauthorized access to ePHI being transmitted over a network |

---

## Do / Don't

- **Do** treat addressable specifications seriously. "Addressable" means
  you must implement the specification if reasonable and appropriate, or
  document why you chose an equivalent alternative.
- **Do** encrypt ePHI both at rest and in transit. While encryption is
  addressable, HHS has made clear that failing to encrypt is a leading
  cause of enforcement actions.
- **Do** implement audit controls that log access to all systems containing
  ePHI. Review audit logs regularly — logging without review is insufficient.
- **Do** test your contingency plan (disaster recovery, emergency mode
  operations) at least annually.
- **Do** enforce automatic logoff on all workstations and devices that
  access ePHI.
- **Don't** assume cloud providers handle all safeguards. You remain
  responsible for safeguards even when using cloud services — verify
  through BAAs and independent assessments.
- **Don't** use shared accounts for ePHI access. Every user must have a
  unique identifier for audit trail purposes.
- **Don't** neglect physical safeguards. Server rooms, workstations, and
  mobile devices all require physical access controls.
- **Don't** treat the contingency plan as a document that sits on a shelf.
  Test backups, validate recovery procedures, and update contact lists.

---

## Common Pitfalls

1. **Addressable confusion.** Organizations skip addressable specifications
   thinking they are optional. Solution: for each addressable specification,
   document your assessment — implement it, implement an equivalent
   alternative, or document why it is not reasonable and appropriate.
2. **Encryption gaps.** ePHI is encrypted in transit but not at rest, or
   vice versa. Solution: implement encryption for ePHI in all states and
   document the encryption standards used.
3. **Audit log neglect.** Audit controls are enabled but logs are never
   reviewed. Solution: assign log review responsibilities and define
   escalation procedures for anomalies.
4. **Untested contingency plans.** Backup and disaster recovery procedures
   exist on paper but have never been tested. Solution: schedule and
   document annual testing of contingency plan components.
5. **Mobile device blind spots.** Policies cover servers and workstations
   but not laptops, tablets, and phones that access ePHI. Solution: include
   mobile devices in your device inventory and apply appropriate
   safeguards (encryption, remote wipe, screen lock).

---

## Checklist

- [ ] Security official designated with documented responsibilities
- [ ] Risk analysis covers all systems, applications, and devices with ePHI
- [ ] Administrative safeguards implemented (security management, training, incidents, contingency)
- [ ] Physical safeguards implemented (facility access, workstation, device/media controls)
- [ ] Technical safeguards implemented (access control, audit, integrity, transmission)
- [ ] Encryption implemented for ePHI at rest (AES-256 or equivalent)
- [ ] Encryption implemented for ePHI in transit (TLS 1.2+ or equivalent)
- [ ] Unique user identification enforced — no shared accounts
- [ ] Audit logs enabled, reviewed regularly, and retained per policy
- [ ] Contingency plan documented, tested annually, and updated
- [ ] Addressable specifications assessed and documented
- [ ] Mobile device policies established and enforced
