# BEAN-113: Input Bounds & Error Sanitization

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-113 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-10 |
| **Started** | 2026-02-10 |
| **Completed** | 2026-02-10 20:45 |
| **Duration** | 0m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Several secondary security concerns exist in the codebase:

1. **Unbounded string fields** — `ProjectIdentity.name`, `tagline`, `output_root`, and other string fields have no `max_length` constraint. An attacker could submit a composition with a multi-gigabyte name field, causing memory exhaustion.

2. **Unvalidated regex patterns** — `SafetyConfig.secret_patterns` accepts arbitrary regex strings without pre-validation. A catastrophic backtracking pattern (e.g., `(a+)+$`) could cause CPU exhaustion during safety validation.

3. **Unvalidated SVG color injection** — `_tint_svg()` in `icons.py` interpolates the `color` parameter directly into SVG attributes without validating it's a valid hex color. While low-impact in a desktop context (no XSS), it's a code hygiene gap.

4. **Raw exception exposure** — `generation_worker.py` emits `str(exc)` to the UI signal, potentially leaking filesystem paths or internal details in error dialogs.

## Goal

All user-facing string fields have sensible length limits. Regex patterns are pre-validated at parse time. SVG color injection is prevented. Error messages shown to the user are sanitized to avoid leaking internal paths.

## Scope

### In Scope
- Add `max_length` to `ProjectIdentity.name` (200), `tagline` (500), `output_root` (500), `output_folder` (200)
- Add `max_length` to `PersonaSelection.id` (100), `StackSelection.id` (100), `HookPackSelection.id` (100)
- Add `max_items` to list fields: `CompositionSpec.team.personas` (50), `stacks` (50), `hooks.packs` (50)
- Add `field_validator` to `SafetyConfig` that pre-compiles `secret_patterns` via `re.compile()` with a timeout or try/except to catch invalid regex
- Add hex color validation to `_tint_svg()` / `load_icon()` in `icons.py`
- Wrap exception in `generation_worker.py` to emit generic message, log full traceback
- Add tests for boundary cases (max length, invalid regex, invalid color)

### Out of Scope
- Path traversal hardening (covered by BEAN-112)
- Log file permissions (acceptable risk for desktop app)
- Concurrent generation locking (acceptable for single-user desktop app)

## Acceptance Criteria

- [x] `ProjectIdentity.name` with 201+ characters is rejected by Pydantic validation
- [x] `SafetyConfig` with an invalid regex in `secret_patterns` is rejected at parse time
- [x] `load_icon()` with a non-hex color string does not produce malformed SVG
- [x] Generation error dialog shows a generic message, not raw exception text
- [x] Full traceback is still available in the log file for debugging (logger.exception)
- [x] All existing tests pass (`uv run pytest`) — 430 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Add max_length to string fields | Developer | — | Done |
| 2 | Add regex pre-validation to SecretPolicy | Developer | — | Done |
| 3 | Add hex color validation to icons.py | Developer | — | Done |
| 4 | Sanitize error messages in generation_worker | Developer | — | Done |
| 5 | Add security tests (20 tests) | Tech-QA | 1-4 | Done |

## Notes

- Depends on: BEAN-112 (Path Traversal Hardening) should be done first since it modifies the same model validators
- Key files: `foundry_app/core/models.py`, `foundry_app/ui/icons.py`, `foundry_app/ui/generation_worker.py`
- The `max_length` values are suggestions — adjust based on real-world usage patterns

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 0m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
