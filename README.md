# Foundry

**A desktop application and CLI for generating Claude Code project folders from reusable building blocks.**

Foundry is a project factory that combines **personas** (role definitions like Architect, Developer, QA) with **tech-stack packs** (language/framework best practices) to produce fully configured project directories — complete with `.claude/` sub-agents, compiled team member prompts, starter tasks, and safety hooks.

Built with PySide6 (Qt for Python), Foundry provides both a visual desktop GUI and a headless CLI for batch automation.

---

## Table of Contents

- [Why Foundry](#why-foundry)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Running Foundry](#running-foundry)
- [The GUI](#the-gui)
- [The CLI](#the-cli)
- [The Library](#the-library)
- [Generated Project Structure](#generated-project-structure)
- [Pipeline Stages](#pipeline-stages)
- [Data Contracts](#data-contracts)
- [Configuration](#configuration)
- [Development](#development)
- [Project Structure](#project-structure)
- [License](#license)

---

## Why Foundry

When working with Claude Code on multi-agent projects, each team member (sub-agent) needs a carefully constructed prompt that combines:

- **Who they are** — role identity, operating principles, definition of done
- **What they know** — tech stack conventions, testing practices, security patterns
- **What they produce** — deliverables, output routing, quality bars
- **How they collaborate** — task dependencies, handoff checklists, escalation rules

Writing these prompts by hand for every project is repetitive and error-prone. Foundry solves this by treating personas and stacks as **independent, reusable building blocks** that get **compiled** into project-specific team member prompts at generation time.

> **TeamMember** = **Persona** (role behaviors) + **StackPack** (tech best practices) + **ProjectContext** (domain + constraints)

The same Architect persona works equally well with a Python project, a React+Node project, or a .NET project — Foundry handles the merge.

---

## How It Works

1. **Curate a library** of personas, tech stacks, hook policies, and templates
2. **Compose** a project spec by selecting which building blocks to include
3. **Generate** a self-contained project folder with compiled agents, scaffolded structure, and starter tasks
4. **Export** the folder to its final location and optionally initialize a git repo

The generated project is completely self-contained — no runtime dependency on Foundry or the library. You can move it anywhere, `git init`, and start working with Claude Code immediately.

---

## Installation

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install with uv

```bash
git clone https://github.com/beekeeper-lab/foundry.git
cd foundry
uv sync
```

### Install with pip

```bash
git clone https://github.com/beekeeper-lab/foundry.git
cd foundry
pip install -e .
```

### Dev dependencies (for running tests and linting)

```bash
uv sync --group dev
```

---

## Running Foundry

### Desktop GUI

```bash
# Via installed entry point
uv run foundry

# Or as a Python module
python -m foundry_app
```

### CLI (headless)

```bash
# Via installed entry point
uv run foundry-cli --help

# Or directly
foundry-cli generate composition.yml --library ./ai-team-library
```

---

## The GUI

Foundry's desktop interface uses a three-pane layout:

- **Left** — Navigation tree with search
- **Center** — Content area (lists, editors, wizard steps)
- **Right** — Inspector panel (preview, validation, diffs)

### Library Mode

Browse, create, and edit the building blocks that define how agentic teams work.

| Screen | Purpose |
|---|---|
| **Personas** | Create and edit persona definitions (persona.md, outputs.md, prompts.md, templates/) |
| **Stacks** | Manage tech-stack convention docs (conventions, testing, security, etc.) |
| **Templates** | Cross-cut searchable view of all templates across all personas |
| **Hooks** | Define hook policy packs with posture presets (baseline / hardened / regulated) |
| **Workflows** | Manage pipeline and task taxonomy documentation |
| **Skills / Commands** | Two-tab browser for Claude Code skill and command definitions |

### Project Builder Mode

Collect decisions, generate a project, and export it.

| Screen | Purpose |
|---|---|
| **New Project Wizard** | 5-step guided flow: Identity, Stacks, Personas, Hooks, Review & Generate |
| **Composition Editor** | Power-edit `composition.yml` with synchronized Form and YAML views |
| **Generate** | Run the pipeline, watch stage progress, inspect the generation manifest |
| **Export** | Copy/move the project to its final destination with pre-export validation |

### Other Screens

| Screen | Purpose |
|---|---|
| **History** | Recent projects, generation logs, and manifest viewer |
| **Settings** | Library/workspace paths, editor preferences, validation strictness, git options |

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+O | Open Library |
| Ctrl+N | New Project |
| Ctrl+G | Generate |
| Ctrl+E | Export |
| Ctrl+, | Settings |

---

## The CLI

The `foundry-cli` command provides headless access to the full pipeline for scripting and CI/CD integration.

### Commands

#### `generate` — Run the full generation pipeline

```bash
foundry-cli generate composition.yml \
  --library ./ai-team-library \
  --output ./my-project \
  --strictness standard
```

Options:
- `--library, -l` (required) — Path to the ai-team-library root
- `--output, -o` — Override the output directory
- `--strictness, -s` — Validation strictness: `light`, `standard`, or `strict`

#### `validate` — Check a composition without generating

```bash
foundry-cli validate composition.yml \
  --library ./ai-team-library \
  --strictness strict
```

Returns exit code 0 on success, 1 on validation failure.

#### `export` — Export a generated project

```bash
foundry-cli export ./generated-projects/my-proj ./releases/my-proj \
  --mode copy \
  --git-init \
  --validate
```

Options:
- `--mode, -m` — `copy` (default) or `move`
- `--git-init` — Run `git init` in the destination after export
- `--validate` — Run pre-export validation before copying

#### `info` — Display generation manifest

```bash
foundry-cli info ./generated-projects/my-proj
```

Shows project name, generation timestamp, and per-stage file counts.

#### `diff` — Display diff report

```bash
foundry-cli diff ./generated-projects/my-proj
```

Shows the diff report comparing the current generation against any previous run.

---

## The Library

Foundry ships with a built-in library (`ai-team-library/`) containing a comprehensive set of building blocks ready to use.

### Personas (13)

Each persona includes four components: `persona.md` (identity + principles), `outputs.md` (deliverables contract), `prompts.md` (invocation playbook), and `templates/` (forms the role fills out).

| Persona | Role |
|---|---|
| **team-lead** | Orchestration, scope control, task dependency management |
| **ba** | Requirements, user stories, acceptance criteria |
| **architect** | System design, ADRs, boundaries, contracts |
| **developer** | Implementation, testing, code quality |
| **tech-qa** | Verification, test charters, regression, traceability |
| **code-quality-reviewer** | Readability, maintainability, ship/no-ship decisions |
| **devops-release** | CI/CD, environments, deployments, rollbacks |
| **security-engineer** | Threat modeling (STRIDE), secure design review, hardening |
| **compliance-risk** | Regulatory constraints, auditability, evidence planning |
| **researcher-librarian** | Research memos, decision matrices, source logs |
| **technical-writer** | READMEs, runbooks, onboarding, ADR summaries |
| **ux-ui-designer** | User flows, wireframes, component specs, accessibility |
| **integrator-merge-captain** | Integration plans, conflict resolution, release notes |

### Tech Stacks (11)

Each stack contains convention docs covering best practices, testing strategies, security patterns, and tooling.

| Stack | Focus |
|---|---|
| **python** | Python conventions, packaging, testing, security |
| **python-qt-pyside6** | Qt/PySide6 desktop app patterns |
| **react** | React conventions, state management, accessibility |
| **typescript** | TypeScript conventions, type safety, tooling |
| **node** | Node.js backend, API design, testing |
| **java** | Java conventions, architecture, testing |
| **dotnet** | .NET architecture, conventions, testing |
| **sql-dba** | Database design, query optimization, migrations |
| **devops** | CI/CD pipelines, infrastructure, monitoring |
| **security** | Security practices, threat modeling, hardening |
| **clean-code** | Cross-cutting code quality principles |

### Hook Packs (5)

Hook packs define safety guardrails for generated projects.

| Hook Pack | Purpose |
|---|---|
| **hook-policy** | Base policy document defining posture levels |
| **pre-commit-lint** | Enforce formatting and lint checks before commits |
| **post-task-qa** | Quality gate after task completion |
| **security-scan** | Security scanning policies |
| **compliance-gate** | Regulatory compliance checks |

### Claude Code Integration

The library also includes **16 commands** and **16 skills** for Claude Code, covering operations like `compile-team`, `seed-tasks`, `scaffold-project`, `review-pr`, `threat-model`, `release-notes`, and more.

### Library Templates with Jinja2

Library markdown files support Jinja2 template variables that get rendered at compile time:

- `{{ project_name }}` — The project name from the composition spec
- `{{ stacks | join(", ") }}` — Comma-separated list of selected stacks
- `{{ strictness }}` — The persona's strictness setting
- `{{ slug }}` — The project slug

Invalid Jinja2 syntax is handled gracefully — the raw text is preserved rather than crashing.

---

## Generated Project Structure

When Foundry generates a project, it creates a self-contained directory with this structure:

```
my-project/
  CLAUDE.md                          # Project entry point for Claude Code
  README.md                          # Basic project readme
  .claude/
    agents/                          # Sub-agent definitions (one per persona)
      team-lead.md
      developer.md
      ...
    skills/                          # Project-specific skills
    commands/                        # Project-specific commands
    hooks/                           # Hook policy files
  ai/
    context/
      project.md                     # Project overview, team, stacks, conventions
      stack.md                       # Stack context summary
      decisions.md                   # Architecture decision records
    team/
      composition.yml                # The authoritative project spec
    generated/
      members/                       # Compiled team member prompts
        team-lead.md                 # Persona + stack + context merged
        developer.md
        ...
      manifest.json                  # Generation metadata and file manifest
      diff-report.md                 # Changes vs previous generation (if enabled)
    outputs/
      team-lead/                     # Output directory per role
        README.md
      developer/
        README.md
      ...
    tasks/
      seeded-tasks.md                # Starter task list with dependency waves
```

### What Each Part Does

- **CLAUDE.md** — The first file Claude Code reads. Contains project context, team members, stacks, hooks posture, and directory layout.
- **.claude/agents/** — Thin wrappers that point to the full compiled prompts in `ai/generated/members/`. Claude Code uses these as sub-agent definitions.
- **ai/generated/members/** — The compiled team member prompts. Each file merges the persona's identity, outputs contract, invocation prompts, relevant stack conventions, and project context into a single comprehensive prompt.
- **ai/team/composition.yml** — The full composition spec, preserved in the project for traceability.
- **ai/outputs/** — Per-role output directories where each agent writes its deliverables.
- **ai/tasks/seeded-tasks.md** — Starter task list following a wave-based dependency model: BA first, then Architect, then Dev, then QA — with parallel lanes for Security, DevOps, Code Quality, and Docs.

---

## Pipeline Stages

Foundry uses a deterministic pipeline with named stages:

| Stage | Verb | What It Does |
|---|---|---|
| **Validate** | check | Verifies composition completeness, library references, template paths, stack/persona existence |
| **Scaffold** | create | Builds the directory structure: CLAUDE.md, .claude/agents/, ai/context/, ai/outputs/, ai/tasks/ |
| **Compile** | generate | Merges persona + stack + project context into compiled member prompts via Jinja2 rendering |
| **Seed** | populate | Creates starter task lists with wave-based dependencies across roles |
| **Export** | handoff | Copies/moves the project to its final location, optionally runs `git init` |

Each stage produces a `StageResult` recording which files were written and any warnings encountered. These results are aggregated into a `GenerationManifest` stored at `ai/generated/manifest.json`.

### Validation Strictness

Three levels control how validation issues are treated:

| Level | Behavior |
|---|---|
| **light** | Only fatal errors block generation |
| **standard** | Errors block; warnings are reported but don't block |
| **strict** | All warnings are promoted to errors |

---

## Data Contracts

Foundry's behavior is driven by three core data structures, all defined as Pydantic models.

### CompositionSpec (`composition.yml`)

The authoritative project specification produced by the wizard or composition editor.

```yaml
project:
  name: "My Project"
  slug: "my-project"
  output_root: "./generated-projects"
  output_folder: "my-project"

stacks:
  - id: python
    order: 10
  - id: react
    order: 20

team:
  personas:
    - id: team-lead
      include_agent: true
      include_templates: false
      strictness: standard
    - id: developer
      include_agent: true
      include_templates: true
      strictness: standard
    - id: security-engineer
      include_agent: true
      include_templates: true
      strictness: strict

hooks:
  posture: hardened
  packs:
    - id: pre-commit-lint
      enabled: true
      mode: enforcing
    - id: security-scan
      enabled: true
      mode: enforcing

generation:
  seed_tasks: true
  write_manifest: true
  write_diff_report: true
```

### GenerationManifest (`manifest.json`)

A machine-readable record of every generation run, stored in the generated project.

```json
{
  "run_id": "2026-02-06T20-10-33Z",
  "library_version": "abc1234",
  "composition_snapshot": { ... },
  "stages": {
    "scaffold": { "wrote": ["CLAUDE.md", ".claude/agents/developer.md", ...], "warnings": [] },
    "compile": { "wrote": ["ai/generated/members/developer.md", ...], "warnings": [] },
    "seed": { "wrote": ["ai/tasks/seeded-tasks.md"], "warnings": [] }
  }
}
```

### LibraryIndex

A computed index built at runtime by scanning the library directory. Lists all available personas (with their files and templates), stacks (with their convention docs), and hook packs.

---

## Configuration

### Settings File

Foundry stores persistent settings at `~/.config/foundry/settings.json`:

| Setting | Description | Default |
|---|---|---|
| `library_root` | Path to ai-team-library | `./ai-team-library` |
| `workspace_root` | Default output directory for generated projects | `./generated-projects` |
| `editor_font_family` | Font for the markdown editor | `monospace` |
| `editor_font_size` | Font size for the editor | `12` |
| `editor_tab_width` | Tab width in the editor | `4` |
| `validation_strictness` | Default strictness level | `standard` |
| `git_auto_init` | Auto-initialize git in exported projects | `false` |

### Logging

Foundry writes structured logs to `~/.local/share/foundry/logs/foundry.log` with automatic rotation (5 MB max, 3 backups). The CLI uses file-only logging; the GUI additionally shows warnings on the console.

---

## Development

### Run tests

```bash
uv run pytest
```

The test suite includes 195 tests covering the full pipeline, data contracts, IO layer, validation, CLI, and service modules.

### Lint

```bash
uv run ruff check foundry_app/
```

### Build

```bash
uv build
```

Uses `hatchling` as the build backend.

### Project layout

```
foundry/
  pyproject.toml                       # Project metadata, dependencies, entry points
  README.md                            # This file
  CHANGELOG.md                         # Release history
  foundry_app/
    __init__.py                        # Version (1.0.0)
    __main__.py                        # python -m foundry_app support
    main.py                            # GUI entry point
    cli.py                             # CLI entry point (foundry-cli)
    core/
      models.py                        # Pydantic data contracts (15 model classes)
      settings.py                      # Persistent user preferences + validation
      logging.py                       # Structured logging with rotation
    services/
      generator.py                     # Pipeline orchestrator
      compiler.py                      # Meta-prompt compiler (Jinja2)
      scaffold.py                      # Directory structure creator
      seeder.py                        # Starter task generator
      validator.py                     # Pre/post-generation validation
      library_indexer.py               # Library directory scanner + cache
      export.py                        # Copy/move/git-init export service
      diff_reporter.py                 # Generation diff reports
    io/
      composition_io.py                # YAML/JSON read/write with error handling
    ui/
      main_window.py                   # Three-pane QMainWindow layout
      widgets/
        markdown_editor.py             # Source + preview editor widget
      screens/
        library/
          persona_browser.py           # Persona CRUD + file editor
          stack_browser.py             # Stack convention browser
          template_browser.py          # Cross-cut template search
          hooks_browser.py             # Hook pack manager
          workflows_browser.py         # Workflow doc browser
          skills_commands_browser.py   # Skills + commands two-tab view
        builder/
          wizard.py                    # 5-step project wizard
          composition_editor.py        # Synced form + YAML editor
          generate_screen.py           # Pipeline runner + manifest inspector
          export_screen.py             # Export with pre-flight checklist
        settings_screen.py             # Application preferences
        history_screen.py              # Recent projects + logs + manifests
  ai-team-library/                     # Bundled building-block library
    personas/                          # 13 role definitions
    stacks/                            # 11 tech-stack packs
    workflows/                         # Pipeline + task taxonomy docs
    claude/
      commands/                        # 16 Claude Code commands
      skills/                          # 16 Claude Code skills
      hooks/                           # 5 hook policy packs
  tests/                               # 195 tests across 16 files
  generated-projects/                  # Default output directory
  resources/
    icons/                             # App icons (placeholder)
```

---

## License

MIT License. See [pyproject.toml](pyproject.toml) for details.
