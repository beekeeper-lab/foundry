# BEAN-069: Workflow Hook Packs (Git & Az)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-069 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The current hook system has code-quality hook packs (pre-commit-lint, post-task-qa, security-scan, compliance-gate) but lacks workflow-oriented hooks that automate the git branching/PR lifecycle and cloud CLI operations. The user's vision includes two new hook categories:

1. **Git Workflow Hooks** — automate common git operations: commit to feature branch, push feature branch, generate PR, merge PR to test, merge test to prod
2. **Az (Azure CLI) Hooks** — control Azure CLI access: read-only mode (only `az ... show/list/get` allowed) or limited-ops mode (allow deploy, block destructive operations like `az group delete`)

These should be selectable in the wizard's Hook & Safety page, grouped by category (Git, Az, Code Quality) rather than the current flat list.

## Goal

Create fully functional Git and Az workflow hook packs as Claude Code hook definitions, update the library and UI to present hooks grouped by category, and wire them into generated projects via the asset copier.

## Scope

### In Scope

#### Git Workflow Hooks
- **git-commit-branch**: Hook that ensures commits go to a feature branch (never directly to main/test/prod), auto-creates branch if needed
- **git-push-feature**: Hook that pushes the current feature branch to origin with `-u` flag, validates branch naming convention
- **git-generate-pr**: Hook that creates a PR from current feature branch to test using `gh pr create`, with template body
- **git-merge-to-test**: Hook that merges an approved PR to the test branch, runs pre-merge checks
- **git-merge-to-prod**: Hook that merges test to prod/main after approval, with safety gates (require CI green, require approval count)

#### Az Workflow Hooks
- **az-read-only**: Hook that intercepts `az` commands and only allows read operations (`show`, `list`, `get`, `account show`). Blocks `create`, `delete`, `update`, `start`, `stop`, `restart`.
- **az-limited-ops**: Hook that allows common deployment operations (`az webapp deploy`, `az functionapp deploy`, `az acr build`) but blocks destructive operations (`az group delete`, `az vm delete`, `az storage account delete`)

#### UI Changes
- Update `HookSafetyPage` to group hooks by category (Git Workflow, Azure CLI, Code Quality)
- Each category is a collapsible section with its hooks listed inside
- Add new `HookCategory` field to `HookPackSelection` model

#### Model Changes
- Add `category` field to `HookPackInfo` and `HookPackSelection` models
- Categories: `git`, `az`, `code-quality`

#### Library Content
- New hook pack files in `ai-team-library/claude/hooks/` for each Git and Az hook
- Each hook file defines: trigger, condition, action script, description
- Hook files follow Claude Code hook format (`.claude/hooks/` JSON or script format)

### Out of Scope
- Other cloud providers (AWS, GCP) — future beans
- CI/CD pipeline integration (Jenkins, GitHub Actions) — separate concern
- Custom user-defined hooks (future extensibility)

## Acceptance Criteria

- [ ] 5 Git workflow hook packs created in library with functional scripts
- [ ] 2 Az hook packs created in library with functional scripts
- [ ] `HookPackInfo` and `HookPackSelection` models have `category` field
- [ ] `HookSafetyPage` groups hooks by category with collapsible sections
- [ ] Git hooks enforce branch naming conventions and prevent direct main commits
- [ ] Az read-only hook correctly blocks write operations while allowing reads
- [ ] Az limited-ops hook allows deploy operations but blocks destructive ones
- [ ] All hook packs appear in wizard and are selectable per-hook
- [ ] Selected hooks are copied to generated project's `.claude/hooks/` directory
- [ ] Hook configuration written to generated project's `.claude/settings.json`
- [ ] Tests for new hook pack selection logic and category grouping
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-067 (Wire Pipeline) so that asset copier actually copies hooks to generated projects
- The Git workflow hooks should work with the `gh` CLI for PR operations — this is a runtime dependency for generated projects
- Az hooks should validate that `az` CLI is installed before attempting to intercept commands
- Hook format should match Claude Code's `.claude/hooks/` specification (JSON with event/pattern/command fields)
- The category grouping in the UI is a visual change to `HookSafetyPage` — the underlying `HooksConfig` model just needs a category field on each pack
- Consider making hook scripts portable (bash for Linux/macOS, with notes about Windows compatibility)
- The existing code-quality hooks (pre-commit-lint, post-task-qa, security-scan, compliance-gate) get category `code-quality`
