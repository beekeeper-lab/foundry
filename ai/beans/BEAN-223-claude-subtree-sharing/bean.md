# BEAN-223: Share .claude/ Across Projects via Git Subtree

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-223 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-21 19:56 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

The `.claude/` directory (skills, commands, agents, hooks, settings) is maintained in Foundry but needs to be shared with other projects across multiple machines (laptop and remote). Currently there is no mechanism to keep these files in sync — changes made while working in another project don't propagate back, and vice versa.

## Goal

Extract `.claude/` into a standalone git repository (`claude-kit`) and embed it back into Foundry (and other projects) as a git subtree. This provides a single source of truth that works across machines and projects via standard git operations.

## Scope

### In Scope
- Create a new `claude-kit` repo from the current `.claude/` contents
- Set up git subtree in Foundry pointing to `claude-kit`
- Add convenience aliases/commands for push/pull (`claude-push`, `claude-pull`)
- Document the subtree workflow for use in other projects
- Verify Claude Code reads skills/commands correctly from subtree directory
- Update CLAUDE.md with subtree workflow instructions

### Out of Scope
- Migrating other projects to use the subtree (they can adopt independently)
- Splitting project-specific overrides into `.claude.local/` (future enhancement)
- CI/CD for the `claude-kit` repo

## Acceptance Criteria

- [x] `claude-kit` repo exists with all current `.claude/` contents
- [x] Foundry's `.claude/` is a git subtree linked to `claude-kit`
- [x] `git subtree push --prefix=.claude claude-kit main` works to push changes back
- [x] `git subtree pull --prefix=.claude claude-kit main --squash` works to pull updates
- [x] Claude Code reads skills, commands, and agents correctly from the subtree
- [x] Convenience aliases documented
- [x] Another project can add the subtree with standard git commands
- [x] All tests pass (`uv run pytest`) — 659 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create claude-kit repo and set up git subtree | Developer | — | Done |
| 2 | Verify subtree setup and documentation | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default)

## Changes

| File | Lines |
|------|-------|
| CLAUDE.md | +15/-5 |
| ai/beans/BEAN-223-claude-subtree-sharing/bean.md | +22/-13 |
| ai/beans/BEAN-223-claude-subtree-sharing/tasks/01-developer-create-claude-kit-and-subtree.md | +61 |
| ai/beans/BEAN-223-claude-subtree-sharing/tasks/02-tech-qa-verify-subtree.md | +37 |
| ai/beans/_index.md | +1/-1 |

## Notes

Depends on BEAN-222 (trunk-based development) completing first. The subtree setup should reference the simplified trunk-based workflow rather than the old test/main two-branch model.

Git subtree was chosen over submodule because:
- Clones just work (files are real files in the tree, no `--recurse-submodules`)
- No detached HEAD issues
- Normal edit/commit workflow (no two-step commit for the parent repo)
- Works identically on laptop and remote

Push/pull aliases:
```bash
alias claude-push='git subtree push --prefix=.claude claude-kit main'
alias claude-pull='git subtree pull --prefix=.claude claude-kit main --squash'
```

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create claude-kit repo and set up git subtree | Developer | — | — | — | — |
| 2 | Verify subtree setup and documentation | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |