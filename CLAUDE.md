# Foundry

Foundry is a PySide6 desktop application and Python service layer that generates Claude Code project folders from reusable building blocks. Version 1.0.0.

## Repository Structure

```
foundry_app/          # Application source (core/, services/, ui/, io/)
tests/                # pytest test suite (1811 tests)
ai-team-library/      # Reusable library: personas, stacks, templates, workflows
ai/                   # AI team workspace (context, outputs, beans, tasks)
.claude/              # Claude Code config (agents, skills, commands, hooks, settings)
examples/             # Example composition YAMLs
```

## AI Team

| Persona | Role | Agent | Output Directory |
|---------|------|-------|------------------|
| Team Lead | Coordinates work, decomposes beans, assigns tasks | `.claude/agents/team-lead.md` | `ai/outputs/team-lead/` |
| BA | Requirements, user stories, acceptance criteria | `.claude/agents/ba.md` | `ai/outputs/ba/` |
| Architect | System design, ADRs, module boundaries | `.claude/agents/architect.md` | `ai/outputs/architect/` |
| Developer | Implementation, refactoring, code changes | `.claude/agents/developer.md` | `ai/outputs/developer/` |
| Tech QA | Test plans, test implementation, quality gates | `.claude/agents/tech-qa.md` | `ai/outputs/tech-qa/` |

## Beans Workflow

A **Bean** is a unit of work (feature, enhancement, bug fix, or epic). Beans live in `ai/beans/BEAN-NNN-<slug>/`.

**Lifecycle:** Unapproved → Approved → In Progress → Done

1. Create a bean from `ai/beans/_bean-template.md` (status: `Unapproved`)
2. User reviews and approves beans (status: `Approved`)
3. Team Lead picks approved beans from the backlog (`ai/beans/_index.md`)
4. Team Lead decomposes into tasks. Default wave: Developer → Tech-QA. BA and Architect are opt-in when criteria are met. Tech-QA is mandatory for every bean.
5. Each persona claims tasks, produces outputs, creates handoffs
6. Team Lead verifies outputs against acceptance criteria
7. Bean marked Done

See `ai/context/bean-workflow.md` for the full lifecycle specification.

## Tech Stack

- **Python** >=3.11 (running 3.14.2), **PySide6**, **Pydantic**, **Jinja2**, **PyYAML**
- **Build:** `hatchling` (note: `packages = ["foundry_app"]` because package name != project name)
- **Deps:** `uv` for dependency management
- **Lint:** `ruff` (line-length 100, target py311, select E/F/I/W)
- **Tests:** `pytest` (testpaths = tests/)

## Key Commands

```bash
uv run pytest                          # Run all tests
uv run pytest tests/test_foo.py -v     # Run one test file
uv run ruff check foundry_app/         # Lint check
uv run ruff check foundry_app/ --fix   # Lint auto-fix
uv run foundry                         # Launch GUI
uv run foundry-cli generate <yml> --library ai-team-library  # CLI generation
/bg <command> [args...]                # Run any slash command in a background tmux window
```

## Rules

- **Do not modify** files in `ai-team-library/` — that is the shared library
- **All AI outputs** go to `ai/outputs/<persona>/`
- **Run tests** before marking any task done (`uv run pytest`)
- **Run ruff** before committing (`uv run ruff check foundry_app/`)
- **Bean tasks** live in `ai/beans/BEAN-NNN-<slug>/tasks/`
- **ADRs** go in `ai/context/decisions.md`
