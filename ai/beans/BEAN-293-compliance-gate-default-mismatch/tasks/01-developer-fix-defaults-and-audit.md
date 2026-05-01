# Task 01 — Developer: Drop posture-incompatible packs from default selection + audit

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-293 / 01 |
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 18:15 |
| **Completed** | 2026-05-01 18:19 |
| **Duration** | 4m |

## Goal

Make the wizard's default state self-consistent: with the default
posture (`baseline`), no hook pack should be enabled-by-default if its
`Posture Compatibility` table marks that posture as `Included: No`. The
fix lives at the page-defaults layer — the validator, the
`HookPackInfo.posture_compatibility` data, and the `compliance-gate`
pack file all stay as-is.

Implementation choice (Option A from the bean): when the hook-safety
page renders cards, walk all cards after creation and uncheck any pack
whose `posture_compatibility[current_posture].included == "No"`. Also
re-run that check when the posture combo changes, so that switching
`regulated → baseline` immediately disables `compliance-gate` (and any
analogous pack), rather than leaving the user with an invalid state to
discover at Generate time.

Audit other packs in the library for the same trap under each of the
three postures (`baseline`, `hardened`, `regulated`). Document any
discoveries in the commit message; if the fix in this task closes
them (it should, since it operates on whatever posture is selected),
no follow-up bean is needed.

## Inputs

- `ai/beans/BEAN-293-compliance-gate-default-mismatch/bean.md` — full
  Problem Statement, Goal, Scope, Acceptance Criteria, and the
  rationale for choosing Option A over B/C in the bean's Notes.
- `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` —
  - `HookPackCard._build_ui` line ~226: `_checkbox.setChecked(True)`
    is the unconditional default-on. Do NOT remove this — the
    page-level filter is the right layer (so an explicit
    `card.is_enabled = True` from `load_from_selection` still works).
  - `load_hook_packs` line ~604 — calls `_resolve_default_conflicts`
    after building cards. Add a sibling/follow-up step that filters
    by posture compatibility against `self._posture_combo.currentText()`
    (or the equivalent property) **after** the conflict resolution.
  - `_on_posture_changed` line ~877 — currently just emits
    `selection_changed`. Add the posture-incompatibility filter here
    too so user-driven posture changes trigger the same purge.
- `foundry_app/services/validator.py` —
  `_check_hook_posture_compatibility` line ~157, the source of the
  ERROR this defaults bug trips. Read for context but do NOT modify;
  the validator is correct.
- `foundry_app/core/models.py` — `HookPackInfo.posture_compatibility`
  line ~673. The `included` field is the truth source ("No" → drop
  the pack at default time).
- `ai-team-library/claude/hooks/compliance-gate.md` — the pack whose
  Posture Compatibility table currently shows `baseline | No |`.
  Confirm the parser populates `posture_compatibility` for this pack
  (the test fixtures already do; spot-check the real library if you
  add doubts).
- `ai-team-library/claude/hooks/*.md` — audit each pack file's
  `## Posture Compatibility` table for any other "Included: No"
  rows.
- `tests/test_hook_safety_page.py` — existing tests for default state
  and posture switching. The new behavior must be regression-tested
  here.

## Acceptance Criteria

- [ ] After `load_hook_packs(library_index)` is called on a fresh page
      with the default `Posture.BASELINE`, no card is enabled whose
      `pack.posture_compatibility["baseline"].included` equals "No"
      (case-insensitive). For the real library, this means
      `compliance-gate` is unchecked-by-default.
- [ ] After the user switches posture via the combo (e.g.,
      `baseline → regulated`), packs that were previously hidden by
      the posture filter and are now compatible become checked again
      **only** if they were checked-by-default to start with — i.e.,
      the page tracks "user explicit choice" vs "default" if a clean
      revert behavior is needed. If implementing that distinction is
      heavier than the bean warrants, the simpler behavior is
      acceptable: switching back keeps the pack unchecked. Document
      whichever you choose.
- [ ] After the user switches posture via the combo from `regulated →
      baseline`, any pack that is now incompatible at baseline is
      unchecked automatically (no error surfaces at Generate time
      from a stale enabled pack).
- [ ] `_resolve_default_conflicts` continues to work as-is for the
      conflict-pair behavior. The new posture filter runs **after**
      conflict resolution so the two policies compose without
      undoing each other's choices. (Order matters: if we resolved
      conflicts on a posture-incompatible enabled pack, we'd be
      resolving against a card we'd then disable — wasted work, no
      correctness impact, but cleaner to filter first by posture.)
      Either order is acceptable; pick one and document.
- [ ] (test:tests/test_hook_safety_page.py) A new test asserts that
      `load_hook_packs(real_library_index)` with default posture
      `baseline` leaves `compliance-gate` unchecked. Use the real
      library fixture if one already exists; otherwise build a
      synthetic `LibraryIndex` with a single posture-incompatible
      pack.
- [ ] (test:tests/test_hook_safety_page.py) A new test asserts that
      after the page is loaded with `baseline` and `compliance-gate`
      unchecked, switching posture to `regulated` (programmatically
      via the page's posture setter) does **not** check
      `compliance-gate` (default behavior: posture switching purges,
      not restores), OR (alternative behavior the developer picks)
      checks it back if the developer implemented the explicit
      tracking. The test should reflect the implemented behavior.
- [ ] (test:tests/test_hook_safety_page.py) A new test asserts that
      switching posture from `regulated → baseline` after
      `compliance-gate` was checked unchecks the card.
- [ ] (test:tests/) Wizard-default regression: a wizard composition
      built from defaults at the default posture passes
      `run_pre_generation_validation` with no
      `hook-pack-posture-incompatible` errors. Use the existing
      `_make_spec`-style helpers if any; if not, construct a
      `CompositionSpec` from the page's `to_*_config()` accessors
      and call the validator directly.
- [ ] (test:tests/) Posture-incompatibility regression for each
      posture: for `baseline`, `hardened`, and `regulated`, the page's
      default selection (after `load_hook_packs`) yields zero
      `hook-pack-posture-incompatible` errors against the real
      library.
- [ ] (test:tests/) The validator's existing
      `hook-pack-posture-incompatible` check still fires when the user
      explicitly enables an incompatible pack at the wrong posture
      (e.g., manually checking `compliance-gate` at `baseline`). The
      validator surface is unchanged — no test in
      `TestHookPackPostureCompatibility` should regress.
- [ ] Audit the library: scan `ai-team-library/claude/hooks/*.md` for
      any other pack whose Posture Compatibility table marks any of
      the three postures as `Included: No`. Document the findings in
      the commit message body. If the audit surfaces a pack that the
      new defaults filter does NOT cover (e.g., a pack that's loaded
      but its metadata isn't parsed), file a follow-up note in the
      task's Notes section — the orchestrator can decide whether to
      open a follow-up bean.
- [ ] `uv run pytest` passes locally.
- [ ] `uv run ruff check foundry_app/` passes locally.

## Definition of Done

- All acceptance criteria checked.
- Code committed on branch `bean/BEAN-293-compliance-gate-default-mismatch`.
- Status set to `Done`; the PostToolUse telemetry hook auto-stamps
  `Completed` and `Duration`.
- Hand off to Tech-QA via `/handoff` (or by setting Task 02 to ready).

## Notes

**Why this lives on the page, not in the model.** The bean's Notes
explicitly call this a *defaults* bug, not a *validator* bug. The
`HookPackSelection.enabled` field default in `models.py` is generic
across postures — there's no per-posture default that lives there
sensibly. The page is the only place that knows both the current
posture and the pack metadata at the same time, which is exactly what
the filter needs.

**One more detail.** When the page is restored from a saved
composition (`load_from_selection`), do not run the posture filter —
the saved state is the source of truth. The filter only applies at
fresh `load_hook_packs` time and on user-driven posture changes.

**Audit hint.** The kit ships ten hook packs by my count (compliance-
gate, post-task-qa, security-scan, pre-commit-lint, hook-policy, and
five git-* packs). The `Posture Compatibility` tables are short — a
five-minute scan should suffice.
