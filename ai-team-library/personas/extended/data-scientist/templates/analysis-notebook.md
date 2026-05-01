# Analysis Notebook Spec: [Title]

*This is the markdown sidecar that documents the companion `.ipynb` (or
`.qmd` / `.Rmd`) notebook. The notebook is the primary, executable artifact;
this spec is the human-readable summary reviewers and stakeholders read
before opening the code.*

## Metadata

| Field          | Value                                       |
|----------------|---------------------------------------------|
| Date           | YYYY-MM-DD                                  |
| Analyst        | [Data Scientist name]                       |
| Notebook path  | [repo-relative path to the executable file] |
| Data snapshot  | [snapshot id or hash]                       |
| Code version   | [git commit hash]                           |
| Environment    | [pointer to env file: requirements.txt, environment.yml, renv.lock] |
| Status         | Draft / Reviewed / Final                    |

---

## Question

[State the research question in one or two sentences. E.g., "Does the new
recommendation algorithm improve 7-day retention for new users compared to
the baseline?"]

---

## Executive Summary

- **Headline finding:** [Effect direction and magnitude with confidence interval]
- **Confidence:** [Strength of evidence in plain language]
- **Recommendation:** [Concrete next step the finding supports]

---

## Approach

- **Type:** Exploratory / Confirmatory / Modeling / Inference
- **Pre-registration:** [Link to experiment-design or N/A with reason]
- **Method:** [E.g., logistic regression with cluster-robust SEs; cross-validated gradient-boosted trees; Bayesian linear model with weakly informative priors]
- **Population:** [Who or what the analysis applies to]
- **Date range:** [Time window of the data]

---

## Reproducibility Manifest

- **Random seed(s):** [Set at the top of the notebook]
- **Library versions:** [Pinned in env file; key versions listed inline]
- **Data snapshot:** [Versioned reference; not a live mutable table]
- **Re-run instructions:** [Single command or short steps to re-execute]
- **Last verified clean run:** [Date and operator who confirmed top-to-bottom clean execution]

---

## EDA Highlights

- **Sample size:** [N rows, N per relevant subgroup, N for any target]
- **Distributions:** [Brief description of key feature/target distributions]
- **Missingness:** [Per-column missingness summary; how it was handled]
- **Outliers:** [What counted as an outlier and what was done about it]
- **Class balance (for classification):** [proportion per class]

---

## Model / Test Details

- **Model or test:** [Specific method]
- **Assumptions checked:** [Which assumptions, with diagnostic outcomes]
- **Hyperparameters / settings:** [Final values; how chosen]
- **Validation:** [Holdout, k-fold CV, bootstrap, etc.]

---

## Results

| Metric          | Value | 95% CI / posterior interval | Notes |
|-----------------|-------|-----------------------------|-------|
| [primary]       |       |                             |       |
| [secondary 1]   |       |                             |       |
| [secondary 2]   |       |                             |       |

**Subgroup results (if pre-specified):**

| Segment   | N | Metric | Value | 95% CI |
|-----------|---|--------|-------|--------|
|           |   |        |       |        |

**Calibration / residuals (figures in the notebook):** [Brief verbal summary]

---

## Interpretation

- [What the result says in plain language]
- [Practical significance assessment, not just statistical significance]
- [What the result does *not* say -- bound the claim]

---

## Limitations

- [E.g., observational data: causal claims are not warranted]
- [E.g., training distribution differs from deployment population in known ways]
- [E.g., sample size for subgroup X is small (n=...); interpret with caution]

---

## Follow-Up

- [What further analysis would strengthen or extend this finding]
- [Any data gaps to flag back to Data Engineering]

---

## Definition of Done Checklist

- [ ] Notebook re-runs from a clean kernel without errors
- [ ] Cells execute top-to-bottom; no out-of-order state
- [ ] Random seeds set; library versions pinned
- [ ] Data loaded from a versioned snapshot
- [ ] EDA included before modeling
- [ ] Model assumptions checked with diagnostics
- [ ] Holdout or cross-validation results reported
- [ ] Confidence intervals or posteriors accompany every estimate
- [ ] Visualizations include axis labels, units, and uncertainty bands where appropriate
- [ ] Notebook and this spec are committed to the repository
- [ ] No hardcoded credentials or PII exposure
