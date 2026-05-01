# Model Card: [Model Name]

## Metadata

| Field         | Value                                          |
|---------------|------------------------------------------------|
| Model name    | [unique identifier]                            |
| Version       | [semver or commit hash]                        |
| Date trained  | YYYY-MM-DD                                     |
| Author        | [Data Scientist name]                          |
| Code version  | [git commit hash of training code]             |
| Data version  | [snapshot id or hash of training data]         |
| Status        | Draft / Reviewed / Approved / Retired          |

*Standardized record describing the trained model: what it predicts, how it
performs, where it should and should not be applied, and how to monitor it.*

---

## Intended Use

- **Primary use case:** [In one sentence, what decision the model supports]
- **Target users:** [Who will consume the predictions and in what workflow]
- **In scope inputs:** [Population the model was trained for]
- **Out of scope inputs:** [Populations or contexts where the model should NOT be applied]

---

## Training Data

- **Source:** [Tables, datasets, or systems used]
- **Time window:** [e.g., 2024-01-01 to 2024-12-31]
- **Sample size:** [N rows; N positive class for classifiers]
- **Snapshot id / hash:** [versioned reference]
- **Known biases or coverage gaps:** [e.g., underrepresented segments, sampling decisions]
- **Preprocessing:** [Imputation, normalization, encoding decisions]

---

## Architecture

- **Model type:** [e.g., logistic regression, gradient-boosted trees, transformer]
- **Hyperparameters:** [Final values; how chosen — grid search, manual, defaults]
- **Feature set:** [Number of features; brief description; pointer to feature spec]
- **Training procedure:** [Loss, optimizer, stopping rule, seed]

---

## Performance

| Split       | Metric          | Value | 95% CI / bootstrap range |
|-------------|-----------------|-------|--------------------------|
| Train       | [metric]        |       |                          |
| Validation  | [metric]        |       |                          |
| Holdout     | [metric]        |       |                          |

**Discrimination (classifiers):**
- AUROC: [value, CI]
- AUPRC: [value, CI] -- include for imbalanced classification

**Calibration (classifiers):**
- Brier score: [value]
- Calibration plot: [link to figure or notebook cell]

**Subgroup performance:**

| Subgroup    | N   | Metric | Value |
|-------------|-----|--------|-------|
| [segment]   |     |        |       |

---

## Failure Modes

- [e.g., Mispredicts cohort X under condition Y]
- [e.g., Confidence is poorly calibrated above threshold T]
- [e.g., Performance degrades on inputs outside the training distribution]

---

## Input / Output Contract

### Inputs

| Name        | Type    | Range / values     | Null handling |
|-------------|---------|--------------------|---------------|
| [feature]   | [type]  | [allowed values]   | [policy]      |

### Output

- **Type:** [prediction type — class label, probability, regression value]
- **Schema:** [shape; for classifiers, the class index ↔ label map]
- **Units:** [where applicable]
- **Confidence/uncertainty:** [whether the model emits one and how to interpret it]

---

## Monitoring Recommendations

- **Drift signals:** [which input distributions or output distributions to monitor]
- **Refresh cadence:** [recommended retraining frequency or trigger]
- **Alert thresholds:** [performance floor or drift bound that should page someone]
- **Evaluation cadence:** [how often to re-score on a fresh holdout]

---

## Ethical & Compliance Considerations

- **Sensitive attributes:** [whether the training data includes any]
- **Fairness analysis:** [link to subgroup fairness report or N/A with reason]
- **Consent / governance:** [confirm consent and policy compliance for the data used]
- **Regulatory:** [HIPAA / GDPR / SOX / industry-specific notes if relevant]

---

## Definition of Done Checklist

- [ ] Intended use, target users, and scope are documented in plain language
- [ ] Training data is described with version, time window, sample size, and biases
- [ ] Held-out performance is reported with confidence intervals
- [ ] Calibration is reported alongside discrimination for classifiers
- [ ] Subgroup performance is reported where relevant
- [ ] Known failure modes and out-of-scope inputs are listed
- [ ] Input/output contract is documented
- [ ] Monitoring recommendations are included
- [ ] Author, date, code version, and data version are recorded
- [ ] Sensitive-attribute and consent considerations are addressed
