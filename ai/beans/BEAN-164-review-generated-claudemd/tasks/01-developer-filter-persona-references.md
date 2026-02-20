# Task 01: Filter Non-Selected Persona References in Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:15 |
| **Completed** | 2026-02-20 20:20 |
| **Duration** | 5m |

## Goal

Add post-processing to the compiler service (`foundry_app/services/compiler.py`) so that generated CLAUDE.md content only references team members that are actually selected in the composition spec.

## Problem

Each persona's `persona.md` in the library contains:
1. A **Collaboration & Handoffs** table listing ALL 13 possible personas as collaborators
2. A **"Does not:"** section referencing specific personas (e.g., "defer to Architect")

The compiler includes this content verbatim, so even a 5-persona team gets CLAUDE.md referencing 12+ non-selected personas.

## Inputs

- `foundry_app/services/compiler.py` — the compilation service to modify
- `foundry_app/core/models.py` — LibraryIndex and PersonaInfo models
- `ai-team-library/personas/team-lead/persona.md` — example persona file showing the Collaboration table structure
- `tests/test_compiler.py` — existing tests to understand test patterns

## Implementation Plan

1. **Build a persona name→ID map** from the library index by reading the `# Persona: <Name>` header from each persona.md
2. **Filter Collaboration & Handoffs table rows** — remove rows where the collaborator maps to a known-but-not-selected persona. Keep rows for selected personas and unknown entities (e.g., "Stakeholders").
3. **Clean "defer to X" references** — in "Does not:" sections, remove the `(defer to X)` parenthetical when X is a non-selected persona. Keep the constraint itself (e.g., "Write production code" stays, but "(defer to Developer)" is removed if Developer isn't selected).
4. **Wire into `_compile_persona_section()`** — pass `selected_ids: set[str]` and the name map, apply filtering after content assembly.
5. **Update `compile_project()`** — build the name map once, pass selected IDs through to the persona compilation.

## Example Output

For a team of [compliance-risk, team-lead, technical-writer], the team-lead's Collaboration & Handoffs table in the generated CLAUDE.md should only show:

```markdown
| Collaborator               | Interaction Pattern                          |
|----------------------------|----------------------------------------------|
| Technical Writer           | Seed documentation tasks post-implementation |
| Compliance / Risk Analyst  | Route compliance-sensitive items for review |
```

And the "Does not:" section should become:
```markdown
- Write production code
- Make architectural decisions
- Override security findings
- Perform code reviews
- Design user interfaces
- Write end-user documentation (defer to Technical Writer)
```

## Definition of Done

- [ ] `_compile_persona_section()` filters Collaboration & Handoffs table to selected personas only
- [ ] `_compile_persona_section()` cleans "defer to" references for non-selected personas
- [ ] Filtering is wired into `compile_project()` with the name map built from the library
- [ ] Existing tests still pass
- [ ] New tests added for the filtering logic
- [ ] `uv run ruff check foundry_app/` is clean
