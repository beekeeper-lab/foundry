# BEAN-226: Claude Kit Lifecycle Scripts

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-226 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-02-22 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

When creating git worktrees or switching branches, `.claude/` content may be missing (submodule mode) or stale (subtree mode). There is no automation to detect and repair this. Additionally, pushing changes that touch `.claude/` requires a two-step process (push shared config first, then the consuming repo), and forgetting the first step silently desynchronizes the shared config. No scripts exist to enforce this workflow.

## Goal

Provide versioned, generic shell scripts that any claude-kit consuming repo can adopt to: (1) self-heal `.claude/` content after checkout/worktree creation, (2) sync `.claude/` with one command, and (3) safely push both `.claude/` and the main repo in the correct order. Scripts detect whether the repo uses a git submodule (at `.claude/kit/`) or a git subtree (at `.claude/`) and behave accordingly.

## Scope

### In Scope
- Versioned post-checkout git hook at `scripts/githooks/post-checkout`
- `scripts/claude-sync.sh` for hook installation and `.claude/` content sync
- `scripts/claude-publish.sh` for safe two-step push
- `docs/claude-kit.md` documenting the two-commit workflow
- Dual-pattern detection: submodule (`.claude/kit/.git` exists) vs subtree (`.claude/` exists, no `.claude/kit/.git`)
- Immediate activation: install post-checkout hook into `.git/hooks/` in this clone
- All scripts use relative paths and are generic enough for any claude-kit consuming project

### Out of Scope
- Migrating Foundry from subtree to submodule (or vice versa)
- Modifying any files inside `.claude/` itself
- CI/CD integration for the hooks
- Pre-commit or pre-push hooks (only post-checkout)
- Automatic conflict resolution during subtree pull

## Acceptance Criteria

- [ ] `scripts/githooks/post-checkout` exists and is executable
- [ ] Post-checkout hook fires only on branch checkouts (3rd arg flag=1), not file checkouts
- [ ] Hook detects submodule mode (`.claude/kit/.git` exists) vs subtree mode and runs appropriate repair
- [ ] In submodule mode, hook runs `git submodule update --init --recursive` if `.claude/kit` is missing or empty
- [ ] In subtree mode, hook warns if `.claude/` is missing or empty
- [ ] Hook runs `scripts/claude-sync.sh` if it exists and is executable
- [ ] `scripts/claude-sync.sh` exists and is executable
- [ ] claude-sync.sh copies all hooks from `scripts/githooks/` into `.git/hooks/` with `chmod +x`
- [ ] claude-sync.sh runs `git submodule sync --recursive && git submodule update --init --recursive` in submodule mode
- [ ] claude-sync.sh runs `git subtree pull --prefix=.claude claude-kit main --squash` in subtree mode
- [ ] `scripts/claude-publish.sh` exists and is executable
- [ ] claude-publish.sh pushes `.claude/kit` submodule (or subtree) before main repo push
- [ ] claude-publish.sh prints clear success/failure messages for each step
- [ ] claude-publish.sh aborts main repo push if `.claude/` push fails
- [ ] `docs/claude-kit.md` documents the two-commit workflow for both subtree and submodule patterns
- [ ] Post-checkout hook is installed into `.git/hooks/post-checkout` immediately in this clone
- [ ] All scripts pass `bash -n` syntax check
- [ ] All scripts use relative paths (no hardcoded absolute paths)

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

- Detection logic: if `.claude/kit/.git` exists → submodule mode; if `.claude/` exists without `.claude/kit/.git` → subtree mode; otherwise skip with warning.
- Subtree pull in claude-sync.sh may encounter merge conflicts — script should handle this gracefully with a clear error message rather than failing silently.
- Scripts are generic for claude-kit distribution but initially deployed/tested in the Foundry repo.
- Related: BEAN-223 (Share .claude/ Across Projects via Git Subtree) established the current subtree pattern.

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
