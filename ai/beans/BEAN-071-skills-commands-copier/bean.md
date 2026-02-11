# BEAN-071: Skills & Commands Copier Enhancement

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-071 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The asset copier service (`asset_copier.py`) copies commands and hooks from the library but does not copy skills to `.claude/skills/`. The library has a `claude/skills/` directory with skill definitions, but the copier's `_GLOBAL_ASSET_DIRS` list only includes `claude/commands` and `claude/hooks`.

Additionally, generated projects should get the same foundational commands and skills that make Foundry's own AI team workflow functional — things like `/pick-bean`, `/new-bean`, `/bean-status`, `/deploy`, `/compile-team`, etc. These are the workflow tools that make the generated team effective.

## Goal

Extend the asset copier to also copy skills from the library to `.claude/skills/` in generated projects. Ensure the full set of workflow commands and skills from the library are available in generated projects.

## Scope

### In Scope
- Add `("claude/skills", ".claude/skills")` to `_GLOBAL_ASSET_DIRS` in `asset_copier.py`
- Verify all library commands in `claude/commands/` are suitable for generated projects (some may be Foundry-specific and should be excluded)
- Add a filtering mechanism: allow the composition spec to include/exclude specific commands and skills
- Add `SkillSelection` or similar model to `CompositionSpec` if needed for selective copying
- Update wizard UI to show available commands/skills with checkboxes (or just copy all by default)
- Tests for skills copying and filtering

### Out of Scope
- Creating new skills or commands (library content stays as-is)
- Skill/command editor UI (that's BEAN-042)
- MCP config (that's BEAN-070)

## Acceptance Criteria

- [ ] `asset_copier.py` copies skills from `claude/skills/` to `.claude/skills/` in generated projects
- [ ] `_GLOBAL_ASSET_DIRS` updated to include skills directory
- [ ] Generated projects have populated `.claude/skills/` directory
- [ ] Generated projects have populated `.claude/commands/` directory (already works after BEAN-067)
- [ ] Foundry-specific commands/skills that don't apply to generated projects are excluded or flagged
- [ ] Tests verify skills are copied alongside commands and hooks
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-067 (Wire Pipeline) so that asset copier is actually called during generation
- The simplest fix is literally adding one line to `_GLOBAL_ASSET_DIRS` in `asset_copier.py`
- The harder part is deciding which commands/skills from the library are universal vs. Foundry-specific
  - Universal: `/compile-team`, `/seed-tasks`, `/bean-status`, `/pick-bean`, `/new-bean`, `/deploy`
  - Possibly Foundry-specific: `/spawn-bean`, `/long-run`, `/backlog-refinement` (these reference Foundry's own tmux setup)
- Consider a `library_metadata.json` or marker in each command/skill that flags it as "include in generated projects" vs. "Foundry internal only"
- For the initial implementation, copying all commands/skills is acceptable — filtering can be refined later

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

> Duration backfilled from git timestamps (commit→merge, 7s).
