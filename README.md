# Foundry

**A project factory for AI-assisted software teams.**

Foundry is a desktop application and CLI that generates fully configured [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) project folders from reusable building blocks. It combines **personas** (role definitions like Architect, Developer, QA) with **tech-stack packs** (language/framework best practices) to produce self-contained project directories — complete with sub-agents, compiled team prompts, starter tasks, and safety hooks.

Built with PySide6 (Qt for Python), Foundry provides both a visual desktop GUI and a headless CLI for batch automation.

---

### Overview

Foundry is a project factory for AI-assisted software teams. If you've ever set up a Claude Code project and spent hours writing agent prompts, defining team roles, configuring safety hooks, and scaffolding directory structures — only to do it all over again for the next project — Foundry eliminates that repetition entirely.

The core idea is simple: the knowledge that makes an AI agent effective — how a developer should write code, how an architect should design systems, how a QA engineer should verify work — doesn't change from project to project. What changes is the tech stack, the domain, and the team composition. Foundry treats these as independent building blocks. Pick your roles, pick your stacks, set your safety posture, and Foundry compiles everything into a ready-to-go project folder with fully wired agents, starter tasks, and quality gates. No prompt engineering required.

But Foundry isn't just a project generator — it's also the operating system for the team it creates. Work gets organized into "beans" (discrete units like features or bug fixes) that flow through a structured lifecycle: backlog, approval, decomposition into tasks, execution by specialized AI personas, verification, and merge. The whole process can run autonomously with a single command, or you can drive it step by step. It even syncs with Trello so stakeholders can manage priorities in a familiar tool while the AI team handles execution behind the scenes.

The result is that standing up a new AI-powered project goes from a day of boilerplate to a few minutes of choices. And once the project is running, the team collaboration patterns — handoffs, quality checks, telemetry, traceability — are already baked in rather than reinvented every time.

---

## Table of Contents

**Concepts & Architecture**
- [Why Foundry](#why-foundry)
- [Design Principles](#design-principles)
- [Architecture Overview](#architecture-overview)
- [Data Contracts](#data-contracts)
- [The Compilation Model](#the-compilation-model)
- [Generated Project Structure](#generated-project-structure)

**The Building Block Library**
- [Library Overview](#library-overview)
- [Personas](#personas-13)
- [Tech Stacks](#tech-stacks-11)
- [Hook Packs](#hook-packs-5)
- [Jinja2 Templating](#jinja2-templating)

**Execution Model**
- [AI Team & Beans Workflow](#ai-team--beans-workflow)
- [Trello Integration](#trello-integration)

**User Interfaces**
- [The Desktop GUI](#the-desktop-gui)
- [The CLI](#the-cli)

**Automation**
- [Skills & Commands Summary](#skills--commands-summary)
- [Skills & Commands Reference](#skills--commands-reference)

**Operations**
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Project Structure](#project-structure)
- [License](#license)

---

# Concepts & Architecture

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

## Design Principles

Foundry's architecture is guided by five core principles:

### Composition Over Configuration

Teams are assembled by combining independent building blocks — not by configuring a monolithic template. A persona knows nothing about tech stacks; a stack knows nothing about roles. Foundry merges them at compile time, producing combinations that neither component could anticipate on its own. This makes the library open for extension without modifying existing blocks.

### Self-Contained Output

Every generated project is a complete, standalone directory. There is no runtime dependency on Foundry, the library, or any external service. You can copy the output folder to another machine, `git init`, and start working with Claude Code immediately. The composition spec, generation manifest, and compiled prompts are all preserved inside the project for traceability and reproducibility.

### Deterministic Pipeline

The generation pipeline runs the same named stages in the same order every time: Validate, Scaffold, Compile, Copy Assets, Seed. Each stage produces a typed result recording exactly which files were written and any warnings encountered. The full run is captured in a machine-readable manifest, making it possible to diff generations, audit changes, and reproduce results.

### Contract-Driven Data Flow

Three Pydantic models define the system's data boundaries. The **CompositionSpec** is the input contract (what the user wants). The **LibraryIndex** is the capability contract (what the library offers). The **GenerationManifest** is the output contract (what was produced). Every service in the pipeline operates on these contracts — not on raw files or ad-hoc dictionaries.

### Human-in-the-Loop by Default

Foundry never assumes full autonomy. Beans require explicit human approval before execution. The `/long-run` command processes work autonomously but only touches pre-approved items. Trello integration imports cards as "Approved" because sprint backlog curation is the human gate. Every escalation point — scope ambiguity, conflicting requirements, architectural trade-offs — routes back to a human decision.

---

## Architecture Overview

Foundry is organized into four layers, each with a clear responsibility boundary:

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
│  ┌─────────────────────┐  ┌──────────────────────────┐  │
│  │   Desktop GUI        │  │   CLI (foundry-cli)      │  │
│  │   (PySide6/Qt)       │  │   (argparse)             │  │
│  └──────────┬──────────┘  └────────────┬─────────────┘  │
├─────────────┴──────────────────────────┴────────────────┤
│                    Service Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │Validator │ │Scaffolder│ │ Compiler │ │  Seeder    │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │Generator │ │Asset     │ │Safety    │ │Diff        │ │
│  │(orchestr)│ │Copier    │ │Writer    │ │Reporter    │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Core Layer                            │
│  ┌──────────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  Data Contracts   │  │  Settings   │  │  Logging   │ │
│  │  (Pydantic)       │  │  (JSON)     │  │  (rotating)│ │
│  └──────────────────┘  └─────────────┘  └────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    Library Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Personas │ │  Stacks  │ │  Hooks   │ │ Templates  │ │
│  │ (13)     │ │  (11)    │ │  (5)     │ │ (72)       │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**User Interfaces** provide two entry points — a desktop GUI for interactive composition and a CLI for scripting and CI/CD. Both delegate to the same service layer.

**Service Layer** contains the pipeline stages. The `Generator` orchestrates the flow: it calls the `Validator`, `Scaffolder`, `Compiler`, `AssetCopier`, `Seeder`, and `SafetyWriter` in sequence, collecting `StageResult` objects into a `GenerationManifest`. Each service is stateless and operates on the data contracts.

**Core Layer** defines the Pydantic data contracts (`CompositionSpec`, `LibraryIndex`, `GenerationManifest`), user settings, and structured logging with automatic rotation.

**Library Layer** is a filesystem-based content store. The `LibraryIndexer` scans it at runtime to build the `LibraryIndex`. The library is never modified by the application — it is treated as a read-only asset catalog.

---

## Data Contracts

Foundry's behavior is driven by three core data structures, all defined as Pydantic models in `foundry_app/core/models.py`.

### CompositionSpec — The Input Contract

The authoritative project specification, produced by the wizard or composition editor. Declares what the user wants: which personas, which stacks, what safety posture, and how to generate.

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

### GenerationManifest — The Output Contract

A machine-readable record of every generation run, stored in the generated project for traceability and diffing.

```json
{
  "run_id": "2026-02-06T20-10-33Z",
  "library_version": "abc1234",
  "composition_snapshot": { "..." : "..." },
  "stages": {
    "scaffold": { "wrote": ["CLAUDE.md", ".claude/agents/developer.md"], "warnings": [] },
    "compile": { "wrote": ["ai/generated/members/developer.md"], "warnings": [] },
    "seed": { "wrote": ["ai/tasks/seeded-tasks.md"], "warnings": [] }
  }
}
```

### LibraryIndex — The Capability Contract

A computed index built at runtime by scanning the library directory. Enumerates all available personas (with their component files and templates), stacks (with their convention docs), and hook packs. The GUI and CLI use this index to populate selection lists and validate composition references.

---

## The Compilation Model

Foundry uses a deterministic, staged pipeline to transform a composition spec into a generated project:

```
CompositionSpec ──→ Validate ──→ Scaffold ──→ Compile ──→ Copy Assets ──→ Seed ──→ GenerationManifest
                       │             │            │             │            │
                       ▼             ▼            ▼             ▼            ▼
                   Check refs    Create dirs   Merge prompts  Copy skills  Create tasks
                   & schemas     & CLAUDE.md   via Jinja2     & hooks      & dependencies
```

### Pipeline Stages

| Stage | Responsibility |
|---|---|
| **Validate** | Verifies composition completeness, checks that all referenced personas, stacks, and templates exist in the library, enforces strictness rules |
| **Scaffold** | Creates the directory structure: `CLAUDE.md`, `.claude/agents/`, `ai/context/`, `ai/outputs/`, `ai/tasks/` |
| **Compile** | Merges each persona's identity, outputs contract, and invocation prompts with the selected stack conventions and project context into a single compiled prompt per team member, rendered via Jinja2 |
| **Copy Assets** | Copies skills, commands, and hook packs from the library into the generated project's `.claude/` directory |
| **Seed** | Creates starter task lists with wave-based dependencies. Default wave: Developer → Tech-QA. BA and Architect included only when specific criteria are met. |

Each stage produces a `StageResult` recording which files were written and any warnings. These are aggregated into the `GenerationManifest` at `ai/generated/manifest.json`.

### Validation Strictness

Three levels control how validation issues are treated:

| Level | Behavior |
|---|---|
| **light** | Only fatal errors block generation |
| **standard** | Errors block; warnings are reported but don't block |
| **strict** | All warnings are promoted to errors |

---

## Generated Project Structure

Every generated project is self-contained — no runtime dependency on Foundry or the library. The structure follows a consistent layout:

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
      composition.yml                # The authoritative project spec (preserved)
    generated/
      members/                       # Compiled team member prompts
        team-lead.md                 # Persona + stack + context merged
        developer.md
        ...
      manifest.json                  # Generation metadata and file manifest
      diff-report.md                 # Changes vs previous generation
    outputs/
      team-lead/                     # Output directory per role
        README.md
      developer/
        README.md
      ...
    tasks/
      seeded-tasks.md                # Starter task list with dependency waves
```

### Component Roles

| Component | Purpose |
|---|---|
| **CLAUDE.md** | The first file Claude Code reads. Contains project context, team roster, stack conventions, hooks posture, and directory layout. |
| **.claude/agents/** | Thin wrappers that point to the full compiled prompts in `ai/generated/members/`. Claude Code loads these as sub-agent definitions. |
| **ai/generated/members/** | The compiled team member prompts. Each merges the persona's identity, outputs contract, invocation prompts, relevant stack conventions, and project context into a single comprehensive prompt. |
| **ai/team/composition.yml** | The full composition spec, preserved in the project for traceability. |
| **ai/outputs/** | Per-role output directories where each agent writes its deliverables. |
| **ai/tasks/seeded-tasks.md** | Starter task list following a wave-based dependency model: Developer → Tech-QA (default), with BA and Architect included when criteria are met. Parallel lanes for Security, DevOps, Code Quality, and Docs. |

---

# The Building Block Library

## Library Overview

Foundry ships with a built-in library (`ai-team-library/`) containing a comprehensive set of building blocks ready to use. The library is a read-only content store — Foundry never modifies it. It is designed to be extended by adding new personas, stacks, or hook packs without changing existing ones.

The library contains **207 markdown files** across **13 personas**, **11 tech stacks**, **72 templates**, and **5 hook packs**.

---

## Personas (13)

Each persona includes four component files that together define the role's complete behavior:

| File | Purpose |
|---|---|
| `persona.md` | Identity, operating principles, definition of done |
| `outputs.md` | Deliverables contract — what artifacts the role produces and where they go |
| `prompts.md` | Invocation playbook — how to invoke and interact with the role |
| `templates/` | Forms and checklists the role fills out during execution |

### Available Personas

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

---

## Tech Stacks (11)

Each stack contains convention docs covering best practices, testing strategies, security patterns, and tooling. Stacks are technology-specific — they know nothing about roles. At compile time, the relevant stack docs are injected into each persona's compiled prompt.

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

---

## Hook Packs (5)

Hook packs define safety guardrails that get installed into generated projects. Each pack supports three posture levels — **baseline**, **hardened**, and **regulated** — allowing teams to dial safety up or down based on their risk profile.

| Hook Pack | Purpose |
|---|---|
| **hook-policy** | Base policy document defining posture levels |
| **pre-commit-lint** | Enforce formatting and lint checks before commits |
| **post-task-qa** | Quality gate after task completion |
| **security-scan** | Security scanning policies |
| **compliance-gate** | Regulatory compliance checks |

---

## Jinja2 Templating

Library markdown files support Jinja2 template variables that get rendered at compile time, allowing library content to adapt to the specific project:

| Variable | Description |
|---|---|
| `{{ project_name }}` | The project name from the composition spec |
| `{{ stacks \| join(", ") }}` | Comma-separated list of selected stacks |
| `{{ strictness }}` | The persona's strictness setting |
| `{{ slug }}` | The project slug |

Invalid Jinja2 syntax is handled gracefully — the raw text is preserved rather than crashing the pipeline.

---

# Execution Model

## AI Team & Beans Workflow

Beyond project generation, Foundry provides a structured execution framework that organizes work into **Beans** — discrete units of work (features, enhancements, bug fixes, or epics) that flow through a managed lifecycle.

### The AI Team

Five core personas collaborate through a structured workflow, each backed by a Claude Code sub-agent:

| Persona | Agent | Responsibility |
|---------|-------|----------------|
| **Team Lead** | `.claude/agents/team-lead.md` | Orchestrates work, decomposes beans, assigns tasks, enforces quality gates |
| **BA** | `.claude/agents/ba.md` | Requirements, user stories, acceptance criteria |
| **Architect** | `.claude/agents/architect.md` | System design, ADRs, module boundaries |
| **Developer** | `.claude/agents/developer.md` | Implementation, refactoring, code changes |
| **Tech-QA** | `.claude/agents/tech-qa.md` | Test plans, test implementation, quality gates |

### Bean Lifecycle

Every bean progresses through four states:

```
Unapproved ──→ Approved ──→ In Progress ──→ Done
    │              │              │              │
    ▼              ▼              ▼              ▼
  Human          Human        Team Lead      All criteria
  creates        reviews      claims bean,    met, tests
  via /new-bean  & approves   decomposes      green, merged
                              into tasks      to test
```

1. **Unapproved** — A bean is created via `/new-bean` or `/backlog-refinement` and added to `ai/beans/_index.md`. It awaits human review and approval.
2. **Approved** — The user reviews the bean (e.g., in Obsidian via `/review-beans`) and changes its status to `Approved`, signaling it is ready for execution.
3. **In Progress** — The Team Lead claims the bean via `/pick-bean`, assigns ownership, creates a feature branch, and decomposes it into tasks. Default wave: Developer → Tech-QA. BA and Architect are included only when their criteria are met (see `ai/context/bean-workflow.md`). Tech-QA is mandatory for every bean.
4. **Done** — All acceptance criteria pass, tests are green, lint is clean, and the bean is merged to the `test` branch.

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

Each task follows a consistent pattern with built-in verification:

1. Persona reads the task file and its inputs
2. Persona records the `Started` timestamp and begins work
3. Persona produces outputs in `ai/outputs/<persona>/`
4. Team Lead runs `/close-loop` to verify outputs against acceptance criteria
5. If pass: `/handoff` packages context for the next persona in the wave
6. If fail: task is returned with specific, actionable feedback
7. Task telemetry is recorded (duration, token usage)

### Telemetry

Every bean and task tracks timing and token consumption for cost analysis and velocity tracking:

- **Bean level**: `Started`, `Completed`, `Duration` in the header metadata
- **Task level**: `Started`, `Completed`, `Duration`, `Tokens` (format: `12,450 in / 3,200 out`)
- **Summary**: Total tasks, total duration, total tokens in/out

### Git Branching Model

Foundry enforces a structured branching model with promotion gates:

```
main ← (deploy) ← test ← (merge-bean) ← bean/BEAN-NNN-slug
```

| Branch | Role |
|---|---|
| `bean/BEAN-NNN-<slug>` | Feature branch — one per bean, isolated work |
| `test` | Integration branch — completed beans merge here via `/merge-bean` |
| `main` | Release branch — `test` promotes here via `/deploy` (creates a PR, runs tests, merges) |

No direct commits to `main`. Every change flows through the bean lifecycle.

### Parallel Execution

Use `/long-run --fast N` or `/spawn-bean --count N` to process multiple beans simultaneously:

- Each parallel worker gets an isolated git worktree at `/tmp/foundry-worktree-BEAN-NNN/`
- Workers run in separate tmux windows/panes
- A dashboard in the main window tracks progress via status files
- Completed beans are merged sequentially by the orchestrator

---

## Trello Integration

Foundry integrates with Trello to bridge sprint planning with the agentic beans workflow. Cards in a Trello board flow automatically into the backlog as approved beans, get processed by the AI team, and move through Trello lists as work completes.

### Setup

Trello integration uses the [MCP Trello Server](https://www.npmjs.com/package/@delorenj/mcp-server-trello) and requires an API key and token.

#### 1. Get Your Trello API Key

1. Log in to Trello and visit the [Trello Power-Ups admin page](https://trello.com/power-ups/admin)
2. Create a new Power-Up (or integration) — give it any name (e.g., "Foundry MCP")
3. After creating it, you'll see your **API Key** on the Power-Up details page
4. Copy the API key — you'll need it for both the config file and for generating a token

#### 2. Generate a Trello Token

1. With your API key in hand, visit the following URL in your browser (replace `YOUR_API_KEY`):
   ```
   https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_API_KEY
   ```
2. Trello will prompt you to grant access — click **Allow**
3. Copy the token displayed on the resulting page

#### 3. Configure Foundry

Add the Trello MCP server to your `.mcp.json` file in the project root:

```json
{
  "mcpServers": {
    "trello": {
      "command": "npx",
      "args": ["-y", "@delorenj/mcp-server-trello"],
      "env": {
        "TRELLO_API_KEY": "your-api-key-here",
        "TRELLO_TOKEN": "your-token-here"
      }
    }
  }
}
```

Replace `your-api-key-here` and `your-token-here` with the values from steps 1 and 2.

> **Note:** The `.mcp.json` file is gitignored. Each developer configures their own credentials locally.

#### 4. Set Up Your Trello Board

Create a Trello board with these three lists (naming is flexible — underscores, hyphens, spaces, and case are all treated equivalently):

| List | Purpose |
|------|---------|
| **Sprint_Backlog** | Cards queued for the next development cycle |
| **In_Progress** | Cards currently being worked as beans |
| **Completed** | Cards whose beans have been merged |

Name the board to match your project directory (e.g., "Foundry") for automatic board selection, or use the `--board` flag to specify a board ID.

### How It Works

The Trello integration creates a bidirectional flow between Trello cards and the beans workflow:

```
Trello                              Foundry Beans
─────────────────                   ─────────────────
Sprint_Backlog ──── /trello-load ──→ Bean (Approved)
       ↓                                  ↓
  In_Progress        ← card moved ── /pick-bean (In Progress)
       ↓                                  ↓
                                     Team executes tasks
       ↓                                  ↓
   Completed         ← card moved ── /merge-bean (Done)
```

#### Importing Cards (`/trello-load`)

The `/trello-load` command pulls cards from the **Sprint_Backlog** list and creates approved beans:

1. Connects to Trello and auto-selects the board (matches project directory name, or uses `--board`)
2. Fetches all cards from the **Sprint_Backlog** list
3. For each card, reads the full description, checklists, and comments
4. Creates a bean with status **Approved** (sprint backlog cards are considered pre-vetted)
5. Maps card data to bean fields:
   - Card name becomes the bean title
   - Card description becomes the problem statement and goal
   - Checklist items become acceptance criteria
   - Label colors map to priority (red = High, yellow = Medium, green = Low)
   - A source reference linking back to the Trello card is added to the bean's Notes
6. Moves the card to **In_Progress** in Trello

Use `--dry-run` to preview what would be imported without creating beans or moving cards.

#### Automatic Sync in `/long-run`

The `/long-run` command automatically invokes `/trello-load` before processing beans (Phase 0.5: Trello Sync). This means:

- New sprint cards are imported at the start of every autonomous run
- After a bean is merged to `test`, the corresponding Trello card is moved to **Completed**
- The sync is best-effort — if Trello is unavailable or the sprint backlog is empty, processing continues normally

#### Card Completion

When a bean is merged (via `/merge-bean` or `/long-run`), Foundry checks the bean's Notes for a Trello source reference. If found, it automatically moves the matching card from **In_Progress** to **Completed** in Trello.

### Typical Workflow

1. **Product owner** creates cards in the Trello board's **Sprint_Backlog** list with descriptions, checklists, and labels
2. **Developer** runs `/trello-load` (or `/long-run` which calls it automatically) to import cards as approved beans
3. **AI team** processes beans through the standard lifecycle: pick, decompose, execute, verify, merge
4. **Trello board** updates automatically — cards move to **In_Progress** on import and **Completed** on merge
5. **Stakeholders** track progress in Trello without needing access to the codebase

---

# User Interfaces

## The Desktop GUI

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
| **New Project Wizard** | 4-step guided flow: Project, Team & Stack, Safety, Review & Generate |
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

The `foundry-cli` command provides headless access to the full generation pipeline for scripting and CI/CD integration. It shares the same service layer as the GUI — both interfaces produce identical output for the same inputs.

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

# Automation

## Skills & Commands Summary

Foundry provides a comprehensive set of Claude Code skills and commands that automate every phase of the development lifecycle. Skills contain the full implementation logic (in `.claude/skills/<name>/SKILL.md`). Commands are the slash-command triggers (in `.claude/commands/<name>.md`) that invoke skills.

### Quick Reference

| Command | Category | What It Does |
|---------|----------|-------------|
| `/backlog-consolidate` | Planning | Detect and resolve duplicates, overlaps, and contradictions across beans |
| `/backlog-refinement` | Planning | Turn raw ideas into well-formed beans through iterative dialogue |
| `/bean-status` | Planning | Display backlog summary grouped by status with optional task detail |
| `/build-traceability` | Quality | Map acceptance criteria to test cases; identify coverage gaps |
| `/close-loop` | Quality | Verify task outputs against acceptance criteria; record telemetry |
| `/compile-team` | Generation | Resolve persona/stack references; produce unified CLAUDE.md |
| `/deploy` | Deployment | Promote `test` to `main` (or current branch to `test`) via PR with tests and release notes |
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
| `/review-beans` | Planning | Generate MOC and open Obsidian for bean review and approval |
| `/spawn-bean` | Execution | Spawn parallel tmux workers for concurrent bean processing |
| `/status-report` | Reporting | Generate a progress summary with blockers, velocity, and next steps |
| `/telemetry-report` | Reporting | Generate telemetry summary across beans and tasks |
| `/trello-load` | Integration | Import Trello sprint backlog cards as approved beans |
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
- `--status` — Filter beans: `Unapproved` (default), `open`, `all`, or any single status
- `--dry-run` — Show findings without applying changes

**What it does:**
1. Loads all target beans and Done beans as reference
2. Runs 8 analysis checks: duplicate detection, scope overlap, contradictions, missing dependencies, merge candidates, done duplication, dependency cycles, priority inconsistencies
3. Presents findings grouped by severity with evidence
4. Applies agreed changes (merge, delete, add dependency, rewrite scope)

**Produces:** Modified beans, deleted duplicates, updated `_index.md`, change log

---

#### `/pick-bean` — Claim a Bean for Execution

Updates a bean's status from `Approved` to `In Progress`, assigning ownership to the Team Lead and creating the feature branch. Only `Approved` beans can be picked — `Unapproved` beans must be reviewed first.

```
/pick-bean <bean-id>
```

**What it does:**
1. Resolves bean ID (accepts `BEAN-006`, `006`, or `6`)
2. Validates the bean is `Approved` and not locked by another agent
3. Updates `bean.md` and `_index.md` with `In Progress` status and owner
4. Ensures `test` branch exists locally
5. Creates `bean/BEAN-NNN-<slug>` feature branch and records `Started` timestamp

**Produces:** Updated `bean.md`, updated `_index.md`, feature branch

---

#### `/bean-status` — View Backlog Dashboard

Displays the current state of the beans backlog grouped by status.

```
/bean-status [--filter <status>] [--verbose]
```

**Options:**
- `--filter` — Show only beans with this status: `unapproved`, `approved`, `in-progress`, `done`, `deferred`
- `--verbose` — Include task-level detail, telemetry (duration, tokens) for active beans

**What it does:**
1. Reads `_index.md` and each bean's `bean.md`
2. Groups beans by status: In Progress, Approved, Unapproved, Deferred, Done
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
- `--status` — Filter: `Unapproved`, `Approved`, `In Progress`, `Done`, `Deferred`, `open`, `all`
- `--category` — Filter: `App`, `Process`, `Infra`

**Produces:** Markdown table with bean ID, summary, and category; count totals

---

#### `/review-beans` — Review Beans in Obsidian

Generates a filtered Map of Content (MOC) linking to beans by status, then opens Obsidian for review. Edit bean files directly to approve, defer, or refine them.

```
/review-beans [--status <status>] [--category <cat>]
```

**Options:**
- `--status` — Filter: `unapproved` (default), `approved`, `in-progress`, `done`, `deferred`, `all`
- `--category` — Filter: `App`, `Process`, `Infra`

**What it does:**
1. Reads `_index.md` and applies filters
2. Generates `ai/beans/_review.md` with Obsidian wiki-links to matching beans
3. Opens Obsidian on `ai/beans/` (falls back to printing the path if Obsidian is not installed)

**Produces:** MOC file at `ai/beans/_review.md`, Obsidian launched

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
7. Generates task files with acceptance criteria and telemetry fields

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

#### `/trello-load` — Import Trello Sprint Backlog

Imports cards from a Trello board's Sprint_Backlog list and creates approved beans in the backlog.

```
/trello-load [--board <id>] [--dry-run]
```

**Options:**
- `--board` — Trello board ID (auto-selects by project name if omitted)
- `--dry-run` — Preview imports without creating beans or moving cards

**What it does:**
1. Connects to Trello MCP and verifies health
2. Auto-selects board (matches project directory name, or uses `--board`)
3. Finds Sprint_Backlog and In_Progress lists (flexible name matching)
4. For each card: reads description, checklists, comments
5. Creates a bean with `Approved` status, mapped fields, and Trello source reference
6. Moves the card to In_Progress in Trello

**Produces:** Approved beans in `ai/beans/`, updated `_index.md`, cards moved in Trello

---

#### `/long-run` — Autonomous Backlog Processing

Puts the Team Lead into autonomous mode, processing beans from the backlog until none remain.

```
/long-run [--fast N] [--category <cat>]
```

**Options:**
- `--fast N` — Run N beans in parallel using tmux windows and git worktrees
- `--category` — Only process beans matching: `App`, `Process`, or `Infra`

**Sequential mode** (default): Pick, decompose, execute wave, verify, commit, merge, loop.

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

# Operations

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

### Running Foundry

```bash
# Desktop GUI
uv run foundry

# CLI
uv run foundry-cli --help

# As a Python module
python -m foundry_app
```

### Dev dependencies (for running tests and linting)

```bash
uv sync --group dev
```

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

### Tech Stack

| Component | Technology |
|---|---|
| **Language** | Python 3.11+ (running 3.14.2) |
| **GUI Framework** | PySide6 (Qt for Python) |
| **Data Validation** | Pydantic |
| **Template Engine** | Jinja2 |
| **Config Format** | YAML (PyYAML) / JSON |
| **Build Backend** | hatchling |
| **Package Manager** | uv |
| **Linter** | ruff (line-length 100, target py311, select E/F/I/W) |
| **Tests** | pytest |

### Run tests

```bash
uv run pytest
```

The test suite covers the full pipeline, data contracts, IO layer, validation, CLI, and service modules.

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
  ai-team-library/                     # Bundled building-block library (read-only)
    personas/                          # 13 role definitions
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
    skills/                            # Skill definitions
    commands/                          # Command definitions
    hooks/                             # Git/operation hooks
  tests/                               # Test suite
  examples/                            # 4 example composition YAML files
  resources/
    icons/                             # App icons
```

---

## License

MIT License. See [pyproject.toml](pyproject.toml) for details.
