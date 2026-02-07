# BEAN-004: Safety Source Directory Config

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-004 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |

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

- [x] Composition spec supports `editable_dirs` field on `FileSystemPolicy`
- [x] Generated `settings.local.json` uses configured directories in `Edit()` rules
- [x] Default behavior (`src/**`, `tests/**`, `ai/**`) unchanged when field is omitted
- [x] Wizard Safety page includes an input for source directories
- [x] Tests cover custom source dirs, default fallback, and multiple dirs (13 new tests)
- [x] All tests pass (`uv run pytest`) — 313 total
- [x] Lint clean (`uv run ruff check foundry_app/`) — 0 new issues

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Source Dirs Requirements | ba | — | Done |
| 02 | Source Dirs Design Spec | architect | 01 | Done |
| 03 | Source Dirs Implementation | developer | 02 | Done |
| 04 | Source Dirs Verification | tech-qa | 03 | Done |

## Notes

This is the pain point that triggered the manual `settings.local.json` fix during dogfooding setup.
