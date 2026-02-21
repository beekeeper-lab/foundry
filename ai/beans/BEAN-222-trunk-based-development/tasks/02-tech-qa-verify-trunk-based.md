# Task 02: Verify Trunk-Based Development Migration

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01-developer-update-all-workflow-files |
| **Status** | Done |
| **Started** | 2026-02-21 17:58 |
| **Completed** | 2026-02-21 18:03 |
| **Duration** | 5m |

## Goal

Verify all `test` branch workflow references are gone and the trunk-based model is consistently documented.

## Verification Checklist

- [x] grep for `checkout test` in .claude/ and ai-team-library/claude/ returns zero results
- [x] grep for `merge.*test` in workflow files returns zero results (excluding historical beans)
- [x] grep for `pull.*test` in workflow files returns zero results
- [x] grep for `push.*test` in workflow files returns zero results
- [x] `/long-run` SKILL.md Phase 0 checks for `main`
- [x] `/merge-bean` SKILL.md defaults to `main`
- [x] Library templates are consistent with local templates
- [x] bean-workflow.md has no test branch integration concept
- [x] MEMORY.md updated
- [x] Tests pass (`uv run pytest`) — 659 passed
- [x] Lint clean (`uv run ruff check foundry_app/`)

**Additional stale references found and fixed by Tech-QA:**
- `ai-team-library/claude/skills/deploy/SKILL.md` — completely not updated (rewrote to match local)
- `.claude/hooks/hook-policy.md` — Branch Protection section referenced `test`
- `.claude/hooks/telemetry-stamp.py` + `ai-team-library/claude/hooks/telemetry-stamp.py` — code referenced `test`
- `ai-team-library/claude/hooks/git-merge-to-test.md` — updated for trunk-based
- `ai-team-library/claude/hooks/git-merge-to-prod.md` — updated for trunk-based
- `ai-team-library/claude/hooks/git-generate-pr.md` — updated for trunk-based
- `ai-team-library/claude/hooks/git-commit-branch.md` — removed `test` from protected branches
- `ai-team-library/claude/commands/pick-bean.md` — removed "ensure test branch" step
- `ai-team-library/claude/skills/pick-bean/SKILL.md` — removed "ensure test branch" step
- `.claude/skills/commands/SKILL.md` — updated deploy description
- `.claude/skills/run/SKILL.md` + `ai-team-library/claude/skills/run/SKILL.md` — removed `test` branch option
- `ai-team-library/claude/commands/run.md` — removed `test` branch option
- `ai-team-library/process/context/bean-workflow.md` — updated branch strategy
- `ai-team-library/personas/tech-qa/templates/test-plan.md` — updated merge target

## Acceptance Criteria

- [x] All verification items pass
- [x] No stale references found (14 additional stale files discovered and fixed)

## Definition of Done

Full verification complete. Trunk-based workflow consistently documented.
