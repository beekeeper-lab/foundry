# Task 01: Define BA Engagement Rules and Modes

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-23 20:52 |
| **Completed** | 2026-02-23 20:54 |
| **Duration** | 2m |

## Goal

Define a two-mode BA engagement system (full mode and partial mode) controlled by a project-level flag. Update `team-lead.md`, `ba.md`, and `bean-workflow.md` with the new rules. Follow the pattern established in BEAN-228 for architect engagement rules (numbered rules, exclusion list, "when in doubt" heuristic).

## Inputs

- `.claude/agents/team-lead.md` — current Participation Decisions section (see Architect Engagement Rules as pattern)
- `.claude/agents/ba.md` — current "When You Are Activated" section
- `ai/context/bean-workflow.md` — current "Inclusion Criteria for Optional Personas" BA section
- `ai/beans/BEAN-229-ba-engagement-rules/bean.md` — full bean context and user requirements

## Key Design Decisions

### Flag Location
The BA engagement mode flag should live in `bean-workflow.md` in a new "## BA Engagement Mode" section near the top (after the lifecycle diagram). This keeps all workflow configuration in one place. The flag is a simple markdown value: `**BA Mode:** Full` or `**BA Mode:** Partial (default)`.

### Full Mode Workflow
When `BA Mode: Full`:
1. BA runs at the start of every bean (before Developer/Architect)
2. BA maintains a requirements register at `ai/outputs/ba/requirements-register.md`
3. For each bean, BA analyzes impact on requirements, updates the register, and hands off relevant requirements to the next persona
4. Wave becomes: **BA → [Architect if needed] → Developer → Tech-QA**

### Partial Mode Rules (Numbered, Following BEAN-228 Pattern)
When `BA Mode: Partial` (default), engage the BA when ANY of these apply:

1. **Requirements ambiguity** — the bean has 3+ valid interpretations
2. **User-facing behavior change** — the bean changes how end users interact with the system (new screens, modified workflows, changed defaults)
3. **Multi-stakeholder trade-offs** — the bean involves competing concerns that need documented trade-off analysis
4. **Documentation or specification task** — the bean's primary deliverable is documentation, specifications, or process definitions (BA is better suited than Developer for these)
5. **Scope uncertainty** — the bean's In Scope / Out of Scope boundaries are unclear or contentious
6. **Cross-bean impact** — the bean may affect requirements or assumptions of 2+ other beans
7. **New user-facing concept** — the bean introduces a concept, term, or workflow that users need to understand

### Exclusions (Partial Mode)
Do NOT engage the BA for:
- Bug fixes with obvious expected behavior
- Infrastructure/CI/CD changes with no user-facing impact
- Code refactoring that preserves existing behavior
- Test-only beans
- Single-file configuration changes
- Beans where Problem Statement, Goal, and Acceptance Criteria are already precise and unambiguous

## Acceptance Criteria

- [ ] BA Mode flag defined in `bean-workflow.md` with Full and Partial options
- [ ] Full mode workflow specified (requirements register, pre-bean analysis, handoff)
- [ ] Partial mode has numbered rules (7+ rules)
- [ ] Exclusion list defined for partial mode
- [ ] `team-lead.md` updated with both modes and partial-mode rules
- [ ] `ba.md` updated with two operating modes
- [ ] `bean-workflow.md` updated with mode flag and revised BA criteria
- [ ] Requirements register template location specified (`ai/outputs/ba/requirements-register.md`)
- [ ] All three files are consistent

## Example Output

The updated Participation Decisions in `team-lead.md` should follow this format:

```markdown
### BA Engagement Rules

**Mode:** Controlled by the `BA Mode` flag in `bean-workflow.md`. Default: `Partial`.

**Full mode** — BA runs on every bean. See bean-workflow.md for the full-mode workflow.

**Partial mode** — Add the BA when ANY of the following conditions apply:

| # | Rule | Description |
|---|------|-------------|
| 1 | **Requirements ambiguity** | The bean has 3+ valid interpretations... |
...
```

## Definition of Done

All three files updated with BA engagement modes and rules. Flag mechanism defined. Full-mode and partial-mode workflows documented. Consistent across all files.
