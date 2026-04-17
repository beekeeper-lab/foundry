# Task 02 — Developer: Parser, Validator Check, Safety-Writer Filter

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Wire up the schema defined in task 01: parse each pack's posture
compatibility, expose it on `HookPackInfo`, raise a pre-generation
validation error for incompatibilities, and filter incompatible packs at
safety-writer emit time.

## Inputs

- Task 01 decisions
- `foundry_app/core/models.py` — `HookPackInfo`
- `foundry_app/services/library_indexer.py`
- `foundry_app/services/validator.py`
- `foundry_app/services/safety_writer.py`
- `foundry_app/services/generator.py` (plumbing if `write_safety` gains
  a `library` argument)

## Required Changes

1. **`HookPackInfo` (models.py)** — add
   `posture_compatibility: dict[str, dict[str, str]]` with
   `default_factory=dict`.
2. **Parser (library_indexer.py)** — `_parse_hook_posture_compatibility(path)`
   reads the `## Posture Compatibility` section and returns a dict like
   `{"baseline": {"included": "No", "default_mode": "—"}, ...}`. Keys lower-cased.
3. **Indexer wiring** — `_scan_hook_packs` populates the new field.
4. **Validator (validator.py)** — `_check_hook_posture_compatibility` reports
   an error for each active pack whose compatibility row declares
   `included == "No"` for the current `spec.hooks.posture`. Error code
   `hook-pack-posture-incompatible`; message includes pack id, posture, and
   advises either lowering enforcement, removing the pack, or raising the
   posture.
5. **Safety writer (safety_writer.py)** — accept an optional
   `library: LibraryIndex | None = None` parameter in `write_safety`. When
   provided, `_resolve_packs` filters incompatible packs and records a
   warning. When `None`, behaviour matches today's (backward compatible).
   Update `generator.py` to pass `library` into `write_safety`.
6. **Test fixture note** — where existing tests construct tiny ad-hoc
   libraries or skip the library argument, keep them working.

## Acceptance Criteria

- [ ] `HookPackInfo.posture_compatibility` populated for every real pack.
- [ ] `validator.py` emits `hook-pack-posture-incompatible` error for a
      baseline composition that enables `compliance-gate`.
- [ ] `write_safety` skips incompatible packs and emits a warning when
      given a library.
- [ ] `uv run ruff check foundry_app/` passes.
