# Task 03 — Tech-QA: Tests for Posture Compatibility Enforcement

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 02 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Prove the parser, validator check, and safety-writer filter behave as
specified. Ensure the full suite remains green and ruff is clean.

## Inputs

- Task 02 implementation
- `tests/test_library_indexer.py` (pattern for indexer tests)
- `tests/test_validator.py` (pattern for validator tests)
- `tests/test_safety_writer.py` (pattern for safety-writer tests)

## Required Tests

1. **Parser** — for a synthetic hook pack markdown, assert the parsed dict
   matches the expected `{posture: {included, default_mode}}` structure. Cover
   `Yes`, `No`, `Optional`, and a conditional `Yes (when …)` value.
2. **Live packs** — every pack discovered by `library_indexer` on the real
   `ai-team-library/` directory has non-empty `posture_compatibility` for
   all three postures (`baseline`, `hardened`, `regulated`). `hook-policy`
   is excluded (no table).
3. **Validator** — baseline composition with `compliance-gate` enabled
   raises the `hook-pack-posture-incompatible` error with a clear message.
   Same composition at `regulated` posture is clean.
4. **Safety writer** — `write_safety(spec, out, library=index)` with a
   baseline-plus-compliance-gate spec omits `compliance-gate` from emitted
   hooks and returns a warning mentioning the pack id and posture.
5. **Regression** — all existing tests still pass (`uv run pytest`).

## Acceptance Criteria

- [ ] Full test suite green (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).
- [ ] New tests cover the incompatibility path end-to-end.
