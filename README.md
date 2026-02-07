# Foundry

A PySide6 desktop application that generates Claude Code project folders from reusable building blocks.

Foundry combines **personas** (role-agnostic behavior definitions) with **tech-stack packs** (language/framework best practices) to produce fully configured `.claude/` directories with sub-agents, tasks, skills, and hooks.

## Quickstart

### 1. Install

```bash
uv sync
```

### 2. Launch

```bash
uv run foundry
```

### 3. Open a library

Click **Open Library** in the toolbar and select the `ai-team-library/` directory (included in this repo). The navigation tree will populate with personas, stacks, and templates.

### 4. Browse and edit library content

Use the left sidebar to navigate:
- **Personas** — view and edit persona definitions, outputs contracts, and prompt files
- **Stacks** — view and edit stack convention docs and overrides
- **Templates** — cross-cut view of all templates across personas, with search and filtering
- **Hooks** — browse, create, and delete hook definitions; apply posture presets
- **Workflows** — browse, create, and delete workflow markdown files
- **Skills / Commands** — two-tab view for browsing command and skill definitions

Click any file to open it in the built-in markdown editor (right panel). Changes are saved back to the library.

### 5. Edit compositions

Open the **Composition Editor** for full control over a project's `composition.yml`. The editor provides synchronized form and YAML views -- edits in one are reflected in the other in real time. Inline validation highlights errors before you generate.

### 6. Run the project wizard

Click **New Project** (or navigate to Project Builder > New Project Wizard). Walk through the five steps:

1. **Project Identity** — name, slug, description, output directory
2. **Tech Stack** — select and order stack packs (e.g. python, react)
3. **Team Personas** — pick personas for the team and configure each (agent mode, templates, strictness)
4. **Hooks & Policies** — enable/disable safety hooks and guardrails
5. **Review & Generate** — see a summary, review validation results, and click Generate

### 7. Generate the project

The **Generate** screen includes a pipeline runner and a manifest inspector. Load a `composition.yml`, click Run, and watch each stage execute:

- **Validate** — checks composition spec completeness and library references
- **Scaffold** — creates the project directory structure (`CLAUDE.md`, `.claude/agents/`, `ai/`)
- **Compile** — generates team member prompts from persona + stack + project context
- **Seed** — creates starter task lists with dependency waves

After generation completes, the manifest inspector shows every file that was created.

### 8. Export

Navigate to **Export** to copy or move the generated project to its final location. Options include initializing a git repo and running a pre-export checklist.

### 9. Settings

Open **Settings** (Ctrl+,) to configure persistent preferences:

- **Paths** — default library and output directories
- **Editor** — font family, font size, tab width
- **Validation** — strictness level for composition checks
- **Git** — auto-initialize a git repo in generated projects

### 10. History

The **History** screen has three tabs:

- **Recent Projects** — quick access to previously generated projects
- **Generation Logs** — timestamped log of past generation runs with status
- **Manifest Viewer** — inspect the full manifest of any past generation

## Keyboard shortcuts

| Shortcut | Action        |
|----------|---------------|
| Ctrl+O   | Open Library  |
| Ctrl+N   | New Project   |
| Ctrl+G   | Generate      |
| Ctrl+E   | Export        |
| Ctrl+,   | Settings      |

## Project structure

```
foundry/
  pyproject.toml
  README.md
  foundry_app/
    __init__.py
    main.py                          # entry point
    core/
      models.py                      # Pydantic data contracts
      settings.py                    # persistent user preferences
    services/
      generator.py                   # pipeline orchestrator
      compiler.py                    # meta-prompt compiler
      scaffold.py                    # directory structure creator
      seeder.py                      # starter task generator
      validator.py                   # pre/post-generation checks
      library_indexer.py             # library directory scanner
    io/
      composition_io.py              # YAML/JSON read/write
    ui/
      main_window.py                 # three-pane layout
      widgets/
        markdown_editor.py           # source/preview editor
      screens/
        library/
          persona_browser.py         # persona list + file viewer
          stack_browser.py           # stack list + file viewer
          template_browser.py        # cross-cut template view
          hooks_browser.py           # hook definitions + posture presets
          workflows_browser.py       # workflow markdown file manager
          skills_commands_browser.py  # two-tab commands/skills view
        builder/
          wizard.py                  # 5-step project wizard
          composition_editor.py      # synced form + YAML editor
          generate_screen.py         # pipeline runner + manifest inspector
          export_screen.py           # project export with checklist
        settings_screen.py           # paths, editor, validation, git prefs
        history_screen.py            # recent projects, logs, manifests
  ai-team-library/                   # reusable building blocks
    personas/                        # 13 role definitions
    stacks/                          # 4 tech-stack packs
    workflows/                       # task taxonomy, DoD
    claude/                          # command/skill/hook templates
  tests/
    test_smoke.py                    # library index + pipeline tests
```

## Core concept

> **TeamMember** = **Persona** (role behaviors) + **StackPack** (tech best practices) + **ProjectContext** (domain + constraints)

The library stores personas and stacks independently. At generation time, the compiler merges them into team member prompts tailored to the specific project.

## Pipeline stages

| Stage    | Verb     | Description                                         |
|----------|----------|-----------------------------------------------------|
| Select   | choose   | Pick stack packs + personas + optional extras       |
| Compose  | configure| Write `composition.yml` describing selections       |
| Compile  | generate | Merge persona + stack + context into member prompts |
| Scaffold | create   | Build project directory structure                   |
| Seed     | populate | Create starter task list with dependency waves      |
| Run      | orchestrate | Let the lead coordinate via shared task list     |
| Export   | handoff  | Move project out and init as its own git repo       |

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Lint
uv run ruff check foundry_app/
```
