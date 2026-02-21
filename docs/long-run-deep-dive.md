# /long-run — Deep Dive

How the `/long-run` command works under the hood: step-by-step execution, skill call chains, flags, parallel mode, and how to run specific beans.

## Flags

| Flag | What it does |
|------|-------------|
| *(no flags)* | Sequential mode — processes one bean at a time in a loop |
| `--fast N` | Parallel mode — spawns N tmux workers, each processing a bean simultaneously |
| `--category App\|Process\|Infra` | Filters beans — only processes beans matching that category |
| `--fast 3 --category Infra` | Both — 3 parallel workers, Infra beans only |

---

## Sequential Mode (default)

```
YOU type: /long-run
│
├─ Phase 0: Branch Check
│   └─ git branch --show-current
│   └─ Must be on `main` (auto-checkouts if clean)
│   └─ Any other branch or dirty tree → STOP
│
├─ Phase 0.5: Trello Sync
│   └─ CALLS: /internal:trello-load          ← SKILL CALL
│       └─ Connects to Trello MCP
│       └─ Pulls cards from Sprint_Backlog list
│       └─ Creates beans with Approved status (inline, no dialogue)
│       └─ Moves processed cards to In_Progress on Trello
│       └─ Best-effort — if Trello is down, continues without it
│
├─ Phase 1: Backlog Assessment
│   └─ READ  ai/beans/_index.md
│   └─ Filter: status=Approved, not blocked, not locked by another agent
│   └─ Apply --category filter if provided
│   └─ No actionable beans? → STOP ("Backlog clear")
│
├─ Phase 2: Bean Selection
│   └─ READ each candidate bean.md
│   └─ Selection heuristics:
│       1. Priority (High > Medium > Low)
│       2. Inter-bean dependencies (do prerequisites first)
│       3. Logical order (infra before features, models before UI)
│       4. ID order (lowest first as tiebreaker)
│
├─ Phase 3: Bean Execution
│   ├─ Update bean.md status → "In Progress"
│   ├─ Update _index.md status + owner
│   ├─ git checkout -b bean/BEAN-NNN-<slug>     ← feature branch
│   └─ Decompose into task files in tasks/ directory
│       └─ Default wave: Developer → Tech-QA
│       └─ BA/Architect added only if criteria met
│       └─ Tech-QA is ALWAYS included, no exceptions
│
├─ Phase 4: Wave Execution
│   └─ For each task (in dependency order):
│       ├─ Set task status → "In Progress" (telemetry hook auto-stamps Started)
│       ├─ Perform work as the assigned persona
│       ├─ Produce outputs in ai/outputs/<persona>/
│       └─ Set task status → "Done" (telemetry hook auto-stamps Completed + Duration)
│
├─ Phase 5: Verification & Closure
│   ├─ Check every acceptance criterion
│   ├─ uv run pytest                            ← runs tests
│   ├─ uv run ruff check foundry_app/           ← runs lint
│   ├─ Update bean.md status → "Done"
│   └─ git commit on feature branch: "BEAN-NNN: <title>"
│
├─ Phase 5.5: Merge Captain
│   ├─ CALLS: /internal:merge-bean NNN          ← SKILL CALL
│   │   ├─ Aggregates telemetry totals into bean.md
│   │   ├─ git checkout main && git pull origin main
│   │   ├─ git merge bean/BEAN-NNN-<slug> --no-ff
│   │   ├─ git push origin main
│   │   ├─ git branch -d bean/BEAN-NNN-<slug>   ← deletes feature branch
│   │   └─ Conflict? → abort merge, STOP loop
│   ├─ Update _index.md → "Done", commit, push
│   └─ Move Trello card to Completed (if Source=Trello, best-effort)
│       └─ Reads bean's ## Trello section for Card ID
│       └─ Calls mcp__trello__move_card
│
├─ Phase 6: Loop
│   └─ Go back to Phase 1
│   └─ Repeat until no actionable beans remain
│   └─ Final message: "All beans merged to main. Backlog clear."
```

### Skills called in sequential mode

1. `/internal:trello-load` — once at startup (Trello sync)
2. `/internal:merge-bean` — once per completed bean

---

## Parallel Mode (`--fast N`)

```
YOU type: /long-run --fast 3
│
├─ Same Phase 0 (branch check on main) and Phase 0.5 (Trello sync)
│
├─ Parallel Phase 2: Backlog Assessment
│   └─ Same filtering as sequential
│   └─ Select up to N independent beans (no unmet inter-bean deps)
│
├─ Parallel Phase 3: Worker Spawning
│   └─ For EACH selected bean:
│       ├─ Update _index.md → "In Progress" (commit on main)
│       ├─ Write status file: /tmp/foundry-worker-BEAN-NNN.status
│       ├─ Create git worktree: /tmp/foundry-worktree-BEAN-NNN/
│       │   └─ git worktree add -b bean/BEAN-NNN-slug /tmp/... main
│       ├─ Create launcher script (temp .sh file)
│       └─ tmux new-window -n "bean-NNN" "bash $LAUNCHER"
│           └─ Spawns: claude --dangerously-skip-permissions --agent team-lead "..."
│           └─ Each child Claude runs the full bean lifecycle AUTONOMOUSLY
│           └─ Child does NOT merge, does NOT edit _index.md
│
├─ Parallel Phase 4: Dashboard Loop (runs in YOUR window)
│   └─ Every ~30 seconds:
│       ├─ Read all /tmp/foundry-worker-*.status files
│       ├─ For completed workers (status: done):
│       │   ├─ git worktree remove --force
│       │   ├─ git fetch && git pull origin main
│       │   ├─ CALLS: /internal:merge-bean NNN      ← SKILL CALL
│       │   ├─ Update _index.md → "Done", commit, push
│       │   └─ Move Trello card (if applicable)
│       ├─ For empty worker slots:
│       │   ├─ RE-READ _index.md (fresh — not cached)
│       │   ├─ Find next Approved unblocked bean
│       │   └─ Spawn NEW worker (worktree + tmux window)
│       ├─ Render dashboard (progress bars, status emoji)
│       ├─ Alert on blocked and stale (5+ min) workers
│       └─ Exit when: all merged AND no Approved beans remain
│
├─ Parallel Phase 5: Cleanup
│   └─ rm -f /tmp/foundry-worker-*.status
│   └─ git worktree prune
│   └─ git fetch && git pull origin main
│   └─ Final report
```

### Key difference

In parallel mode, the main window **never processes beans itself** — it only orchestrates (assigns, monitors, merges). The child Claude instances do all the actual work in isolated git worktrees.

---

## Running Specific Beans

`/long-run` itself doesn't let you pick specific beans — it always auto-selects based on priority heuristics. For specific beans, use `/spawn-bean`:

| Command | What happens |
|---------|-------------|
| `/spawn-bean` | 1 worker, auto-picks highest priority bean |
| `/spawn-bean 16` | 1 worker, runs BEAN-016 specifically |
| `/spawn-bean 16 17 18` | 3 workers, one per specified bean, separate tmux windows |
| `/spawn-bean --count 3` | 3 workers, each auto-picks, separate windows |
| `/spawn-bean 16 17 18 --wide` | 3 workers in ONE window as tiled panes (grid layout) |
| `/spawn-bean --count 4 --wide` | 4 auto-pick workers in a tiled grid |

`/spawn-bean` uses the same worktree isolation, status file protocol, and dashboard loop as `/long-run --fast`, but gives you direct control over **which** beans to run.

---

## Worker Isolation Model

Each parallel worker gets full isolation via git worktrees:

```
Main repo: /home/gregg/.../foundry/     (orchestrator — on `main` branch)
Worker 1:  /tmp/foundry-worktree-BEAN-016/  (own feature branch, own .venv)
Worker 2:  /tmp/foundry-worktree-BEAN-017/  (own feature branch, own .venv)
Worker 3:  /tmp/foundry-worktree-BEAN-018/  (own feature branch, own .venv)
```

- Worktrees share the same `.git` object store — no full clones needed
- Each worker has its own working directory, feature branch, and virtual environment
- No branch collisions, no file stomping between workers
- Workers communicate via status files in `/tmp/foundry-worker-BEAN-NNN.status`

---

## Status File Protocol

Workers write progress to `/tmp/foundry-worker-BEAN-NNN.status`:

```
bean: BEAN-018
title: Library Indexer Service
tasks_total: 4
tasks_done: 2
current_task: 03-developer-implement
status: running
message:
worktree: /tmp/foundry-worktree-BEAN-018
updated: 2026-02-07T14:32:01
```

### Status Values

| Status | Meaning | Dashboard |
|--------|---------|-----------|
| `starting` | Worker launched, Claude initializing | White/dim |
| `decomposing` | Breaking bean into tasks | Blue |
| `running` | Executing tasks normally | Green |
| `blocked` | Needs human input — see `message` | Red |
| `error` | Unrecoverable error — see `message` | Orange |
| `done` | Bean completed successfully | Checkmark |

### Dashboard Display

```
╔══════════════════════════════════════════════════════════════════╗
║  Bean Workers — 3 active                          14:32:01     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  BEAN-018  Library Indexer Service     ████████░░  50% (2/4)    ║
║  Running — 03-developer-implement                               ║
║                                                                 ║
║  BEAN-019  Wizard Project Identity     ██████████░ 75% (3/4)    ║
║  Running — 04-tech-qa-tests                                     ║
║                                                                 ║
║  BEAN-020  Wizard Persona Selection    ███░░░░░░░  25% (1/4)    ║
║  FEEDBACK NEEDED — Need clarification on persona filter UX      ║
║     → Switch to worker: Alt-3                                   ║
║                                                                 ║
╚══════════════════════════════════════════════════════════════════╝

  1 worker needs attention — see blocked worker above
```

---

## Complete Skill/Command Call Tree

```
/long-run
├── /internal:trello-load          (once at startup — Trello → beans)
│   └── Trello MCP calls (list_boards, get_lists, get_cards, move_card...)
│   └── Inline bean creation (reads _bean-template.md, writes bean.md)
│
├── [per bean — sequential mode, or per worker completion — parallel mode]
│   └── /internal:merge-bean       (merge feature branch → main)
│       └── Pure git operations (checkout, pull, merge --no-ff, push, branch -d)
│
└── [parallel mode only — inside each child Claude]
    └── The child prompt references these skills:
        ├── /internal:seed-tasks    (decompose bean → task files)
        ├── /close-loop             (verify task against acceptance criteria)
        ├── /internal:handoff       (transition between personas)
        └── /status-report          (final summary)
```

`/long-run` itself directly calls **2 skills**. In parallel mode, each spawned child Claude independently calls **4 more skills** during its autonomous bean execution.

---

## How It All Connects

There is no runtime engine. The `.md` skill files are prompt instructions injected into Claude's context window. Claude reads them and follows them using its available tools (Read, Write, Edit, Bash, Glob, Grep, etc.).

When `/long-run` says "call `/internal:merge-bean`", Claude either:
1. Invokes the `Skill` tool (which loads `merge-bean/SKILL.md` into context), or
2. Just performs the git operations directly because it already knows what to do

The skill files are **runbooks for an LLM** — they shape behavior but there's no compiler or runtime enforcing the interface. The consistency comes from well-written instructions and the template system for beans.
