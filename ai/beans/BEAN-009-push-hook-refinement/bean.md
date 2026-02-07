# BEAN-009: Push Hook Refinement

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-009 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

The current safety hooks and settings protect against git pushes broadly. With the introduction of feature branches and a test branch workflow, we need more nuanced push permissions: pushing to feature branches and a test/dev branch should be allowed, but pushing directly to main/master should be blocked.

## Goal

Refine the hook-policy and safety settings to support branch-level push permissions. Allow pushes to feature branches (`bean/*`) and integration branches (`test`, `dev`), but block direct pushes to protected branches (`main`, `master`).

## Scope

### In Scope
- Update hook-policy to support branch-level push rules
- Define protected branches: `main`, `master` (blocked for push)
- Define allowed branch patterns: `bean/*`, `test`, `dev`, feature branches
- Update `settings.local.json` generation in safety service if needed
- Update `.claude/agents/` files to reflect push permissions
- Document the branch protection policy

### Out of Scope
- GitHub branch protection rules (external to Claude Code)
- Force-push rules (already handled by existing `GitPolicy.allow_force_push`)
- CI/CD pipeline triggers on branch push
- Pull request requirements

## Acceptance Criteria

- [ ] Hook policy distinguishes between protected and allowed branches
- [ ] Pushes to `bean/*` branches are allowed
- [ ] Pushes to `test` and `dev` branches are allowed
- [ ] Pushes to `main` and `master` are blocked (with warning message)
- [ ] Safety settings updated to reflect branch-level rules
- [ ] Agent files updated with push permission awareness
- [ ] Policy documented in project context or agent instructions

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Update Push Hooks, Settings, and Agent Files | developer | — | Done |
| 02 | Push Hook Refinement Verification | tech-qa | 01 | Done |

> BA and Architect skipped — requirements are clear and this is a configuration/documentation change, not an architectural decision.

## Notes

This bean is independent of the Long Run command but is a prerequisite for the Merge Captain auto-merge workflow (BEAN-011). Without refined push hooks, the Merge Captain cannot push to the test branch.

The key principle: protect the production branch (main/master) while enabling workflow branches. This mirrors standard Git Flow / GitHub Flow patterns.
