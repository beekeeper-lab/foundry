# Foundry GUI Design (Qt for Python / PySide6) — v0.1

This document defines the **WHAT** for the Foundry desktop app: screens, flows, data contracts, and file interactions.
It is meant to be paired with **Agentic Project Workflow Builder (v0.4)** and then fed to Claude for implementation.

---

## 1. Purpose

Foundry is a **desktop “project factory”** and **library editor** for agentic development.

It has two primary modes:

1. **Library Mode (Editor)**
   - Edit the building blocks that define how agentic teams work:
     - Personas (persona/output/prompt/templates)
     - Tech stacks (stack context modules)
     - Hooks policies (rules + templates)
     - Workflows, skills, commands
2. **Project Builder Mode (Generator)**
   - Collect a set of decisions (stack + personas + hooks)
   - Produce a **self-contained project folder** (scaffold + compiled sub-agents + starter tasks)
   - Allow the user to **export/move** that folder and initialize a new Git repo

---

## 2. Principles

- **Deterministic outputs**: given the same library + the same inputs, the generated project folder is the same.
- **Thin UI, strong contracts**: UI drives a `composition.yml` (or `composition.json`) spec and uses Foundry pipeline stages.
- **Library-first**: the library is the source of truth; generated content is derived.
- **Safe by default**: validate before write; show diffs; no destructive actions without review.
- **Human-editable artifacts**: everything generated is plain text and can be edited outside Foundry.

---

## 3. Supported Platform / Toolkit

- **Qt for Python (PySide6)**
- Cross-platform targets: Linux, macOS, Windows

---

## 4. The Foundry Pipeline (UI to Generation)

Foundry uses these stage names consistently (UI labels, logs, docs, and tasks):

1. **Select** – choose stacks, personas, policies
2. **Compose** – create/edit the project spec (`composition.yml`)
3. **Compile** – generate project-specific member prompts/sub-agent files from library + spec
4. **Scaffold** – create folder structure and baseline files
5. **Seed** – create initial task list templates / starter artifacts (optional)
6. **Export** – copy/move project folder out; optionally `git init`

Each stage produces a **log**, a **manifest of file writes**, and a **validation report**.

---

## 5. User Personas (end-users of Foundry)

- **Builder (You)**: curates library, generates projects frequently
- **Contributor**: edits templates/personas/stacks but doesn’t ship generator changes
- **Consumer**: uses wizard to generate a project and exports it to a new repo

---

## 6. Information Architecture (IA)

### 6.1 Primary Navigation (left sidebar)

- **Library**
  - Personas
  - Stacks
  - Templates (cross-cut view)
  - Hooks
  - Workflows
  - Skills/Commands
- **Project Builder**
  - New Project Wizard
  - Composition Editor
  - Generate
  - Export
- **History**
  - Recent projects
  - Generation logs
  - Diff/manifest viewer
- **Settings**
  - Paths (library root, workspace root)
  - Editor preferences
  - Validation strictness
  - Git integration options

### 6.2 Main Window Layout

**Three-pane, persistent layout**:

- **Left:** Navigation + search
- **Center:** List/detail view or wizard step
- **Right:** Inspector / Preview / Validation / Diff

Top toolbar: Open Library, Open Workspace, Save, Validate, Generate, Export, Settings.

---

## 7. Screen Designs (first pass)

### 7.1 Library → Personas

**Goal:** Create and maintain persona modules:
- `persona.md`
- `outputs.md`
- `prompts.md`
- `templates/*.md`

**Center Panel**
- Persona list (searchable)
- Buttons: New, Duplicate, Delete, Rename

**Detail Panel**
- File list for the persona
- Editor tabs:
  - Markdown editor (source)
  - Preview (rendered)
  - Validation (rules + warnings)
- Template management:
  - Create new template
  - Rename template
  - “Open referenced template” from outputs/prompts

**Validation Rules**
- `persona.md` exists (or is creatable)
- `outputs.md` points to templates that exist
- template filenames are kebab-case
- no absolute paths in template links; only repo-relative

---

### 7.2 Library → Stacks

**Goal:** Manage stack context modules (e.g., react, node, dotnet, python).

**Center Panel**
- Stack list (searchable)
- Buttons: New, Duplicate, Delete, Rename

**Detail Panel**
- File list inside stack folder
- Editor + preview + validation

**Suggested stack files (convention)**
- `overview.md`
- `conventions.md`
- `testing.md`
- `security.md`
- `ci-cd.md`
- `observability.md`

**Validation Rules**
- `overview.md` recommended
- ensure links are relative
- warn if stack modules overlap without ordering (e.g., two `security.md` of same scope)

---

### 7.3 Library → Hooks

**Goal:** Define policy packs and hook templates used in generated projects.

**Center Panel**
- Hook pack list (e.g., formatting, secrets, lint, commit-msg)
- Toggles:
  - enabled by default
  - advisory vs enforcing
- Preset dropdown:
  - baseline / hardened / regulated

**Detail Panel**
- Hook pack files (policy + templates)
- Hook explanation panel:
  - “what it enforces”
  - “why it exists”
  - “how to bypass / break-glass”

---

### 7.4 Project Builder → New Project Wizard (multi-step)

**Wizard Steps (minimum)**
1. **Identity**
   - Project name
   - Destination root
   - Generated folder name
   - Output mode:
     - generate under Foundry workspace
     - generate to external folder
2. **Tech Stack**
   - Multi-select stacks
   - Stack ordering (drag/drop)
   - “stack overrides” notes
3. **Team Personas**
   - Multi-select personas
   - For each persona:
     - include sub-agent file (yes/no)
     - include templates (yes/no)
     - strictness (light/standard/strict)
4. **Hooks & Policies**
   - Select hook packs
   - posture preset
   - enforcement mode
5. **Review & Generate**
   - Display planned tree
   - Display validation warnings
   - Generate button
   - Option: “open folder after generation”

**Wizard Output**
- A `composition.yml` file representing all selections.
- A preview of compiled member prompts before generation.

---

### 7.5 Project Builder → Composition Editor

**Goal:** Allow power editing of the project spec.

Two synchronized views:
- **Form view** (tables + toggles)
- **YAML view** (raw)

Right Inspector shows:
- computed outputs (resolved templates, resolved stacks)
- dependency graph preview (roles → outputs → tasks)
- warnings (missing persona files, missing templates)

---

### 7.6 Project Builder → Generate

**Goal:** Run the Foundry pipeline deterministically.

- Run stages: Compile → Scaffold → Seed
- Show:
  - stage progress
  - file write manifest
  - warnings/errors
- Provide:
  - “open generated folder”
  - “view manifest”
  - “view diff vs previous run”

---

### 7.7 Project Builder → Export

**Goal:** Move/copy a generated project into its own repo.

Actions:
- **Copy to…**
- **Move to…**
- Optional: `git init`
- Optional: write “first run” README
- Optional: create remote (not required; keep minimal)

Right Inspector:
- checklist:
  - project is self-contained
  - no symlinks back to library (unless user opted in)
  - licenses and readmes exist

---

### 7.8 Templates (cross-cut view)

**Goal:** A searchable list of all templates across personas.

- Filter by persona
- Filter by template type (bug, story, ADR, design spec, runbook, etc.)
- Quick preview + edit

---

## 8. Data Model (contracts)

Foundry’s UI edits and generation are driven by these core objects.

### 8.1 Library Index (computed)

A computed index created on app load:

```yaml
library_index:
  root: /path/to/ai-team-library
  personas:
    - id: ba
      files: [persona.md, outputs.md, prompts.md]
      templates: [user-story.md, acceptance-criteria.md, bug-report.md]
    - id: architect
      templates: [adr.md, design-spec.md]
  stacks:
    - id: react
      files: [overview.md, conventions.md, testing.md]
  hooks:
    - id: secrets-scan
      default_enabled: true
      mode: enforcing
```

### 8.2 Project Spec: `composition.yml` (authoritative)

This is the core contract produced by the wizard and edited in Composition Editor.

```yaml
project:
  name: "acme-widget"
  slug: "acme-widget"
  output_root: "/path/to/generated-projects"
  output_folder: "acme-widget"
  created_utc: "2026-02-06T00:00:00Z"

stacks:
  - id: react
    order: 10
  - id: node
    order: 20
  - id: azure
    order: 30
stack_overrides:
  notes_md: |
    Use Entra ID auth; prefer managed identities.

team:
  personas:
    - id: team-lead
      include_agent: true
      include_templates: false
      strictness: standard
    - id: ba
      include_agent: true
      include_templates: true
      strictness: standard
    - id: security-engineer
      include_agent: true
      include_templates: true
      strictness: strict

hooks:
  posture: hardened  # baseline|hardened|regulated
  packs:
    - id: formatting
      enabled: true
      mode: enforcing
    - id: secrets-scan
      enabled: true
      mode: enforcing

generation:
  seed_tasks: true
  write_manifest: true
  write_diff_report: true
```

### 8.3 Generation Manifest (produced each run)

A machine- and human-readable record of file operations.

```yaml
manifest:
  run_id: "2026-02-06T20-10-33Z"
  stages:
    compile:
      wrote:
        - "ai/generated/members/team-lead.md"
      warnings: []
    scaffold:
      wrote:
        - "CLAUDE.md"
        - ".claude/agents/team-lead.md"
      warnings: ["hooks pack formatting enabled but templates missing"]
    seed:
      wrote:
        - "ai/tasks/seeded/tasks.yml"
```

---

## 9. File System Interactions (what Foundry reads/writes)

### 9.1 Inputs

- Library root: `ai-team-library/`
- Optional Foundry workspace root: `generated-projects/` within Foundry repo

### 9.2 Outputs (generated project folder)

Minimum baseline:

```text
<project>/
  CLAUDE.md
  .claude/
    agents/              # compiled per-role sub-agent definitions
    skills/              # project skills
    commands/            # project commands (optional)
    hooks/               # project hook policy
  ai/
    context/
    outputs/
      ba/
      architect/
      developer/
      tech-qa/
    generated/
      members/
    tasks/
  README.md
```

### 9.3 Export guarantees

- Exported folder contains **no required dependency** on Foundry repo.
- Any library references must be **copied** (not symlinked) unless the user explicitly enables symlink mode.

---

## 10. Validation & Quality Gates (UI-level)

- **Pre-generation validation** (Wizard step 5)
  - ensure all selected personas exist
  - ensure required files exist or can be created
  - ensure template pointers resolve
  - ensure stacks exist and ordering has no duplicates
- **Pre-export validation**
  - project is self-contained
  - manifest exists
  - no unresolved links
- **“Ship/No-Ship” gating option**
  - allow the user to require green validation before enabling “Generate” or “Export”

---

## 11. Extensibility Requirements

Foundry must support:
- adding a new persona type without code changes (directory-driven)
- adding a new stack module without code changes
- new hook packs and policies without code changes
- additional wizard steps via config later (keep architecture modular)

---

## 12. Initial Acceptance Criteria (v0.1 GUI)

### Library Mode
- Open a library root and browse personas.
- Create a new persona folder with required files.
- Edit and save markdown files.
- Add/rename/delete templates for a persona.
- Preview markdown in-app (basic rendering acceptable).

### Project Builder Mode
- Wizard creates a valid `composition.yml`.
- “Generate” produces a project folder with baseline structure.
- Generate writes a manifest.
- Export can copy/move the folder.

### Non-goals for v0.1
- Visual wireframe drawing (textual wireframes only)
- GitHub remote creation
- Rich markdown rendering plugins (basic is fine)
- Background automation / scheduled runs

---

## 13. Suggested Foundry App Repo Structure (implementation hint)

This is the *recommended* structure for the Foundry codebase itself (separate from generated projects):

```text
foundry/
  app/
    main.py
    ui/
      main_window.py
      widgets/
      screens/
        library/
        builder/
    services/
      library_indexer.py
      composition_service.py
      generator_service.py
      validator_service.py
      export_service.py
    models/
      composition.py
      manifest.py
      library_index.py
  resources/
  tests/
  README.md
```

---

## 14. Notes for Claude Implementation

- Use PySide6 `QMainWindow` + `QSplitter` + `QStackedWidget`.
- Prefer a “service layer” for file IO and generation; UI should call services.
- Make all write operations go through a single `write_file()` function that can log to the manifest.
- Keep `composition.yml` as the single source of truth for generation.

