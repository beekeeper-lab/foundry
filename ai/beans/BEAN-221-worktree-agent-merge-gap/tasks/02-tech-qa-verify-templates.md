# Task 02: Verify Template Consistency and Correctness

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends On** | 01-developer-fix-library-templates |
| **Status** | Done |
| **Started** | 2026-02-21 16:48 |
| **Completed** | 2026-02-21 16:49 |
| **Duration** | 1m |

## Goal

Verify that the updated library templates are correct, internally consistent, and will produce a working parallel merge flow in generated sub-apps.

## Inputs

- `ai-team-library/claude/skills/long-run/SKILL.md` — updated library long-run skill
- `ai-team-library/claude/commands/long-run.md` — updated library long-run command
- `ai-team-library/claude/commands/spawn-bean.md` — updated library spawn-bean command
- `.claude/skills/long-run/SKILL.md` — Foundry's working reference

## Verification Checklist

- [ ] Library long-run SKILL.md has "Continuous Assignment Dashboard Loop" (not "Dashboard Monitoring")
- [ ] Library long-run SKILL.md has explicit per-iteration steps (read → merge → assign → render → sleep)
- [ ] Merge step includes: remove worktree, sync, merge, update index, mark as merged
- [ ] Replacement assignment step includes: re-read _index.md fresh
- [ ] Exit condition explicitly requires BOTH: all done/merged AND no approved beans
- [ ] Library long-run command parallel section describes same pattern
- [ ] Library spawn-bean Step 4 integrates merge into loop (not separate section)
- [ ] No references to Foundry-specific paths (/tmp/foundry-*) in library templates
- [ ] Library templates use generic paths (/tmp/agentic-*)
- [ ] Tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Acceptance Criteria

- [ ] All verification checklist items pass
- [ ] Templates are internally consistent
- [ ] No regressions in test suite

## Definition of Done

All checks pass. Templates verified as correct and consistent.
