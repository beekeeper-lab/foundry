# BEAN-291: Add Data Scientist Persona to the Library

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-291 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-05-01 |
| **Started** | — |
| **Completed** | — |
| **Owner** | (unassigned) |
| **Category** | App |
| **Depends On** | — |
| **Duration** | — |

## Problem Statement

The library has personas for the *adjacent* data roles but not the
core modeling/statistics one:

- `data-analyst` — KPIs, dashboards, BI reporting, A/B test design.
- `data-engineer` — pipelines, ETL/ELT, infrastructure for data flow.
- `researcher-librarian` — literature, sources, citation work.
- expertise: `mlops`, `data-engineering`, `business-intelligence`.

A user who wants to compose a team for **academic research, ML
modeling, statistical inference, or hypothesis-driven experimentation**
has no good fit. `data-analyst` is the closest neighbor, but its
mission is "define and communicate the metrics that drive decisions"
— reporting, not modeling. Its outputs (`kpi-definition`,
`dashboard-spec`, `analysis-report`, `ab-test-plan`) are BI artifacts,
not modeling artifacts.

Reported 2026-05-01: user wants to scaffold an academic-research
project (radioactive-decay analysis). The domain itself is
correctly out-of-scope for the shared library — the user will add
the radioactive-decay expertise pack into the generated project's
`.claude/local/`. But the **role** of "person who designs models,
runs statistical analyses, validates results" is general across
academic research, ML projects, and analytics teams — and it
belongs in the library's extended tier.

## Goal

The library ships a `data-scientist` persona at the extended tier
that a user can select for projects centered on modeling,
inference, or scientific analysis. Its prompts, outputs, and
templates target modeling work, not BI work, so the persona is
useful out of the box without requiring the user to override its
defaults.

## Scope

### In Scope

- **New persona directory** at
  `ai-team-library/personas/extended/data-scientist/` with the same
  shape as its siblings (data-analyst, data-engineer):
    - `persona.md` — Category, Mission, Scope (Does/Does not),
      Activated When (modeling, inference, experimentation triggers),
      Hand-off boundaries, Strictness levels, Templates inventory.
    - `outputs.md` — output specifications for each artifact this
      persona produces (e.g., model-card, experiment-design,
      analysis-notebook, statistical-report).
    - `prompts.md` — task prompts for the typical work modes
      (exploratory analysis, hypothesis test, model selection,
      result reporting).
    - `templates/` — at minimum: `model-card.md`,
      `experiment-design.md`, `analysis-notebook.md`,
      `statistical-report.md`. Other templates as the BA / Developer
      determine fit.
- **README** in `ai-team-library/README.md`: persona table updated
  with the new entry; persona count incremented from 24 → 25.
- **Wiring through the library indexer** — the indexer already
  scans `extended/`, so no code changes are expected. Validate by
  re-indexing and confirming the persona shows up in
  `LibraryIndex.personas`.
- **Distinguish from data-analyst** — explicitly call out, in
  `data-scientist/persona.md`'s Hand-off section, that BI / KPI
  / dashboard work belongs to data-analyst. Symmetrically, update
  `data-analyst/persona.md`'s Hand-off section to defer
  modeling / statistical-test design / ML to data-scientist.

### Out of Scope

- **Domain-specific expertise** (radioactive decay, biology,
  finance, etc.) — those are project-specific and live in the
  user's `.claude/local/` after generation, not in the shared
  library.
- **`contracts.yml` for the new persona** — extended personas don't
  declare produces/consumes today (only the 5 core do). Adding
  contracts to extended personas is a broader question tracked
  separately; this bean follows the existing extended-tier shape.
- **MLOps / DevOps / pipeline ownership** — those belong to
  data-engineer + devops-release; the data-scientist hands off
  productionization, doesn't own it.
- **Business strategy / product decisions** — those are BA /
  product-owner.

## Acceptance Criteria

- [ ] (file:ai-team-library/personas/extended/data-scientist/persona.md)
      Persona file exists with sections matching the data-analyst
      template: Category, Mission, Scope (Does / Does not),
      Activated When, Hand-off, Strictness, Templates.
- [ ] (file:ai-team-library/personas/extended/data-scientist/outputs.md)
      Outputs file exists with at least four output specs.
- [ ] (file:ai-team-library/personas/extended/data-scientist/prompts.md)
      Prompts file exists with at least four task-mode prompts.
- [ ] (file:ai-team-library/personas/extended/data-scientist/templates/model-card.md)
      Model-card template exists.
- [ ] (file:ai-team-library/personas/extended/data-scientist/templates/experiment-design.md)
      Experiment-design template exists.
- [ ] (file:ai-team-library/personas/extended/data-scientist/templates/analysis-notebook.md)
      Analysis-notebook template exists.
- [ ] (file:ai-team-library/personas/extended/data-scientist/templates/statistical-report.md)
      Statistical-report template exists.
- [ ] (file-contains:ai-team-library/personas/extended/data-analyst/persona.md::data-scientist)
      Data-analyst hand-off section names data-scientist as the
      modeling / statistics owner.
- [ ] (file-contains:ai-team-library/personas/extended/data-scientist/persona.md::data-analyst)
      Data-scientist hand-off section names data-analyst as the BI
      / KPI / dashboard owner.
- [ ] (test:tests/test_library_indexer.py) The library indexer
      picks up `data-scientist` and surfaces it in
      `LibraryIndex.personas` (count is 25, not 24; new id appears).
- [ ] (file-contains:ai-team-library/README.md::data-scientist)
      README persona table includes the new persona row.
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check
      foundry_app/`).
- [ ] (manual) Launch the wizard, confirm Data Scientist appears in
      the Persona Selection page under the extended tier, and that
      a team of `team-lead + researcher-librarian + data-scientist
      + developer + tech-qa` validates green (no missing producers,
      no orphan-produces — depends on BEAN-289 which is already
      shipped).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Likely wave: **BA** (canonical mission, scope boundaries, and
> activation triggers — wording matters for personas), **Developer**
> (write persona.md / outputs.md / prompts.md / four templates),
> **Tech-QA** (indexer test, persona-content review for tone
> consistency with siblings, README update verification).
> Architect not required — this is content for an existing
> extended-tier slot, no new abstractions or module boundaries.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Why now.** User reported the gap while planning a real project
(academic research on radioactive decay). The radioactive-decay
domain itself is appropriately project-local, but the
data-scientist *role* is reusable and belongs in the library's
extended tier alongside data-analyst and data-engineer.

**Sibling reference.** Use
`ai-team-library/personas/extended/data-analyst/` and `…/data-engineer/`
as structural templates. They share the same shape: persona.md
(~160 lines), outputs.md (~180 lines), prompts.md (~165 lines), 3-4
templates in `templates/`. The data-scientist file should match
this scale and tone.

**Persona naming.** ID is `data-scientist` (slug). Display name is
"Data Scientist". This matches the `data-analyst` / `data-engineer`
naming pattern.

**Activation triggers** to seed BA's work (subject to refinement):
modeling task (regression / classification / clustering / Bayesian),
hypothesis test (t-test, ANOVA, chi-square, etc.), experiment
design (sample-size calculation, power analysis), model selection,
feature engineering for inference, statistical interpretation of
data-engineer outputs, scientific reporting (for academic projects).

**Out-of-scope reminder.** This bean does NOT add ML / stats
*expertise packs* (e.g., `scikit-learn`, `pytorch`, `bayesian-stats`).
Those are a separate library-content question. The data-scientist
persona's prompts and outputs should be method-agnostic enough to
combine with `python` + `mlops` (already in the library) and any
domain-specific expertise the user adds locally.

**Companion to BEAN-289.** Now that the contract-graph validator
correctly suppresses unactionable warnings, the user's first
realistic compose attempt (researcher + data-scientist + dev +
tech-qa) should validate green out of the box. This bean delivers
the persona that makes that compose attempt possible.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | — (comma-separated, actual not planned) |
| **Bounces** | — (Tech-QA → Developer kicks) |
| **Scope changes** | — (in-flight scope edits) |
| **Contract violations** | — (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | — (BEAN-272's NONE-justified) |
| **Dispatch mode** | — (in-process / tmux-worker / mixed) |