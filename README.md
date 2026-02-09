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
- [AI Team & Beans Workflow](#ai-team--beans-workflow)
- [Skills & Commands Summary](#skills--commands-summary)
- [Skills & Commands Reference](#skills--commands-reference)
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

### Personas (14)

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

## AI Team & Beans Workflow

Foundry includes a built-in AI team collaboration framework that organizes work into **Beans** — discrete units of work (features, enhancements, bug fixes, or epics).

### The AI Team

Five core personas collaborate through a structured workflow:

| Persona | Agent | Responsibility |
|---------|-------|----------------|
| **Team Lead** | `.claude/agents/team-lead.md` | Orchestrates work, decomposes beans, assigns tasks, enforces quality gates |
| **BA** | `.claude/agents/ba.md` | Requirements, user stories, acceptance criteria |
| **Architect** | `.claude/agents/architect.md` | System design, ADRs, module boundaries |
| **Developer** | `.claude/agents/developer.md` | Implementation, refactoring, code changes |
| **Tech-QA** | `.claude/agents/tech-qa.md` | Test plans, test implementation, quality gates |

### Bean Lifecycle

```
New → Picked → In Progress → Done
```

1. **New** — A bean is created via `/new-bean` or `/backlog-refinement` and added to `ai/beans/_index.md`
2. **Picked** — The Team Lead claims the bean via `/pick-bean`, assigning ownership
3. **In Progress** — The Team Lead decomposes the bean into tasks via `/seed-tasks` and creates a feature branch. Personas execute tasks in dependency waves: BA → Architect → Developer → Tech-QA
4. **Done** — All acceptance criteria pass, tests are green, lint is clean, and the bean is merged

### Bean Directory Structure

```
ai/beans/
  _index.md                          # Backlog index — all beans in one table
  _bean-template.md                  # Template for new beans
  BEAN-001-feature-name/
    bean.md                          # Bean spec with metadata, acceptance criteria, telemetry
    tasks/
      01-ba-requirements.md          # Task files, one per assignment
      02-architect-design.md
      03-developer-implement.md
      04-tech-qa-verify.md
```

### Task Execution Flow

Each task follows this pattern:

1. Persona reads the task file and its inputs
2. Persona records the `Started` timestamp and begins work
3. Persona produces outputs in `ai/outputs/<persona>/`
4. Team Lead runs `/close-loop` to verify outputs against acceptance criteria
5. If pass: `/handoff` packages context for the next persona
6. If fail: task is returned with specific feedback
7. Task telemetry is recorded (duration, token usage)

### Telemetry

Every bean and task tracks timing and token consumption:

- **Bean level**: `Started`, `Completed`, `Duration` in the header metadata
- **Task level**: `Started`, `Completed`, `Duration`, `Tokens` (format: `12,450 in / 3,200 out`)
- **Summary**: Total tasks, total duration, total tokens in/out

### Git Branching Model

```
main ← (deploy) ← test ← (merge-bean) ← bean/BEAN-NNN-slug
```

- Every bean gets its own feature branch: `bean/BEAN-NNN-<slug>`
- Completed beans merge to `test` via `/merge-bean`
- `test` promotes to `main` via `/deploy` (creates a PR, runs tests, merges)
- No direct commits to `main`

### Parallel Execution

Use `/long-run --fast N` or `/spawn-bean --count N` to process multiple beans simultaneously:

- Each parallel worker gets an isolated git worktree at `/tmp/foundry-worktree-BEAN-NNN/`
- Workers run in separate tmux windows/panes
- A dashboard in the main window tracks progress via status files
- Completed beans are merged sequentially by the orchestrator

---

## Skills & Commands Summary

Foundry provides **22 skills** and **24 commands** for Claude Code automation. Skills contain the full implementation logic (in `.claude/skills/<name>/SKILL.md`). Commands are the slash-command triggers (in `.claude/commands/<name>.md`) that invoke skills.

### Quick Reference

| Command | Category | What It Does |
|---------|----------|-------------|
| `/backlog-consolidate` | Planning | Detect and resolve duplicates, overlaps, and contradictions across beans |
| `/backlog-refinement` | Planning | Turn raw ideas into well-formed beans through iterative dialogue |
| `/bean-status` | Planning | Display backlog summary grouped by status with optional task detail |
| `/build-traceability` | Quality | Map acceptance criteria to test cases; identify coverage gaps |
| `/close-loop` | Quality | Verify task outputs against acceptance criteria; record telemetry |
| `/compile-team` | Generation | Resolve persona/stack references; produce unified CLAUDE.md |
| `/deploy` | Deployment | Promote `test` → `main` (or current branch → `test`) via PR with tests and release notes |
| `/handoff` | Workflow | Package artifacts and context for the next persona in the wave |
| `/long-run` | Execution | Autonomous backlog processing — pick, decompose, execute, merge, loop |
| `/merge-bean` | Integration | Merge a bean's feature branch into `test` with conflict detection |
| `/new-adr` | Documentation | Create an Architecture Decision Record with options analysis |
| `/new-bean` | Planning | Create a new work unit in the beans backlog |
| `/new-dev-decision` | Documentation | Record a lightweight developer implementation decision |
| `/new-work` | Planning | Single entry point for bugs, features, chores, spikes, refactors |
| `/notes-to-stories` | Requirements | Transform unstructured notes into user stories with acceptance criteria |
| `/pick-bean` | Planning | Claim a bean from the backlog and create its feature branch |
| `/review-pr` | Quality | Structured code review covering readability, correctness, security |
| `/run` | Execution | Pull latest code and launch the desktop app |
| `/scaffold-project` | Generation | Create standard project folder structure from a composition spec |
| `/seed-tasks` | Planning | Decompose objectives into assignable tasks with dependencies |
| `/show-backlog` | Planning | Display the bean backlog in a concise table format |
| `/spawn-bean` | Execution | Spawn parallel tmux workers for concurrent bean processing |
| `/status-report` | Reporting | Generate a progress summary with blockers, velocity, and next steps |
| `/validate-config` | Quality | Check secrets hygiene, env vars, and config schemas |
| `/validate-repo` | Quality | Structural health check: folders, files, links, stack-specific tooling |

---

## Skills & Commands Reference

Detailed documentation for every skill and command, organized by category.

---

### Planning & Backlog Management

#### `/new-bean` — Create a New Bean

Creates a new bean in the project's beans backlog with the next sequential ID.

```
/new-bean "<title>" [--priority <level>]
```

**Options:**
- `--priority` — `Low`, `Medium` (default), or `High`

**What it does:**
1. Reads `_index.md` to determine the next available ID
2. Generates a slug from the title (kebab-case, max 50 chars)
3. Creates directory `ai/beans/BEAN-NNN-<slug>/` with `tasks/` subdirectory
4. Populates `bean.md` from the bean template
5. Appends a row to `_index.md`

**Produces:** Bean directory, `bean.md`, updated `_index.md`

---

#### `/backlog-refinement` — Refine Raw Ideas into Beans

Turns raw ideas, feature descriptions, or broad vision text into one or more well-formed beans through iterative dialogue.

```
/backlog-refinement <text> [--dry-run]
```

**Options:**
- `--dry-run` — Show proposed beans without creating them

**What it does:**
1. Analyzes raw text to identify distinct work units
2. Drafts bean proposals with working titles
3. Presents initial breakdown and asks clarifying questions
4. Iterates until user approves scope, priority, and acceptance criteria
5. Creates each bean via `/new-bean` in sequence

**Produces:** One or more `bean.md` files, updated `_index.md`, summary table

---

#### `/backlog-consolidate` — Clean Up the Backlog

Detects and resolves duplicates, scope overlaps, contradictions, missing dependencies, and merge opportunities across beans.

```
/backlog-consolidate [--status <status>] [--dry-run]
```

**Options:**
- `--status` — Filter beans: `New` (default), `open`, `all`, or any single status
- `--dry-run` — Show findings without applying changes

**What it does:**
1. Loads all target beans and Done beans as reference
2. Runs 8 analysis checks: duplicate detection, scope overlap, contradictions, missing dependencies, merge candidates, done duplication, dependency cycles, priority inconsistencies
3. Presents findings grouped by severity with evidence
4. Applies agreed changes (merge, delete, add dependency, rewrite scope)

**Produces:** Modified beans, deleted duplicates, updated `_index.md`, change log

---

#### `/pick-bean` — Claim a Bean for Execution

Updates a bean's status from `New` to `Picked` (or `In Progress`), assigning ownership to the Team Lead and creating the feature branch.

```
/pick-bean <bean-id> [--start]
```

**Options:**
- `--start` — Set status directly to `In Progress`, create feature branch, and record `Started` timestamp

**What it does:**
1. Resolves bean ID (accepts `BEAN-006`, `006`, or `6`)
2. Validates the bean is available (not locked by another agent)
3. Updates `bean.md` and `_index.md` with new status and owner
4. Ensures `test` branch exists locally
5. If `--start`: creates `bean/BEAN-NNN-<slug>` feature branch and records `Started` timestamp

**Produces:** Updated `bean.md`, updated `_index.md`, feature branch

---

#### `/bean-status` — View Backlog Dashboard

Displays the current state of the beans backlog grouped by status.

```
/bean-status [--filter <status>] [--verbose]
```

**Options:**
- `--filter` — Show only beans with this status: `new`, `picked`, `in-progress`, `done`, `deferred`
- `--verbose` — Include task-level detail, telemetry (duration, tokens) for active beans

**What it does:**
1. Reads `_index.md` and each bean's `bean.md`
2. Groups beans by status: In Progress, Picked, New, Deferred, Done
3. In verbose mode: parses task tables and telemetry sections
4. Highlights actionable items (beans ready to pick, ready to close, or blocked)

**Produces:** Formatted backlog summary with counts and actionable items

---

#### `/show-backlog` — Quick Backlog View

Displays the bean backlog in a concise table format with optional filtering.

```
/show-backlog [--status <status>] [--category <cat>]
```

**Options:**
- `--status` — Filter: `New`, `Picked`, `In Progress`, `Done`, `Deferred`, `open`, `all`
- `--category` — Filter: `App`, `Process`, `Infra`

**Produces:** Markdown table with bean ID, summary, and category; count totals

---

#### `/seed-tasks` — Decompose into Tasks

Generates an initial set of tasks from project objectives, assigns them to personas, and links dependencies.

```
/seed-tasks [objectives-file] [--max-tasks <n>] [--format <md|yaml>] [--dry-run]
```

**Options:**
- `--max-tasks` — Cap total tasks generated
- `--format` — Output format: `md` (default) or `yaml`
- `--persona-filter` — Only generate tasks for specific personas
- `--dry-run` — Show what would be generated without writing

**What it does:**
1. Parses project objectives into discrete goals
2. Maps goals to task categories using the task taxonomy
3. Decomposes into tasks scoped to a single work cycle
4. Assigns a primary persona per task
5. Links dependencies (blockers before dependents)
6. Priority-ranks with strict ordering (no ties)
7. Generates task files with acceptance criteria and telemetry fields (`Started`, `Completed`, `Duration`, `Tokens` initialized to `—`)

**Produces:** Task files, dependency graph (Mermaid), assignment summary

---

#### `/new-work` — Create Any Type of Work Item

Single entry point for bugs, features, chores, spikes, and refactors.

```
/new-work <type> "<goal>" [--urgency <level>] [--constraints <text>] [--no-seed]
```

**Options:**
- `--urgency` — `low`, `normal` (default), `high`, `critical`
- `--constraints` — Time, scope, or technical constraints
- `--areas` — Comma-separated affected components
- `--no-seed` — Create task spec without seeding tasks

**Type-specific behavior:**
- **feature**: Drafts a user story
- **bug**: Drafts a bug report
- **spike**: Creates a spike brief with timespan and success criteria
- **refactor**: Creates a refactoring brief with current/target state and risk assessment
- **chore**: No additional artifact

**Produces:** Task spec, type-specific BA artifact, seeded tasks, work summary

---

### Requirements & Documentation

#### `/notes-to-stories` — Convert Notes to User Stories

Transforms unstructured input (meeting notes, brainstorming, feature requests) into structured user stories.

```
/notes-to-stories <notes-file-or-text> [--template <path>] [--existing <dir>]
```

**Options:**
- `--template` — Custom story template
- `--existing` — Directory of existing stories for deduplication
- `--format` — `brief` or `full` (default)

**What it does:**
1. Identifies distinct features/requests in the input
2. Drafts stories in "As a / I want / So that" format
3. Defines testable acceptance criteria (binary pass/fail)
4. Identifies open questions with suggested answerers
5. Assesses risks and rates impact
6. Deduplicates against existing stories

**Produces:** User story files, summary, open questions, risk register

---

#### `/new-adr` — Create Architecture Decision Record

Creates a new ADR from a structured template with context, options analysis, and consequences.

```
/new-adr "<decision title>" [--context <text>] [--related <ids>]
```

**Options:**
- `--context` — Provide context inline instead of interactive prompt
- `--related` — Comma-separated story/task/issue IDs
- `--output` — Override ADR output directory

**What it does:**
1. Auto-assigns the next ADR number
2. Captures context and decision drivers
3. Documents at least two options with pros/cons
4. Records the chosen option with rationale and consequences
5. Updates ADR index if one exists

**Produces:** ADR file (`adr-NNN-slug.md`), index update

---

#### `/new-dev-decision` — Record Implementation Decision

Creates a lightweight developer decision record for implementation-level choices.

```
/new-dev-decision "<title>" [--context <text>] [--chosen <text>] [--tags <list>]
```

**Options:**
- `--context` — Why the decision was needed
- `--chosen` — What was decided and rationale
- `--alternatives` — Comma-separated alternatives considered
- `--tags` — Tags for categorization
- `--work` — Related work item ID

**Produces:** Decision file (`DD-NNN-slug.md`), log update

---

### Quality & Verification

#### `/close-loop` — Verify Task Completion

Verifies task outputs against acceptance criteria and records completion telemetry. The quality gate between task completion and handoff.

```
/close-loop <task-id>
```

**What it does:**
1. Loads the task spec and extracts each acceptance criterion
2. Confirms every claimed artifact exists and is non-empty
3. Evaluates each criterion as pass, fail, or partial with evidence
4. Runs automated quality checks (lint, tests, format checks)
5. If all pass: marks task `complete`, records `Completed` timestamp, computes `Duration`, prompts for token self-report
6. If any fail: marks task `returned` with specific, actionable failure descriptions

**Produces:** Verification report, updated task status, telemetry data

---

#### `/review-pr` — Structured Code Review

Performs a repeatable code review across six dimensions.

```
/review-pr [diff-or-pr] [--security-only] [--self-review] [--skip-checks]
```

**Options:**
- `--skip-checks` — Skip test and lint prerequisite checks
- `--self-review` — Self-review mode with author-facing language
- `--security-only` — Only run security checks

**Review dimensions:**
1. **Readability** — Naming, organization, comments
2. **Correctness** — Logic, null handling, race conditions, edge cases
3. **Maintainability** — Coupling, cohesion, abstraction levels
4. **Consistency** — Naming patterns, code organization, project conventions
5. **Test coverage** — New behavior has tests, tests are meaningful
6. **Security** — Injection, secrets, auth, OWASP Top 10

**Verdicts:** `ship`, `ship-with-comments`, `request-changes`

**Produces:** Review report with per-file, per-line findings

---

#### `/build-traceability` — Requirements-to-Tests Matrix

Maps acceptance criteria to test cases and identifies coverage gaps.

```
/build-traceability [--stories <dir>] [--tests <dir>] [--update <path>]
```

**Options:**
- `--stories` — Story files directory (default: `ai/outputs/ba/user-stories/`)
- `--tests` — Test files directory (default: `ai/outputs/tech-qa/`)
- `--update` — Update an existing matrix incrementally

**Produces:** Traceability matrix, coverage percentage, gap report with uncovered criteria and orphaned tests

---

#### `/validate-repo` — Structural Health Check

Runs a comprehensive health check on a Foundry project or any repo following the Foundry structure.

```
/validate-repo [project-dir] [--check-level structure|content|full] [--fix]
```

**Options:**
- `--check-level` — Depth: `structure`, `content`, or `full` (default)
- `--strict` — Treat warnings as errors
- `--fix` — Auto-fix simple issues

**Checks performed:**
- Expected directories exist and required files are present
- Agent completeness and output directory setup
- Broken internal links and manifest consistency
- Stack-specific tooling (pyproject.toml, package.json, pom.xml, etc.)
- Secrets exposure (.env files, hardcoded keys)

**Produces:** Validation report with pass/fail/warn per check, exit code

---

#### `/validate-config` — Secrets & Config Hygiene

Checks configuration hygiene and detects exposed secrets across the project.

```
/validate-config [project-dir] [--environments <list>] [--fix-gitignore]
```

**Options:**
- `--schema` — Config schema file for validation
- `--environments` — Comma-separated env names (e.g., `dev,staging,prod`)
- `--fix-gitignore` — Auto-add `.env` to `.gitignore` if missing

**What it checks:**
- Hardcoded API keys, passwords, connection strings, private keys
- `.env` files in `.gitignore` and `.env.example` presence
- Config schema completeness (required variables, types)
- Cross-environment consistency

**Produces:** Config report with severity-categorized findings and remediation guidance

---

### Workflow & Handoffs

#### `/handoff` — Create Persona-to-Persona Handoff

Packages artifacts, decisions, and context for the next persona in the dependency wave.

```
/handoff <from-persona> <to-persona> [--work <id>] [--notes <text>]
```

**Options:**
- `--work` — Related work item ID
- `--artifacts` — Comma-separated artifact paths (auto-detected if omitted)
- `--notes` — Free-form context

**Produces:** Handoff packet at `ai/handoffs/{from}-to-{to}-{work-id}.md` containing:
- Artifacts summary with one-liner per deliverable
- Decisions made with links to full records
- Assumptions (explicitly labeled)
- Next steps and expected outputs
- Risks and open questions
- "Start here" file pointers

---

#### `/status-report` — Generate Progress Summary

Produces a status report summarizing progress, blockers, velocity, and next steps.

```
/status-report [--format brief|full] [--cycle current|all] [--include-velocity]
```

**Options:**
- `--format` — `brief` or `full` (default)
- `--cycle` — Which cycle(s) to cover
- `--include-velocity` — Include velocity metrics (default: true)

**Report sections:** Summary, Completed Items, In Progress, Blocked Items, Decisions Made, Risks & Escalations, Next Period Plan

**Produces:** Status report at `ai/reports/status-{cycle}-{date}.md`

---

### Generation & Scaffolding

#### `/compile-team` — Assemble Team Configuration

Resolves persona/stack references from a composition spec and merges them into a unified CLAUDE.md.

```
/compile-team [composition-file] [--strict] [--dry-run] [--no-manifest]
```

**Options:**
- `--strict` — Treat warnings as errors
- `--dry-run` — Validate and report without writing
- `--no-manifest` — Skip writing manifest

**Produces:** Compiled CLAUDE.md, `manifest.json`, persona templates, validation report

---

#### `/scaffold-project` — Create Project Structure

Creates the standard project folder structure from a composition spec.

```
/scaffold-project [composition-file] [--output <path>] [--force] [--dry-run]
```

**Options:**
- `--output` — Override output directory
- `--force` — Overwrite existing files
- `--dry-run` — Show what would be created without writing

**Produces:** Full project structure including CLAUDE.md, README.md, `.claude/` tree, `ai/` tree, agent wrappers, context docs, composition snapshot

---

### Execution & Deployment

#### `/long-run` — Autonomous Backlog Processing

Puts the Team Lead into autonomous mode, processing beans from the backlog until none remain.

```
/long-run [--fast N] [--category <cat>]
```

**Options:**
- `--fast N` — Run N beans in parallel using tmux windows and git worktrees
- `--category` — Only process beans matching: `App`, `Process`, or `Infra`

**Sequential mode** (default): Pick → decompose → execute wave → verify → commit → merge → loop

**Parallel mode** (`--fast N`):
1. Selects up to N independent beans
2. Creates isolated git worktrees for each worker
3. Spawns tmux workers, each running a full Team Lead agent
4. Dashboard monitors progress via status files
5. Merges completed beans and spawns replacements
6. Exits when all workers done and no actionable beans remain

**Produces:** Task files, persona outputs, updated beans, git commits, merge results

---

#### `/spawn-bean` — Spawn Parallel Workers

Spawns one or more tmux workers, each running a Team Lead agent for a specific bean.

```
/spawn-bean              # Spawn 1 auto-pick worker
/spawn-bean 16           # Spawn 1 worker for BEAN-016
/spawn-bean --count 3    # Spawn 3 auto-pick workers
/spawn-bean 16 17 18     # Spawn 3 workers (one per bean)
```

**Options:**
- `--count N` — Number of workers to spawn
- `--wide` — Tile workers in panes within one tmux window

**Worker isolation:** Each worker gets its own git worktree at `/tmp/foundry-worktree-BEAN-NNN/` and reports progress via status files at `/tmp/foundry-worker-BEAN-NNN.status`.

**Produces:** Parallel bean processing with live dashboard, completion report

---

#### `/merge-bean` — Merge Feature Branch to Test

Safely merges a bean's feature branch into the `test` integration branch.

```
/merge-bean <bean-id> [--target <branch>]
```

**Options:**
- `--target` — Target branch (default: `test`)

**What it does:**
1. Validates bean status is `Done`
2. Checks out target branch and pulls latest
3. Merges with `--no-ff` to preserve merge history
4. On conflict: lists files, aborts merge, returns to feature branch
5. Pushes to remote

**Produces:** Merge commit on target branch, merge report

---

#### `/deploy` — Deploy via Pull Request

Promotes a source branch into a target branch via PR with full verification.

```
/deploy              # test → main (release)
/deploy test         # current branch → test (integration)
/deploy --tag v2.0.0 # test → main with version tag
```

**Options:**
- `target` — Target branch: `main` (default) or `test`
- `--tag` — Version tag for the merge commit (main only)

**What it does:**
1. Determines source/target — `main`: source is `test`. `test`: source is current branch.
2. Runs `uv run pytest` and `uv run ruff check` — stops if either fails
3. Builds release notes from bean commits
4. Shows summary and waits for single user approval
5. Creates PR via `gh pr create --base <target> --head <source>`
6. Merges PR, optionally tags
7. Deletes merged feature branches (main deploys only)
8. Syncs local target branch

**Produces:** Merged PR, deployment report with PR URL, branch cleanup (main only)

---

#### `/run` — Pull and Launch App

Pulls the latest code and launches the Foundry desktop app.

```
/run [branch]
```

**Options:**
- `branch` — Which branch to pull: `main` (default) or `test`

**Produces:** Running app window; after exit, restores original branch and stash

---

## Development

### Run tests

```bash
uv run pytest
```

The test suite includes 565+ tests covering the full pipeline, data contracts, IO layer, validation, CLI, and service modules.

### Lint

```bash
uv run ruff check foundry_app/
uv run ruff check foundry_app/ --fix   # Auto-fix
```

### Build

```bash
uv build
```

Uses `hatchling` as the build backend. Note: `packages = ["foundry_app"]` in `pyproject.toml` because the package name differs from the project name.

---

## Project Structure

```
foundry/
  pyproject.toml                       # Project metadata, dependencies, entry points
  README.md                            # This file
  CLAUDE.md                            # Claude Code project instructions
  foundry_app/
    __init__.py                        # Version (1.0.0)
    __main__.py                        # python -m foundry_app support
    main.py                            # GUI entry point
    cli.py                             # CLI entry point (foundry-cli)
    core/
      models.py                        # Pydantic data contracts
      settings.py                      # Persistent user preferences
      logging_config.py                # Structured logging with rotation
    services/
      generator.py                     # Pipeline orchestrator
      compiler.py                      # Meta-prompt compiler (Jinja2)
      scaffold.py                      # Directory structure creator
      seeder.py                        # Starter task generator
      validator.py                     # Pre/post-generation validation
      library_indexer.py               # Library directory scanner + cache
      asset_copier.py                  # Copies skills, commands, hooks
      safety_writer.py                 # settings.local.json generation
      overlay.py                       # Overlay engine for regeneration
      diff_reporter.py                 # Generation diff reports
    io/
      composition_io.py                # YAML/JSON read/write
    ui/
      main_window.py                   # Three-pane QMainWindow layout
      theme.py                         # Dark/light theme support
      icons.py                         # Icon management
      screens/
        builder/                       # Project generation wizard
          wizard_pages/                # 4-step wizard pages
        generation_progress.py         # Pipeline runner
        export_screen.py               # Export with pre-flight checklist
        history_screen.py              # Recent projects + logs
        library_manager.py             # Library browser
      widgets/
        branded_empty_state.py         # Empty state placeholder
        markdown_editor.py             # Source + preview editor
  ai-team-library/                     # Bundled building-block library (do not modify)
    personas/                          # 14 role definitions
    stacks/                            # 11 tech-stack packs
    workflows/                         # Pipeline + task taxonomy docs
    claude/
      commands/                        # Claude Code commands
      skills/                          # Claude Code skills
      hooks/                           # Hook policy packs
  ai/                                  # AI team workspace
    beans/                             # Work items (beans) with backlog index
    context/                           # Project context docs
    outputs/                           # Per-persona output directories
    handoffs/                          # Handoff packets between personas
  .claude/                             # Claude Code configuration
    agents/                            # 5 agent definitions
    skills/                            # 22 skill definitions
    commands/                          # 24 command definitions
    hooks/                             # Git/operation hooks
  tests/                               # 565+ tests across 16 files
  examples/                            # 4 example composition YAML files
  resources/
    icons/                             # App icons
```

---

## License

MIT License. See [pyproject.toml](pyproject.toml) for details.
