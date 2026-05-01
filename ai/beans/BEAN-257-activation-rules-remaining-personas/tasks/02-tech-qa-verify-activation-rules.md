# Task 02: Verify Activation Rules Coverage

| Field         | Value   |
| ------------- | ------- |
| **Owner**     | tech-qa |
| **Depends On** | 01      |
| **Status**    | Done |
| **Started**   | 2026-04-17 19:55 |
| **Completed** | 2026-04-17 20:00 |
| **Duration**  | 5m |

## Verification Results

- ✅ All 24 library personas have `## Activated When` section (`grep -L` returns nothing)
- ✅ Each section contains numbered triggers (4-9 per persona), explicit exclusions, and a fallback rule
- ✅ Mandatory framing confirmed for team-lead, developer, tech-qa
- ✅ Bench-pull framing confirmed for the 21 opt-in personas (BEAN-269 alignment)
- ✅ `.claude/agents/team-lead.md` adds "Activation Rules for Other Personas" section pointing at library `Activated When` as authoritative
- ✅ `ai/context/persona-activation-audit.md` lists all 24 personas with stance + format + maintenance guidance
- ✅ `uv run pytest`: 1903 passed, 4 warnings (pre-existing Qt deprecation, unrelated)
- ✅ `uv run ruff check foundry_app/`: All checks passed
- ✅ Spot-check (developer, tech-qa, code-quality-reviewer, ux-ui-designer, integrator-merge-captain): triggers are concrete and persona-tailored, not boilerplate

## Goal

Verify that every library persona has a tailored `## Activated When` section, the bench-model framing is consistent, and the team-lead agent references the library as authoritative. Confirm tests + lint stay clean.

## Inputs

- `ai-team-library/personas/*/persona.md` — all 24 persona files (post Task 01)
- `.claude/agents/team-lead.md` — updated reference
- `ai/context/team-lead.md` (or wherever the audit note lives) — coverage audit
- `ai/beans/BEAN-257-activation-rules-remaining-personas/bean.md` — acceptance criteria

## Verification Checklist

- [ ] Run `grep -L "## Activated When" ai-team-library/personas/*/persona.md` → no missing files
- [ ] Spot-check 5 personas (developer, tech-qa, code-quality-reviewer, ux-ui-designer, integrator-merge-captain): triggers are concrete and evaluable, not boilerplate
- [ ] Developer + Tech-QA sections explicitly state mandatory-default
- [ ] Non-mandatory personas use bench-pull framing per BEAN-269
- [ ] Each section has triggers + exclusions + fallback rule
- [ ] `.claude/agents/team-lead.md` references library `Activated When` sections as authoritative
- [ ] Coverage audit lists all 24 personas
- [ ] `uv run pytest` passes (no regressions)
- [ ] `uv run ruff check foundry_app/` passes

## Definition of Done

All checklist items pass. Any gaps fed back to Task 01 for fix; otherwise mark task Done.
