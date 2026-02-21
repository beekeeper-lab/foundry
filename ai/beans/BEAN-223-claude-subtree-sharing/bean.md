# BEAN-223: Share .claude/ Across Projects via Git Subtree

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-223 |
| **Status** | In Progress |
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

- [ ] `claude-kit` repo exists with all current `.claude/` contents
- [ ] Foundry's `.claude/` is a git subtree linked to `claude-kit`
- [ ] `git subtree push --prefix=.claude claude-kit main` works to push changes back
- [ ] `git subtree pull --prefix=.claude claude-kit main --squash` works to pull updates
- [ ] Claude Code reads skills, commands, and agents correctly from the subtree
- [ ] Convenience aliases documented
- [ ] Another project can add the subtree with standard git commands
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create claude-kit repo and set up git subtree | Developer | — | In Progress |
| 2 | Verify subtree setup and documentation | Tech-QA | 1 | Pending |

> Skipped: BA (default), Architect (default)

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

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