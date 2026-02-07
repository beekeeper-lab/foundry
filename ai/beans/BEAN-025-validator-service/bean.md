# BEAN-025: Validator Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-025 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Before generating a project, the composition spec must be validated: do the referenced personas exist in the library? Are the stack IDs valid? Are there conflicting safety settings? Without pre-generation validation, the pipeline fails mid-execution with cryptic errors.

## Goal

Rebuild the validator service that checks a CompositionSpec against the library and reports errors, warnings, and info messages at configurable strictness levels.

## Scope

### In Scope
- `foundry_app/services/validator.py`
- `run_pre_generation_validation(composition, library_index, strictness)` function
- Validation checks: persona references, stack references, template paths, hook pack references, required fields
- Strictness levels: light (fatal only), standard (errors block), strict (warnings promoted to errors)
- ValidationResult model with errors, warnings, info lists
- Unit tests

### Out of Scope
- UI for displaying results (that's BEAN-024 Review Page)
- Runtime validation during generation
- Schema validation (Pydantic handles that)

## Acceptance Criteria

- [x] Validator catches missing persona references
- [x] Validator catches invalid stack IDs
- [x] Validator catches missing required fields
- [x] Strictness levels work: light allows warnings, strict promotes them to errors
- [x] ValidationResult contains categorized messages (error/warning/info)
- [x] Unit tests cover all validation checks
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement validator service | developer | — | Done |
| 2 | Write unit tests | tech-qa | 1 | Done |

## Notes

Depends on BEAN-016 (models) and BEAN-018 (library indexer). Used by BEAN-024 (Review Page) and BEAN-032 (Generator Orchestrator).
