# BEAN-293: Compliance-Gate Hook Pack Should Not Default-On at Baseline Posture

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-293 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 18:12 |
| **Completed** | 2026-05-01 18:25 |
| **Duration** | 13m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

A fresh wizard session at the default `baseline` safety posture, with
the user touching nothing on the hook-safety page, fails generation
with the (correctly user-friendly, post-BEAN-290) error:

```
Can't generate yet — The 'compliance-gate' hook pack isn't available
at the 'baseline' safety posture. Either remove the pack, or raise your
composition's posture so it's allowed.
```

Reported 2026-05-01: the user explicitly stated they did **not** select
`compliance-gate`. It was sitting in the composition as a default. The
`compliance-gate` pack's own `Posture Compatibility` table declares
itself incompatible with `baseline` (and `hardened`), only allowed at
`regulated`. So the system ships a default selection that fails its own
default-posture validator on the first generation attempt.

This is not a validator bug — the validator is correctly catching a
genuine mismatch. It is a **defaults bug**: the default state of the
wizard is internally inconsistent. A first-time user who clicks through
without changing hook settings cannot generate a project.

## Goal

Out-of-the-box defaults must be self-consistent. After this bean, a
fresh wizard session at the default posture, with no user changes to
the hook-safety page, generates a project successfully. The `baseline`
posture remains the wizard default, the `compliance-gate` pack remains
in the library, and the validator's posture-compatibility check stays
intact — only the **default hook-pack selection** changes (or the
inverse: posture default changes), so the initial state is valid.

## Scope

### In Scope

- **Investigate the default source.** Trace where `compliance-gate`
  gets selected by default in a fresh wizard session. Likely sites:
  - The hook-safety wizard page (`hook_safety_page.py`) initial
    selection logic — does it default-select all packs, or specific
    packs?
  - The `HookPackSelection.enabled` field default in
    `foundry_app/core/models.py`.
  - Any "default-enabled" metadata in the `compliance-gate` pack
    file under `ai-team-library/claude/hooks/compliance-gate.md`.
  - The `safety_writer` service defaults.
  - The `_make_spec`-style fixtures or `composition.yml` template the
    wizard initializes from.
- **Pick a fix and apply it.** Three viable options; the Developer
  picks one with rationale documented inline:
  - **Option A (preferred):** Drop `compliance-gate` from any
    default-on selection. It stays in the library; users select it
    consciously when their project warrants it. Posture default stays
    `baseline`.
  - **Option B:** Keep `compliance-gate` default-selected, but at
    selection time the wizard auto-bumps the composition's posture to
    the lowest level the pack accepts (`regulated` here). This makes
    the user-facing posture change visible, not silent.
  - **Option C:** Wizard prevents incompatible combinations at the UI
    level — gray out (or visibly mark as locked) any pack whose
    posture-compatibility table excludes the current posture. Selecting
    a locked pack either does nothing or raises a tooltip explaining
    the posture requirement. (This is broader UX work — likely a
    follow-up bean rather than this one.)
- **Cover the default state with a regression test.** A test that
  builds the wizard's default composition (no user input) and runs
  `run_pre_generation_validation` must produce zero errors.
- **Audit other packs for the same trap.** While in the area, check
  whether any other pack is default-on with a posture mismatch under
  any of the three postures (`baseline`, `hardened`, `regulated`). Fix
  any others surfaced by the audit, or file follow-up beans if the
  scope grows.

### Out of Scope

- Changing the `compliance-gate` pack's posture-compatibility metadata.
  The pack genuinely is for compliance contexts and should remain
  off-limits at baseline.
- Re-wording the validator error (BEAN-290 already friendlified it —
  it reads correctly when it does fire on a *user-chosen* incompatible
  combo).
- Changing the validator's posture-compatibility check itself. The
  check stays; only defaults change.
- BEAN-292's contract-graph relaxation. These two beans are
  independent: BEAN-292 changes severity for `missing-producer`;
  BEAN-293 changes the *default selection* so a real ERROR doesn't
  fire on first run.
- A full hook-safety-page UX redesign (Option C above is sketched but
  out of scope here unless the Developer finds it cheaper than A/B
  during investigation).

## Acceptance Criteria

- [ ] (test:tests/) A wizard composition built from defaults at the
      default posture (`baseline`) validates with zero errors and zero
      `hook-pack-posture-incompatible` warnings.
- [ ] (test:tests/test_hook_safety_page.py) The hook-safety page's
      initial selection state, when constructed with a fresh
      `LibraryIndex` and the default `Posture.BASELINE`, does not
      include any pack whose `posture_compatibility` table marks
      baseline as `Included: No`.
- [ ] (test:tests/) Posture-incompatibility regression test: for each
      posture (`baseline`, `hardened`, `regulated`), the default pack
      selection produces zero `hook-pack-posture-incompatible` errors
      against `_library_with_compliance_gate()` (or the real library).
- [ ] (test:tests/) The validator's existing
      `hook-pack-posture-incompatible` check still fires when the user
      explicitly enables an incompatible pack at the wrong posture
      (the existing tests in `TestHookPackPostureCompatibility` continue
      to pass — no regression of the validator surface).
- [ ] (test:tests/) All tests pass (`uv run pytest`).
- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).
- [ ] (manual) Launch the wizard, do not change anything on the
      hook-safety page, click Generate → succeeds without the
      compliance-gate posture error.
- [ ] (manual) Launch the wizard, manually enable `compliance-gate` at
      the default `baseline` posture, click Generate → still fails with
      the friendly BEAN-290 message (validator surface intact).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Drop posture-incompatible packs from default selection + audit | developer | — | Done |
| 2 | Regression sweep + manual wizard verification at all three postures | tech-qa | 01 | Done |

> Skipped: BA (default), Architect (default)
> Wave: **Developer → Tech-QA**. Architect not required — this is a
> defaults alignment, not a model change. BA not required — the wording
> is already correct; only the trigger condition changes.

## Changes

| File | Lines |
|------|-------|
| `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` | +49 / -0 |
| `tests/test_hook_safety_page.py` | +369 / -0 |
| `ai/outputs/tech-qa/BEAN-293-manual-verification.md` | +149 / -0 |
| `ai/beans/BEAN-293-…/tasks/01-developer-fix-defaults-and-audit.md` | +172 / -0 |
| `ai/beans/BEAN-293-…/tasks/02-tech-qa-regression-and-manual.md` | +127 / -0 |
| `ai/beans/BEAN-293-…/bean.md` | +9 / -9 |

## Notes

**Why High priority.** A first-time user clicking through the wizard
with all defaults cannot generate a project. That is a P0-style
broken-out-of-box defect for a tool whose core value proposition is
"generate a Claude Code project from defaults."

**Investigation hint.** Likely starting points based on a quick
codebase scan: `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py`
for the page-side default selection logic;
`foundry_app/core/models.py` for `HookPackSelection.enabled`'s
field default; any "default-enabled" or "default-on" annotation in the
`compliance-gate.md` pack file under `ai-team-library/claude/hooks/`.

**Why not just bump the default posture?** Bumping `baseline →
regulated` would silently flip the safety posture for every new
project, which is a much bigger behavioral change than dropping one
pack from the default selection. Option A keeps the surface change
minimal and respects the principle that posture is the user's choice,
not an indirect side effect of pack selection.

**Reported by user 2026-05-01** while doing the live BEAN-290
verification. The friendly message worked exactly as designed (clear
problem, clear options) — the underlying defaults bug was independent.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Drop posture-incompatible packs from default selection + audit | developer | 4m | 687,276 | 5,484 | $1.48 |
| 2 | Regression sweep + manual wizard verification at all three postures | tech-qa | 4m | 546,816 | 3,321 | $1.42 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 8m |
| **Total Tokens In** | 1,234,092 |
| **Total Tokens Out** | 8,805 |
| **Total Cost** | $2.90 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | developer, tech-qa |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |