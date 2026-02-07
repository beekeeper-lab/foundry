# BEAN-004: Safety Source Directory Config

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-004 |
| **Status** | New |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

## Problem Statement

The safety service hardcodes `Edit(src/**)` in `settings.local.json`. Projects like Foundry use `foundry_app/` instead of `src/`, requiring a manual fix after generation. The source directory should be configurable in the composition spec or inferred from the project structure.

## Goal

Allow the composition spec to define which directories are editable, so that `settings.local.json` is generated with the correct `Edit()` permissions from the start.

## Scope

### In Scope
- New field in `SafetyConfig` or `CompositionSpec` for source directories
- Safety service reads the configured directories when generating `settings.local.json`
- Sensible default (`src/**`) when not configured
- Wizard UI field for source directories on the Safety page

### Out of Scope
- Auto-detection of source directories by scanning the filesystem
- Changes to deny rules (those remain static)

## Acceptance Criteria

- [ ] Composition spec supports a `source_dirs` field (or similar)
- [ ] Generated `settings.local.json` uses configured directories in `Edit()` rules
- [ ] Default behavior (`src/**`) is unchanged when field is omitted
- [ ] Wizard Safety page includes an input for source directories
- [ ] Tests cover custom source dirs, default fallback, and multiple dirs
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

This is the pain point that triggered the manual `settings.local.json` fix during dogfooding setup.
