# Task 02 — Tech-QA: per-state coverage + default-load regression

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-05-01 11:41 |
| **Completed** | 2026-05-01 11:41 |
| **Duration** | < 1m |

## Goal

Lock the new behavior with tests. Cover each indicator state, the "+N more" truncation cap, and a default-load regression test that fails today and passes after BEAN-286 lands.

## Inputs

- `ai/beans/BEAN-286-wizard-inline-validation-findings/bean.md` — acceptance criteria
- `ai/beans/BEAN-286-wizard-inline-validation-findings/tasks/01-developer-validation-inline.md` — implementation contract
- `tests/test_persona_page.py` — existing coherence-indicator tests (BEAN-274, lines 756+)
- `tests/test_hook_safety_page.py` — existing hook-card / hook-page tests
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` — under test
- `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` — under test

## Acceptance Criteria

### Persona-page indicator (verbatim messages)
- [ ] (test:tests/test_persona_page.py) Test asserts that in 🔴 state the indicator label text contains a verbatim missing-producer message — at minimum the substring `"Missing producer for type"` plus the producer-list phrase `"Producers in library:"`.
- [ ] (test:tests/test_persona_page.py) Test asserts that in 🟡 state the indicator label contains the verbatim orphan phrase `"produces type"` and `"no persona on the team consumes it"`.
- [ ] (test:tests/test_persona_page.py) Truncation: with ≥6 missing producers, the indicator caps visible lines at 5 and renders `+N more` (where N = total − 5).

### Hook Safety page — conflict indicator
- [ ] (test:tests/test_hook_safety_page.py) Page exposes a `_conflict_label` (or equivalent attribute / public accessor); hidden when no library is loaded.
- [ ] (test:tests/test_hook_safety_page.py) With a fixture library containing one declared conflict pair (e.g. mock packs `pack-a` and `pack-b`, where `pack-a.conflicts_with = ["pack-b"]`), enabling both turns the indicator 🔴 and names both pack ids.
- [ ] (test:tests/test_hook_safety_page.py) Toggling one of the pair off transitions the indicator back to 🟢 (no conflicts).

### Default-load regression
- [ ] (test:tests/test_hook_safety_page.py) Default-load with the **real library** (`ai-team-library/`): after `load_hook_packs(real_index)`, the wizard's pack selection is conflict-free under the validator's `_check_hook_conflicts` semantics. (No fixture mocks — this is the regression that BEAN-286 fixes.)

### Suite-wide
- [ ] All tests pass: `uv run pytest`.
- [ ] Lint clean: `uv run ruff check foundry_app/`.

## Definition of Done

- [ ] New tests added under the existing class structure (Coherence-indicator tests near BEAN-274 block; Hook-safety tests in a new `TestConflictIndicator` class).
- [ ] No flakiness — tests are deterministic and offscreen-safe (no GUI display required).
- [ ] Status set to `Done`.

## Notes

- Use `LibraryIndex(...)` direct construction with `HookPackInfo` fixtures for the conflict-indicator tests — avoid disk reads where possible to keep tests fast.
- For the default-load regression, use `LibraryIndexer` against `ai-team-library/` (or the project's existing test helper that loads the real library).
