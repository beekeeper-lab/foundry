# BEAN-246: Wizard Card UX — Collapsed Categories and Click-to-Toggle

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-246 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 16:51 |
| **Completed** | 2026-04-17 16:57 |
| **Duration** | 1267h 50m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Two UX issues with the wizard's persona / expertise / architecture selection pages, observed on `test` branch today:

1. **Categories expanded by default.** BEAN-230/231/232 introduced `CollapsibleGroupBox` for persona, expertise, and architecture sections, but the default state is **expanded** (`self._expanded = True` in `persona_page.py:166`). Users with many personas (24 in the default library) are overwhelmed at first load — the entire library unfurls as soon as the page opens. The user wants all categories **collapsed by default** so they can open only the ones they care about.
2. **Card click area is just the checkbox.** To toggle a persona/expertise/architecture selection, the user must hit the small checkbox indicator. Clicking the card's name, description, or badge area does nothing. Other card-based UIs (including Foundry's own earlier behavior, per the user) treat the entire row as a click target. Users want clicking anywhere on a card to toggle its checkbox.

## Goal

- All category sections on the persona, expertise, and architecture wizard pages default to **collapsed** at first page load. The user can expand any section by clicking its header.
- Clicking anywhere on a card (persona card, expertise card, architecture card, hook pack card) toggles the card's checkbox. Interactive child widgets (checkboxes, combo boxes, buttons) still capture their own clicks and are not affected.

## Scope

### In Scope
- Change `CollapsibleGroupBox` default state (in each of `persona_page.py`, `expertise_page.py`, `architecture_page.py`) to collapsed at page load. Preserve the toggle behavior so users can expand.
- Make every card (`PersonaCard`, `ExpertiseCard`, `ArchitectureCard`, `HookPackCard` in `hook_safety_page.py`) respond to a mouse click anywhere on the card by toggling its checkbox:
  - Override `mousePressEvent` on each card to call `checkbox.toggle()` on left-click.
  - Mark text-only labels (name labels, description labels, badges) with `Qt.WA_TransparentForMouseEvents` so clicks pass through to the card.
  - Do NOT set that attribute on interactive children (checkbox, combo box, buttons) — they must continue to capture their own clicks.
- Update existing wizard-page tests to reflect the new collapsed-by-default behavior and click-to-toggle behavior.

### Out of Scope
- Replacing `CollapsibleGroupBox` with a different widget.
- Per-section persistent state across app restarts.
- Keyboard-based selection (orthogonal improvement).

## Acceptance Criteria

- [x] Persona page: all category sections are collapsed on first load. Clicking a section header expands it.
- [x] Expertise page: same — all sections collapsed on first page load.
- [x] Architecture page: same — all sections collapsed on first page load.
- [x] Clicking anywhere on a persona card toggles the checkbox state.
- [x] Clicking anywhere on an expertise card toggles the checkbox state.
- [x] Clicking anywhere on an architecture card toggles the checkbox state.
- [x] Clicking anywhere on a hook pack card toggles the checkbox state.
- [x] Clicking the combo box on a card does NOT toggle the checkbox (QComboBox absorbs its own events; card's mousePressEvent never sees the click).
- [x] `test_all_groups_expanded_by_default` renamed → `test_all_groups_collapsed_by_default` and asserts the new state.
- [x] New `test_click_on_card_toggles_checkbox` added to each of the four wizard-page test files.
- [x] All tests pass (`uv run pytest` → 1808 passed).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Collapsed default + click-to-toggle | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

> Skipped: BA (default — criteria clear), Architect (default — per-file tweaks, no new widget).

## Changes

| File | Lines |
|------|-------|
| `ai/beans/BEAN-246-wizard-card-ux-collapsed-and-click-toggle/bean.md` | ±49 |
| `ai/beans/BEAN-246-wizard-card-ux-collapsed-and-click-toggle/tasks/01-developer-collapsed-and-click.md` | +47 |
| `ai/beans/BEAN-246-wizard-card-ux-collapsed-and-click-toggle/tasks/02-tech-qa-verification.md` | +65 |
| `foundry_app/ui/screens/builder/wizard_pages/architecture_page.py` | +13 / -1 |
| `foundry_app/ui/screens/builder/wizard_pages/expertise_page.py` | +14 / -2 |
| `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` | +12 |
| `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` | +25 / -3 |
| `tests/test_architecture_page.py` | +17 |
| `tests/test_expertise_page.py` | +17 |
| `tests/test_hook_safety_page.py` | +17 |
| `tests/test_persona_page.py` | +23 / -3 |

Totals: 11 files changed, +275 / -33.

## Notes

**Origin.** User feedback today (2026-04-17): "Business Operations has six things in it. I would like to have them all collapsed by default, be able to expand them to select the items inside. Make this the same for expertise, architecture, all the other tabs." And: "I want to be able to select the area and have it select the checkbox for me" (rather than hitting the tiny checkbox only).

**Builds on existing work.** BEAN-230, 231, 232 (all Done on `test`) introduced `CollapsibleGroupBox`. This bean tweaks defaults and adds click-to-toggle — it does NOT introduce a new widget or restructure the page.

**Files to touch:**
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`
- `foundry_app/ui/screens/builder/wizard_pages/expertise_page.py`
- `foundry_app/ui/screens/builder/wizard_pages/architecture_page.py`
- `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py`
- `tests/test_persona_page.py`, `tests/test_expertise_page.py`, `tests/test_architecture_page.py`, `tests/test_hook_safety_page.py`

Fits blast-radius budget (≤10 files, 1 boundary, small diff per file).

**Downstream verification:**

| System | Impact | Verification Command |
|--------|--------|---------------------|
| Tests  | Wizard page tests | `uv run pytest tests/test_persona_page.py tests/test_expertise_page.py tests/test_architecture_page.py tests/test_hook_safety_page.py` |
| Lint   | `foundry_app/` changes | `uv run ruff check foundry_app/` |
| Manual | Run the GUI | `uv run foundry` → open the builder wizard → verify each page starts with collapsed sections and that card rows respond to clicks |

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Collapsed default + click-to-toggle | Developer | — | — | — | — |
| 2 | Tech-QA Verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1267h 50m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |