# BEAN-222: Move to Trunk-Based Development

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-222 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-21 |
| **Started** | 2026-02-21 17:46 |
| **Completed** | 2026-02-21 18:03 |
| **Duration** | 18m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The current two-branch workflow (`test` → `main`) adds ceremony without value. There is no independent validation, staging environment, or QA gate on the `test` branch — beans merge to `test` then immediately deploy to `main`. This creates unnecessary merge points, complicates the long-run orchestrator, and adds friction to every bean lifecycle.

## Goal

Eliminate the `test` branch and adopt trunk-based development. Feature branches merge directly to `main`. The `/deploy` command becomes a tagging/release tool (or is removed). All skills, commands, agents, and workflow docs are updated to reflect the simplified flow.

## Scope

### In Scope
- Update `/long-run` skill and command (Phase 0 targets `main`, no deploy step)
- Update `/merge-bean` skill and command (default target becomes `main`)
- Update `/spawn-bean` command (worktrees branch from `main`, merge to `main`)
- Update `/deploy` skill and command (repurpose as tag/release, or remove)
- Update bean workflow docs (`ai/context/bean-workflow.md`)
- Update all agent files that reference the `test` branch (`.claude/agents/`)
- Update `CLAUDE.md` if it references the `test` branch workflow
- Update library templates in `ai-team-library/` (long-run, merge-bean, spawn-bean)
- Update MEMORY.md entries that reference `test` branch workflow
- Delete the `test` branch (local and remote) after migration
- Update any hooks that reference the `test` branch

### Out of Scope
- Adding CI/CD pipeline (future bean if needed)
- Changing the bean lifecycle model itself
- Adding branch protection rules

## Acceptance Criteria

- [x] Feature branches created from `main` and merge directly to `main`
- [x] `/long-run` works with `main` as the sole integration branch
- [x] `/merge-bean` defaults to `main`
- [x] `/deploy` is repurposed as tag/release tool
- [x] All agent files updated (no stale `test` branch references)
- [x] All skill/command files updated
- [x] Library templates updated for generated sub-apps
- [x] Bean workflow docs updated
- [ ] `test` branch deleted (local + remote) — deferred to post-deploy
- [x] All tests pass (`uv run pytest`) — 659 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Update all workflow files for trunk-based development | Developer | — | Done |
| 2 | Verify trunk-based development migration | Tech-QA | 1 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| .claude/agents/team-lead.md | 12 |
| .claude/commands/deploy.md | 68 |
| .claude/commands/internal/merge-bean.md | 24 |
| .claude/commands/internal/spawn-bean.md | 16 |
| .claude/commands/long-run.md | 24 |
| .claude/hooks/hook-policy.md | 3 |
| .claude/hooks/telemetry-stamp.py | 6 |
| .claude/skills/commands/SKILL.md | 2 |
| .claude/skills/deploy/SKILL.md | 110 |
| .claude/skills/internal/merge-bean/SKILL.md | 14 |
| .claude/skills/long-run/SKILL.md | 40 |
| .claude/skills/run/SKILL.md | 13 |
| ai-team-library/claude/commands/deploy.md | 72 |
| ai-team-library/claude/commands/long-run.md | 25 |
| ai-team-library/claude/commands/merge-bean.md | 24 |
| ai-team-library/claude/commands/pick-bean.md | 5 |
| ai-team-library/claude/commands/run.md | 7 |
| ai-team-library/claude/commands/spawn-bean.md | 12 |
| ai-team-library/claude/hooks/git-commit-branch.md | 4 |
| ai-team-library/claude/hooks/git-generate-pr.md | 4 |
| ai-team-library/claude/hooks/git-merge-to-prod.md | 6 |
| ai-team-library/claude/hooks/git-merge-to-test.md | 6 |
| ai-team-library/claude/hooks/telemetry-stamp.py | 6 |
| ai-team-library/claude/skills/deploy/SKILL.md | 125 |
| ai-team-library/claude/skills/long-run/SKILL.md | 41 |
| ai-team-library/claude/skills/merge-bean/SKILL.md | 14 |
| ai-team-library/claude/skills/pick-bean/SKILL.md | 8 |
| ai-team-library/claude/skills/run/SKILL.md | 13 |
| ai-team-library/personas/tech-qa/templates/test-plan.md | 2 |
| ai-team-library/process/context/bean-workflow.md | 15 |
| ai/context/bean-workflow.md | 15 |
| docs/backlog-refinement-deep-dive.md | 6 |
| docs/long-run-deep-dive.md | 20 |

## Notes

This is a process simplification. The test branch has never served as a real integration gate — it's just a pass-through. Trunk-based development with short-lived feature branches is the natural fit for how we actually work.

BEAN-223 (claude subtree sharing) depends on this bean completing first, since the subtree migration will reference the new trunk-based workflow.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Update all workflow files for trunk-based development | Developer | 7m | 1,288,363 | 2,196 | $2.48 |
| 2 | Verify trunk-based development migration | Tech-QA | 5m | 6,559,096 | 1,008 | $15.05 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 12m |
| **Total Tokens In** | 7,847,459 |
| **Total Tokens Out** | 3,204 |
| **Total Cost** | $17.53 |