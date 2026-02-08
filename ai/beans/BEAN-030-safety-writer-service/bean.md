# BEAN-030: Safety Writer Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-030 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generator orchestrator calls `_stub_write_safety()` as a placeholder. Generated projects need a `.claude/settings.json` file with safety policies based on the composition spec's `hooks.posture` (BASELINE, HARDENED, REGULATED) and per-hook-pack configurations. Without this service, generated projects have no safety enforcement.

## Goal

Implement a `SafetyWriterService` that generates `.claude/settings.json` in generated projects by assembling safety policies from the composition spec's posture and hook pack selections.

## Scope

### In Scope
- Implement `foundry_app/services/safety_writer.py`
- Function: `write_safety(spec: CompositionSpec, output_dir: Path) -> StageResult`
- Load appropriate `SafetyConfig` based on `spec.hooks.posture`
- Use factory methods: `baseline_safety()`, `hardened_safety()`, `permissive_safety()`
- Merge with inline `spec.safety` overrides if provided
- Apply per-hook-pack tweaks from `spec.hooks.packs[]`
- Serialize to `.claude/settings.json`
- Replace `_stub_write_safety()` in generator with real call
- Comprehensive test suite

### Out of Scope
- Custom policy editor UI
- Runtime policy enforcement

## Acceptance Criteria

- [x] `foundry_app/services/safety_writer.py` exists with `write_safety()` function
- [x] Supports BASELINE, HARDENED, and REGULATED postures
- [x] Merges inline safety overrides correctly
- [x] Generates valid JSON settings file
- [x] Generator stub replaced with real service call
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement safety writer service | Developer | — | Done |
| 2 | Integrate with generator | Developer | 1 | Done |
| 3 | Write tests (22 tests) | Tech-QA | 1 | Done |

## Notes

- Models already exist: `SafetyConfig`, `Posture`, policy models in `core/models.py`
- Generator stub at `generator.py:55-58`
- Factory methods available on SafetyConfig model
- Depends on BEAN-016 (models) and BEAN-032 (generator orchestrator), both Done
