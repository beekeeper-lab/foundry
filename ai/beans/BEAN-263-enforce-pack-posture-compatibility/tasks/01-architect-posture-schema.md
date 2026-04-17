# Task 01 — Architect: Posture Compatibility Schema and Integration Plan

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 19:29 |
| **Completed** | 2026-04-17 19:29 |
| **Duration** | < 1m |

## Goal

Pin down the canonical machine-readable representation of each hook pack's
posture compatibility and how the generator consults it.

## Inputs

- `ai/beans/BEAN-263-enforce-pack-posture-compatibility/bean.md`
- `ai-team-library/claude/hooks/*.md` (existing `## Posture Compatibility` tables)
- `foundry_app/services/safety_writer.py`
- `foundry_app/services/library_indexer.py`
- `foundry_app/services/validator.py`
- `foundry_app/core/models.py` (`HookPackInfo`)

## Decisions

1. **Source of truth** — the existing `## Posture Compatibility` table in every
   hook pack markdown. The three-column format
   (`Posture | Included | Default Mode`) is deterministic enough to parse. No
   modification of `ai-team-library/` is required.
2. **Parsed shape** —
   ```python
   posture_compatibility: dict[str, dict[str, str]]
   # e.g. {"baseline": {"included": "No", "default_mode": "—"}, ...}
   ```
   Stored on `HookPackInfo`.
3. **Compatibility rule** — a row with `included == "No"` marks the pack
   incompatible with that posture. Any other value (`Yes`, `Optional`,
   `Yes (…conditional…)`) counts as compatible.
4. **Enforcement point** — pre-generation `validator.py` raises
   `Severity.ERROR` (`code=hook-pack-posture-incompatible`) when an active
   pack declares `included=No` for the selected posture. `safety_writer.py`
   filters incompatible packs at emit time as a defensive fallback and adds
   an identical warning to `StageResult.warnings` so programmatic callers of
   `write_safety` that skip validation still get a signal.
5. **Policy** — validation error (not silent downgrade). An incompatible pack
   either declares itself enforcing-only (`compliance-gate`) or implies
   behaviour the posture shouldn't carry; emitting it at a lower level is
   misleading.

## Deliverable

This task produces no code — only the contract recorded here and in the
bean's Decisions section. Developer task 02 implements it.

## Acceptance Criteria

- [x] Schema and parser location documented.
- [x] Policy decision recorded (validation error + defensive filter).
- [x] Compatibility rule spelled out (literal `No` = incompatible).
