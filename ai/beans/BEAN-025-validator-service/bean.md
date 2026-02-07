# BEAN-025: Validator Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-025 |
| **Status** | In Progress |
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

- [ ] Validator catches missing persona references
- [ ] Validator catches invalid stack IDs
- [ ] Validator catches missing required fields
- [ ] Strictness levels work: light allows warnings, strict promotes them to errors
- [ ] ValidationResult contains categorized messages (error/warning/info)
- [ ] Unit tests cover all validation checks
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement validator service | developer | — | Pending |
| 2 | Write unit tests | tech-qa | 1 | Pending |

## Notes

Depends on BEAN-016 (models) and BEAN-018 (library indexer). Used by BEAN-024 (Review Page) and BEAN-032 (Generator Orchestrator).
