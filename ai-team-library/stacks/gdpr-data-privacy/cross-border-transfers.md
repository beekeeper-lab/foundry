# Cross-Border Data Transfers & Breach Notification

Standards for transferring personal data outside the EEA and for handling
personal data breaches under Articles 44–49 (transfers) and Articles 33–34
(breach notification) of the GDPR.

---

## Defaults

- **Transfer Restriction:** Personal data may only be transferred to a third
  country or international organisation if the controller or processor has
  provided appropriate safeguards (Article 44). Transfers without a valid
  mechanism are prohibited.
- **Adequacy Decisions:** The European Commission may determine that a third
  country ensures an adequate level of protection (Article 45). Transfers to
  adequate countries require no further authorisation.
- **Breach Notification to Authority:** A personal data breach must be notified
  to the competent supervisory authority within 72 hours of becoming aware of
  it, unless the breach is unlikely to result in a risk to data subjects'
  rights and freedoms (Article 33).
- **Breach Notification to Data Subjects:** When a breach is likely to result
  in a high risk to data subjects' rights and freedoms, the controller must
  communicate the breach to affected data subjects without undue delay
  (Article 34).

---

## Transfer Mechanisms (Chapter V)

| Mechanism | Article | Description | When to Use |
|-----------|---------|-------------|-------------|
| **Adequacy Decision** | Art. 45 | Commission determines the third country provides adequate protection. Transfers proceed as if within the EEA. | Transferring to countries with adequacy status (e.g., Japan, South Korea, UK, Canada for commercial organisations, EU-US Data Privacy Framework participants). |
| **Standard Contractual Clauses (SCCs)** | Art. 46(2)(c) | Commission-approved contractual clauses between controller/processor and the recipient. Current version: June 2021 SCCs (four modules). | Most common mechanism for transfers to non-adequate countries. |
| **Binding Corporate Rules (BCRs)** | Art. 47 | Internal rules adopted by a multinational group, approved by a supervisory authority. | Intra-group transfers in large multinational organisations. |
| **Codes of Conduct** | Art. 46(2)(e) | Approved codes of conduct with binding and enforceable commitments from the recipient. | Sector-specific transfers where an approved code exists. |
| **Certification Mechanisms** | Art. 46(2)(f) | Approved certification schemes with binding and enforceable commitments. | Where an approved certification mechanism exists. |
| **Derogations** | Art. 49 | Specific situations: explicit consent, contract necessity, public interest, legal claims, vital interests. | Occasional, non-repetitive transfers where no other mechanism is available. Not suitable for systematic transfers. |

---

## Transfer Impact Assessment (TIA)

Since the *Schrems II* ruling (CJEU, Case C-311/18, 2020), organisations
relying on SCCs or BCRs must assess whether the laws of the recipient country
provide essentially equivalent protection to the EEA.

| Step | Activity |
|------|----------|
| 1 | **Map transfers** — identify all transfers of personal data outside the EEA, including sub-processor transfers. |
| 2 | **Identify the transfer mechanism** — SCCs, BCRs, adequacy decision, or derogation. |
| 3 | **Assess recipient country laws** — evaluate whether local laws (surveillance, government access) undermine the safeguards provided by the transfer mechanism. |
| 4 | **Identify supplementary measures** — if local laws are problematic, determine whether technical (encryption, pseudonymisation), contractual, or organisational measures can bridge the gap. |
| 5 | **Document and decide** — record the assessment. If supplementary measures cannot ensure essentially equivalent protection, the transfer must be suspended or not initiated. |
| 6 | **Review periodically** — reassess when laws change, new guidance is issued, or transfer circumstances change. |

---

## Personal Data Breach Response

### Breach Notification Timeline

```
Breach detected
     │
     ▼
Assess within hours ─── Is it a breach? (unauthorized access,
     │                    loss, destruction, alteration, disclosure)
     │
     ▼
Risk assessment ──────── Likely to result in risk to data subjects?
     │
     ├─── No risk ──────── Document internally (no notification required)
     │
     ├─── Risk ──────────── Notify supervisory authority within 72 hours
     │                       (Article 33)
     │
     └─── High risk ─────── Notify supervisory authority within 72 hours
                             AND notify affected data subjects without
                             undue delay (Article 34)
```

### Notification to Supervisory Authority (Article 33)

| Field | Requirement |
|-------|-------------|
| **Deadline** | Without undue delay and, where feasible, within 72 hours of becoming aware. If notification is late, include reasons for the delay. |
| **Nature of the breach** | Categories and approximate number of data subjects and records affected. |
| **DPO contact** | Name and contact details of the Data Protection Officer or other contact point. |
| **Likely consequences** | Description of the likely consequences of the breach. |
| **Measures taken** | Measures taken or proposed to address the breach and mitigate its adverse effects. |
| **Documentation** | All breaches must be documented regardless of whether notification is required (Article 33(5)). |

### Notification to Data Subjects (Article 34)

Required when the breach is likely to result in a **high risk** to data
subjects' rights and freedoms. Not required if:

- The controller has applied appropriate protection measures (e.g., encryption)
  that render the data unintelligible to unauthorised persons.
- The controller has taken subsequent measures ensuring the high risk is no
  longer likely to materialise.
- Notification would involve disproportionate effort — in which case a public
  communication or similar measure is required instead.

---

## Do / Don't

- **Do** map all international data transfers, including those made by
  sub-processors and cloud providers. You cannot protect what you have not
  identified.
- **Do** use the June 2021 SCCs for new transfers. The old (2001/2010) SCCs
  are no longer valid.
- **Do** conduct a Transfer Impact Assessment for every transfer relying on
  SCCs or BCRs. This is not optional after *Schrems II*.
- **Do** have a documented breach response plan before a breach occurs.
  Improvising during a breach wastes the 72-hour window.
- **Do** maintain a breach register documenting all breaches, including those
  that do not require notification (Article 33(5)).
- **Don't** assume a cloud provider's region selection eliminates transfer
  concerns. Sub-processors, support access, and data replication may involve
  transfers to non-adequate countries.
- **Don't** rely on Article 49 derogations for systematic or repeated
  transfers. Derogations are for occasional, non-repetitive situations.
- **Don't** delay breach notification while investigating. If you cannot
  provide full details within 72 hours, provide what you have and supplement
  in phases (Article 33(4)).
- **Don't** notify data subjects for every breach. Only high-risk breaches
  require data subject notification. Over-notification causes fatigue and
  undermines trust.
- **Don't** treat breach response as purely a legal function. Technical,
  security, communications, and management teams must be involved.

---

## Common Pitfalls

1. **Unmapped transfers.** The organisation does not know where personal data
   flows internationally, especially through SaaS tools and sub-processors.
   Solution: conduct a data flow mapping exercise covering all systems that
   process personal data.
2. **Stale SCCs.** Contracts still reference the old (pre-2021) SCCs, which
   are no longer valid. Solution: audit all transfer agreements and update to
   the June 2021 SCCs with the appropriate module.
3. **No Transfer Impact Assessment.** SCCs are signed but no assessment of
   recipient country laws is conducted. Solution: implement a TIA process as
   part of vendor onboarding and contract renewal.
4. **72-hour clock misunderstood.** Teams assume the clock starts when the
   breach is fully investigated, not when it is first detected. Solution:
   train teams that "becoming aware" means the moment there is a reasonable
   degree of certainty a breach has occurred.
5. **No breach register.** Only reported breaches are documented. Internal
   breaches that do not require notification are not recorded. Solution:
   maintain a register of all breaches per Article 33(5), regardless of
   notification status.

---

## Checklist

- [ ] All international data transfers mapped, including sub-processor transfers
- [ ] Valid transfer mechanism in place for each transfer (adequacy, SCCs, BCRs)
- [ ] June 2021 SCCs used for all new and renewed transfer agreements
- [ ] Transfer Impact Assessments conducted for SCCs and BCRs
- [ ] Supplementary measures implemented where required by TIA
- [ ] Breach response plan documented and tested
- [ ] Incident response team identified with clear roles and escalation paths
- [ ] Breach register maintained for all breaches (Article 33(5))
- [ ] Supervisory authority notification process tested (within 72 hours)
- [ ] Data subject notification template and process prepared for high-risk breaches
