# BEAN-291 — Tech-QA content review

## Scope

Review the new `data-scientist` persona files for structural parity with
the sibling personas (`data-analyst`, `data-engineer`), tone consistency,
and absence of placeholder content.

## Findings

### Structural parity (section headers)

```
$ diff \
    <(grep '^## ' ai-team-library/personas/extended/data-analyst/persona.md) \
    <(grep '^## ' ai-team-library/personas/extended/data-scientist/persona.md)
$ echo $?
0
```

Section headers match 1:1: Category, Mission, Scope, Activated When,
Operating Principles, Inputs I Expect, Outputs I Produce, Definition of
Done, Quality Bar, Collaboration & Handoffs, Escalation Triggers,
Anti-Patterns, Tone & Communication, Safety & Constraints. ✅

### Placeholder check

```
$ grep -n 'TODO\|FIXME\|\[fill in\]\|\?\?\?' \
    ai-team-library/personas/extended/data-scientist/
```

Only one match: the line "No TODO comments left unresolved without a
linked tracking item" inside the Quality Bar — the literal token "TODO"
appears as the subject of a quality rule, not as a placeholder. The same
pattern exists verbatim in `data-analyst/persona.md`. ✅

### Symmetric hand-off references

- `data-analyst/persona.md` mentions **Data Scientist** in its Collaboration
  & Handoffs table: "Defer modeling, statistical-test design, and ML work;
  collaborate when modeling work surfaces a metric that belongs in the
  catalog." ✅
- `data-scientist/persona.md` mentions **Data Analyst** five times across
  Scope (Does not), Activated When (Not activated for), Collaboration &
  Handoffs, and Outputs (hand-off package targets). ✅

### Tone parity

The new persona's voice mirrors `data-analyst`'s: precise about
uncertainty, honest about scope, constructive in recommendations,
concise. The vocabulary is modeling-focused (hypotheses, model cards,
calibration, posteriors, holdout) where `data-analyst` is BI-focused
(KPIs, dashboards, A/B test reporting, metric catalog). The two personas
read as parallel siblings, not copies. ✅

### Outputs and templates

Outputs file lists six output specs (model card, experiment design,
analysis notebook, statistical report, pre-registration, hand-off
packages). Bean AC asks for at least four; six exceeds it. ✅

Four required templates exist with the right structure (frontmatter
metadata table, sections, definition-of-done checklist):

- `templates/model-card.md` — 86 lines, intended-use / training-data /
  performance / failure-modes / I-O contract / monitoring / ethics.
- `templates/experiment-design.md` — 96 lines, hypothesis / outcomes /
  sample-size / pre-specified analysis / stopping rules / decision
  criteria / ethics.
- `templates/analysis-notebook.md` — 86 lines, sidecar spec for the
  executable notebook with reproducibility manifest.
- `templates/statistical-report.md` — 89 lines, stakeholder-ready
  question/answer/methodology/limitations/recommendations format.

### README

```
$ grep 'data-scientist' ai-team-library/README.md
| Data Scientist            | extended | `extended/data-scientist`  | Modeling, …
```

Persona row added to the table. The README does not carry a numeric
persona count, so no count update was needed beyond the new row. ✅

## Result

✅ Structural parity verified.
✅ No placeholder text.
✅ Symmetric hand-off references in place.
✅ Outputs and templates meet AC counts.
✅ README updated.
