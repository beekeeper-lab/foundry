# BEAN-016: Core Data Models & IO Layer

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-016 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The Foundry application was deleted for a full rebuild. No Pydantic models or IO helpers exist. Every other bean — UI, services, CLI — depends on the data contracts that define how composition specs, safety configs, generation manifests, and library indexes are structured and serialized.

## Goal

Rebuild all Pydantic model classes and the YAML/JSON IO layer so that the rest of the application has a stable data foundation to build on.

## Scope

### In Scope
- ProjectIdentity, StackSelection, StackOverrides, PersonaSelection, TeamConfig models
- HookPackSelection, HooksConfig models
- SafetyConfig with 6 sub-policies (GitPolicy, ShellPolicy, FileSystemPolicy, NetworkPolicy, SecretPolicy, DestructiveOpsPolicy)
- GenerationOptions model
- CompositionSpec (top-level composition)
- StageResult, GenerationManifest models
- FileAction, OverlayPlan models (for overlay mode)
- LibraryIndex model (for library scanning results)
- composition_io.py: load_composition(), save_composition(), save_manifest()
- Unit tests for all models and IO functions

### Out of Scope
- UI code
- Service implementations
- CLI argument parsing

## Acceptance Criteria

- [x] All 15+ Pydantic model classes defined in `foundry_app/core/models.py`
- [x] Models use strict validation (Pydantic v2 style)
- [x] CompositionSpec can round-trip through YAML (load → save → load produces identical object)
- [x] SafetyConfig preset factories work: permissive_safety(), baseline_safety(), hardened_safety()
- [x] GenerationManifest can serialize to/from JSON
- [x] composition_io.py provides load_composition() and save_composition()
- [x] Unit tests cover model validation, serialization, and edge cases
- [x] All tests pass (`uv run pytest`) — 83 tests
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Define all Pydantic models | developer | — | Done |
| 2 | Implement IO layer (YAML/JSON) | developer | 1 | Done |
| 3 | Write unit tests | tech-qa | 1, 2 | Done |

## Notes

This is the foundation bean. BEAN-017 through BEAN-035 all depend on this directly or transitively.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 62s).
