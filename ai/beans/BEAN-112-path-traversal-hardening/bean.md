# BEAN-112: Path Traversal Hardening

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-112 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 20:41 |
| **Duration** | 0m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

A malicious YAML composition file can escape the intended output directory via path traversal. The `output_root` and `output_folder` fields in `ProjectIdentity` accept arbitrary paths (including `../../../` sequences and absolute paths) without validation. Similarly, `PersonaSelection.id`, `StackSelection.id`, and `HookPackSelection.id` only enforce `min_length=1` with no pattern constraint, allowing traversal sequences like `../../admin` to be injected into path construction in `asset_copier.py`, `compiler.py`, and `agent_writer.py`. The `slug` field has a regex pattern (`^[a-z0-9][a-z0-9-]*$`), but the other path-sensitive fields do not.

While `FileAction.path` has proper traversal validation (rejects `..` and absolute paths) and the library manager has boundary checks (`is_relative_to`), the primary generation pipeline from composition YAML to output directory has no such protection.

## Goal

All path-sensitive fields in the composition spec are validated to prevent directory traversal. The generator resolves the final output directory and verifies it is contained within a safe boundary (workspace_root or a sensible default) before writing any files. Both relative and absolute `output_root` values are allowed, but the resolved path must pass a containment check.

## Scope

### In Scope
- Add `pattern` validator to `PersonaSelection.id`, `StackSelection.id`, and `HookPackSelection.id` in `models.py` (same pattern as `slug`: `^[a-z0-9][a-z0-9-]*$`)
- Add `field_validator` to `ProjectIdentity.output_root` rejecting `..` in path parts
- Add `field_validator` to `ProjectIdentity.output_folder` rejecting `..` in path parts and enforcing safe characters
- Add containment check in `generator.py` `generate_project()`: resolve the final output directory and verify it is within `workspace_root` (from settings) or the composition's `output_root` parent
- Add integration tests with malicious composition YAMLs: traversal in output_root, output_folder, persona.id, stack.id
- Ensure existing tests still pass after tightening validation

### Out of Scope
- Sandboxing or OS-level isolation
- Library content validation (library is trusted by design)
- Network security (app is local-only)

## Acceptance Criteria

- [x] `PersonaSelection.id` rejects values containing `..` or `/` (e.g., `../../evil`)
- [x] `StackSelection.id` rejects values containing `..` or `/`
- [x] `HookPackSelection.id` rejects values containing `..` or `/`
- [x] `ProjectIdentity.output_root` rejects paths with `..` in parts
- [x] `ProjectIdentity.output_folder` rejects paths with `..` or `/` in them
- [x] `generate_project()` resolves and validates the final output directory against a containment boundary before writing
- [x] Integration test: composition with `output_root: "../../../tmp"` is rejected
- [x] Integration test: composition with `persona.id: "../../evil"` is rejected
- [x] All existing tests pass (`uv run pytest`) — 410 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add path validators to models.py | Developer | — | Done |
| 2 | Add containment check in generator.py | Developer | 1 | Done |
| 3 | Add security tests (24 tests) | Tech-QA | 2 | Done |

## Notes

- Existing secure patterns to follow: `FileAction.validate_path()` in models.py (lines 418-426) and library manager boundary check in library_manager.py (lines 1226-1230)
- The containment check should use `Path.resolve()` + `is_relative_to()` pattern
- Allow both relative and absolute output_root, but always resolve and verify containment
- Key files: `foundry_app/core/models.py`, `foundry_app/services/generator.py`, `foundry_app/services/asset_copier.py`

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 4s).
