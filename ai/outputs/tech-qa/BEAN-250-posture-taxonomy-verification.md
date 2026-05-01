# BEAN-250 — Tech-QA Output: Posture Taxonomy Verification

| Field | Value |
|-------|-------|
| **Bean** | BEAN-250 |
| **Persona** | Tech-QA |
| **Date** | 2026-04-17 |

## Tests added

`tests/test_safety_writer.py::TestPostureTaxonomy` — 7 lock-in tests:

1. `test_baseline_base_packs` — exact list match against `ai/context/hook-posture.md`.
2. `test_hardened_base_packs` — exact list match.
3. `test_regulated_base_packs` — exact list match.
4. `test_baseline_count_is_less_than_hardened` — ordering invariant (1 < 3 < 5).
5. `test_hardened_is_superset_of_baseline` — baseline pack is included at hardened.
6. `test_regulated_is_superset_of_hardened` — hardened packs are included at regulated.
7. `test_returned_list_is_fresh_copy` — `posture_base_packs()` returns a copy; mutating it doesn't corrupt state.

The class docstring points maintainers at ADR-006 and `hook-posture.md` to keep doc + test in sync.

## Gates

```
uv run pytest     → 1893 passed, 4 warnings (Qt deprecation, unrelated)
uv run ruff check foundry_app/ → All checks passed!
```

## Acceptance criteria verification

- [x] `ai/context/hook-posture.md` exists — one-page taxonomy doc with per-level intent, pack list, default mode.
- [x] No mixed terminology — enum values unchanged (`baseline` / `hardened` / `regulated`); all existing YAMLs, tests, UI labels continue to work.
- [x] The generated project's narrative accurately reflects enabled packs — `hook-posture.md` and `hook-selection.md` (stack-aware layer) cross-reference each other.
- [x] At least one test asserts `Posture.BASELINE` matches the documented pack list — actually covered all three levels plus ordering + superset invariants.
- [x] `uv run pytest` passes — 1893 tests.
- [x] `uv run ruff check foundry_app/` clean.
