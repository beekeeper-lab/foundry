# Foundry Presentation Outline

**Target Length:** ~30 minutes talking time (fast-forward through AI execution)
**Format:** Working demo — building things live, pausing/fast-forwarding AI execution
**Website:** https://foundry-ai.io/

## Screens

- **Website** — foundry-ai.io for intro/branding
- **Terminal** — Claude Code running in the Foundry project
- **Trello** — Board with Backlog, Sprint Backlog, In Progress, Completed lists
- **Remote Server** — tmux with parallel long-run workers

## Terminology

- **Playbooks** — The orchestrated multi-step slash commands (`/long-run`, `/backlog-refinement`, `/backlog-consolidate`, `/deploy`, etc.). Not just a single action — a coordinated sequence with multiple steps, decision points, and team coordination.

---

## Act 1: Build the Foundation (~13 min)

### 1. The Problem (1.5 min — Talk — Website)

The pain points we're solving:
- Every new Claude Code project starts from scratch. You write a CLAUDE.md by hand, maybe copy-paste from a previous project, tweak it. No structure, no consistency.
- If you have multiple projects, each one drifts. Different conventions, different agent setups, different quality.
- There's no concept of "roles" in a vanilla Claude Code project. One agent tries to do everything — architecture, implementation, testing, documentation. It's like hiring one person and expecting them to be an architect, developer, QA, and tech writer simultaneously.
- Teams can't share their Claude Code setup. There's no reusable library. Every team reinvents the wheel.
- No workflow orchestration. You can ask Claude Code to do one thing at a time, but there's no way to say "here are 9 features, go build them in parallel with 5 teams."

### 2. What Foundry Is (1.5 min — Talk — Website)

The elevator pitch:
- Foundry is a tool that compiles AI software teams from a reusable library of building blocks.
- You pick personas (who's on the team), attach expertise (what they know), choose workflows (how they operate), and Foundry generates a complete Claude Code project folder.
- The generated project has specialized agents, each with a defined role, clear responsibilities, and domain knowledge. Instead of one generalist, you get a team of specialists.
- But Foundry doesn't stop at generation. It ships with playbooks — orchestrated workflows that let your AI team take work from a Trello board, process it in parallel, and deliver completed features.
- Think of it as: **Library + Compiler + Orchestrator**. You build the team, Foundry compiles it, and then playbooks orchestrate the work.

### 3. The Library (2.5 min — Demo — Terminal)

What to show:
- Browse `ai-team-library/` — this is the building block inventory
- **Personas** — 24 personas across 4 categories:
  - Software Development (14): Team Lead, Developer, Architect, BA, Tech QA, Code Quality Reviewer, UX/UI Designer, Database Administrator, Data Engineer, DevOps/Release, Mobile Developer, Platform/SRE, Integrator/Merge Captain, Technical Writer
  - Data & Analytics (3): Data Analyst, Researcher/Librarian, Technical Writer
  - Business Operations (6): Product Owner, Change Management, Customer Success, Financial Operations, Legal Counsel, Sales Engineer
  - Compliance & Legal (2): Compliance/Risk Analyst, Security Engineer
- Open one persona file (e.g., `developer/persona.md`) — show that each persona has a full constitution: mission, scope, operating principles, inputs/outputs, collaboration patterns
- Each persona also has `outputs.md`, `prompts.md`, and `templates/`
- **Expertise modules** — 39 domains: Python, .NET, Java, Go, Rust, React, Kubernetes, Terraform, AWS/Azure/GCP, HIPAA, GDPR, PCI-DSS, SOX, ISO 9000, API Design, Clean Code, DevOps, Security, FinOps, MLOps, and more
- Expertise is separate from personas — you can attach Python expertise to any persona. The architect knows Python conventions. The QA engineer knows Python testing patterns. Same expertise, different lens.
- **Workflows and templates** — the operational patterns that define how the team works together

Key point: This library is open and extensible. These aren't hard-coded. You can add your own personas, your own expertise modules, your own templates.

### 4. Composing a Team (2 min — Demo — Terminal)

What to show:
- Open `examples/small-python-team.yml` — a real composition file
- Walk through the structure:
  - `project:` — name, slug, output location
  - `expertise:` — which knowledge domains to include (e.g., Python, Clean Code) with ordering
  - `team.personas:` — which roles to put on the team, each with settings for agents, templates, strictness
  - `hooks:` — policy enforcement (e.g., hook-policy in enforcing mode)
  - `generation:` — options like seed_tasks, write_manifest
- The composition is declarative. You're describing *what* team you want, not *how* to build it.
- Show other example compositions briefly: `full-stack-web.yml`, `security-focused.yml`, `foundry-dogfood.yml` (Foundry's own team — we eat our own cooking)
- Point out that you can compose a team in minutes that would take hours to set up by hand

### 5. Generation (1 min — Demo — Terminal)

What to show:
- Run the CLI: `foundry-cli generate examples/small-python-team.yml --library ai-team-library`
- Watch the output scroll — files being generated, agents being compiled, templates being copied
- This takes seconds, not hours
- Mention the GUI exists too — `foundry` launches a PySide6 desktop app for visual composition

### 6. The Generated Output (2.5 min — Demo — Terminal)

What to show:
- `cd` into the generated project folder and explore the structure
- **CLAUDE.md** — the master instruction file, automatically composed from all the personas and expertise. This is what Claude Code reads to understand the project.
- **Agent files** (`.claude/agents/`) — each persona gets its own agent file. Open the developer agent and the tech-qa agent. Show they have distinct personalities, responsibilities, and domain knowledge.
- **Commands and skills** — the playbooks and tools that come with the project
- **Templates** — role-specific output templates (test plans, ADRs, etc.)
- **Folder structure** — `ai/beans/`, `ai/outputs/<persona>/`, `ai/context/` — the workspace where the team operates
- Key message: You didn't write any of this. Foundry compiled it from the library based on your composition. And every project you generate from the same library will be consistent.

### 7. Claude Kit / Sharing Across Projects (2 min — Talk + Light Demo)

What to explain:
- The `.claude/kit/` submodule system — a shared git submodule that lives inside your Claude Code project
- If you have 5 projects, they can all point to the same kit. Update the kit once, pull it everywhere with `claude-sync.sh`.
- The kit contains the shared commands, skills, agents, hooks, and settings that are common across projects
- `.claude/local/` holds project-specific overrides — if you need something unique to one project, put it in local
- Assembly symlinks tie it all together — Claude Code sees everything in its expected paths
- This is the **organizational scale** story: one team maintains the kit, every project benefits
- Light demo: show the symlink structure briefly, run `claude-sync.sh` to show how simple an update is

---

## Act 2: Two Ways to Work (~14 min)

Transition: "Now that we've built a team, let's put them to work. There are two ways to feed work into the system."

### Path A: Developer-Driven (Claude Code)

#### 8. The Bean Lifecycle (1.5 min — Demo — Terminal)

What to show:
- A **bean** is a unit of work — a feature, enhancement, bug fix, or epic
- Show the bean template (`ai/beans/_bean-template.md`) — what goes into a bean definition
- Lifecycle: **Unapproved → Approved → In Progress → Done**
- Beans live in `ai/beans/BEAN-NNN-<slug>/`
- The backlog index (`ai/beans/_index.md`) tracks all beans and their statuses
- Each bean gets decomposed into tasks by the Team Lead, assigned to the right personas
- Default task wave: Developer → Tech QA (mandatory). BA and Architect are opt-in.
- Key message: Beans are the currency of work. Everything flows through them.

#### 9. Parallel Backlog Refinement (2.5 min — Demo — Terminal)

What to show:
- This is how a developer brainstorms and creates new work items
- Open 3 Claude Code windows side by side, same project, same branch
- In each window, run `/backlog-refinement`
- Each instance works independently — generating 2-3 beans per session
- Explain while the AI works (fast-forward): each instance is having a conversation about what features the project needs, then creating well-formed beans with acceptance criteria
- After fast-forward: show the results — ~6-9 raw beans created across the 3 sessions
- Point out: because these ran in separate Claude instances, there may be overlap or duplication. Two instances might independently decide the project needs a "user authentication" feature. That's expected and handled in the next step.

#### 10. Backlog Consolidation (2 min — Demo — Terminal)

What to show:
- Run `/backlog-consolidate` in a single window
- This playbook analyzes all the beans and detects:
  - Duplicates — two beans that describe the same thing
  - Scope overlaps — beans that partially cover the same ground
  - Contradictions — beans that conflict with each other
  - Merge candidates — beans that are better combined
  - Missing dependencies — beans that should depend on each other
- It presents findings grouped by severity (Critical, High, Medium) with evidence
- Walk through a couple of findings interactively — merge one, delete one, add a dependency
- After cleanup: a clean, non-overlapping backlog ready for execution
- Push to main — at this point we're only committing bean definitions, no code yet

#### 11. Long Run — Parallel Execution (3 min — Demo — Remote Server)

What to show:
- SSH into the remote server
- Explain briefly: this is a VPS with Claude Code installed, configured to work with the same repo
- Open the Foundry project directory, start tmux
- Run `/long-run --fast 5`
- Explain what happens:
  - Long Run reads the backlog and picks up approved beans
  - It creates 5 git worktrees — isolated copies of the repo, one per team
  - It spawns 5 parallel Claude Code instances, each in its own tmux window
  - Each instance gets a Team Lead who picks a bean, decomposes it into tasks, and coordinates the team through the work
  - As each team completes a bean, the worktree is merged back to the main branch, cleaned up, and the team picks up the next bean
  - 9 beans across 5 teams — parallel throughput
- Fast-forward through execution
- Show results: completed beans, merged code, tests passing
- Key message: You went from "brainstorm features" to "working code" with minimal manual intervention. The AI team did the implementation, testing, and integration.

### Path B: Team-Driven (Trello)

Transition: "That's the developer-driven path. But what if the work isn't coming from a developer brainstorming in a terminal? What if it's coming from your QA team, your VAs, your product manager?"

#### 12. Trello Board Setup (2 min — Demo — Trello)

What to show:
- Switch to the Trello board
- Walk through the lists:

| List | Purpose | Who uses it |
|------|---------|-------------|
| **Backlog** | Ideas and potential work, not yet committed | Anyone — VAs, testers, PMs, developers |
| **Sprint Backlog** | Work committed for this cycle | Developer or PM moves cards here |
| **In Progress** | Picked up by Long Run, actively being worked | Automated by playbook |
| **Completed** | Bean finished, code merged | Automated by playbook |

- Show some example cards — a feature request from a VA, a bug report from a manual tester
- Explain: these people never touch a terminal. They write a card title, add a description, maybe attach a screenshot. That's it.
- Drag a few cards from Backlog to Sprint Backlog — "this is me deciding what we're building this sprint"
- Key message: Trello is the interface for non-technical team members. They contribute work items in a tool they already know.

#### 13. Trello-Driven Long Run (3 min — Demo — Remote Server + Trello)

What to show:
- Switch back to the remote server (tmux still open)
- Run `/long-run --fast 5`
- Explain the flow:
  1. Long Run connects to Trello and pulls all cards from Sprint Backlog
  2. Each card gets run through `/backlog-refinement` to create a proper bean with acceptance criteria
  3. These beans are **auto-approved** because they came from the Sprint Backlog (someone already committed to this work)
  4. Cards move from Sprint Backlog → In Progress on the Trello board
  5. Bean metadata records which Trello board and card it originated from — full traceability
  6. Teams process beans in parallel, same as before — git worktrees, tmux windows
  7. When a bean completes, the corresponding Trello card moves from In Progress → Completed
- Switch to Trello during fast-forward to show cards moving between lists
- Show a completed card — the bean reference is linked, the work is done
- Key message: A VA creates a Trello card, you run one command, and 5 AI teams pick it up, build it, test it, and mark it done. The card moves through the board automatically. That's the full loop.

---

## Act 3: Close (~3 min)

### 14. Customization / Extensibility (2 min — Talk + Light Demo)

What to explain:
- Everything in the library is open and extensible
- Adding a new persona: create a folder in `ai-team-library/personas/`, add `persona.md`, `outputs.md`, `prompts.md`, and optional `templates/`
- Adding new expertise: create a folder in `ai-team-library/expertise/`, add topic markdown files
- Your custom additions compose with the built-in library — mix and match
- Show the file structure briefly: "Here's what it looks like to add a new persona. It's just markdown files in a folder."
- Industry-specific compliance: the library already has HIPAA, GDPR, PCI-DSS, SOX, ISO 9000. You can add your own regulatory domain the same way.
- The library is designed to grow with your organization

### 15. Wrap-Up (1 min — Talk — Website)

Recap the arc:
- **Build** — Compose a team from the library in minutes
- **Compile** — Generate a complete Claude Code project
- **Orchestrate** — Use playbooks to run work through the team in parallel
- **Integrate** — Connect to Trello for non-technical team members
- **Scale** — Share the kit across projects, extend the library for your domain

Where to go:
- Website: foundry-ai.io
- What's coming next (brief tease of roadmap if applicable)
- Thank you / Q&A
