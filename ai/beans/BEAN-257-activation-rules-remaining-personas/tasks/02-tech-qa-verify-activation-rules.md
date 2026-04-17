# Task 02: Verify Activation Rules Coverage

| Field         | Value   |
| ------------- | ------- |
| **Owner**     | tech-qa |
| **Depends On** | 01      |
| **Status**    | Pending |
| **Started**   | —       |
| **Completed** | —       |
| **Duration**  | —       |

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
