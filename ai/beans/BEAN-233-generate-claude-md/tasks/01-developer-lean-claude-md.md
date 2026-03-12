# Task 01: Add description field and refactor compiler for lean CLAUDE.md

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-03-12 03:09 |
| **Completed** | 2026-03-12 03:09 |
| **Duration** | < 1m |

## Goal

Refactor the compiler service so that `compile_project()` generates a lean CLAUDE.md (~100 lines) containing only universal project context, while writing full persona and expertise content to separate files under `ai/generated/`.

## Inputs

- `foundry_app/core/models.py` — add optional `description` field to `ProjectIdentity`
- `foundry_app/services/compiler.py` — refactor `compile_project()`
- `foundry_app/services/scaffold.py` — add `ai/generated/members/` and `ai/generated/expertise/` dirs
- `foundry_app/templates/agent.md.j2` — already references `ai/generated/members/`

## Changes Required

1. **models.py** — Add `description: str | None = None` to `ProjectIdentity`
2. **scaffold.py** — Add `ai/generated/members` and `ai/generated/expertise` to `_AI_DIRS`
3. **compiler.py** — Refactor `compile_project()`:
   - Generate lean CLAUDE.md with: project header + description, tech stack table, directory structure, team overview table, key conventions, pointers to detailed docs
   - Write full persona content to `ai/generated/members/<persona_id>.md`
   - Write full expertise content to `ai/generated/expertise/<expertise_id>.md`
   - Keep the existing helper functions for reference filtering, substitution, etc.

## Example Output

The generated CLAUDE.md should look approximately like:

```markdown
# My Project

One-line description here.

## Tech Stack

| Technology | Role |
|------------|------|
| Python | Primary language |
| Clean Code | Conventions |

## Directory Structure

```
.claude/          # Claude Code config (agents, commands, hooks, skills)
ai/               # AI team workspace
  context/        # Project context docs
  outputs/        # Persona output directories
  generated/      # Generated persona and expertise prompts
  beans/          # Work tracking
  tasks/          # Task lists
```

## Team

| Persona | Role | Agent | Prompt |
|---------|------|-------|--------|
| Developer | ... | `.claude/agents/developer.md` | `ai/generated/members/developer.md` |

## Conventions

- Key universal convention 1
- Key universal convention 2

## Detailed Documentation

Full persona prompts and expertise conventions are in `ai/generated/`:
- **Persona prompts:** `ai/generated/members/<persona>.md`
- **Expertise conventions:** `ai/generated/expertise/<expertise>.md`
```

## Definition of Done

- [ ] `ProjectIdentity` has optional `description` field
- [ ] Scaffold creates `ai/generated/members/` and `ai/generated/expertise/` directories
- [ ] `compile_project()` writes lean CLAUDE.md under 100 lines
- [ ] `compile_project()` writes full persona files to `ai/generated/members/<id>.md`
- [ ] `compile_project()` writes full expertise files to `ai/generated/expertise/<id>.md`
- [ ] CLAUDE.md includes project name, description, tech stack, directory overview, team table, pointers
- [ ] Ruff clean (`uv run ruff check foundry_app/`)
