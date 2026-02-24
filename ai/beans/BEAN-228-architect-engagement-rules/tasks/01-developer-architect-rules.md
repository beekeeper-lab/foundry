# Task 01: Draft and Apply Architect Engagement Rules

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-23 20:04 |
| **Completed** | 2026-02-23 20:05 |
| **Duration** | 1m |

## Goal

Define a clear, numbered set of rules that tell the Team Lead when to engage the Architect persona. Update all three files that currently specify architect activation criteria: `team-lead.md`, `architect.md`, and `bean-workflow.md`. The rules should lower the activation threshold compared to current criteria while still avoiding engagement for trivial changes.

## Inputs

- `.claude/agents/team-lead.md` — current Participation Decisions section
- `.claude/agents/architect.md` — current "When You Are Activated" section
- `ai/context/bean-workflow.md` — current "Inclusion Criteria for Optional Personas" section
- Trello card description (in bean.md Notes) — user's guidance on when architect should be engaged

## Key Requirements from User

The user identified these specific gaps:
1. **Refactoring**: When new functionality causes any refactoring, the architect should be engaged
2. **Early project setup**: During project foundations/setup, the architect (not developer) should be doing structural work
3. **ADR creation**: Every architectural decision should produce an ADR — the architect is the one with this skill
4. **Current threshold is too high**: The architect is almost never engaged, which is wrong

## Example Output

The updated Participation Decisions table in `team-lead.md` should follow this format:

```markdown
### Architect Engagement Rules

The architect is engaged when ANY of the following conditions apply:

1. **New subsystem or module** — the bean creates a module, service, or package not in the existing codebase
2. **Refactoring triggered by new functionality** — the bean adds features that require restructuring existing code (moving functions between modules, changing class hierarchies, splitting/merging files)
3. **Cross-cutting change** — the bean modifies public APIs or data models used by 3+ modules
...
```

The same numbered rules should appear (or be referenced) in all three files for consistency.

## Acceptance Criteria

- [ ] Numbered rules are defined (aim for 7-10 rules)
- [ ] Rules cover: refactoring, new functionality with structural changes, early project setup, ADR-worthy decisions, new subsystems, cross-cutting changes, new dependencies
- [ ] Rules explicitly exclude: trivial UI additions, text/copy changes, single-file bug fixes, config tweaks
- [ ] `team-lead.md` Participation Decisions section updated with the new rules
- [ ] `architect.md` "When You Are Activated" section updated to match
- [ ] `bean-workflow.md` "Inclusion Criteria for Optional Personas" Architect section updated to match
- [ ] All three files are consistent — same rule set, no contradictions
- [ ] Rules are concrete and evaluable — the Team Lead can check each rule with a yes/no answer

## Definition of Done

All three agent/workflow files updated with the new architect engagement rules. Rules are numbered, clear, and consistent across all files.
