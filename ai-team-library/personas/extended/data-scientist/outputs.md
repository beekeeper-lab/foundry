# Data Scientist -- Outputs

This document enumerates every artifact the Data Scientist is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Model Cards

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Model Card                                         |
| **Cadence**        | Per trained model handed off to downstream consumers |
| **Template**       | `model-card.md`                                    |
| **Format**         | Markdown                                           |

**Description.** A standardized record describing a trained model: what it
predicts, what data trained it, how it performs, where it should and should
not be applied, and how to monitor it once deployed. Model cards make models
inspectable and govern their reuse.

**Quality Bar:**
- Intended use is stated in plain language with target users named.
- Training data is described (source, time window, size, known biases, version).
- Performance is reported on a held-out set with confidence intervals or
  bootstrap estimates.
- Calibration is reported alongside discrimination for classifiers.
- Subgroup performance is reported where relevant (fairness, segment slicing).
- Known failure modes and out-of-scope inputs are explicitly listed.
- Required input schema and output contract are documented (types, ranges,
  null handling).
- Monitoring recommendations (drift signals, refresh cadence) are included.
- Author, date trained, and code/data version are recorded.

**Downstream Consumers:** Data Engineer (for productionizing), Developer (for
embedding inference), Architect (for platform fit), Tech-QA (for validation
strategy), audit/compliance reviewers.

---

## 2. Experiment Designs

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Experiment Design Document                         |
| **Cadence**        | Before any confirmatory analysis or formal study   |
| **Template**       | `experiment-design.md`                             |
| **Format**         | Markdown                                           |

**Description.** A pre-registered plan specifying what an experiment will
measure, how it will be measured, what counts as a positive result, and what
guard rails will catch harm. Pre-registration separates confirmatory science
from exploratory pattern-finding.

**Quality Bar:**
- Hypothesis is stated with expected direction and magnitude before any data
  is collected or analyzed.
- Primary outcome metric is specified; secondary metrics labeled as such.
- Sample-size calculation is included with: minimum detectable effect,
  significance level, statistical power, and the assumed baseline rate or
  variance.
- Randomization or assignment scheme is documented; the unit of analysis is
  named.
- Pre-specified analysis plan (which test, which adjustments for multiple
  comparisons, which subgroup analyses) is written before data collection.
- Stopping rules are stated (time-based, event-based, futility).
- Guard-rail metrics (safety/quality counter-metrics) are defined.
- Decision criteria are pre-specified: what result triggers what action.
- Ethical / IRB / consent considerations are addressed where applicable.

**Downstream Consumers:** Team Lead (for go/no-go), Data Engineer (for
instrumentation), Developer (for implementation), Tech-QA (for verifying
correct rollout), Business Analyst (for decision context).

---

## 3. Analysis Notebooks

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Reproducible Analysis Notebook                     |
| **Cadence**        | Per analytical task (modeling, EDA, inference)     |
| **Template**       | `analysis-notebook.md`                             |
| **Format**         | Jupyter (`.ipynb`) or quarto/rmarkdown plus a markdown spec sidecar |

**Description.** End-to-end reproducible analysis covering the question,
exploratory data analysis, modeling or testing, validation, and
interpretation. The notebook is the primary artifact; the spec sidecar is
the human-readable summary.

**Quality Bar:**
- Notebook re-runs from a clean kernel without errors.
- Cells execute top-to-bottom; no out-of-order state.
- Random seeds are set at the top; library versions are pinned in a manifest
  cell or environment file.
- Data sources are loaded from versioned snapshots, not live mutable tables.
- EDA is included before modeling: distributions, missingness, outliers,
  correlations.
- Model assumptions are checked with diagnostics; violations are reported.
- Holdout or cross-validation results are reported, not just training metrics.
- Visualizations include axis labels, units, sample sizes, and uncertainty
  bands where appropriate.
- Conclusion section answers the original question with quantified
  uncertainty.
- The notebook is committed to the repository, not left on a personal machine.

**Downstream Consumers:** Tech-QA (for verification), Business Analyst (for
decision), Data Engineer (for productionization handoff), peer reviewers.

---

## 4. Statistical Reports

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Statistical Report                                 |
| **Cadence**        | Per finding that informs a decision or publication |
| **Template**       | `statistical-report.md`                            |
| **Format**         | Markdown                                           |

**Description.** A stakeholder-ready prose document translating notebook
output into findings, recommendations, and quantified uncertainty. Reports
are the artifact decision-makers read; notebooks are the artifact reviewers
audit.

**Quality Bar:**
- Question and answer are stated in the first 100 words.
- Methodology is described at a level appropriate for the audience, with a
  link to the full notebook for technical readers.
- Findings include effect sizes, confidence intervals (or posteriors), and
  practical significance, not only p-values.
- Visualizations are accessible (color-blind-safe palettes, labeled axes,
  legends, sample sizes shown).
- Limitations and generalizability bounds are explicit.
- Causal language is reserved for designs that warrant it; correlational
  findings are labeled as such.
- Recommendations include trade-offs and confidence levels.
- Pre-registration link is provided for confirmatory work.
- Sources, references, and prior work are cited.

**Downstream Consumers:** Business Analyst (for decision), Team Lead (for
prioritization), executive stakeholders, external reviewers (for
publication-grade work).

---

## 5. Pre-Registration Documents

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Pre-Registration Document                          |
| **Cadence**        | Before data collection for confirmatory studies     |
| **Template**       | `experiment-design.md` (with `pre-registered: true`) |
| **Format**         | Markdown                                           |

**Description.** A version-controlled record of the hypothesis and analysis
plan, time-stamped before outcome data is examined. Pre-registration makes
exploratory and confirmatory work distinguishable after the fact.

**Quality Bar:**
- Hypothesis, primary outcome, and analysis plan are specified before
  outcome data is observed.
- A commit hash or external pre-registration ID (OSF, AsPredicted, ClinicalTrials)
  is recorded.
- Any deviations from the plan made during execution are documented and
  labeled "exploratory" in downstream reporting.

**Downstream Consumers:** Tech-QA (for distinguishing planned from
post-hoc analyses), peer reviewers, audit/compliance reviewers.

---

## 6. Hand-Off Packages

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Productionization or Operationalization Hand-Off   |
| **Cadence**        | When a model or query needs to leave the analysis environment |
| **Template**       | None (uses the per-edge handoff packet contract)   |
| **Format**         | Markdown packet with attached model artifacts      |

**Description.** A bundled package handed to Data Engineering (for serving)
or Data Analyst (for catalog inclusion) when modeling work needs to live
beyond the analysis notebook.

**Quality Bar:**
- For models: includes the model artifact (or pointer), input schema, output
  schema, performance summary, monitoring recommendations, and the model card.
- For queries / metrics: includes the query, the validated calculation logic,
  refresh cadence, and the data sources used.
- A rerun command or runbook is included so the receiver can reproduce the
  source result before going live.
- Open questions, known limitations, and required follow-up are stated.

**Downstream Consumers:** Data Engineer (for productionizing models), Data
Analyst (for catalog inclusion of metrics surfaced during modeling), Platform/
SRE Engineer (for monitoring setup).

---

## Output Format Guidelines

- All outputs are committed to the project repository or its analytics
  artifact store. No deliverables live in personal notebooks or local
  filesystems only.
- Notebooks are committed in re-runnable form (cleared outputs in PRs unless
  the rendered output is part of the artifact).
- Reports are written as if the reader has no prior context about the
  analysis.
- Code and queries follow the project's stack-specific conventions
  (`expertise/<id>/conventions.md`).
- Random seeds, library versions, and data snapshots are pinned for any
  result that will inform a decision.
