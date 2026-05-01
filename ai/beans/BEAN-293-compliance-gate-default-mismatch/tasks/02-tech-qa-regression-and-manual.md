# Task 02 — Tech-QA: Regression sweep + manual wizard verification at all three postures

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-293 / 02 |
| **Owner** | tech-qa |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify that Developer's Task 01 commit makes wizard
defaults self-consistent at all three postures, that user-driven
posture changes don't leave the page in an invalid state, that the
validator's posture-compatibility check still fires when a user
explicitly enables an incompatible pack, and that no other pack in
the library fell through the audit.

Run the manual wizard verification listed in the bean's Acceptance
Criteria (or document the headless substitution if no display is
available). Capture observations in
`ai/outputs/tech-qa/BEAN-293-manual-verification.md`.

## Inputs

- `ai/beans/BEAN-293-compliance-gate-default-mismatch/bean.md` — full
  AC list. The (manual) AC items are this task's responsibility.
- Developer's Task 01 commit on
  `bean/BEAN-293-compliance-gate-default-mismatch` — the page-level
  defaults filter, any new helper, the new tests, and the audit
  notes from the commit message body.
- `tests/test_hook_safety_page.py` — Developer's new tests. Tech-QA
  should add coverage for any gap they identify (e.g., the empty-
  `posture_compatibility` case for older library packs).
- `ai-team-library/claude/hooks/*.md` — re-walk the audit
  independently. Confirm Developer's findings; flag any pack
  Developer missed.
- `foundry_app/services/validator.py` —
  `_check_hook_posture_compatibility` (no change expected; verify
  none).

## Acceptance Criteria

- [ ] Re-walk the library audit independently. Compare your list to
      Developer's. If you find any divergence, document it in the
      manual-verification observation file and either (a) add a
      regression test that pins the new pack as default-off at the
      right posture, or (b) file a follow-up note for the
      orchestrator to open a bean.
- [ ] Verify the validator surface is unchanged: every test in
      `TestHookPackPostureCompatibility` (in `tests/test_validator.py`)
      still passes with no edit. If Developer touched the validator,
      that's a deviation from scope and you should kick it back via
      `/handoff` rather than absorb it.
- [ ] Add a regression test for the older-library case: if a
      `HookPackInfo.posture_compatibility` is empty (older library
      that hasn't been re-indexed), the page's posture filter must
      not crash and must leave the card in its existing checked
      state. This is the parser fallback path that
      `_check_hook_posture_compatibility` already documents (line
      ~167 — "Packs whose metadata is missing (older libraries) are
      skipped"). The page should mirror that policy.
- [ ] Add a regression test for the user-explicit case: with the
      page loaded at `baseline` (so `compliance-gate` is unchecked),
      programmatically check the `compliance-gate` card and call
      `to_hooks_config()`; pass the resulting composition through
      `run_pre_generation_validation` and assert that
      `hook-pack-posture-incompatible` ERROR fires. This proves the
      validator surface is reachable when the user explicitly opts in
      to the incompatible state — the bean's last (manual) AC item
      converted to an automated test.
- [ ] (manual) Launch `uv run foundry`. Walk the wizard with all
      defaults; confirm: (a) Generate succeeds, (b) on the
      hook-safety page, `compliance-gate` is unchecked, (c) toggling
      the posture combo updates the card states sensibly. Capture
      observations in `ai/outputs/tech-qa/BEAN-293-manual-verification.md`.
      If no display is available (headless session), document the
      substitution: list the automated tests that exercise the same
      page-state transitions, and note the SHA on the branch.
- [ ] (manual) From the same wizard, manually check `compliance-gate`
      at `baseline` and click Generate; confirm generation now
      blocks with the friendly BEAN-290 message (validator surface
      intact). Headless substitution: the user-explicit regression
      test above covers this.
- [ ] `uv run pytest` passes — full suite, no skips beyond pre-existing
      ones.
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] If any criterion fails or any regression surfaces, do NOT close
      this task as Done. Set Status back to `In Progress`, document
      the failure in the task's Notes section, and return so the
      orchestrator can dispatch a Developer follow-up.

## Definition of Done

- All acceptance criteria checked.
- Manual-verification observation file at
  `ai/outputs/tech-qa/BEAN-293-manual-verification.md`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Bean is ready for the orchestrator's verification + close phase
  (Phase 5 of `/long-run`).

## Notes

**Audit divergence.** If your audit surfaces a pack Developer missed,
your default response is to absorb the additional regression test
yourself rather than send the work back. The bean's audit AC is
intentionally lightweight ("document any divergence") because the
scope is "make defaults consistent," not "exhaustively re-validate
the library."

**Older-library case.** Older libraries (pre-BEAN-263) may have
hook-pack files without a `## Posture Compatibility` section, in
which case `posture_compatibility` is `{}`. The validator's existing
fallback ("if missing, skip") is correct; the page should mirror it
silently rather than crash or assume a default. If Developer's
implementation already handles this, your test serves as a
regression pin; if not, file the gap as a Tech-QA → Developer kick
with a one-line note.

**No mocks for the manual substitution.** The headless substitution
test must run the **real** library through the **real** page (no
mocked HookPackInfo). The wizard's own integration is the load-
bearing path; mocking it defeats the purpose.
