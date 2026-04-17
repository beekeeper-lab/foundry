# BEAN-250 — Architect Output: Posture Taxonomy Decision

| Field | Value |
|-------|-------|
| **Bean** | BEAN-250 |
| **Persona** | Architect |
| **Date** | 2026-04-17 |
| **Decision** | Keep posture names; document the taxonomy and lock it in with a test. |

## Summary

External review called the posture taxonomy "muddy." The code is not — `_POSTURE_BASE` in `safety_writer.py` already encodes a clean 1 → 3 → 5 ordering of base packs, and stack-aware layering adds at most one lint pack + one cloud pack per provider (only at `hardened`/`regulated`). The gap is documentation, not design.

**Chosen direction:** keep the names `baseline` / `hardened` / `regulated`, publish `ai/context/hook-posture.md`, and expose `posture_base_packs()` so the mapping is importable and testable. See `ai/context/decisions.md` ADR-006 for the full reasoning.

## Why not rename

- Every composition YAML, settings default, test fixture, and UI label references the current names. Renaming is a migration, not a taxonomy fix.
- The reviewer's premise (that `baseline` enables Azure, compliance, QA, lint, secret controls) does not match the base-pack set. It matches what someone sees if they scan the library directory or look at a YAML where an explicit `packs:` list overrides stack-aware defaults.
- Once the taxonomy is published and the pack list is assertable, the original concern disappears.

## Why not slim further

- `baseline` already has one base pack: `git-commit-branch`. Dropping it means every generated project starts without the one guardrail that blocks edits on `main` / `master` / `test` / `prod`.
- The stack-aware layer is a separate design (BEAN-255) and is not what the reviewer was reacting to.

## Hand-off to Developer

Deliverables:
- `ai/context/hook-posture.md` — one page, per-level intent + base pack list + default mode + stack-aware layering summary.
- `safety_writer.posture_base_packs(posture) -> list[str]` — public helper wrapping `_POSTURE_BASE`.
- `safety_writer.py` module docstring + `hook-selection.md` reference the new doc.

## Hand-off to Tech-QA

Lock-in test asserting:
- `posture_base_packs(Posture.BASELINE) == ["git-commit-branch"]`
- `posture_base_packs(Posture.HARDENED) == ["git-commit-branch", "git-push-feature", "security-scan"]`
- `posture_base_packs(Posture.REGULATED) == ["git-commit-branch", "git-push-feature", "security-scan", "compliance-gate", "post-task-qa"]`
