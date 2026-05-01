# Task 02 — Developer: Wire canonical messages into validator + UI

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-290 / 02 |
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Replace every in-scope `ValidationMessage.message` string with the BA's
canonical phrasing, add an artifact-id → human label helper, fix the
persona-page headline, drop the banner double-prefix, and strip
data-structure parentheticals. Codes and severities stay unchanged.

## Inputs

- `ai/outputs/ba/BEAN-290-validator-message-phrasing.md` — canonical
  phrasing reference produced by Task 01 (variable names, per-code text,
  headline copy, artifact-label table, banner lead-in decision).
- `foundry_app/services/validator.py` — message construction sites for
  every in-scope code.
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` —
  `_update_coherence_indicator` and the headline strings around it.
- `foundry_app/ui/generation_worker.py` — site of the inner `"Validation
  failed:"` prefix to drop.
- `foundry_app/ui/screens/generation_progress.py` — site of the outer
  `"Generation failed:"` prefix; confirm whether to keep it or replace
  with the BA-recommended lead-in.
- `ai-team-library/contracts/artifact-types.yml` — source for artifact
  human labels (read description; fall back to BA's overrides table).
- `foundry_app/core/models.py` — `PersonaInfo` shape, including the
  display-name field (use it instead of the persona id wherever a persona
  is named in user-facing prose).

## Acceptance Criteria

- [ ] Every in-scope code in `validator.py` constructs its `.message`
      from the BA reference doc — no leftover internal vocabulary
      (`producer`, `consumer`, `orphan`, `node`, `graph`, or
      `type '<id>'`).
- [ ] An artifact-label helper exists (e.g.,
      `foundry_app/services/artifact_labels.py` or a private function on
      validator) that resolves an artifact id to its human label. Prefer
      reading `artifact-types.yml` via `LibraryIndex` if it already
      exposes the registry; otherwise add a small mapping next to the
      validator with the labels from BA's table.
- [ ] Persona display name is used wherever a persona is named in a
      message; persona id only appears as a fallback when no display
      name exists.
- [ ] `hook-pack-posture-incompatible` message contains no substring
      `Posture Compatibility table` or `Included: No`. The internal
      detail can land on the logger; the message stays clean.
- [ ] `generation_worker.py` no longer wraps validator errors with
      `"Validation failed: …"`. The cleaned validator messages reach the
      banner unprefixed (or with the BA-recommended lead-in).
- [ ] `_coherence_label` headline copy in `persona_page.py` matches the
      BA reference doc's red / amber / green strings.
- [ ] `uv run pytest` — all tests pass.
- [ ] `uv run ruff check foundry_app/` — clean.

## Definition of Done

- All listed files updated; no internal-vocabulary regressions
  introduced elsewhere (`grep -n 'producer\|consumer\|orphan' validator.py`
  shows only code-name usages, no message-text usages).
- Artifact-label helper covers every id referenced by in-scope messages.
- Status updated to Done; the telemetry hook stamps Completed/Duration.
