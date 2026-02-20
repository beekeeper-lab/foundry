# Task 02: Verify Changes Section Implementation

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-20 20:20 |
| **Completed** | 2026-02-20 20:23 |
| **Duration** | 3m |

## Goal

Verify that the Changes section placeholder exists in the template, the merge-bean workflow documents the population step correctly, and all quality gates pass.

## Inputs

- Task 01 output (changed files)
- `ai/beans/_bean-template.md` — verify Changes section exists
- `.claude/skills/internal/merge-bean/SKILL.md` — verify new step documented
- `.claude/commands/internal/merge-bean.md` — verify command doc updated

## Verification Checklist

- [ ] `_bean-template.md` contains `## Changes` section with placeholder table
- [ ] Merge-bean SKILL.md has a step for generating the change summary from git diff
- [ ] Merge-bean SKILL.md step is sequenced correctly (after validation, before merge)
- [ ] Merge-bean command doc mentions Changes section population
- [ ] Changes table format includes file paths and +/- line counts
- [ ] The workflow update clearly documents which step populates the section
- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check foundry_app/` — lint clean

## Definition of Done

- [ ] All verification checklist items pass
- [ ] Any issues found are reported and fixed
