# Task 01 — Developer: inline validation findings + conflict indicator + default-load fix

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 11:39 |
| **Completed** | 2026-05-01 11:39 |
| **Duration** | < 1m |

## Goal

Make the wizard surface the validator's actionable messages **at the page where the user can act on them**. Cover the three failures called out in BEAN-286: persona-page coherence indicator collapses to opaque counts; Hook Safety page has no real-time conflict indicator; hook-pack defaults ship a conflicting configuration.

## Inputs

- `ai/beans/BEAN-286-wizard-inline-validation-findings/bean.md` — bean spec
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` — `_update_coherence_indicator()` lines 608-676
- `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` — `HookPackCard._build_ui()` line 232 (default `setChecked(True)`); `HookSafetyPage.load_hook_packs()` lines 591-635
- `foundry_app/services/validator.py` — `validate_contract_graph()` (per-message text source) and `_check_hook_conflicts()` lines 94-134 (pair-detection logic to mirror)
- `foundry_app/core/models.py` — `HookPackInfo.conflicts_with` field (line ~669)

## Acceptance Criteria

### Persona page
- [ ] `_update_coherence_indicator()` renders the validator's per-message text, not just counts. Each message from `validate_contract_graph().messages` is rendered verbatim in a bullet list, in the order the validator returns (errors first, warnings after).
- [ ] Header line preserved: `🔴 Team coherence: N missing producer(s) …` / `🟡 Team coherence: N orphan produce(s) …` / `🟢 Team coherence: all consumes satisfied.` (ensures existing pluralization tests still pass).
- [ ] Visible findings capped at 5; longer lists collapse to a final `… +N more` line.
- [ ] Word-wrap on the label so long messages don't expand the page horizontally.

### Hook Safety page
- [ ] New `_conflict_label: QLabel` rendered above the hook card container (same visual treatment as persona-page coherence label).
- [ ] `_update_conflict_indicator()` walks each enabled pack's `conflicts_with` (or the partner's `conflicts_with`) and names conflicting pairs verbatim. 🔴 when ≥1 pair; 🟢 when none. Hidden when no library is loaded.
- [ ] Indicator updates synchronously when any pack checkbox toggles (wired via `_on_card_toggled`).
- [ ] Pair detection mirrors `validator._check_hook_conflicts` semantics: symmetric, deduped, only enabled packs.

### Default-load conflict-free fix
- [ ] After `load_hook_packs()` populates cards, the first pack of any conflicting pair stays checked; the conflicting partner(s) are unchecked. Implementation: walk cards in render order; if an earlier still-enabled card declares a conflict with the current pack (or vice versa), uncheck the current.
- [ ] After load, `validate_pack_compatibility` (i.e. `_check_hook_conflicts` semantics) reports no errors against the freshly-loaded selection.

## Definition of Done

- [ ] Code changes land in the two files above.
- [ ] No regression in existing tests (`uv run pytest tests/test_persona_page.py tests/test_hook_safety_page.py -q`).
- [ ] `uv run ruff check foundry_app/` passes.
- [ ] Status set to `Done`.

## Notes

- Reuse the persona-page coherence label's stylesheet/layout pattern for the new Hook Safety conflict label — don't reinvent.
- Keep helper logic (pair-finding, message-rendering) inside the page modules; do not add a new shared module.
