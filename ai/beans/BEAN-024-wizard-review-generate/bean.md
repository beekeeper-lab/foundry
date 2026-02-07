# BEAN-024: Wizard — Review & Generate Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-024 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs a final review page where users can see a summary of all their selections (project identity, personas, stacks) before triggering generation. This page should validate the composition spec against the library and display any errors/warnings, giving users confidence before generating.

## Goal

Build the review & generate wizard page that displays a read-only summary of the composition spec, runs pre-generation validation, shows validation results (errors/warnings/info), and provides a "Generate" button that is only enabled when validation passes.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/review_page.py`
- Read-only summary sections: Project Identity, Personas, Stacks, Hooks/Safety
- Integration with `run_pre_generation_validation()` from validator service
- Validation result display with severity-colored messages
- Generate button that is disabled when errors exist
- Visual consistency with other wizard pages (Catppuccin Mocha theme)
- Data binding: accepts a CompositionSpec + LibraryIndex, displays summary
- `tests/test_review_page.py` with comprehensive test coverage

### Out of Scope
- Actually running the generation pipeline (that's BEAN-032)
- Editing values on this page (user navigates back to change)
- Export/save composition spec to YAML
- Progress indicators during generation

## Acceptance Criteria

- [x] Summary displays project name, slug, and output path
- [x] Summary lists selected personas with their config
- [x] Summary lists selected stacks in order
- [x] Validation runs automatically when page is loaded/refreshed
- [x] Validation errors shown in red, warnings in yellow, info in blue
- [x] Generate button disabled when validation errors exist
- [x] Generate button enabled when no validation errors
- [x] `generate_requested` signal emitted when Generate is clicked
- [x] All tests pass (`uv run pytest`) — 362 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement review page | developer | — | Done |
| 2 | Write comprehensive tests (66 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (CompositionSpec model), BEAN-025 (validator service), BEAN-019/020/021 (prior wizard pages). This is wizard page 5 of 6 (pages 4 is architecture/cloud — BEAN-022).
