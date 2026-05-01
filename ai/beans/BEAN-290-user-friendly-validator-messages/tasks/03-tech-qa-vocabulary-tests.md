# Task 03 — Tech-QA: Vocabulary tests + regression sweep

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-290 / 03 |
| **Owner** | tech-qa |
| **Depends On** | 02 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Bind the new vocabulary into the test suite so future regressions fail
fast: every UI-surfaced message is exercised, the blocklist words never
appear in `.message`, the user-vocabulary nouns DO appear, and the
banner double-prefix can never come back.

## Inputs

- `ai/outputs/ba/BEAN-290-validator-message-phrasing.md` — the source of
  truth for what each message should say (use this to derive positive
  assertions).
- `tests/test_validator.py` — existing validator tests; extend rather
  than replace. Codes are unchanged, so existing code-keyed assertions
  stay green.
- `foundry_app/services/validator.py` — the implementation you are
  protecting.
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` and
  `tests/test_persona_page.py` (or whichever wizard tests already
  cover `_coherence_label`) — extend with the new headline copy.
- `foundry_app/ui/generation_worker.py` and any existing test that
  exercises the failure emit path — add the no-double-prefix assertion.

## Acceptance Criteria

- [ ] `tests/test_validator.py` has, for every in-scope code, at least
      one test that constructs a composition triggering the code and
      asserts:
        - **Negative:** none of the substrings `producer`, `consumer`,
          `orphan`, `node`, `graph`, `type '` appear in `msg.message`.
        - **Positive — persona present:** when the message names a
          persona, the persona's display name appears in `msg.message`.
        - **Positive — artifact present:** when the message names an
          artifact, the human label from the BA reference doc appears
          in `msg.message`.
- [ ] `tests/test_validator.py` has a `missing-producer` test asserting
      the message includes a concrete action (e.g., contains "Add" plus
      the producer persona's display name).
- [ ] `tests/test_validator.py` has an `orphan-produces` test asserting
      the message reads as a friendly suggestion (no graph vocabulary,
      a display name appears for the suggested consumer).
- [ ] `tests/test_validator.py` has a `hook-pack-posture-incompatible`
      test asserting `msg.message` does NOT contain
      `Posture Compatibility table` or `Included: No`.
- [ ] Persona-page test asserts the new red / amber / green headline
      strings (no "missing producers" / "orphan produces" leakage).
- [ ] Banner-construction test asserts the failure path does not emit a
      string starting with `"Validation failed:"` (or containing the
      sequence `"Generation failed: Validation failed:"`).
- [ ] `uv run pytest` — all tests pass.
- [ ] `uv run ruff check foundry_app/` — clean.
- [ ] **Manual** — launch the wizard with a deliberately broken team
      (e.g., `developer + tech-qa` only). Confirm every surfaced
      message reads like English a non-engineer would write. Record the
      verification (screenshot or quoted text + selected team) in
      `ai/outputs/tech-qa/BEAN-290-manual-verification.md`. If the
      environment cannot launch the GUI, note that explicitly in the
      same file and document the equivalent text-based proof.

## Definition of Done

- All tests pass and lint is clean.
- Manual-verification doc committed.
- Status updated to Done; the telemetry hook stamps Completed/Duration.
