# BEAN-019: Wizard — Project Identity Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-019 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs an inviting first screen that captures the project's identity — name and tagline. This is the user's first impression of Foundry and sets the tone for the entire experience.

## Goal

Build the first wizard page: a clean, polished screen where the user enters their application name and an optional tagline/subtitle. Auto-generate a slug from the name.

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/project_page.py`
- Project name input field (required)
- Tagline/subtitle input field (optional)
- Auto-generated slug (read-only, derived from name)
- Clean, inviting visual design — this is the first screen the user sees
- Input validation (name required, reasonable length limits)
- Data binding to CompositionSpec.project (ProjectIdentity model)

### Out of Scope
- Output directory selection (can be in settings or review page)
- Library path selection (settings)

## Acceptance Criteria

- [x] Page displays project name input, tagline input, and auto-generated slug
- [x] Slug updates live as user types the project name
- [x] Name field is required — cannot proceed without it
- [x] Page looks professional and welcoming
- [x] Data populates ProjectIdentity model correctly
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement project identity page | developer | — | Done |
| 2 | Write UI and integration tests | tech-qa | 1 | Done |

## Notes

Depends on BEAN-016 (ProjectIdentity model) and BEAN-017 (app shell/wizard framework). This is wizard page 1 of 6.

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

> Duration backfilled from git timestamps (commit→merge, 13s).
