---
id: gdpr-data-privacy
category: Compliance & Governance
entry: true
last-reviewed: 2026-07
---

# GDPR Data Privacy Conventions

## Category
Compliance & Governance

Standards for complying with the General Data Protection Regulation (EU)
2016/679, which governs processing of personal data of individuals in the
EEA regardless of where the organization is established (Article 3). These
conventions distill the pack's guidance on fundamentals, privacy by design,
cross-border transfers, and breach response.

---

## Defaults

| Concern | Default Rule |
|---------|--------------|
| Lawful basis | Every processing activity requires a documented Article 6 basis before processing begins |
| Accountability | Compliance must be demonstrable — records, policies, evidence (Article 5(2)) |
| Processing register | Record of Processing Activities (ROPA) maintained under Article 30 |
| Data subject requests | Respond within 1 calendar month (extendable +2 months for complex requests, with notice) |
| Privacy by design | Technical/organisational measures embedded at design time; most privacy-protective setting is the default (Article 25) |
| DPIA | Mandatory before processing likely to result in high risk (Article 35); consult supervisory authority if residual high risk (Article 36) |
| International transfers | Valid Chapter V mechanism required (adequacy, SCCs, BCRs); June 2021 SCCs only |
| Transfer Impact Assessment | Required for every transfer relying on SCCs or BCRs (post-*Schrems II*) |
| Breach → authority | Notify supervisory authority within 72 hours of becoming aware (Article 33) |
| Breach → data subjects | Notify without undue delay when high risk is likely (Article 34) |
| Breach register | Document ALL breaches, notified or not (Article 33(5)) |

---

## 1. Lawful Basis and Core Principles

- Every processing activity maps to one Article 6 basis: consent, contract,
  legal obligation, vital interests, public task, or legitimate interests.
- Consent must be freely given, specific, informed, and unambiguous — and as
  easy to withdraw as to give. Do not default to consent where a power
  imbalance exists (e.g., employer–employee).
- Legitimate interests (Art. 6(1)(f)) requires a documented three-part test:
  purpose, necessity, and balancing against data subject rights.
- The Article 5 principles are binding: purpose limitation, data minimisation,
  accuracy, storage limitation, integrity/confidentiality, and accountability.
  Collecting data "just in case" violates data minimisation.

Full detail: `fundamentals.md`

---

## 2. Data Subject Rights

- Rights under Chapter III: information (Arts. 13–14), access (Art. 15),
  rectification (Art. 16), erasure (Art. 17), restriction (Art. 18),
  portability (Art. 20), objection (Art. 21), and protection from solely
  automated decisions with legal/significant effects (Art. 22).
- Standard response deadline is one month; objection to direct marketing is
  absolute and must be honoured without undue delay.
- Erasure is not absolute (legal obligations can override) but systems must
  be designed to support deletion from the start.
- Handle DSARs through a formal process with tracking, templates, and
  escalation paths — not ad hoc.

Full detail: `fundamentals.md`

---

## 3. Privacy by Design and DPIAs

- Embed privacy at requirements and design phases, not after build. Defaults
  must be the most privacy-protective option; users opt in to less privacy.
- Standard technical measures: pseudonymisation, encryption at rest and in
  transit, least-privilege access controls, data minimisation in schemas,
  automated retention enforcement, audit logging, and purpose separation.
- A DPIA is always required for: systematic and extensive profiling with
  legal/significant effects, large-scale special category (Art. 9) or
  criminal conviction (Art. 10) data, or systematic large-scale monitoring
  of publicly accessible areas.
- DPIA process: describe processing → assess necessity/proportionality →
  identify risks → define mitigations → document → consult the DPO
  (Art. 35(2)) → review when processing changes.

Full detail: `privacy-by-design.md`

---

## 4. Cross-Border Transfers

- Transfers outside the EEA require a Chapter V mechanism: adequacy decision
  (Art. 45), SCCs (Art. 46(2)(c)), BCRs (Art. 47), codes of conduct or
  certification (Art. 46(2)(e)/(f)), or — for occasional, non-repetitive
  cases only — Article 49 derogations.
- Use the June 2021 SCCs (Commission Decision (EU) 2021/914, four modules);
  the 2001/2010 SCCs are no longer valid.
- Since *Schrems II* (C-311/18, 2020), every SCC/BCR transfer needs a
  Transfer Impact Assessment: map transfers (including sub-processors),
  assess recipient country laws, apply supplementary measures (encryption,
  pseudonymisation) or suspend the transfer, document, and review.
- Cloud region selection does not eliminate transfer concerns — support
  access, replication, and sub-processors may still transfer data.

Full detail: `cross-border-transfers.md`

---

## 5. Breach Response

- The 72-hour clock (Art. 33) starts at "becoming aware" — reasonable
  certainty a breach occurred — not when investigation completes. Notify in
  phases if full details are not yet available (Art. 33(4)).
- Authority notification covers: nature of the breach, categories and
  approximate numbers affected, DPO contact, likely consequences, and
  measures taken or proposed.
- Notify data subjects only for high-risk breaches (Art. 34); exceptions
  apply if data was rendered unintelligible (e.g., encrypted) or risk has
  been neutralised. Over-notification causes fatigue.
- Maintain a breach register for all breaches regardless of notification
  status, and have a documented, tested response plan before a breach occurs.

Full detail: `cross-border-transfers.md`

---

## Do / Don't

**Do:**
- Identify and document a lawful basis before processing begins.
- Maintain a ROPA (Article 30) and specific, plain-language privacy notices.
- Conduct a DPIA before high-risk processing starts, with DPO involvement.
- Map all international transfers, including sub-processor and SaaS flows.
- Run a TIA for every SCC/BCR transfer and keep a breach register.
- Appoint a DPO when required (Article 37).

**Don't:**
- Treat consent as the default lawful basis or bundle it with T&Cs.
- Collect data "just in case" — minimisation is a legal requirement.
- Rely on Article 49 derogations for systematic transfers.
- Delay breach notification while investigating; supplement in phases.
- Treat the DPIA as a paper exercise disconnected from engineering.
- Define retention in policy without technical enforcement.

---

## Common Pitfalls

1. **No lawful basis documented.** Map every activity to its Article 6 basis
   in a processing register before processing begins.
2. **Dark patterns in consent.** Pre-ticked boxes and asymmetric refusal
   flows are invalid (*Planet49*, C-673/17). Consent must be an active,
   affirmative act.
3. **Unmapped transfers and stale SCCs.** SaaS and sub-processor flows go
   untracked; contracts still cite pre-2021 SCCs. Audit and update.
4. **72-hour clock misunderstood.** Teams start the clock after full
   investigation instead of at first reasonable certainty of a breach.
5. **Over-retention.** Data stored indefinitely with no enforced retention —
   automate deletion or anonymisation per purpose.
6. **Privacy bolted on at the end.** Include privacy requirements in project
   briefs and design review gates, not post-build reviews.

---

## Checklist

- [ ] Lawful basis identified and documented for every processing activity
- [ ] ROPA maintained under Article 30
- [ ] Privacy notices provided at all points of collection
- [ ] DSAR process in place; responses within one calendar month
- [ ] Consent meets GDPR standard; withdrawal as easy as giving
- [ ] Privacy by design review at architecture/design phases; protective defaults
- [ ] DPIA threshold assessment for all new processing; full DPIA where required
- [ ] DPO appointed if required and consulted on DPIAs
- [ ] Retention periods defined and technically enforced
- [ ] All international transfers mapped with valid mechanisms (June 2021 SCCs)
- [ ] TIAs conducted for SCC/BCR transfers; supplementary measures applied
- [ ] Breach response plan documented and tested; 72-hour notification path ready
- [ ] Breach register maintained for all breaches (Article 33(5))
