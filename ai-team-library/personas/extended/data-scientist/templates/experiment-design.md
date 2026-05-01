# Experiment Design: [Title]

## Metadata

| Field             | Value                                       |
|-------------------|---------------------------------------------|
| Date              | YYYY-MM-DD                                  |
| Author            | [Data Scientist name]                       |
| Pre-registered    | true / false                                |
| Pre-reg id / hash | [OSF id, AsPredicted id, or commit hash]    |
| Status            | Draft / Pre-registered / Running / Complete |
| Related links     | [related beans, prior analyses]             |

*Pre-registered plan specifying what the experiment will measure, how it
will be measured, what counts as a positive result, and what guard rails
will catch harm.*

---

## Background & Question

[2–4 sentences. What prompted this experiment, and what specific question
does it answer?]

---

## Hypothesis

- **Null (H0):** [no-effect statement]
- **Alternative (H1):** [direction and approximate magnitude]
- **Rationale:** [why this hypothesis — prior data, theory, or stakeholder ask]

---

## Outcomes

- **Primary outcome metric:** [name, definition, calculation]
- **Secondary outcome metrics (labeled secondary):**
  - [metric] -- [definition]
  - [metric] -- [definition]
- **Guard-rail metrics (must not regress):**
  - [metric] -- [tolerance]
  - [metric] -- [tolerance]

---

## Design

- **Unit of analysis:** [e.g., user, session, account]
- **Assignment scheme:** [e.g., simple randomization 50/50; cluster randomization by account; matched pairs]
- **Treatment:** [what the treated group receives]
- **Control:** [what the control group receives]
- **Blinding (if applicable):** [single-blind, double-blind, or N/A]

---

## Sample Size & Power

- **Minimum detectable effect:** [in the units of the primary outcome]
- **Significance level (α):** [e.g., 0.05]
- **Statistical power (1 − β):** [e.g., 0.80]
- **Assumed baseline (H0 distribution):** [rate, mean, variance assumed]
- **Required sample size per arm:** [N]
- **Calculation method:** [closed-form formula, simulation, or tool used]

---

## Pre-Specified Analysis Plan

- **Statistical test:** [e.g., two-sample t-test, chi-square, mixed-effects regression]
- **Why this test:** [assumption check or robustness rationale]
- **Multiple-comparison adjustment:** [e.g., Bonferroni, BH-FDR, none with reason]
- **Subgroup analyses (pre-specified only):** [list]
- **Robustness checks:** [e.g., per-protocol vs. intent-to-treat, outlier sensitivity]

---

## Stopping Rules

- **Time-based:** [e.g., minimum 14 days, maximum 28 days]
- **Event-based:** [e.g., stop when N events accumulate]
- **Futility:** [e.g., conditional power < 10% at interim]
- **Harm:** [e.g., guard-rail metric regression beyond tolerance]

---

## Decision Criteria

| Outcome                                      | Action |
|----------------------------------------------|--------|
| Primary metric improves significantly, no guard-rail regression | [e.g., ramp to 100%]   |
| Primary metric improves but guard-rail regresses               | [e.g., investigate]   |
| Primary metric does not move                                    | [e.g., revert]        |
| Primary metric regresses significantly                          | [e.g., revert + post-mortem] |

---

## Ethical & Compliance Review

- **Subject population:** [e.g., logged-in adult users in the US]
- **IRB / ethics review:** [required? if so, status]
- **Consent / disclosure:** [how participants are informed, if at all]
- **Data handling:** [PII exposure, retention policy, governance]

---

## Risks & Limitations

- [e.g., Selection bias risk: assignment may correlate with confounders]
- [e.g., Novelty effect may inflate short-term results]
- [e.g., Cross-arm contamination is possible if users see both]

---

## Definition of Done Checklist

- [ ] Hypothesis stated with direction and magnitude before data collection
- [ ] Primary outcome and secondary outcomes (labeled) defined upfront
- [ ] Sample-size calculation documented
- [ ] Randomization scheme and unit of analysis stated
- [ ] Pre-specified analysis plan written before outcome data is observed
- [ ] Stopping rules and decision criteria pre-specified
- [ ] Guard-rail metrics defined with tolerances
- [ ] Ethical / IRB / consent considerations addressed
- [ ] Document committed and time-stamped
- [ ] Pre-registration id (or commit hash) recorded
