# BEAN-012: Enforce Feature Branch Workflow

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-012 |
| **Status** | Done |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

BEAN-008 documented the feature branch workflow and BEAN-011 created the Merge Captain, but in practice we've been committing directly to `main`. The Team Lead needs to actually enforce the branch-first workflow: every bean gets its own branch, all work happens there, and the Merge Captain merges to `test` at the end.

The `test` integration branch may not exist yet — it needs to be checked and created if missing. All references to the integration branch should be standardized on `test`.

## Goal

Make the feature branch workflow the enforced default for all bean processing. The Team Lead creates a `bean/BEAN-NNN-<slug>` branch immediately when picking a bean, all team work happens on that branch, and the Merge Captain merges to `test` when the bean is done. No more committing to `main` during normal bean execution.

## Scope

### In Scope
- Update Team Lead agent to always create feature branch as first action when picking a bean
- Update `/pick-bean` skill to enforce branch creation (remove `--no-branch` as the default path)
- Update `/long-run` skill to enforce branch-per-bean in both sequential and parallel modes
- Check for `test` branch existence; create it if missing (from current `main` HEAD)
- Standardize all docs on `test` as the integration branch name
- Update bean-workflow.md to make branching mandatory (not optional)
- Update Merge Captain to always merge to `test` after bean completion

### Out of Scope
- Merging `test` → `main` (that's BEAN-013, the `/deploy` command)
- CI/CD integration
- Branch protection rules on the remote (GitHub settings)

## Acceptance Criteria

- [ ] Team Lead always creates `bean/BEAN-NNN-<slug>` branch when picking a bean
- [ ] `test` branch exists (created if missing)
- [ ] All bean work happens on the feature branch, never directly on `main`
- [ ] Merge Captain merges feature branch → `test` as the final bean step
- [ ] `/pick-bean` skill enforces branch creation by default
- [ ] `/long-run` skill enforces branch-per-bean workflow
- [ ] `bean-workflow.md` updated to make branching mandatory
- [ ] Team Lead and Developer agent docs updated with branch-first rules

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Enforce branching in all workflow docs and skills | developer | — | Done |
| 02 | Create test branch and verify enforcement | tech-qa | 01 | Done |

> BA and Architect skipped — this updates existing docs to enforce an already-designed workflow.

## Notes

Depends on: BEAN-008 (Feature Branch Workflow), BEAN-011 (Merge Captain Auto-Merge).

This bean transitions us from "branching is documented but optional" to "branching is the enforced default." Working on `main` was appropriate for the early project bootstrapping phase, but going forward all bean work should be isolated on feature branches.

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

> Duration backfilled from git timestamps (single commit, no merge).
