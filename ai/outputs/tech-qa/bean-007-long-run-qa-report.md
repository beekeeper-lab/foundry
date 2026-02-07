# BEAN-007: Long Run Command — QA Report

**Author:** Tech-QA | **Date:** 2026-02-07 | **Bean:** BEAN-007

## Verdict: GO

## Test Results

- **Total tests:** N/A (no Python source changes — command/skill markdown only)
- **Lint:** N/A
- **Files created:** 2 new, 1 updated

## Traceability Matrix

| Bean AC | Evidence | Status |
|---------|----------|--------|
| `/long-run` command exists | `.claude/commands/long-run.md` — 100 lines, all 9 standard sections | PASS |
| Skill exists | `.claude/skills/long-run/SKILL.md` — 108 lines, all 8 standard sections | PASS |
| Team Lead selects beans based on priority, dependencies, logical order | Command: Options > Bean Selection Heuristics table (4 criteria). Skill: Phase 2 steps 4-6 with detailed heuristics | PASS |
| Full lifecycle per bean | Command: 11-step process. Skill: 6 phases (Assessment → Selection → Execution → Wave → Verification → Loop) with 16 steps | PASS |
| Roles skipped when not needed | Skill: Phase 4 step 11 explicitly documents role skipping | PASS |
| Progress summary after each bean | Command: step 10 + Examples section with sample output. Skill: Phase 5 step 15 | PASS |
| Changes committed after each bean | Command: step 9. Skill: Phase 5 step 14. Commit message format: `BEAN-NNN: <title>` | PASS |
| Stops gracefully when no beans remain | Command: step 2 + Error Handling table. Skill: Phase 1 step 3 + Error Conditions table | PASS |
| Command format matches existing | 9 sections: Purpose, Usage, Inputs, Process, Output, Options, Error Handling, Examples — matches pick-bean.md | PASS |
| Skill format matches existing | 8 sections: Description, Trigger, Inputs, Process, Outputs, Quality Criteria, Error Conditions, Dependencies — matches pick-bean SKILL.md | PASS |
| Team Lead agent updated | `.claude/agents/team-lead.md` line 23: `/long-run` added to Skills & Commands table | PASS |

## File Verification

| File | Exists | Sections | Format Match | Issues |
|------|--------|----------|--------------|--------|
| `.claude/commands/long-run.md` | Yes | 9 sections | Matches reference | None |
| `.claude/skills/long-run/SKILL.md` | Yes | 8 sections | Matches reference | None |
| `.claude/agents/team-lead.md` | Yes | Updated | `/long-run` in table | None |

## Additional Verification

- Error handling covers 5 conditions with clear resolution steps
- Bean selection heuristics are prioritized (not ambiguous)
- Examples section shows both typical output and completion output
- Skill process is phased (6 phases) for clarity and auditability
- Quality Criteria section defines 7 measurable criteria
- No placeholder text remains

## Recommendation

**GO** — All 11 acceptance criteria met. Command and skill are thorough, well-structured, and consistent with existing patterns.
