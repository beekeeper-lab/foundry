# BEAN-286: Wizard Surfaces Validation Findings Inline (Persona + Hook Safety Pages)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-286 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-05-01 |
| **Started** | 2026-05-01 11:34 |
| **Completed** | 2026-05-01 11:42 |
| **Duration** | 1598h 34m |
| **Owner** | team-lead |
| **Category** | App |
| **Depends On** | — |

## Problem Statement

Three related UX failures, all the same shape: the validator already constructs **fully actionable** finding messages, but the wizard collapses them to opaque counts (or doesn't show them at all). Users hit the gap when they accept defaults and get a hard validation error at the last step with no explanation of what to fix.

Concrete failures observed during 2026-05-01 GUI walk-through:

1. **Persona page team-coherence indicator**. With the 5 core personas selected, the indicator shows "🟡 Team coherence: 3 orphan produces — produced types with no consumer on the team." It does **not** name the artifact types (`dev-decision`, `merge-summary`, `test-suite`) or the producing personas. The user is told there's a problem but not what it is or what to do about it. The same indicator would behave identically in 🔴 state — counts only, no remediation hints.

2. **Hook Safety page has no real-time conflict indicator at all.** The page lets users select mutually-exclusive hook packs (e.g., `az-limited-ops` + `az-read-only`, declared mutually exclusive per ADR-005) without any in-page warning. The conflict is only caught by the validator at generation time, far too late.

3. **Hook pack defaults ship an invalid configuration.** `hook_safety_page.py:232` defaults every pack's checkbox to `True`. Out of the box, every conflicting pair is enabled simultaneously. A user who accepts defaults and clicks Generate gets a hard validation failure on configuration they did not choose.

## Goal

When the validator has actionable information about the user's current selection, the wizard surfaces it **at the page where the user can act on it** — not at generation time, not as opaque counts.

## Scope

### In Scope

- **Persona page (`foundry_app/ui/screens/builder/wizard_pages/persona_page.py`)**:
  - `_update_coherence_indicator()` (lines 610-674) renders the **per-message text** the validator produces, not just counts.
  - For 🔴: list each missing-producer message verbatim from `validate_contract_graph()` (e.g., "Missing producer for type 'adr'. Consumed by: tech-qa. Producers in library: architect. Add one to your team.").
  - For 🟡: list each orphan-produces message verbatim (e.g., "Persona 'developer' produces type 'dev-decision' but no persona on the team consumes it.").
  - Cap at 5 visible findings; longer lists collapse to "+N more" so the wizard doesn't blow out vertically.
- **Hook Safety page (`foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py`)**:
  - Add a real-time conflict indicator (same shape as the persona page's coherence label) that walks each enabled pack's `## Conflicts With` declarations and surfaces conflicting pairs by name. 🔴 when a conflict exists; 🟢 when clear.
  - Indicator updates when pack checkboxes toggle.
- **Hook pack default selection bug**:
  - When the wizard initially populates packs, walk the conflict graph and uncheck conflicts. Approach: keep the first pack of any conflicting pair checked; leave the rest off. (Or default everything off — pick the simpler implementation; prefer "first wins" to preserve the ergonomic spirit.)
- **Tests** for each:
  - Persona-page indicator renders specific messages in 🔴 / 🟡 states.
  - Hook-safety page conflict indicator transitions through states as packs toggle.
  - Default-load test: with no user input, the wizard's pack selection is conflict-free.

### Out of Scope

- Suggesting *which* persona to add (the missing-producer message already lists library producers — that's enough).
- Changing the validator's message text (it's already good).
- Restyling the indicator beyond layout needed to fit the new content.
- Posture / strictness UI changes (BEAN-262 already wired the underlying validation).

## Acceptance Criteria

- [x] (test:tests/test_persona_page.py) Persona-page indicator shows the validator's per-message text, not counts, in 🔴 and 🟡 states. — `TestCoherenceIndicatorVerbatimMessages`
- [x] (test:tests/test_persona_page.py) Indicator caps visible findings at 5 and shows a "+N more" line when truncated. — `TestCoherenceIndicatorTruncationCap`
- [x] (test:tests/test_hook_safety_page.py) Hook Safety page renders a conflict indicator; transitions through 🔴 (conflicting packs both enabled) → 🟢 (no conflicts) as packs toggle. — `TestConflictIndicator`
- [x] (test:tests/test_hook_safety_page.py) Default-load: with the real library indexed and no user input, the wizard's hook-pack selection is conflict-free under `validate_pack_compatibility()`. — `test_default_load_real_library_is_conflict_free`
- [ ] Manual GUI verification: select 5 core personas → indicator names `dev-decision`, `merge-summary`, `test-suite` and their producers. *(deferred — covered by automated verbatim-message tests)*
- [ ] Manual GUI verification: open Hook Safety page → no conflict warning at default load; manually enable a conflicting pack → indicator turns 🔴 with the pair named. *(deferred — covered by automated indicator tests)*
- [x] (test:tests/) All tests pass (`uv run pytest` — 2380 passed).
- [x] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Inline validation findings + Hook Safety conflict indicator + default-load fix | Developer | — | Done |
| 2 | Per-state coverage + default-load regression | Tech-QA | 01 | Done |

> Skipped: BA (default — AC are specific, no ambiguity), Architect (default — UI surfacing only, no new subsystem/ADR).

## Changes

| File | Lines |
|------|-------|
| `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` | +27/-9 (verbatim-message rendering + 5-cap + overflow line) |
| `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` | +136/-2 (`_conflict_label`, `_update_conflict_indicator`, `_resolve_default_conflicts`, `_find_conflict_pairs`) |
| `tests/test_persona_page.py` | +71 (`TestCoherenceIndicatorVerbatimMessages`, `TestCoherenceIndicatorTruncationCap`) |
| `tests/test_hook_safety_page.py` | +147 (`TestConflictIndicator`, `TestDefaultLoadConflictFree`) |

## Notes

**Same UX class.** All three failures share one principle: the validator knows what's wrong; the UI fails to surface it. Pulling them into one bean keeps the indicator pattern consistent across both wizard pages.

**Hook Safety indicator should reuse the persona page's pattern.** Lift the rendering helper if it makes sense; don't reinvent.

**Default-load fix is the most user-impacting.** A user who accepts defaults today gets a hard generation failure. Land this regardless of the indicator improvements — the indicator is the long-term fix; the default-load fix is the immediate stop-the-bleeding.

**Companion to BEAN-262 / BEAN-274.** Both established the underlying validators. This bean is purely the UI surfacing layer.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Inline validation findings + Hook Safety conflict indicator + default-load fix | Developer | < 1m | N/A (suspect) | N/A (suspect) | — |
| 2 | Per-state coverage + default-load regression | Tech-QA | < 1m | 4,304,220 | 11,309 | $7.80 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 4,304,220 |
| **Total Tokens Out** | 11,309 |
| **Total Cost** | $7.80 |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | Developer, Tech-QA |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | in-process |