# BEAN-227: Migrate Claude Kit from Subtree to Submodule

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-227 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-22 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

The upstream claude-kit repo has restructured its layout, moving all files into a `.claude/shared/` subdirectory (to support the submodule pattern at `.claude/kit/`). This breaks the current git subtree integration at `.claude/` — pulling upstream now produces nested `.claude/.claude/shared/` paths. The subtree approach is no longer compatible with upstream without constant manual conflict resolution.

## Goal

Migrate Foundry from git subtree (`.claude/` prefix) to git submodule (`.claude/kit`) for claude-kit integration. After migration, Claude Code can resolve commands, skills, agents, and hooks from the submodule path, and the BEAN-226 lifecycle scripts work correctly with the submodule pattern.

## Scope

### In Scope
- Remove the git subtree at `.claude/` (remove remote, clean history reference)
- Add `.claude/kit` as a git submodule pointing to `beekeeper-lab/claude-kit`
- Investigate how Claude Code resolves `.claude/` paths with a submodule — determine if symlinks, copies, or settings changes are needed
- Update `.claude/settings.json` to work with the new layout
- Update `CLAUDE.md` to document the submodule pattern (replace subtree instructions)
- Update `docs/claude-kit.md` to reflect the migration
- Update BEAN-226 scripts (`scripts/claude-sync.sh`, `scripts/claude-publish.sh`, `scripts/githooks/post-checkout`) — these already support submodule mode
- Verify all slash commands, skills, agents, and hooks still work after migration

### Out of Scope
- Changing the claude-kit repo itself
- Supporting both subtree and submodule simultaneously in Foundry (we're migrating to submodule only)
- Modifying the Foundry Python application or tests

## Acceptance Criteria

- [ ] `.claude/kit` exists as a git submodule pointing to `beekeeper-lab/claude-kit`
- [ ] `.gitmodules` file correctly references `.claude/kit`
- [ ] No git subtree references remain (no `claude-kit` subtree split prefix)
- [ ] Claude Code can resolve commands from `.claude/` (slash commands work)
- [ ] Claude Code can resolve skills from `.claude/` (skills work)
- [ ] Claude Code can resolve agents from `.claude/` (agent files accessible)
- [ ] `settings.json` paths are valid and functional
- [ ] `CLAUDE.md` documents the submodule workflow (not subtree)
- [ ] `docs/claude-kit.md` updated for submodule pattern
- [ ] `scripts/claude-sync.sh` correctly detects and syncs the submodule
- [ ] `scripts/claude-publish.sh` correctly pushes the submodule
- [ ] `scripts/githooks/post-checkout` correctly initializes the submodule on checkout
- [ ] `git submodule update --init --recursive` restores `.claude/kit` from scratch

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

- The upstream claude-kit repo restructured to: `.claude/shared/{agents,commands,skills,hooks,settings.json}`
- As a submodule at `.claude/kit/`, files would be at `.claude/kit/.claude/shared/...`
- Claude Code expects files directly at `.claude/{commands,skills,agents,hooks,settings.json}`
- Key investigation: how does Claude Code discover files when using a submodule? Symlinks? Includes? Settings path config?
- The BEAN-226 scripts already have submodule detection logic — they should work once `.claude/kit/.git` exists
- Depends on: BEAN-226 (Claude Kit Lifecycle Scripts) — Done
- Related: BEAN-223 (Share .claude/ Across Projects via Git Subtree) — this bean reverses that decision

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
