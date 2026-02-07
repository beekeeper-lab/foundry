# BEAN-020: Wizard — Persona Selection Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-020 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The user needs to select which AI team members (personas) will be part of their generated project. The library has 13 personas, each with different roles and specialties. The selection screen must make it easy to browse, understand, and pick the right team.

## Goal

Build the persona selection wizard page where users can browse all available personas from the library and select one or more for their project. Each persona should show enough context for an informed decision.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`
- List all personas from LibraryIndex (via BEAN-018)
- Multi-select with checkboxes
- Per-persona info: name, role description, what they produce
- Per-persona config options: include agent file, include templates, strictness level (light/standard/strict)
- Visual grouping or categorization to help users find the right personas
- Data binding to CompositionSpec.team (TeamConfig model)

### Out of Scope
- Editing persona content (library browser feature, deferred)
- Creating new personas
- Persona previews (full markdown rendering)

## Acceptance Criteria

- [x] All 13 library personas appear in the selection list
- [x] User can select/deselect personas with checkboxes
- [x] Each persona shows name and role description
- [x] Per-persona config (agent, templates, strictness) is accessible
- [x] At least one persona must be selected to proceed
- [x] Selections populate TeamConfig model correctly
- [x] All tests pass (`uv run pytest`) — 240 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement persona selection page | developer | — | Done |
| 2 | Write UI and integration tests (45 tests) | tech-qa | 1 | Done |

## Notes

Depends on BEAN-016 (TeamConfig model), BEAN-017 (app shell), BEAN-018 (library indexer). This is wizard page 2 of 6.
