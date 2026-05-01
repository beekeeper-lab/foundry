# Statistical Report: [Title]

## Metadata

| Field          | Value                                       |
|----------------|---------------------------------------------|
| Date           | YYYY-MM-DD                                  |
| Author         | [Data Scientist name]                       |
| Audience       | [Stakeholder / team / executive]            |
| Notebook       | [Repo-relative path to the source notebook] |
| Pre-registered | true / false (link if true)                 |
| Status         | Draft / Reviewed / Final                    |

*Stakeholder-ready document translating analytical work into findings,
recommendations, and quantified uncertainty. Lead with the answer; depth
follows.*

---

## Question and Answer

**Question.** [State the research question in one sentence.]

**Answer.** [Direct answer with effect size and confidence interval. E.g.,
"The new onboarding flow increases 7-day retention by 3.2 percentage points
(95% CI: 1.1 to 5.3, p = 0.008)."]

---

## What This Means

- **Practical significance:** [Is the effect large enough to matter to a business or research decision?]
- **Confidence:** [How strong is the evidence in plain language? "Strong / moderate / suggestive"]
- **Where it applies:** [Population, time period, segment for which the finding holds]
- **Where it does not apply:** [Out-of-scope populations and contexts]

---

## Methodology Summary

[3–5 sentences describing the approach at a level the audience can follow.
Mention: the data source and time window, the unit of analysis, the
statistical test or model used, and any key adjustments. Link to the
notebook for technical readers who want every detail.]

---

## Key Results

### Result 1: [Title]

[Description of the finding with the supporting number(s) and visualization
reference.]

| Group | N | Metric | Value | 95% CI |
|-------|---|--------|-------|--------|
|       |   |        |       |        |

**Interpretation:** [What this means for the audience in plain language.]

### Result 2: [Title]

[Description with supporting data.]

---

## Pre-Specified vs. Exploratory

- **Pre-specified analyses:** [List the ones that followed the registered plan]
- **Exploratory analyses (label them as such):** [List analyses decided after looking at the data; flag the inflated false-positive risk]

---

## Limitations and Caveats

- [E.g., Observational data; causal claims not warranted]
- [E.g., Sample size for subgroup X is small (n=...); interpret with caution]
- [E.g., External-validity bound: the finding may not generalize beyond the studied population]
- [E.g., Data quality caveat: missingness in feature Y was imputed; sensitivity analysis available in appendix]

---

## Recommendations

| # | Recommendation | Expected Impact | Confidence | Next Step |
|---|----------------|-----------------|------------|-----------|
| 1 |                |                 |            |           |
| 2 |                |                 |            |           |

---

## Open Questions

- [Question that this analysis surfaced but did not answer]
- [Question that would benefit from a follow-up study]

---

## References

- [Prior work, internal analyses, or external literature cited]

---

## Appendix

### Reproducibility

- Notebook: [path]
- Data snapshot: [id or hash]
- Code commit: [hash]
- Environment: [pointer to env file]

### Detailed Tables

[Full tables of model coefficients, subgroup results, sensitivity analyses
that would clutter the body of the report.]

### Diagnostics

[Calibration plots, residual plots, assumption-check outputs that support
the methodology section above.]

---

## Definition of Done Checklist

- [ ] Question and answer in the first 100 words
- [ ] Effect sizes and confidence intervals reported, not p-values alone
- [ ] Practical-significance assessment included
- [ ] Methodology described at a level appropriate for the audience
- [ ] Visualizations are accessible (color-blind safe, labeled, uncertainty shown)
- [ ] Causal language reserved for designs that warrant it
- [ ] Limitations and generalizability bounds explicit
- [ ] Pre-specified vs. exploratory analyses labeled
- [ ] Recommendations include trade-offs and confidence levels
- [ ] Source notebook, data snapshot, and code version cited in the appendix
