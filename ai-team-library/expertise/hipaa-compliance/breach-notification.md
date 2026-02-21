# Breach Notification

Standards for complying with the HIPAA Breach Notification Rule (45 CFR
§§ 164.400–164.414), as amended by the HITECH Act and the Omnibus Rule.
The rule requires covered entities and business associates to provide
notification following a breach of unsecured protected health information
(PHI).

---

## Defaults

- **Definition of breach:** The acquisition, access, use, or disclosure of
  PHI in a manner not permitted by the Privacy Rule that compromises the
  security or privacy of the PHI.
- **Unsecured PHI:** PHI that has not been rendered unusable, unreadable,
  or indecipherable to unauthorized persons through encryption or
  destruction as specified in HHS guidance.
- **Notification timeline:** Individual notification within 60 days of
  discovery. Discovery occurs on the first day the breach is known or
  reasonably should have been known.
- **Presumption:** An impermissible use or disclosure is presumed to be a
  breach unless the covered entity demonstrates a low probability that PHI
  was compromised, based on a risk assessment.

| Default | Alternative | When to Consider |
|---------|-------------|------------------|
| 60-day notification to individuals | Shorter timeline (e.g., 30 days) | State laws may impose shorter deadlines — always check state requirements |
| Written notification by first-class mail | Email notification | Only if the individual has previously agreed to electronic notice |
| Risk assessment using the four-factor test | Treat every incident as a breach | When the organization prefers a conservative approach to avoid risk assessment disputes |
| Annual reporting of small breaches to HHS | Immediate reporting | Required only for breaches affecting 500+ individuals — small breaches are reported annually |

---

## Four-Factor Risk Assessment

When an impermissible use or disclosure occurs, perform this risk assessment
to determine whether it constitutes a breach requiring notification:

| Factor | Assessment Questions |
|--------|---------------------|
| **1. Nature and extent of PHI** | What types of identifiers and clinical information were involved? Was the PHI highly sensitive (e.g., HIV, mental health, substance abuse)? |
| **2. Unauthorized person** | Who impermissibly used or received the PHI? Was it another covered entity or an unrelated third party? |
| **3. Whether PHI was actually acquired or viewed** | Was the PHI actually accessed or viewed, or was there only an opportunity for access (e.g., a lost encrypted laptop)? |
| **4. Extent of risk mitigation** | Were steps taken to mitigate the risk? Was the PHI returned? Were assurances of destruction obtained? |

If the risk assessment demonstrates a **low probability** that PHI was
compromised, the incident is not a breach and notification is not required.
Document the assessment regardless.

---

## Notification Requirements

| Audience | Threshold | Timeline | Method |
|----------|-----------|----------|--------|
| **Individuals** | Any breach of unsecured PHI | Within 60 days of discovery | Written notice by first-class mail (or email if previously agreed); substitute notice if contact info insufficient |
| **HHS (large breaches)** | 500+ individuals affected | Within 60 days of discovery | Online submission via HHS breach portal |
| **HHS (small breaches)** | Fewer than 500 individuals | Within 60 days after end of calendar year | Annual log submission via HHS breach portal |
| **Media** | 500+ individuals in a single state or jurisdiction | Within 60 days of discovery | Notice to prominent media outlets serving the state/jurisdiction |

---

## Individual Notification Content

The written notification to individuals must include:

| Element | Description |
|---------|-------------|
| **Description of the breach** | What happened, including the date(s) of the breach and date of discovery |
| **Types of information involved** | The types of unsecured PHI involved (e.g., name, SSN, diagnosis, treatment information) |
| **Steps individuals should take** | Recommended steps to protect themselves from potential harm (e.g., credit monitoring, password changes) |
| **What the entity is doing** | Steps the covered entity is taking to investigate, mitigate harm, and prevent future breaches |
| **Contact information** | Toll-free number, email address, postal address, or website for individuals to ask questions |

---

## Exceptions to Breach Definition

| Exception | Description |
|-----------|-------------|
| **Unintentional acquisition** | Good-faith, unintentional acquisition, access, or use of PHI by a workforce member acting within scope of authority, if no further impermissible use or disclosure |
| **Inadvertent disclosure** | Inadvertent disclosure by an authorized person to another authorized person at the same covered entity or business associate, if no further impermissible use or disclosure |
| **Good-faith belief** | Disclosure where the covered entity or business associate has a good-faith belief that the unauthorized person would not reasonably be able to retain the information |

---

## Do / Don't

- **Do** maintain an incident response plan that includes breach
  identification, risk assessment, containment, notification, and
  post-incident review.
- **Do** document every potential breach incident, including incidents you
  determine do not require notification. The risk assessment documentation
  is your evidence.
- **Do** check state breach notification laws in addition to HIPAA. Many
  states have shorter timelines or broader definitions that apply
  concurrently.
- **Do** train workforce members to recognize and report potential breaches
  immediately. The 60-day clock starts at discovery.
- **Do** encrypt PHI at rest and in transit. Encrypted PHI that is breached
  does not require notification (it is not "unsecured PHI").
- **Don't** delay breach investigation to avoid starting the 60-day clock.
  The regulation uses "known or reasonably should have been known" — willful
  delay increases penalty exposure.
- **Don't** skip the four-factor risk assessment and automatically notify.
  While conservative, this approach can cause unnecessary alarm and erode
  trust if incidents are minor.
- **Don't** assume business associates will handle their own notification.
  Business associates must notify the covered entity, but the covered entity
  is responsible for notifying individuals.
- **Don't** forget media notification. Breaches affecting 500+ individuals
  in a state require notice to prominent media outlets.

---

## Common Pitfalls

1. **Delayed discovery.** The breach occurred months ago but was only
   recently discovered, compressing the notification timeline. Solution:
   implement monitoring and detection controls that identify breaches
   promptly (audit logs, access anomaly detection, DLP tools).
2. **Incomplete risk assessment.** The four-factor analysis is superficial
   or undocumented. Solution: use a standardized risk assessment template
   and require sign-off by the privacy officer.
3. **State law conflicts.** The organization follows HIPAA's 60-day
   timeline but violates a state law requiring notification within 30 days.
   Solution: maintain a matrix of applicable state breach notification laws
   and apply the most restrictive timeline.
4. **No post-breach remediation.** The organization notifies but does not
   fix the underlying cause. Solution: include root cause analysis and
   corrective action in the incident response process.
5. **Penalty underestimation.** Leadership views breach notification as a
   reputational issue only. Solution: communicate the financial exposure —
   HIPAA penalties range from $100 to $50,000 per violation, up to $1.5
   million per year per violation category, with criminal penalties for
   knowing violations.

---

## HIPAA Penalty Tiers

| Tier | Knowledge Level | Per Violation | Annual Maximum |
|------|----------------|---------------|----------------|
| 1 | Did not know and would not have known | $137–$68,928 | $2,067,813 |
| 2 | Reasonable cause, not willful neglect | $1,379–$68,928 | $2,067,813 |
| 3 | Willful neglect, corrected within 30 days | $13,785–$68,928 | $2,067,813 |
| 4 | Willful neglect, not corrected | $68,928 | $2,067,813 |

*Penalty amounts adjusted annually for inflation. Criminal penalties
(up to $250,000 and 10 years imprisonment) apply for knowing violations.*

---

## Checklist

- [ ] Incident response plan documented and includes breach notification procedures
- [ ] Breach identification and reporting procedures communicated to all workforce members
- [ ] Four-factor risk assessment template available and used for all incidents
- [ ] Individual notification template prepared with all required content elements
- [ ] HHS breach portal account established and tested
- [ ] State breach notification laws inventoried and most restrictive timelines identified
- [ ] Business associate breach notification timelines defined in BAAs
- [ ] Media notification procedures established for large breaches (500+ in a state)
- [ ] Post-breach remediation and root cause analysis process defined
- [ ] Breach log maintained for annual reporting of small breaches to HHS
- [ ] Encryption implemented to render PHI "secured" under HHS guidance
