# BEAN-250 — Developer Output: Posture Taxonomy Implementation

| Field | Value |
|-------|-------|
| **Bean** | BEAN-250 |
| **Persona** | Developer |
| **Date** | 2026-04-17 |

## Changes

1. **`ai/context/hook-posture.md`** (new) — one-page taxonomy doc: per-posture intent, base packs, default mode, stack-aware layering note, guidance on when to pick / not pick each level.
2. **`foundry_app/services/safety_writer.py`**
   - Added module docstring explaining the posture taxonomy and pointing at `hook-posture.md` + ADR-006.
   - Added public `posture_base_packs(posture: Posture) -> list[str]` that wraps `_POSTURE_BASE` and returns a fresh copy.
   - Replaced the inline `list(_POSTURE_BASE.get(...))` call in `_stack_aware_default_packs` with the new helper.
   - Added a maintainer note in the `_POSTURE_BASE` comment to keep the doc + lock-in test in sync.
3. **`ai/context/hook-selection.md`** — added a forward reference to `hook-posture.md` above the posture-base table.
4. **`ai/context/decisions.md`** — ADR-006 already committed in the Architect task.

## Design choice

Kept the enum values unchanged (`baseline` / `hardened` / `regulated`). Every composition YAML, settings default, and existing test continues to work. The reviewer's concern is addressed by making the mapping legible (doc + public helper) rather than by renaming.

## Hand-off to Tech-QA

Add `TestPostureTaxonomy` in `tests/test_safety_writer.py` asserting:
- `posture_base_packs(Posture.BASELINE) == ["git-commit-branch"]`
- `posture_base_packs(Posture.HARDENED) == ["git-commit-branch", "git-push-feature", "security-scan"]`
- `posture_base_packs(Posture.REGULATED) == ["git-commit-branch", "git-push-feature", "security-scan", "compliance-gate", "post-task-qa"]`
- Returned list is a fresh copy (mutating it does not affect subsequent calls).

Run gates: `uv run pytest` and `uv run ruff check foundry_app/`.
