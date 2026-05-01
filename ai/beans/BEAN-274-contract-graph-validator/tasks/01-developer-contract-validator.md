# Task 01: Implement `contract_validator` — API, Pipeline Integration, Wizard Indicator

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 00:28 |
| **Completed** | 2026-05-01 00:34 |
| **Duration** | 6m |

## Goal

Build a compose-time contract-graph validator that checks every consumed
artifact type has a producer somewhere on the team. Hard-fail standard
generations on unsatisfied consumes, warn (and record in
`GenerationManifest`) on overlay re-generations. Surface a real-time
"team coherence" indicator on the wizard's persona page.

## Inputs

- `ai/beans/BEAN-274-contract-graph-validator/bean.md` — bean spec.
  Read **Scope — In Scope**, **Acceptance Criteria**, **Notes**.
- `ai/context/decisions.md` — **ADR-013** (persona produces/consumes
  contracts) for the contract format. The data is already loaded —
  `PersonaInfo.produces` and `PersonaInfo.consumes` exist.
- `foundry_app/core/models.py`:
  - `PersonaInfo` (around line 596) — fields `produces`, `consumes`.
  - `LibraryIndex` — exposes `personas` and `artifact_types`.
  - `ValidationResult` (around line 479) and `ValidationMessage` —
    reuse the existing structured-finding shape; do not invent a new one.
  - `GenerationManifest` (around line 502) — has `all_warnings`/stage
    warnings. Use the existing manifest channel for overlay warnings.
- `foundry_app/services/generator.py`:
  - `generate_project` (around line 269). Wire the new check between
    `_apply_default_team` (line 334) and `run_pre_generation_validation`
    (line 337) — call it `validate_contract_graph`.
  - The pipeline-stage runner (`_run_stage` in `_run_pipeline`) is the
    pattern for surfacing stage-level warnings if you want a stage entry
    rather than an inline check. Either is acceptable; pick one.
- `foundry_app/services/validator.py` — for the existing validator
  patterns (ValidationResult construction, error/warning emission).
  Either extend this file or add a new `contract_validator.py` —
  the bean's wording is "or extend `validator.py`", you choose.
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` —
  for the team-coherence indicator. Look at the existing tier-group
  rendering (BEAN-271 just landed it) for the pattern. The indicator
  should react to selection changes (signal/slot) and render a
  green/yellow/red badge with the producer/consumer balance summary.

## Acceptance Criteria

- [ ] `validate_contract_graph(personas, registry)` exists and returns
      a structured `ValidationResult` (or equivalent — must include
      ordered messages with severity).
- [ ] Pipeline calls it between `_apply_default_team` and
      `run_pre_generation_validation` in `generator.py`.
- [ ] **Standard generation** (overlay=False): unsatisfied consume
      → hard fail with a clear, actionable message naming the missing
      artifact type and suggesting which producer persona to add.
      Format: `Missing producer for type '<type>'. Consumed by:
      <persona-list>. Producers in library: <persona-list>. Add one to
      your team.`
- [ ] **Overlay generation** (overlay=True): same condition logs a
      warning, records it in `GenerationManifest` (via stage warnings
      or a dedicated field), and the pipeline proceeds.
- [ ] **Orphan produces** (a persona produces a type nobody on the
      team consumes — note: not the same as `_log_dangling_producers`
      which scans the whole library): emit a warning in both modes.
- [ ] Wizard's persona page shows a real-time indicator that reflects
      the contract graph state of the currently-selected team:
      🟢 all consumes satisfied; 🟡 orphan produces; 🔴 missing producer.
      Indicator updates when persona selection changes.
- [ ] Lint clean: `uv run ruff check foundry_app/`.

## Definition of Done

- New API exists with the documented signature.
- Pipeline calls it; standard mode hard-fails; overlay mode warns and
  proceeds.
- Wizard renders the indicator.
- Lint clean.
- Status set to `Done`.

## Notes

**Reuse, don't reinvent.** `ValidationResult`/`ValidationMessage` and
`GenerationManifest.all_warnings` already exist. Use them. Do not
introduce a parallel result type.

**Out-of-scope per the bean:**
- Validating artifact *content* (only graph connectivity here).
- Suggesting which persona to add (the error names producers; that's
  enough — actual suggestion algorithm is a follow-up).
- Validating extended personas (BEAN-271 landed tiering; this bean
  validates *whatever team is composed* — extended or core. There is
  no special "relaxed mode for unknown types"; if an extended persona
  declares an unknown artifact type, that's already caught by the
  existing ADR-013 loader as a warning).

**Tests**: do not write the comprehensive test suite here — Tech-QA
(Task 02) owns it. But add at most 1-2 smoke tests inline if needed
to verify your API shape during development.

**Wizard indicator caveat.** Be conservative with Qt signals — the
persona page already wires selection changes for the tier groups. Add
a single connection that recomputes the indicator. Avoid recomputing
on every checkbox flicker; throttle if needed.
