# /backlog-refinement — Deep Dive

How the `/backlog-refinement` command works under the hood: the dialogue loop, bean creation, skill call chain, and how ideas become actionable work items.

## What It Does

Takes raw, unstructured ideas and turns them into well-formed beans through a conversational refinement process. You describe what you want in plain text — a single sentence or multiple paragraphs — and the Team Lead analyzes it, asks clarifying questions, and creates properly-scoped beans once understanding is clear.

## Usage

```
/backlog-refinement <text>
/backlog-refinement --dry-run <text>
```

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | `false` | Show proposed beans without creating them |

---

## Step-by-Step Call Chain

```
YOU type: /backlog-refinement I want to add parallel processing to the
long-run command. It should use tmux to spawn multiple windows, each
running its own Claude Code instance working on a separate bean.
│
├─ Phase 1: Analysis
│   ├─ READ  ai/beans/_index.md
│   │   └─ Get existing beans (avoid duplicates)
│   │   └─ Understand current priorities and landscape
│   │   └─ Find the next available bean ID range
│   ├─ READ  ai/beans/_bean-template.md
│   │   └─ Know the target format for bean creation
│   └─ Identify work units from your text
│       └─ Separate features and capabilities
│       └─ Infrastructure vs application concerns
│       └─ Dependencies that suggest ordering
│       └─ Independent deliverables
│
├─ Phase 2: Dialogue (interactive — back and forth with you)
│   │
│   ├─ Present initial breakdown (working titles only, NO IDs yet):
│   │   "I've identified 4 potential beans from your input:
│   │    1. Parallel Execution Engine — tmux worker spawning (Priority: High)
│   │    2. Feature Branch Strategy — isolated branches per bean (Priority: High)
│   │    3. Merge Captain — safe merging back to main (Priority: Medium)
│   │    4. Push Hook Safety — prevent accidental pushes to main (Priority: Medium)"
│   │
│   ├─ Ask clarifying questions (2-4 at a time):
│   │   └─ Priority: "How important is X relative to Y?"
│   │   └─ Scope: "Should we include X or defer that?"
│   │   └─ Dependencies: "Does X need Y first, or are they independent?"
│   │   └─ Missing context: "Can you elaborate on X?"
│   │   └─ Acceptance criteria: "What does 'done' look like for X?"
│   │   └─ Splitting: "This seems like two pieces — should I split them?"
│   │   └─ Merging: "X and Y seem related — should they be one bean?"
│   │
│   └─ Iterate until you approve:
│       └─ Adjust titles, descriptions, priorities
│       └─ Split beans that are too large
│       └─ Merge beans that are too small
│       └─ Add details to scope and acceptance criteria
│       └─ Looks for approval signals: "Looks good", "Yes, create those"
│
├─ Phase 3: Creation (sequential — one bean at a time)
│   │
│   ├─ Check: --dry-run? → Skip creation, go to summary
│   │
│   └─ For EACH agreed-upon bean (in sequence, NOT parallel):
│       │
│       ├─ RE-READ  ai/beans/_index.md       ← fresh read every time
│       │   └─ Another agent may have added beans since last read
│       │
│       ├─ CALLS: /internal:new-bean         ← SKILL CALL (or inline)
│       │   ├─ Compute next ID (max existing + 1)
│       │   ├─ Generate slug (title → kebab-case, max 50 chars)
│       │   ├─ Check for duplicate directories
│       │   ├─ MKDIR  ai/beans/BEAN-NNN-<slug>/
│       │   ├─ MKDIR  ai/beans/BEAN-NNN-<slug>/tasks/
│       │   ├─ READ   ai/beans/_bean-template.md
│       │   ├─ WRITE  ai/beans/BEAN-NNN-<slug>/bean.md  (template with placeholders filled)
│       │   └─ EDIT   ai/beans/_index.md                 (append row)
│       │
│       └─ EDIT  ai/beans/BEAN-NNN-<slug>/bean.md    ← fills in rich content
│           └─ Problem Statement (from your description + dialogue)
│           └─ Goal (from acceptance criteria discussion)
│           └─ Scope — In Scope / Out of Scope (from dialogue)
│           └─ Acceptance Criteria (concrete, testable checklist)
│           └─ Priority (as agreed)
│           └─ Dependencies (referencing other beans)
│           └─ Trello section: Source = Manual
│
├─ Phase 3.5: Cross-Reference Fix
│   └─ Single pass over all newly created beans
│   └─ Replace title references with actual BEAN-NNN IDs
│       (e.g., "depends on Merge Captain" → "depends on BEAN-014")
│
├─ Phase 3.6: Duplicate Detection
│   └─ If a proposed bean closely matches an existing bean:
│       └─ Warn: "This looks similar to BEAN-NNN (title). Create anyway?"
│       └─ User says yes → create it
│       └─ User says no → skip it
│
└─ Phase 4: Summary
    └─ Print table of all created beans:
        | Bean ID  | Title            | Priority | Dependencies |
        |----------|------------------|----------|--------------|
        | BEAN-012 | Parallel Engine  | High     | —            |
        | BEAN-013 | Feature Branches | High     | BEAN-012     |
        | BEAN-014 | Merge Captain    | Medium   | BEAN-013     |
        | BEAN-015 | Push Hook Safety | Medium   | —            |
```

---

## The Two-Step Bean Creation

There's a subtle detail in how beans get their content. The creation happens in two steps:

```
Step 1: /internal:new-bean creates the SKELETON
        ├─ Directory structure
        ├─ bean.md from template (with placeholder prose)
        └─ Index entry

Step 2: /backlog-refinement fills in the CONTENT
        ├─ Problem Statement (derived from dialogue)
        ├─ Goal (from acceptance criteria discussion)
        ├─ Scope — In/Out (from scope questions)
        ├─ Acceptance Criteria (from "what does done look like?")
        └─ Dependencies and Notes
```

`/new-bean`'s formal inputs only accept `title`, `priority`, and `problem_statement`. The rich content (Goal, Scope, Acceptance Criteria) lives in Claude's context window from the dialogue phase and gets written directly via the Edit tool after the skeleton is created.

---

## Complete Skill Call Tree

```
/backlog-refinement
│
├── READ ai/beans/_index.md              (existing beans, duplicate check)
├── READ ai/beans/_bean-template.md      (bean format reference)
│
├── [dialogue with user — no skill calls, just conversation]
│
└── [per bean, sequentially]
    └── /internal:new-bean               ← ONLY SKILL CALLED
        ├── RE-READ ai/beans/_index.md   (fresh, multi-agent safety)
        ├── MKDIR bean directory + tasks/
        ├── READ ai/beans/_bean-template.md
        ├── WRITE bean.md (skeleton)
        └── EDIT _index.md (append row)
```

**The chain is only 2 levels deep.** `/backlog-refinement` calls `/new-bean` — and `/new-bean` is a leaf node that calls nothing else. The heavy lifting is all dialogue with you, then file I/O.

---

## What /new-bean Does (the leaf node)

```
/internal:new-bean "Parallel Execution Engine"
│
├─ RE-READ  ai/beans/_index.md        (fresh, multi-agent safety)
├─ Compute next ID (max existing + 1, zero-padded: BEAN-012)
├─ Generate slug (title → kebab-case: parallel-execution-engine)
├─ Check for duplicate directory
├─ MKDIR   ai/beans/BEAN-012-parallel-execution-engine/
├─ MKDIR   ai/beans/BEAN-012-parallel-execution-engine/tasks/
├─ READ    ai/beans/_bean-template.md
├─ WRITE   ai/beans/BEAN-012-parallel-execution-engine/bean.md
└─ EDIT    ai/beans/_index.md  (append row)
```

Calls nothing. Pure file I/O. End of chain.

---

## The Bean Template

Every bean starts from the same template (`ai/beans/_bean-template.md`):

```markdown
# BEAN-NNN: Title

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-NNN |
| **Status** | Unapproved |
| **Priority** | Medium |
| **Created** | YYYY-MM-DD |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | (App | Process | Infra) |

## Problem Statement
## Goal
## Scope
### In Scope
### Out of Scope
## Acceptance Criteria
## Tasks
## Notes
## Trello
## Telemetry
```

The template provides structural consistency. `/new-bean` fills the metadata placeholders (ID, title, date, priority). `/backlog-refinement` fills the prose sections (Problem Statement, Goal, Scope, Acceptance Criteria) from your dialogue.

---

## Quality Criteria

Before creating beans, `/backlog-refinement` enforces these standards:

- Every bean has a non-trivial Problem Statement (not just restating the title)
- Every bean has at least 3 acceptance criteria
- Scope sections distinguish In Scope from Out of Scope
- Dependencies between created beans are noted
- No duplicate beans created without explicit user approval
- At least one clarifying question asked before creating beans
- Bean IDs are sequential and do not collide

---

## Multi-Agent Safety

Because multiple Claude agents can work in the codebase concurrently, `/backlog-refinement` takes precautions:

- **Fresh reads every time** — Re-reads `_index.md` before each bean creation, not just once at the start
- **Sequential creation** — Creates beans one at a time (not parallel) so each new bean sees the correct max ID
- **No pre-assigned IDs** — IDs are computed at creation time from the current state of the index
- **Collision detection** — Checks for duplicate directories before writing

---

## Examples

**Broad vision input:**
```
/backlog-refinement I want to add parallel processing to the long-run
command. It should use tmux to spawn multiple windows, each running
its own Claude Code instance working on a separate bean. We'll need
feature branches, a merge captain to handle merging, and updated
push hooks so we don't accidentally push to main.
```
Team Lead identifies 4 potential beans, asks clarifying questions about priority and scope, creates them sequentially.

**Specific feature input:**
```
/backlog-refinement Add a delete button to the user profile page
```
Team Lead identifies a single bean, asks about confirmation dialog behavior and error handling, creates one bean.

**Dry run (preview without creating):**
```
/backlog-refinement --dry-run We need user authentication, a dashboard,
and an API for mobile clients.
```
Shows proposed beans (auth, dashboard, mobile API) without creating them. Useful for previewing before committing to the backlog.

---

## How It Connects to the Rest of the Pipeline

```
/backlog-refinement          Creates beans (status: Unapproved)
        ↓
  User reviews & approves    Sets status: Approved
        ↓
/long-run                    Picks Approved beans, executes them, merges to main
```

`/backlog-refinement` is the **front door** to the entire pipeline. Everything downstream depends on well-formed beans with clear acceptance criteria — that's what this command produces.
