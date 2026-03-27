# Task 01: Context Budget Guidance

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 11:42 |
| **Completed** | 2026-03-27 11:44 |
| **Duration** | 2m |

## Goal

Add context budget guidance to agent instructions and bean-workflow.md so agents minimize unnecessary context loading, especially for simple tasks.

## Inputs

- `.claude/agents/*.md` — agent instruction files
- `ai/context/bean-workflow.md` — bean lifecycle specification
- `.claude/skills/long-run/SKILL.md` — long-run skill (for context hints to workers)
- Bean scope from BEAN-240

## Implementation

1. **Add "Context Diet" section to `ai/context/bean-workflow.md`** with per-category guidelines:
   - Library content beans: read template + target file only
   - Process beans: read affected doc files only, not entire codebase
   - App beans: read affected modules + test files, not entire service layer
   - General rule: Never re-read files already in context. Use targeted reads (offset/limit) for large files.

2. **Add context budget guidance to agent files**:
   - Developer agent: "Read only what each task's Inputs list specifies. Avoid speculative reads."
   - Tech-QA agent: "Read only the code under test and its test file. Don't read the full service layer."
   - Team Lead agent: "When spawning workers, pass task complexity hints."

3. **Update `/long-run` worker prompt** to include context hints:
   - Add `CONTEXT DIET` section to the worker spawn prompt

4. **Document CLAUDE.md size** — Record current size and note it's under threshold.

## Acceptance Criteria

- [ ] `ai/context/bean-workflow.md` has a "Context Diet" section
- [ ] Agent files include context budget guidance
- [ ] Long-run worker prompt includes context hints
- [ ] CLAUDE.md size documented
- [ ] All tests pass
- [ ] Lint clean

## Definition of Done

- All doc files updated, tests pass, lint clean
