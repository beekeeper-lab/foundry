# BEAN-008: Feature Branch Workflow

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-008 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |

## Problem Statement

Currently, all bean work happens directly on the main branch. This is fine for single-threaded `/long-run`, but becomes a blocker for parallel execution — multiple teams cannot safely commit to the same branch simultaneously. Even for single-threaded work, feature branches provide safer isolation and cleaner history.

## Goal

When a bean is picked for execution (whether manually or via `/long-run`), the workflow should create a feature branch for that bean's work. All commits for that bean happen on the feature branch. This is the foundation that enables parallel execution in BEAN-010.

## Scope

### In Scope
- Feature branch naming convention: `bean/BEAN-NNN-<slug>` (e.g., `bean/BEAN-006-backlog-refinement`)
- Team Lead creates the feature branch when picking a bean
- All task commits happen on the feature branch
- Update `/long-run` skill to incorporate branch creation
- Update `/pick-bean` skill to optionally create a feature branch
- Branch cleanup guidance (after merge)

### Out of Scope
- Merging to test or main branch (that's BEAN-011)
- Parallel execution (that's BEAN-010)
- Push permissions (that's BEAN-009)
- PR creation (future enhancement)

## Acceptance Criteria

- [ ] `/pick-bean` skill updated to create a feature branch `bean/BEAN-NNN-<slug>`
- [ ] `/long-run` skill updated to create feature branches per bean
- [ ] All bean work committed on the feature branch, not main
- [ ] Branch naming convention documented in `bean-workflow.md`
- [ ] Command/skill format matches existing patterns
- [ ] Team Lead agent updated if needed

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Update Commands, Skills, and Workflow for Feature Branches | developer | — | Done |
| 02 | Feature Branch Workflow Verification | tech-qa | 01 | Done |

> BA and Architect skipped — this bean updates existing markdown docs with a well-defined branching convention. No ambiguity or architectural decisions.

## Notes

This bean is a prerequisite for parallel execution (BEAN-010) and auto-merge (BEAN-011). The feature branch pattern also improves single-threaded workflow by keeping main clean and providing a natural review point before merging.

Depends on: BEAN-007 (Long Run Command).
