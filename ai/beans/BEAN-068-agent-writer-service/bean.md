# BEAN-068: Agent Writer Service (Persona + Stack Team Members)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-068 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-08 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Generated projects have minimal stub agent files in `.claude/agents/` that just say "This agent follows the compiled member prompt" with a pointer to `ai/generated/members/<persona>.md`. These stubs don't convey the agent's role, stack context, or operating rules — Claude has to load the full compiled prompt (100KB+) to understand its role.

The user's vision is that each team member is a named combination of persona + tech stack context, like "React Architect" or "Python Developer". The agent file should be a hybrid: a self-contained role summary with key rules inlined, plus a reference to the full compiled prompt for exhaustive detail.

## Goal

Create a new `agent_writer.py` service (or extend the compiler) that generates rich `.claude/agents/<role>.md` files using a Jinja2 template. Each agent file combines persona identity with stack context into a named team member role with enough content to be useful on its own, while referencing the full compiled member prompt for depth.

## Scope

### In Scope
- New service: `foundry_app/services/agent_writer.py`
- Jinja2 template for agent files: `foundry_app/templates/agent.md.j2`
- Agent naming: persona + primary stack = role name (e.g., architect + react = "React Architect")
- Hybrid format: role summary (mission, key rules, stack highlights) + reference to compiled prompt
- Wire into `generator.py` pipeline (new stage after compile, before copy_assets)
- Handle multi-stack personas (e.g., developer with python + react gets both stack contexts summarized)
- Add `agent_writer` to CompositionSpec generation options if needed
- Tests for agent_writer service

### Out of Scope
- Changes to compiled member prompts (those stay as-is in `ai/generated/members/`)
- UI changes to the wizard (persona selection already works)
- Template editor UI for editing the agent template

## Acceptance Criteria

- [ ] New `foundry_app/services/agent_writer.py` service exists
- [ ] Jinja2 template `foundry_app/templates/agent.md.j2` exists with hybrid format
- [ ] Each selected persona generates a `.claude/agents/<persona-id>.md` with:
  - Role name combining persona + primary stack (e.g., "React Architect")
  - Mission statement from persona.md
  - Key operating rules (3-5 bullet points)
  - Stack-specific highlights from conventions.md
  - Reference to full compiled prompt: `ai/generated/members/<persona>.md`
  - Output directory: `ai/outputs/<persona>/`
- [ ] Multi-stack personas get highlights from all selected stacks
- [ ] Agent writer wired into `generator.py` pipeline
- [ ] Tests cover: single persona/single stack, single persona/multi stack, persona not found
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-067 (Wire Pipeline) being complete so the pipeline is accepting real service calls
- The Jinja2 template should be straightforward — persona data comes from the library index, stack data from conventions.md
- Consider extracting key rules from persona.md using a simple header/section parser rather than including the entire file
- The naming convention (persona + stack) should handle edge cases: persona with no stack (just use persona name), persona with multiple stacks (use primary/first stack for the name)
- Example output format:

```markdown
# React Architect

**Role:** System design, architecture decisions, module boundaries
**Stack:** React, TypeScript
**Output directory:** `ai/outputs/architect/`

## Mission
[Extracted from persona.md opening section]

## Key Rules
- [Rule 1 from persona.md]
- [Rule 2]
- [Stack-specific rule from conventions.md]

## Stack Context
### React
[Key highlights from react/conventions.md]

### TypeScript
[Key highlights from typescript/conventions.md]

---
*Full compiled prompt:* `ai/generated/members/architect.md`
```
