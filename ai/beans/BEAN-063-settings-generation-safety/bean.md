# BEAN-063: Settings Screen — Generation & Safety Defaults

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-063 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The Settings screen (BEAN-057) provides core path configuration but does not expose generation behavior or safety defaults. Users currently have no way to set default overlay mode, validation strictness, seed mode, or safety configuration without editing YAML files directly. These settings exist as concepts in the service layer (generator, validator, safety) but have no persistent UI defaults.

## Goal

Extend the Settings screen with a "Generation Defaults" section and a "Safety Defaults" section so users can configure their preferred generation behavior once and have it apply to all new compositions unless overridden in the wizard.

## Scope

### In Scope
- Add a "Generation Defaults" group to the Settings screen:
  - Overlay mode toggle (clean vs overlay) with explanation text
  - Validation strictness dropdown (strict, normal, permissive)
  - Default seed mode dropdown (kickoff, full, none)
- Add a "Safety Defaults" group:
  - Toggle for writing `settings.local.json` safety config
  - Default allowed/blocked MCP server patterns
  - Default allowed/blocked shell commands
- Persist all values via FoundrySettings (add new properties as needed)
- Pre-populate wizard fields with these defaults when starting a new composition
- Add tests

### Out of Scope
- Appearance/theme settings — separate bean
- Per-composition overrides in the wizard (already exist in wizard pages)
- Modifying the generator service itself

## Acceptance Criteria

- [ ] Settings screen has a "Generation Defaults" section with overlay mode, strictness, and seed mode
- [ ] Settings screen has a "Safety Defaults" section with toggle and pattern fields
- [ ] New FoundrySettings properties exist for each generation/safety default
- [ ] Values persist across app restarts
- [ ] Wizard pages read defaults from settings when initializing a new composition
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-057 (Settings Screen — Core Paths) being done first so the settings_screen.py file exists.
- The SafetyConfig model in `foundry_app/core/models.py` defines the structure. The safety.py service writes `settings.local.json`. This bean adds persistent defaults, not new safety behavior.
- Consider a "Restore Defaults" button per section.

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

> Duration backfilled from git timestamps (commit→merge, 5s).
