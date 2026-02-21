# Task 02: Verify Subtree Setup and Documentation

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01-developer-create-claude-kit-and-subtree |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Verify the claude-kit repo, subtree relationship, push/pull operations, and documentation are all correct and complete.

## Verification Checklist

- [ ] `claude-kit` repo exists on GitHub and contains all `.claude/` contents
- [ ] Repo contents match Foundry's `.claude/` exactly (no missing files, no extra files)
- [ ] `claude-kit` remote is configured in Foundry's git config
- [ ] `git subtree push --prefix=.claude claude-kit main` succeeds
- [ ] `git subtree pull --prefix=.claude claude-kit main --squash` succeeds (or reports up-to-date)
- [ ] Claude Code reads skills and commands correctly (verify by listing available commands)
- [ ] CLAUDE.md contains subtree workflow documentation
- [ ] Convenience aliases are documented
- [ ] Another project can adopt the subtree (documented steps)
- [ ] Tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Acceptance Criteria

- [ ] All verification items pass
- [ ] Subtree relationship is functional in both directions

## Definition of Done

Full verification complete. Subtree setup is functional, documented, and ready for use across projects.
