# BEAN-293 — Tech-QA Manual-Verification Observations

| Field | Value |
|-------|-------|
| **Bean** | BEAN-293 (compliance-gate hook pack default-on at baseline posture) |
| **Branch** | `bean/BEAN-293-compliance-gate-default-mismatch` |
| **SHA at verification** | `cb6d1d5` (Developer's Task 01) + Tech-QA Task 02 commit on top |
| **Date** | 2026-05-01 |
| **Verifier** | tech-qa |
| **Display available?** | No — headless session. Manual wizard walk substituted with automated tests against the real library through the real `HookSafetyPage`. |

## Headless substitution rationale

The bean's last two AC items are written as manual wizard checks. No
display is available in this session, so per the task file's
"headless substitution" guidance these have been converted to
automated tests that exercise the same page-state transitions. The
substitution tests run the **real** library (`build_library_index`)
through the **real** `HookSafetyPage` widget — no mocked
`HookPackInfo`, no shortcut around the wizard's own integration path.
This is the load-bearing path the user would touch in the GUI; the
only thing missing from the manual walk is the keyboard/mouse input,
which is mechanically equivalent to setting `card.is_enabled` and
calling `page.posture =`.

## Mapping each (manual) AC item to its automated coverage

### AC: "Launch wizard, walk with all defaults, click Generate succeeds"

Substituted by:

- `TestPostureIncompatibleRealLibrary::test_default_load_real_library_no_posture_errors[baseline]`
  — real library, real page, default posture, default selection
  → `_check_hook_posture_compatibility` produces zero messages.
- `TestPostureIncompatibleRealLibrary::test_default_load_real_library_baseline_unchecks_compliance_gate`
  — real library, real page, asserts the compliance-gate card is
  unchecked at default load.
- `TestPostureIncompatibleDefaultsFilter::test_default_load_passes_validator_at_baseline`
  — same assertion against the synthetic library, a tighter unit
  test for the filter logic itself.

The "[baseline]" parametrization plus its `[hardened]` and
`[regulated]` siblings widen this to all three postures, which the
manual walk doesn't cover (the user only walks one posture per
session).

### AC: "Toggling the posture combo updates card states sensibly"

Substituted by:

- `TestPostureIncompatibleDefaultsFilter::test_regulated_to_baseline_unchecks_now_incompatible_pack`
  — programmatic posture flip; pack that was on at the old posture
  and incompatible at the new one is unchecked.
- `TestPostureIncompatibleDefaultsFilter::test_baseline_to_regulated_does_not_restore_filtered_pack`
  — pins the documented one-way behavior so a future "remember
  default-on" refactor doesn't regress silently.
- `TestPostureIncompatibleDefaultsFilter::test_posture_change_with_empty_metadata_does_not_crash`
  (Tech-QA addition) — older-library packs survive the posture-change
  path. Developer's
  `test_pack_without_posture_metadata_not_filtered` only covers the
  `load_hook_packs` entry to `_apply_posture_filter`; this test pins
  the second call site (`_on_posture_changed`) so a refactor that
  replaces `not pack.posture_compatibility` with
  `pack.posture_compatibility[key]` is caught here, not in
  production.

### AC: "Manually enable compliance-gate at baseline, click Generate still fails with friendly BEAN-290 message"

Substituted by:

- `TestPostureIncompatibleRealLibrary::test_user_explicit_check_at_baseline_trips_validator`
  (Tech-QA addition) — load real library through real page at
  default baseline, confirm the defaults filter unchecked
  compliance-gate, then programmatically check it back, build
  `HooksConfig` via `to_hooks_config()`, build a `CompositionSpec`
  with one persona (`developer`), pass through
  `run_pre_generation_validation`, assert at least one
  `hook-pack-posture-incompatible` ERROR fires and that the friendly
  message names both `compliance-gate` and `baseline`. This proves
  the defaults filter and the validator surface are independent: the
  former runs at the page layer, the latter at composition time, and
  the user can still opt into an incompatible state if they
  consciously do so.

The validator surface itself is also independently regression-pinned
by the unchanged `TestHookPackPostureCompatibility` suite in
`tests/test_validator.py`.

## Audit re-walk results

Independently re-walked all 15 hook pack files in
`ai-team-library/claude/hooks/*.md` for `## Posture Compatibility`
tables with `Included: No` rows.

| Pack | baseline | hardened | regulated | Default-on filtered? |
|------|----------|----------|-----------|----------------------|
| `compliance-gate` | No | No | Yes | Yes — at baseline + hardened |
| `aws-limited-ops` | No | Yes | Yes | Yes — at baseline |
| `aws-read-only` | No | Optional | Yes (when explicitly stricter than `aws-limited-ops`) | Yes — at baseline |
| `az-read-only` | No | Yes | Yes | Yes — at baseline |
| `az-limited-ops` | Yes (advisory) | Yes | Yes | No — compatible everywhere |
| `pre-commit-lint` | Yes | Yes | Yes | No |
| `pre-commit-lint-js` | Yes | Yes | Yes | No |
| `post-task-qa` | Yes | Yes | Yes | No |
| `security-scan` | Yes (advisory) | Yes | Yes | No |
| `git-commit-branch` | Yes | Yes | Yes | No |
| `git-push-feature` | Yes (advisory) | Yes | Yes | No |
| `git-generate-pr` | Yes (advisory) | Yes | Yes | No |
| `git-merge-to-test` | Yes | Yes | Yes | No |
| `git-merge-to-prod` | Yes | Yes | Yes | No |
| `hook-policy` | (no posture table) | — | — | N/A — not a checkable pack |

**Divergence from Developer's audit:** none. The four packs Developer
flagged (`compliance-gate`, `aws-limited-ops`, `aws-read-only`,
`az-read-only`) are exactly the four with `Included: No` rows.
`hook-policy` matches Developer's claim of "no posture table". No
follow-up bean is required — the page-level filter keys off the
metadata, not pack id, so it handles all four generically. The
parametrized `test_default_load_real_library_no_posture_errors` test
confirms zero errors at every posture against the real library, which
is the strongest end-to-end pin for the audit conclusion.

## Validator-surface check (scope deviation guard)

```
$ git show cb6d1d5 -- foundry_app/services/validator.py
(no output)
```

Confirmed: Developer did not modify `foundry_app/services/validator.py`.
The bean's stated scope ("only **default hook-pack selection** changes")
is respected. `TestHookPackPostureCompatibility` in
`tests/test_validator.py` still passes unchanged — 5/5 tests green —
proving the validator surface is intact.

## Test counts

| Category | Count |
|----------|-------|
| Tests added by Developer (Task 01) | 8 (across `TestPostureIncompatibleDefaultsFilter` + `TestPostureIncompatibleRealLibrary`, plus `[baseline]/[hardened]/[regulated]` parametrization) |
| Tests added by Tech-QA (Task 02) | 2 (`test_posture_change_with_empty_metadata_does_not_crash`, `test_user_explicit_check_at_baseline_trips_validator`) |
| Full pytest pass count | 2448 (was 2446 on Developer's commit; +2 new) |
| `uv run ruff check foundry_app/` | clean |

## Verdict

All BEAN-293 acceptance criteria are satisfied. No regressions
observed. The bean is ready for the orchestrator's verification +
close phase.
