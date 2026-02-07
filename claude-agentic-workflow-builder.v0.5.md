# Agentic Project Workflow Builder (Claude Code) — Persona + Stack → Team Members

**Version:** 0.3 (2026-02-06)

**Purpose:** This document is a *prompt + runbook* you can give to Claude Code to help you build an “agentic workflow builder” project: a meta-project that **builds projects**.  
It will guide you (via dialog) to define reusable **personas** and **tech-stack context packs**, then **compose them into standardized Claude Team members** (sub-agents) and produce a per-project `.claude/` setup (tasks, sub-agents, commands, skills, MCP tools, and safety hooks).

**Audience:** You (Gregg) working on both WarDog (local) and `terminal-1` (remote).  
**Date:** 2026-02-06 (update as needed)

---

## Reference links (read first for context)

- Claude Code Tasks guide (community writeup):  
  https://www.dplooy.com/blog/claude-code-tasks-complete-guide-to-ai-agent-workflow
- Claude Team updates (official):  
  https://claude.com/blog/claude-team-updates

---

# PART 0 — How to use this document

This document is split into two parts:

1) **CONTEXT** — the *why* and the target architecture (library layout, project layout, persona contracts, Foundry pipeline model).
2) **EXECUTION STEPS FOR CLAUDE** — a concrete, ordered checklist of *what to build* (folders, placeholder files, sample artifacts, the compiler, and the PySide6 Foundry app).

When you feed this to Claude, direct it to **follow the Execution Steps verbatim**, produce artifacts at the specified paths, and keep all placeholders small but well-structured.

# CONTEXT

## High-level outcome

At the end of this workflow, Claude should generate:

1. A **global library repo** (reusable across projects) containing:
   - Personas (stack-agnostic)
   - Tech stack context packs (role-agnostic)
   - Workflow templates (task taxonomy, definition of done, etc.)
   - Command templates, skill templates, MCP tool contracts, hook templates

2. A **project generator** that asks you questions and then emits a **new project folder** (or initializes a repo) with:
   - A complete `.claude/` directory for Claude Teams + Tasks + sub-agents
   - `/commands` and skill definitions (including “meta” commands)
   - MCP tool definitions / server call templates
   - Safety hooks/guardrails for GitHub + cloud (Azure/AWS) access
   - A starter app scaffold (React/Node by default, but can be Flutter/Python/etc.)
   - Optional local emulators (e.g., json-server) where appropriate

---

## Core concept: composable agents

### Naming: Foundry pipeline stages (builders)

This repo is both a **library** (reusable building blocks) and a **foundry** (a generator that uses those blocks to create many different projects).

To keep the steps consistent across stacks and projects, use these names:

1. **Select** (decisions): choose tech-stack packs + personas + optional extras  
2. **Compose** (configuration): write a project-local `composition.yml` describing your selections  
3. **Compile** (generation): generate *team member prompts* (sub-agent definitions) from persona + stack + project context  
4. **Scaffold** (filesystem): create the initial project folder structure (including `.claude/`, `ai/`, and optional starter app)  
5. **Seed** (tasks): create the initial Claude Task List “wave” (BA → Architect → Dev → Tech-QA)  
6. **Run** (orchestrate): let the lead session coordinate teammates via the shared task list  
7. **Export** (handoff): move the generated project folder out and initialize it as its own Git repo

You can think of **Select/Compose** as *builders* and **Compile/Scaffold/Seed** as *transformers*. Practically, “Foundry” is the umbrella name and each stage is a predictable verb.


You want “standard team members” generated from building blocks:

> **TeamMember(project)** = **Persona** (role behaviors) + **StackPack(s)** (tech best practices) + **ProjectContext** (domain + constraints)

### Example: Architect persona (stack-agnostic)
- Systems thinker (sees components + integration points)
- Uses design patterns; avoids anti-patterns
- Pragmatic decision maker (tradeoffs, not dogma)
- Deeply values clean code
- Expert at naming (classes, methods, modules, packages)
- Defines boundaries, contracts, and interfaces
- Leaves the codebase more understandable than before

### Example: React + Node stack pack (role-agnostic)
- React conventions, component design, state management patterns
- Node backend architecture, API design, logging, error handling
- Testing practices (unit/integration/e2e where applicable)
- Security basics (authn/authz boundaries, secret handling)
- Project structure conventions and tooling

The same Architect persona should be reusable across stacks:
- Architect + (React+Node)
- Architect + (Flutter+Firebase)
- Architect + (Python+FastAPI)

---

## The “meta prompt” pattern you’re building

You are building **prompts that build prompts**.

The workflow builder should:
1. Ask you for **persona definitions** (role values, behaviors, outputs).
2. Ask you for **stack context packs** (best practices, conventions, tooling).
3. Ask you for **project context** (domain, constraints, repo structure, environments).
4. Compile those into:
   - **Sub-agent prompts** (“team members”) with the correct combined context
   - **Project-specific commands** and **skills**
   - **Task templates** and an initial task list/backlog
   - **Hook policies** restricting what agents can do in GitHub/cloud

---

# PART 1 — Repository strategy & folder structure

## 1.1 Recommended structure on each machine

Use a consistent workspace root on both WarDog and `terminal-1`:

```
~/ws/
  library/                 # global reusable assets (git repo)
  projects/                # actual project repos
  tools/                   # scripts to scaffold and sync
  logs/
  artifacts/
  secrets/
```

### 1.2 Make the library a Git repo (source of truth)

Create a repo such as:
- `ai-team-library` (recommended name)

Clone it on both local and remote so you can edit anywhere and keep it synced.

### 1.3 Library internal structure (suggested)

This layout keeps the **role identity** (persona), the **deliverables contract** (outputs), the **invocation playbook** (prompts), and the **templates** (forms) separated—so you can reuse and evolve each part independently.

```
ai-team-library/
  personas/
    team-lead/
      persona.md
      outputs.md
      prompts.md
      templates/
        team-charter.md
        task-seeding-plan.md
        status-report.md

    ba/
      persona.md
      outputs.md
      prompts.md
      templates/
        epic-brief.md
        user-story.md
        acceptance-criteria.md
        bug-report.md

    architect/
      persona.md
      outputs.md
      prompts.md
      templates/
        adr.md
        design-spec.md
        review-checklist.md

    developer/
      persona.md
      outputs.md
      prompts.md
      templates/
        dev-design-decision.md
        pr-description.md
        implementation-notes.md

    tech-qa/
      persona.md
      outputs.md
      prompts.md
      templates/
        test-charter.md
        manual-test-case.md
        test-report.md
        traceability-matrix.md
        bug-report.md   # optional wrapper; canonical may live under BA

    code-quality-reviewer/
      persona.md
      outputs.md
      prompts.md
      templates/
        review-comment.md
        ship-no-ship-checklist.md
        suggested-diff.md

    devops-release-engineer/
      persona.md
      outputs.md
      prompts.md
      templates/
        pipeline-yaml.md
        release-runbook.md
        rollback-plan.md
        env-matrix.md

    security-engineer/
      persona.md
      outputs.md
      prompts.md
      templates/
        threat-model-stride.md
        mitigations.md
        security-test-checklist.md

    compliance-risk-analyst/
      persona.md
      outputs.md
      prompts.md
      templates/
        control-mapping.md
        evidence-plan.md
        audit-notes.md

    researcher-librarian/
      persona.md
      outputs.md
      prompts.md
      templates/
        research-memo.md
        decision-matrix.md
        source-log.md

    technical-writer/
      persona.md
      outputs.md
      prompts.md
      templates/
        readme.md
        onboarding.md
        runbook.md
        adr-index.md

    ux-ui-designer/
      persona.md
      outputs.md
      prompts.md
      templates/
        user-flow.md
        wireframes-text.md
        component-spec.md
        accessibility-checklist.md

    integrator-merge-captain/
      persona.md
      outputs.md
      prompts.md
      templates/
        integration-plan.md
        conflict-resolution-log.md
        release-notes.md
```


#### 1.3.1 Persona catalog (extended)

The four “core delivery” personas (BA, Architect, Developer, Tech-QA) are enough to ship features end-to-end.  
The personas below make the system **scale** (bigger codebases, more risk, more stakeholders) by adding specialized review, delivery, and documentation roles.

For each persona, keep the same three file types:

- `persona.md` — identity + operating principles + DoD + anti-patterns  
- `outputs.md` — deliverables contract + quality bar + *canonical template paths*  
- `prompts.md` — prompt starters + “input contract” + micro-workflows

**New personas**

- **Team Lead**: orchestration + scope control + task dependency management.  
  Outputs: team charter, task seeding plan, status reports, integration calls.

- **Code Quality Reviewer**: readability, maintainability, correctness, consistency.  
  Outputs: review comments, suggested diffs, “ship/no-ship” checklist.

- **DevOps / Release Engineer**: CI/CD, environments, deployments, secrets, rollbacks.  
  Outputs: pipeline YAML, infra changes, release runbooks, rollback plans.

- **Security Engineer / Threat Modeler**: STRIDE-style threat modeling, secure design review, hardening steps.  
  Outputs: threat model, mitigations, security test checklist.

- **Compliance / Risk Analyst**: regulatory constraints (medical/finance/etc.), auditability, evidence planning.  
  Outputs: control mapping, evidence plan, audit-friendly docs.

- **Researcher / Librarian**: gathers authoritative references, compares options, summarizes tradeoffs.  
  Outputs: short research memo, decision matrix, source log.

- **Technical Writer / Doc Owner**: turns decisions into crisp docs + onboarding material.  
  Outputs: READMEs, runbooks, ADR summaries, API docs.

- **UX / UI Designer**: IA, flows, interaction design, content design, accessibility.  
  Outputs: textual wireframes, component specs, UX acceptance criteria.

- **Integrator / Merge Captain**: stitches work together, resolves conflicts, ensures cohesive changes.  
  Outputs: integration plan, final patch set guidance, release notes.

> Cross-role reuse rule: when a persona “uses” another persona’s artifact (e.g., Tech-QA filing a bug), prefer **referencing the canonical template** instead of copying it.


#### File purposes (by type)

- **persona.md** — *Who the agent is.*  
  The role's mission, principles, definition of done, and anti-patterns. This should be fairly stable.

- **outputs.md** — *What the agent produces.*  
  A structured catalog of deliverables the role can create, with **quality bars** and **pointers to templates**.  
  Example entry: “User Story → template: templates/user-story.md → quality checklist → downstream consumers (Architect/Dev/Tech-QA).”

- **prompts.md** — *How to invoke the agent.*  
  Copy/paste prompt starters and mini-workflows for common tasks (e.g., “turn meeting notes into stories”, “review requirements for ambiguity”).  
  Prompts can reference templates explicitly, e.g., “Use personas/ba/templates/bug-report.md.”

- **templates/** — *The forms the agent fills out.*  
  Templates are role-owned, versionable artifacts (user story format, ADR format, test report format, etc.). Keep them as their own files so they can evolve without rewriting persona or prompts.

#### Cross-role template reuse (important)

Some outputs are **canonical** to one role but **used** by others (e.g., Tech-QA files bugs using the BA’s bug template).

Two good patterns:

1) **Canonical ownership + reference (recommended):**  
   Tech-QA prompt says: “Use the BA’s canonical bug template at personas/ba/templates/bug-report.md.”

2) **Optional wrapper template:**  
   Tech-QA keeps a small wrapper at personas/tech-qa/templates/bug-report.md that points to BA’s template and adds QA-only fields (regression scope, evidence links, test charter reference).

This avoids copy/paste drift while still letting each role add what it needs.


---


### 1.4 Project Foundry (generator) vs Library (building blocks)

**Library** (`ai-team-library/`) holds reusable building blocks: personas, stack packs, workflow patterns, skills/commands/hooks templates.

**Foundry** (this repo) is the *project generator* that:
- asks for a set of decisions (personas + tech stack + hook policy),
- composes/compiles prompts,
- scaffolds a ready-to-export project folder.

The output is a **self-contained subfolder** you can move elsewhere and `git init` into its own repository.


# PART 2 — Interactive build process (dialog or Python UI)


## 2.0 Bootstrap: make a repo “team-ready”

Before running agent teams, ensure the generated project contains:

- `CLAUDE.md` with project context and operating rules
- `.claude/agents/` with role sub-agents (generated)
- `.claude/skills/` and `.claude/commands/` for repeatable workflows
- `ai/context/` and `ai/outputs/` folders
- A `composition.yml` describing selected personas + stacks + hooks

Then the lead session can:
1) **Compile** agents from the composition
2) **Spawn** the team
3) **Seed** the initial task wave
4) Run orchestration through the shared task list


## 2.1 Claude’s role in this process

**Claude, you are the “Workflow Builder.”**  
You will drive a question-and-answer dialog, produce files, and keep everything consistent.

Constraints:
- Ask short, focused questions.
- After each section, produce an artifact (a file or folder update).
- Keep global library content **stack-agnostic** in personas and **role-agnostic** in stacks.
- Never store secrets in repositories.
- Enforce least-privilege guardrails for tools (GitHub/cloud).

## 2.2 Dialog Step A — Define personas (role building blocks)

For each persona (BA, Architect, Developer, Tech-QA), ask:

1. **Mission:** What does this role optimize for?
2. **Primary outputs:** What should this role deliver (docs, code, reviews, test charters)?
3. **Operating principles:** How should the role think and behave?
4. **Definition of done:** What “good” looks like for the role
5. **Anti-patterns to avoid:** What failures look like
6. **Tone:** How it communicates (direct, collaborative, safety-conscious)
7. **Decision rights:** What it can decide vs must escalate

**Output:** Create/extend:
- `personas/<role>/persona.md`
- `personas/<role>/outputs.md`
- `personas/<role>/prompts.md`

## 2.3 Dialog Step B — Define tech stack context packs (stack building blocks)

For each stack pack (React, Node, Flutter, Python, etc.), ask:

1. **Project structure conventions** (folders, naming)
2. **Coding standards** (linting, formatting, patterns)
3. **Architecture patterns** (component boundaries, API patterns)
4. **Testing strategy** (unit/integration/e2e)
5. **Local dev workflow** (scripts, dev server, env vars)
6. **Observability** (logging, tracing basics)
7. **Security basics** (auth boundaries, secret handling)
8. **Preferred tooling** (package manager, test runner, CI defaults)

**Output:** Create/extend:
- `stacks/<stack>/best-practices.md`
- `stacks/<stack>/conventions.md`
- `stacks/<stack>/testing.md`
- `stacks/<stack>/security.md` (as needed)

## 2.4 Dialog Step C — Define project context (project-specific inputs)

For a new project, ask:

1. Project name + org + repo name
2. Tech stack (frontend/backend/mobile, etc.)
3. Hosting targets (Azure/AWS/Hetzner/local)
4. Desired capabilities (auth, CRUD, APIs, etc.)
5. Data approach: json-server / sqlite / postgres / cloud DB
6. CI/CD expectations (if any)
7. Environment constraints (read-only cloud? branch-only in GitHub?)

**Output:** Create/extend in project repo:
- `ai/context/project.md`
- `ai/context/architecture.md` (initial)
- `ai/context/conventions.md` (initial)

---

# PART 3 — Composition: persona + stack → team members (sub-agents)

## 3.1 Composition file (project-local)

Create `ai/team/composition.yml` like:

```yaml
project:
  name: "example-project"
  task_list_id: "org-example-project"   # shared Claude task list id
members:
  - id: "ba"
    display_name: "Business Analyst"
    persona: "ba"
    stacks: ["react", "node"]
    owns_tags: ["requirements", "acceptance-criteria", "uat"]
  - id: "architect"
    display_name: "Software Architect"
    persona: "architect"
    stacks: ["react", "node"]
    owns_tags: ["architecture", "design-review", "naming", "boundaries"]
  - id: "dev"
    display_name: "Developer"
    persona: "developer"
    stacks: ["react", "node"]
    owns_tags: ["implementation", "refactor", "tests"]
  - id: "tech-qa"
    display_name: "Technical QA"
    persona: "tech-qa"
    stacks: ["react", "node"]
    owns_tags: ["verification", "test-charter", "regression"]
```

## 3.2 Compilation step (“meta prompt compiler”)

Claude should implement a compiler that reads:
- persona docs
- stack docs
- project context
- composition.yml

And generates:
- `ai/generated/members/<member-id>.md` — the fully expanded prompt for that member
- `ai/generated/task-templates/<member-id>/*.md` — how that role writes tasks
- `ai/generated/README.md` — what was generated and from which sources/versions

### Generated member prompt format (recommended)
Each member prompt should include:
- Role mission + outputs
- “How I work” principles
- Stack-specific do/don’t
- Project context summary
- Tool permissions (derived from hooks policy)
- How to interact with tasks (claim, update, create dependencies)
- A “handoff checklist” (what to leave behind for other agents)

---

# PART 4 — Claude Tasks: shared orchestration layer

## 4.1 Task list naming convention

### Required fields per task (project standard)

Each task should include these fields so Claude teammates can work independently without re-asking basic questions:

- **Owner role:** BA | Architect | Dev | Tech-QA
- **Goal:** one-sentence outcome
- **Inputs:** explicit file paths and/or pasted content
- **Outputs:** exact file paths to write (and which template to use)
- **Definition of Done:** checkable bullets
- **Dependencies:** blocked-by tasks or artifacts
- **Notes:** assumptions / risks / open questions


Use a stable task list ID per project (e.g., repo name):
- `org-repo` or `stonewaters-casetrac`

This allows multiple terminals/sub-agents to share the same task list.

## 4.2 Task taxonomy + routing

### Output routing (where artifacts live)

Standardize output locations so every teammate writes to predictable paths:

- BA → `ai/outputs/ba/` (stories, epics, bugs)
- Architect → `ai/outputs/architect/` (ADRs, design specs)
- Dev → `ai/outputs/dev/` (dev design decisions, PR notes)
- Tech-QA → `ai/outputs/tech-qa/` (test plans, test reports, traceability)

Your `outputs.md` files should point to both:
1) the **template path** (under `personas/<role>/templates/`) and  
2) the **project output path** (under `ai/outputs/<role>/`).


Your tasks should include:
- **Owner role** (ba/architect/dev/tech-qa)
- **Tags** (requirements, architecture, implementation, verification)
- **Dependencies** (blocked-by relationships)

Claude should generate tasks in waves:
1. BA: break epics → stories → AC
2. Architect: define boundaries + ADRs + review plan
3. Dev: implement + tests
4. Tech-QA: verify + file defects + confirm fixes

---

# PART 5 — /commands, skills, MCP tools, and safety hooks

## 5.1 /commands (project-local)

Create a `.claude/commands/` set that mirrors your workflow, for example:

- `/new-project` — asks questions and scaffolds the project + `.claude/`
- `/define-persona` — helps write persona docs in the library
- `/define-stack` — helps write stack pack docs in the library
- `/compile-team` — compiles composition.yml into generated member prompts
- `/seed-tasks` — creates initial task backlog in Claude Tasks

## 5.2 Skills (capability bundles)

Define reusable skills that sub-agents can call, such as:
- `create_story_with_ac`
- `generate_adr`
- `write_test_charter`
- `create_branch_and_commit` (but not merge)
- `read_azure_resources` (no mutation)
- `read_aws_resources` (no mutation)

Keep skills in:
- library: `claude/skills/common-skills.md`
- project: `.claude/skills/` (if Claude Code expects a folder)

## 5.3 MCP tool calls (controlled access)

You want MCP servers/tools with *least privilege*.

Examples:
- GitHub MCP: allow read + create branch + commit + PR creation, **deny merge**
- Azure MCP: allow read-only (list resource groups, app configs), **deny changes**
- AWS MCP: allow read-only (describe), **deny changes**

**Claude should propose tool contracts** and a policy file stating what’s allowed.

## 5.4 Hooks (guardrails)

Hooks differ per project, but the workflow builder should ask you:
- “Should agents be allowed to create branches?”
- “Allowed to commit?”
- “Allowed to open PRs?”
- “Allowed to merge? (default: NO)”
- “Allowed to run terraform apply? (default: NO)”
- “Allowed to modify Azure resources? (default: NO)”

Then generate per-project hook policy files.

**Goal:** Make it easy for you to enable read-only access while preventing destructive actions.

---

# PART 6 — Project scaffolding (starter app)

When generating a new project, default to scaffolding a minimal app that matches the selected stack.

## 6.1 React + Node default scaffold


## 6.2 Project Foundry CLI/UI (Python): generate a new project folder

### Purpose
A local **Python UI/CLI** collects the decisions you would otherwise gather through a chat dialog and then generates a project folder under `./generated-projects/<name>/`.

The user can then:
1. Review/edit the generated folder
2. Move it to a new location
3. Run `git init` (or create a remote and push)

### Inputs (what the UI asks for)
- **Project identity**: name, description, repo slug, primary language
- **Tech stack decisions**: pick one or more stack packs (e.g., `react`, `node`, `dotnet`, `python-fastapi`, `flutter-web`)
- **Team personas**: which role agents to include (e.g., Team Lead, BA, Architect, Dev, Tech-QA, Security, DevOps, Code Quality Reviewer, etc.)
- **Hooks policy**: which guardrails are enabled (security checks, no-secrets, licensing, “stop-the-line” rules)
- **Scaffold option**: docs-only, minimal starter, or full starter app template

### Outputs (what it generates)
- `CLAUDE.md` (project entry context)
- `.claude/agents/*` (generated sub-agent definitions per persona)
- `.claude/skills/*` and `.claude/commands/*` (starter automation: compile, seed, status)
- `ai/context/*` (project-local context docs)
- `ai/outputs/*` (output routing folders per role)
- `ai/generated/*` (traceability: what was compiled from what)
- Optional starter app scaffold (e.g., React+Node)

### Suggested implementation layout (inside this repo)
```text
foundry/
  app.py                          # UI entry point (Textual/Typer/Inquirer/etc.)
  wizard/
    steps.py                       # Select → Compose → Hooks → Scaffold → Seed
  generators/
    scaffold.py                    # filesystem + starter app templates
    compile_prompts.py             # persona + stacks + project context → agents
    seed_tasks.py                  # create initial task list wave definitions
  templates/
    project/
      CLAUDE.md.j2
      composition.yml.j2
      ai/context/project.md.j2
      .claude/commands/compile-team.md.j2
      .claude/commands/seed-tasks.md.j2
    starter-apps/
      react-node/
      python-fastapi/
      flutter-web/
generated-projects/
  <project-name>/
```

### Why a UI (vs “just Claude”)
Claude can absolutely guide the dialog, but the UI gives you:
- repeatability (same questions every time),
- fast selection (menus for stacks/personas),
- a clean, exportable folder without manual copy/paste.

Claude’s job then shifts to: **fill in the details** *inside* the generated structure via tasks.



- Frontend: React app skeleton
- Backend: Node API skeleton
- Local emulation: `json-server` (if it fits)
- A minimal README explaining:
  - how to run locally
  - how to run tests
  - where AI context lives (`ai/` and `.claude/`)

## 6.2 Alternate scaffolds

- Flutter app skeleton (mobile-first)
- Python app skeleton (FastAPI or CLI tool)
- Other (ask during project context dialog)

---

# PART 7 — Deliverable: the “new project” output folder

The workflow builder should produce a folder like:

```
projects/<org>/<repo>/
  .claude/
    commands/
    skills/
    mcp/
    hooks/
    team/                # generated member prompts, composition, policies
    tasks/               # templates and guidance
  ai/
    context/
    team/
    tasks/
    generated/
    imports/             # (vendor, submodule, or symlink)
  app/                   # (if scaffolded)
  README.md
```

---

# PART 8 — How Claude should run this with you (scripted steps)

When you start the workflow builder session, Claude should:

1. Confirm workspace paths (WarDog vs terminal-1)
2. Confirm library repo presence and cleanliness (git status)
3. Ask if you are:
   - defining personas
   - defining stack packs
   - creating a new project
4. If creating a new project:
   - gather project requirements
   - generate composition.yml
   - compile member prompts
   - generate `.claude/` folder
   - scaffold app skeleton
   - seed initial tasks
5. Summarize what it wrote/changed and where

---

# Suggested first run (quick start)

1) Create `ai-team-library` repo and put it in `~/ws/library/ai-team-library`  
2) Define 4 personas: BA, Architect, Developer, Tech-QA  
3) Define 2 stack packs: React, Node  
4) Create your first “project generator” run for a sample project  
5) Validate:
   - Sub-agents read their prompts and behave consistently
   - Task list is shared across terminals
   - Hook policies prevent merging/changing cloud resources

---

## Notes & constraints

- Prefer **least privilege**: read-only cloud access unless explicitly enabled.
- Prefer “branch + PR” workflows; avoid direct merges by agents.
- Never store secrets in repos; use `~/ws/secrets` or a secrets manager.
- Keep “global library” reusable; keep project-specific deviations local.

---

## What to ask me next (so we can iterate)

If you want to iterate on this doc, ask Claude to:
- Propose the exact file formats expected by Claude Code for `.claude/commands`, skills, and hooks in your environment
- Draft the initial Architect persona and React/Node stack packs
- Implement the compiler that generates `ai/generated/members/*.md`
- Write the `new-project` workflow command as a guided interview


# EXECUTION STEPS FOR CLAUDE

> Goal: implement **Foundry** as a reusable *project factory* that (a) manages the library of building blocks and (b) generates a new project folder that can be moved out and initialized as its own Git repo.

## Step 1 — Read inputs and set working assumptions
1. Read this workflow builder doc end-to-end.
2. Read the complementary GUI design doc: `foundry-gui-design.v0.1.md` (it will be provided alongside this doc).
3. Assume **Qt for Python (PySide6)** is the GUI framework.
4. Assume the library is a Git repo named `ai-team-library/` and Foundry is a separate repo (or a folder within a mono-repo) that can generate projects using that library.

## Step 2 — Create the Foundry repository skeleton
Create a new repo root with this minimal structure:

```text
foundry/
  README.md
  pyproject.toml
  foundry_app/
    __init__.py
    main.py
    ui/
      __init__.py
    core/
      __init__.py
    io/
      __init__.py
    services/
      __init__.py
  resources/
    icons/
  docs/
    workflow-builder.md              # copy of this document (or link)
    foundry-gui-design.md            # copy of the GUI design doc (or link)
  generated-projects/                # default output location for new projects
```

Populate placeholder Python files with minimal runnable scaffolding (imports, main entry, TODOs).

## Step 3 — Create the library repository skeleton (building blocks)
Create (or update) `ai-team-library/` with the structure below. Ensure all folders exist and each required markdown file exists (even if placeholder).

```text
ai-team-library/
  personas/
    team-lead/
      persona.md
      outputs.md
      prompts.md
      templates/
        status-report.md
        task-seeding.md
    ba/
      persona.md
      outputs.md
      prompts.md
      templates/
        epic-brief.md
        user-story.md
        acceptance-criteria.md
        bug-report.md
    architect/
      persona.md
      outputs.md
      prompts.md
      templates/
        adr.md
        design-spec.md
        review-checklist.md
    developer/
      persona.md
      outputs.md
      prompts.md
      templates/
        dev-design-decision.md
        pr-description.md
        implementation-notes.md
    tech-qa/
      persona.md
      outputs.md
      prompts.md
      templates/
        test-charter.md
        manual-test-case.md
        test-report.md
        traceability-matrix.md
    code-quality-reviewer/
      persona.md
      outputs.md
      prompts.md
      templates/
        review-report.md
        ship-no-ship-checklist.md
    devops-release/
      persona.md
      outputs.md
      prompts.md
      templates/
        pipeline-yaml.md
        release-runbook.md
        rollback-plan.md
    security-engineer/
      persona.md
      outputs.md
      prompts.md
      templates/
        threat-model.md
        mitigations.md
        security-test-checklist.md
    compliance-risk/
      persona.md
      outputs.md
      prompts.md
      templates/
        control-mapping.md
        evidence-plan.md
        audit-notes.md
    researcher-librarian/
      persona.md
      outputs.md
      prompts.md
      templates/
        research-memo.md
        decision-matrix.md
    technical-writer/
      persona.md
      outputs.md
      prompts.md
      templates/
        readme.md
        runbook.md
        adr-summary.md
    ux-ui-designer/
      persona.md
      outputs.md
      prompts.md
      templates/
        user-flow.md
        component-spec.md
        ux-acceptance-criteria.md
    integrator-merge-captain/
      persona.md
      outputs.md
      prompts.md
      templates/
        integration-plan.md
        release-notes.md
        conflict-resolution-notes.md

  stacks/
    python/
      conventions.md
      testing.md
      packaging.md
      security.md
    react/
      conventions.md
      testing.md
      accessibility.md
      security.md
    node/
      conventions.md
      api-design.md
      testing.md
      security.md
    dotnet/
      conventions.md
      architecture.md
      testing.md
      security.md

  workflows/
    foundry-pipeline.md              # Select → Compose → Compile → Scaffold → Seed → Export
    task-taxonomy.md

  claude/
    commands/
      compile-team.md
      seed-tasks.md
      status-report.md
    skills/
      compile-team/SKILL.md
      seed-tasks/SKILL.md
      close-loop/SKILL.md
    hooks/
      hook-policy.md

  README.md
```

## Step 4 — Write *sample* content for key files (not just placeholders)
Create several “good enough” sample files so Claude has anchors.

Minimum samples to write with real content:
- `personas/team-lead/persona.md` — mission: orchestrate, enforce pipeline stages, keep outputs routed, resolve conflicts.
- `personas/team-lead/outputs.md` — status report, task plan, integration summary.
- `personas/architect/templates/adr.md` — short ADR template.
- `personas/security-engineer/templates/threat-model.md` — STRIDE-style template.
- `personas/devops-release/templates/release-runbook.md` — step-by-step release runbook template.
- `personas/code-quality-reviewer/templates/ship-no-ship-checklist.md` — checklist.
- `stacks/python/conventions.md` and `stacks/react/conventions.md` — minimal standards and toolchain assumptions.

Keep each sample under ~150 lines but complete and structured.

## Step 5 — Define the data contracts used by Foundry
Implement and document these artifacts:

1) **Composition spec** (project-local), stored at:
- `ai/team/composition.yml`

It must include:
- project identity
- selected stack packs
- selected personas
- selected hooks/policies
- generation options (include templates or reference library)

2) **Generation manifest** stored at:
- `ai/generated/manifest.json`

It must include:
- timestamp
- library version hash (git commit if available)
- inputs (composition)
- outputs (created files)
- warnings

3) **Library index cache** (optional, generated), stored at:
- `.foundry/cache/library_index.json`

It must list:
- available personas and their files
- available stack packs and their files
- template inventory

## Step 6 — Implement the “Compile” step (meta prompt compiler)
Implement a service that:
1. Reads `composition.yml`
2. Loads selected persona files (`persona.md`, `outputs.md`, `prompts.md`)
3. Loads selected stack pack docs
4. Loads project context docs (if present)
5. Produces compiled member prompt files into:
- `ai/generated/members/<persona>.md`

Compiled files must contain:
- role identity (persona)
- expected outputs (with template paths)
- invocation prompts
- stack constraints
- output routing rules

## Step 7 — Implement the project scaffold generator
Implement a generator that creates a new project folder under:
- `generated-projects/<project-name>/`

The generated project must include:

```text
<project>/
  README.md
  CLAUDE.md
  .claude/
    agents/
      <persona>.md                   # compiled or thin wrapper referencing ai/generated/members
    skills/
    commands/
    hooks/
  ai/
    context/
      project.md
      stack.md
      decisions.md
    team/
      composition.yml
    outputs/
      <role>/
    generated/
      members/
      manifest.json
```

Write placeholder markdown files for outputs folders (one per role) describing expected deliverables.

## Step 8 — Implement “Seed” step: generate a starter task list
Implement a task seeding routine that creates:
- `ai/tasks/seeded-tasks.md` (human-readable)
- (optional) a machine-readable tasks file Foundry can import/export

Seed tasks should follow the Task System Contract in this doc:
- include owner, input paths, output paths, DoD, dependencies
- default dependency wave: BA → Architect → Dev → Tech-QA
- include parallel lanes: Security, DevOps, Code Quality, Docs

## Step 9 — Build the PySide6 Foundry desktop app (GUI)
Follow the provided GUI design doc (`foundry-gui-design.v0.1.md`) and implement:

1) **Library Editor**
- open library root
- browse personas/stacks/templates
- edit markdown files with save + preview
- create new persona / new template
- validation panel

2) **Project Builder Wizard**
- identity → tech stack → personas → hooks → review
- writes `composition.yml`
- runs generator + compile + seed
- shows generation preview + warnings

3) **Generate + Export**
- open generated folder
- export/copy to destination
- optional: initialize git repo (run `git init`) if user chooses

## Step 10 — Validation rules (must implement)
Add validations for:
- required files exist for selected personas (persona/outputs/prompts)
- template paths referenced in outputs.md exist
- composition.yml is complete
- generated project has required entry points (`CLAUDE.md`, `.claude/agents/*`, `ai/team/composition.yml`)
- warn (not error) if optional stack docs missing

## Step 11 — Documentation outputs
Produce:
- `README.md` in Foundry repo explaining usage
- a short “Quickstart” section with:
  - open library
  - run wizard
  - generate project
  - move project folder out
  - `git init` and push

## Step 12 — Deliverables checklist
At completion, ensure:
- Foundry runs locally (`python -m foundry_app.main`)
- Library editor opens and edits persona files
- Wizard generates a project folder with correct structure
- Compiler emits compiled member prompts
- Seeded tasks are produced
- Manifest is written
- Docs explain how to export a generated project into its own repo
