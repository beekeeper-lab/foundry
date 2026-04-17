# Task 01: Collapsed-by-default Sections + Click-to-Toggle Cards

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 16:56 |
| **Completed** | 2026-04-17 16:56 |
| **Duration** | < 1m |

## Goal

Switch each category group on the persona / expertise / architecture wizard pages to collapsed-by-default, and let users toggle a card's selection by clicking anywhere on the card (not only the checkbox).

## Implementation

**Collapsed-by-default:** in each of `persona_page.py`, `expertise_page.py`, `architecture_page.py`, the section widget's `__init__` now sets `_expanded = False`, renders the chevron as `▶`, and calls `self._content.setVisible(False)`. The toggle method remains unchanged, so users can still expand by clicking the header.

**Click-to-toggle cards:** each of `PersonaCard`, `ExpertiseCard`, `ArchitectureCard`, and `HookPackCard` now:
- Overrides `mousePressEvent` — on a left-click, the card's `_checkbox.toggle()` fires and the event is accepted. Other buttons fall through to the base implementation.
- Marks every text-only label (name, description, badge, config label) with `Qt.WidgetAttribute.WA_TransparentForMouseEvents` so clicks on them reach the card's handler. Interactive children (`QCheckBox`, `QComboBox`) continue to absorb their own events, so clicking the strictness selector / mode selector does **not** toggle the card.

## Tests

- Renamed `test_all_groups_expanded_by_default` → `test_all_groups_collapsed_by_default` and asserted `group.is_expanded is False` for every category on the persona page. The previous assertion only checked header visibility and masked the actual state.
- Added `test_click_on_card_toggles_checkbox` to each of `test_persona_page.py`, `test_expertise_page.py`, `test_architecture_page.py`, and `test_hook_safety_page.py`. The tests synthesize a `QMouseEvent` at coordinate `(200, 10)` (outside the checkbox area), dispatch it via `card.mousePressEvent(event)`, and assert the checkbox state flipped.

## Acceptance Criteria

- [x] Persona page — all category sections collapsed on first load.
- [x] Expertise page — same.
- [x] Architecture page — same.
- [x] Click on persona card toggles checkbox.
- [x] Click on expertise card toggles checkbox.
- [x] Click on architecture card toggles checkbox.
- [x] Click on hook pack card toggles checkbox.
- [x] Combo boxes continue to absorb their own events (QComboBox is an interactive widget; its `mousePressEvent` accepts the event before it reaches the card). Verified by inspection of Qt's event model; no new test is needed because no code path routes the combo-box click to the card handler.
- [x] `test_all_groups_expanded_by_default` renamed + inverted.
- [x] New click-to-toggle tests added.
- [x] `uv run pytest` → 1808 passed.
- [x] `uv run ruff check foundry_app/` → clean.

## Definition of Done

- All four wizard pages and four card classes updated.
- Tests and lint pass.
