# BEAN-023: Wizard — Hook & Safety Config Page

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-023 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The wizard needs a page where users configure hook packs and safety policies for their generated project. Without this, users would have no way to control which hooks are active, their enforcement mode, or the safety policies governing git, shell, filesystem, network, secret scanning, and destructive operations.

## Goal

Build the hook & safety config wizard page where users can:
1. Select a safety posture preset (baseline/hardened/regulated)
2. Browse and enable/disable hook packs from the library with per-pack mode control
3. Configure granular safety policies across six domains (git, shell, filesystem, network, secrets, destructive ops)

## Scope

### In Scope
- `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py`
- Posture selector (ComboBox: baseline/hardened/regulated)
- Hook pack cards from LibraryIndex with enable/disable + mode selector
- Safety policy section with toggles for each sub-policy domain
- Preset buttons (Permissive, Baseline, Hardened) for quick safety config
- Data binding to HooksConfig and SafetyConfig models
- Visual consistency with existing wizard pages (Catppuccin Mocha theme)

### Out of Scope
- Editing hook pack content (read-only display)
- Custom hook pack creation
- Per-field list editing for blocked_commands, protected_paths, etc. (advanced config)

## Acceptance Criteria

- [x] Posture selector shows all three posture options
- [x] All library hook packs appear as selectable cards
- [x] Each hook pack card has enable/disable checkbox and mode selector
- [x] Safety preset buttons (Permissive/Baseline/Hardened) configure toggles
- [x] Six safety policy sections display with toggle controls
- [x] get_hooks_config() returns correct HooksConfig
- [x] get_safety_config() returns correct SafetyConfig
- [x] set_hooks_config() / set_safety_config() restore state correctly
- [x] Page is always valid (hooks/safety have sensible defaults)
- [x] All tests pass (`uv run pytest`) — 476 tests pass
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Design and implement hook & safety config page | developer | — | Done |
| 2 | Write comprehensive tests (84 tests) | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (HooksConfig, SafetyConfig models), BEAN-017 (app shell), BEAN-018 (library indexer for hook packs). This is wizard page 5 of 6. The review page (BEAN-024) already expects hooks and safety data from the CompositionSpec.

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

> Duration backfilled from git timestamps (commit→merge, 26s).
