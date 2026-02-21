# BEAN-225: Generate Subtree Setup Instead of Asset Copy for .claude/

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-225 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

When Foundry generates a new project, the asset copier service copies files from `ai-team-library/claude/` into the sub-app's `.claude/` directory. This creates a snapshot that immediately drifts from the source. When skills, commands, or agents are improved, the sub-app doesn't get those updates. The user must manually copy files or re-generate.

With BEAN-223 establishing a shared `claude-kit` repository, Foundry should set up a git subtree in the generated project instead of copying files. This way generated projects are born connected to the shared config and can pull updates with a single command.

## Goal

Modify Foundry's generation pipeline so that instead of copying `.claude/` assets from the library, it initializes a git subtree in the generated project pointing to the `claude-kit` repository. The generated project starts with a working `claude-pull` / `claude-push` workflow from day one.

## Scope

### In Scope
- Modify the generator pipeline to skip the `.claude/` asset copy stage
- Add a new generation stage that initializes a git repo in the output directory (if not already a repo), adds the `claude-kit` remote, and runs `git subtree add`
- Add a configuration option for the `claude-kit` repo URL (in settings or composition YAML)
- Update the generation progress screen to show the subtree setup stage
- Handle the case where the output directory is not a git repo (initialize one)
- Handle the case where the user doesn't want a subtree (fallback to copy mode)
- Update tests for the new generation flow
- Update the CLI interface to support the subtree option

### Out of Scope
- Creating the `claude-kit` repo itself (BEAN-223)
- Migrating existing projects (covered by the migration spec)
- Adding subtree pull/push commands to the generated project's CLAUDE.md (nice-to-have, can be a follow-up)

## Acceptance Criteria

- [x] Generation pipeline sets up git subtree for `.claude/` when a `claude-kit` repo URL is configured
- [x] Generated project has `.claude/` populated via subtree with correct remote
- [x] `git subtree pull --prefix=.claude claude-kit main --squash` works in the generated project
- [x] Fallback to asset copy when no `claude-kit` URL is configured or user opts out
- [x] Settings screen includes a field for the `claude-kit` repo URL — via CLI `--claude-kit-url` and YAML `generation.claude_kit_url`; UI field deferred (PySide6)
- [x] Generation progress screen shows the subtree setup stage — automatic via stage callback mechanism
- [x] All tests pass (`uv run pytest`) — 671 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement subtree generation pipeline | Developer | — | Done |
| 2 | Verify subtree generation pipeline | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| `foundry_app/cli.py` | +10 |
| `foundry_app/core/models.py` | +5 |
| `foundry_app/services/asset_copier.py` | +16/-1 |
| `foundry_app/services/generator.py` | +7 |
| `foundry_app/services/subtree_setup.py` | +103 (new) |
| `tests/test_asset_copier.py` | +113 |
| `tests/test_subtree_setup.py` | +186 (new) |

## Notes

Depends on BEAN-223 (claude-kit subtree setup) being complete. The `claude-kit` repo must exist before Foundry can point generated projects at it.

Key files likely affected:
- `foundry_app/services/asset_copier.py` — skip `.claude/` copy when subtree mode is active
- `foundry_app/services/generator.py` — add subtree setup stage
- `foundry_app/core/models.py` — add `claude_kit_url` field to composition/settings
- `foundry_app/ui/screens/settings_screen.py` — add repo URL field
- `foundry_app/ui/screens/generation_progress.py` — add stage display
- `foundry_app/cli.py` — add `--claude-kit-url` option

The subtree setup requires git commands (`git init`, `git remote add`, `git subtree add`). This should use `subprocess` calls similar to how other git operations work in the codebase.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
