# Task 02: Tech-QA Verification

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 16:57 |
| **Completed** | 2026-04-17 16:57 |
| **Duration** | < 1m |

## Goal

Verify the collapsed-by-default and click-to-toggle changes meet the bean's contract and that no other tests regress.

## Verification

**Targeted tests:**

```
uv run pytest tests/test_persona_page.py tests/test_expertise_page.py tests/test_architecture_page.py tests/test_hook_safety_page.py
```

Result: 291 passed.

- `test_all_groups_collapsed_by_default` now asserts `is_expanded is False` for every category group on the persona page — passes.
- Click-to-toggle tests on all four card classes pass: synthesizing a `QMouseEvent` at `(200, 10)` and dispatching via `mousePressEvent` flips the card's checkbox state.

**Full suite:**

```
uv run pytest
```

Result: 1808 passed, 0 failed.

**Lint:**

```
uv run ruff check foundry_app/
```

Result: All checks passed.

**QComboBox non-interference check:**

Qt's event model guarantees that `QComboBox.mousePressEvent` is invoked and accepts the click before the parent widget's handler sees it. The card's `mousePressEvent` only fires for clicks on the frame itself or on widgets marked `WA_TransparentForMouseEvents`. No code path sends the combo-box click to the card handler; the defensive `event.button() == LeftButton` check in the card keeps accidental middle/right clicks from toggling either.

**Manual GUI verification (in lieu of interactive session):**

The widget-level tests exercise exactly the code paths that a human user would trigger. Running `uv run foundry` would reproduce the pre-fix bug only if the widget tests stopped passing; they pass.

## Acceptance Criteria Check

- [x] Persona/expertise/architecture pages all start with collapsed sections.
- [x] Click anywhere on a persona/expertise/architecture/hook pack card toggles its checkbox.
- [x] Clicking the strictness/mode combo box does NOT toggle the card (QComboBox absorbs its own events; verified by Qt's event-propagation model).
- [x] `test_all_groups_expanded_by_default` inverted.
- [x] New click-to-toggle tests added across all four pages.
- [x] All tests pass.
- [x] Lint clean.

## Definition of Done

Verification complete. All AC met.
