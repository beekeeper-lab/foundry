# Foundry Pipeline

The Foundry pipeline transforms a set of library building blocks -- personas, stacks, workflows, and templates -- into a fully scaffolded, ready-to-use Claude Code project folder. The pipeline runs six stages in sequence: **Select, Compose, Compile, Scaffold, Seed, Export**. Each stage validates its inputs, produces a well-defined artifact, and hands off to the next stage. If any stage fails validation, the pipeline halts with an actionable error before any file system changes are made.

## Pipeline Stages

### 1. Select

Pick the personas, tech stacks, and workflows that define the target project team.

- **Inputs:** The AI Team Library index (all available personas, stacks, workflows, and shared templates).
- **Actions:** The user (or a composition recipe) chooses which personas to include, which tech stacks apply, and which workflow documents to attach. Each selection is validated against the library index to confirm the item exists and its required files are present.
- **Outputs:** A validated selection set -- a list of persona IDs, stack IDs, and workflow references.
- **Validation:** Every selected ID must resolve to a directory in the library with the expected structure (e.g., each persona must have `persona.md`, `outputs.md`, `prompts.md`, and a `templates/` directory).

### 2. Compose

Build a composition spec that describes how the selected items combine.

- **Inputs:** The validated selection set from the Select stage.
- **Actions:** The composition spec is a YAML document (`composition.yaml`) that records the project name, selected personas with their roles and priorities, stack assignments, workflow references, and any overrides or custom settings. The spec may be hand-authored or generated through the Foundry UI.
- **Key fields:** `project_name`, `personas` (list with `id`, `role`, `priority`), `stacks` (list of stack IDs), `workflows` (list of workflow references), `output_dir`, `options` (compile flags, template overrides).
- **Outputs:** A `CompositionSpec` object conforming to the Pydantic data contract.
- **Validation:** Schema validation (all required fields present, correct types), referential integrity (every persona and stack ID exists in the library), and constraint checks (no duplicate personas, at least one persona selected).

### 3. Compile

Merge library source files into a unified `CLAUDE.md` that serves as the project's AI constitution.

- **Inputs:** The validated `CompositionSpec` and the library source files it references.
- **Actions:** For each selected persona, the compiler reads `persona.md`, `outputs.md`, and `prompts.md` and merges them into a single persona section. Stack `conventions.md` files are appended as skill sections. Workflow documents are included as reference appendices. Shared templates are cataloged. The merge follows a deterministic order: personas by priority, then stacks alphabetically, then workflows.
- **Outputs:** A compiled `CLAUDE.md` file containing all persona constitutions, stack conventions, workflow references, and a template index.
- **Validation:** The compiled output is checked for completeness (every selected persona has all three sections), no unresolved placeholders in structural content, and no duplicate section headings.

### 4. Scaffold

Create the target project folder structure.

- **Inputs:** The `CompositionSpec` and the compiled `CLAUDE.md`.
- **Actions:** The scaffolder creates the output directory and populates it with the standard project structure: `.claude/` configuration, the compiled `CLAUDE.md`, a `templates/` directory containing all persona-specific and shared templates, and placeholder directories for each persona's working outputs. The folder structure mirrors what a Claude Code session expects.
- **Outputs:** A complete directory tree on disk, ready for the seeding stage.
- **What gets created:**
  - `CLAUDE.md` -- the compiled AI constitution
  - `.claude/commands/` -- Claude Code slash commands
  - `.claude/skills/` -- skill definitions
  - `templates/` -- all selected persona and shared templates
  - `docs/` -- workflow reference documents
  - Per-persona output directories as defined in `outputs.md`

### 5. Seed

Generate initial task files that give the AI team a starting backlog.

- **Inputs:** The scaffolded project folder and a task-seeding plan (either from the composition spec or a default plan).
- **Actions:** The seeder reads the task-seeding plan -- a structured list of initial tasks with their assigned personas, priorities, and dependencies. For each task, it creates a task spec file from the `task-spec.md` template, pre-filled with the task's metadata. Tasks are organized by wave (parallel execution groups) and dependency chains.
- **Outputs:** A `tasks/` directory populated with initial task spec files, plus an updated seeding plan that records what was generated.
- **Validation:** Every seeded task references a persona that exists in the composition. Dependencies form a valid DAG (no cycles). Task IDs are unique.

### 6. Export

Package the generated project folder for use.

- **Inputs:** The fully scaffolded and seeded project folder.
- **Actions:** The exporter writes a `GenerationManifest` that records what was generated, when, from which composition spec, and with which library version. It performs a final integrity check across all generated files. Optionally, the output can be packaged as a zip archive for distribution.
- **Outputs:** The final project folder containing `CLAUDE.md`, templates, task seeds, workflow docs, Claude configuration, and the generation manifest. This folder is ready to open in Claude Code and start working.
- **Final structure:**
  - `CLAUDE.md` -- AI team constitution
  - `.claude/` -- commands, skills, hooks
  - `templates/` -- all templates
  - `tasks/` -- seeded task specs
  - `docs/` -- workflow and reference docs
  - `generation-manifest.json` -- build metadata

## Artifacts Produced

| Stage    | Primary Artifact               | Format         |
|----------|--------------------------------|----------------|
| Select   | Validated selection set        | In-memory list |
| Compose  | Composition spec               | YAML / Pydantic model |
| Compile  | Compiled CLAUDE.md             | Markdown       |
| Scaffold | Project folder structure       | Directory tree |
| Seed     | Task spec files                | Markdown files |
| Export   | Generation manifest            | JSON           |

## Error Handling

Each stage validates its inputs before performing any work. Failures are reported with enough context to diagnose and fix the problem.

- **Select:** Unknown persona or stack ID produces an error listing the invalid ID and available alternatives. Missing required files within a selected item (e.g., persona directory without `outputs.md`) produce a structural validation error.
- **Compose:** Schema validation errors report the specific field, expected type, and actual value. Referential integrity failures list the unresolved references.
- **Compile:** Missing source files halt compilation with the file path and the persona or stack that expected it. Duplicate section headings are flagged with their locations.
- **Scaffold:** File system errors (permissions, disk space, existing directory conflicts) are caught and reported before partial writes occur. The scaffolder operates atomically -- it either creates the full structure or rolls back.
- **Seed:** Circular dependencies are detected and reported with the cycle path. References to non-existent personas produce an error listing the invalid assignment.
- **Export:** Integrity check failures list every file that is missing or corrupted relative to what the manifest expected.

## Extension Points

The library is designed to grow. New building blocks can be added without modifying the pipeline code.

- **Adding a persona:** Create a new directory under `personas/` with `persona.md`, `outputs.md`, `prompts.md`, and a `templates/` directory containing at least one template. The library indexer will discover it automatically.
- **Adding a tech stack:** Create a new directory under `stacks/` with `conventions.md` and any additional skill files. Follow the naming convention of existing stacks.
- **Adding a shared template:** Place a new `.md` file in `templates/shared/`. It will be available to all compositions.
- **Adding a workflow:** Place a new `.md` document in `workflows/`. Reference it by filename in composition specs.
- **Custom commands and skills:** Add `.md` files to `claude/commands/` or `claude/skills/` to extend the Claude Code integration layer.
