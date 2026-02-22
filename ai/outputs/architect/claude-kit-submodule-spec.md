# Sub-Apps + Claude-Kit: Shared `.claude` Workflow (Submodules + Local Extensions)

## Problem
Each application repo needs Claude Code assets:
- Some are **shared** across all repos (skills/commands/agents/hooks/settings).
- Some are **project-specific** and must live only in that repo.
- You want to improve shared assets from within a sub-app, test them there, and then **promote** those improvements upstream.

## Goals
1. **Shared kit** pulled into every app (Claude-Kit).
2. **Local additions** in each repo that don't leak into the kit.
3. **Promotion path**: improve kit from any repo → push → other repos update.
4. **Repeatable commands** (scripts) so updates don't get forgotten.

---

## Claude-Kit Repo Structure

The `beekeeper-lab/claude-kit` repo mirrors the `.claude/` layout Claude Code expects:

```
claude-kit/               # repo root
  agents/                 # AI team personas
    architect.md
    ba.md
    developer.md
    team-lead.md
    tech-qa.md
  commands/               # slash command definitions
    deploy.md
    long-run.md
    run.md
    ...
    internal/             # agent-only commands (not user-invocable)
      merge-bean.md
      new-bean.md
      ...
  skills/                 # skill implementations
    deploy/SKILL.md
    long-run/SKILL.md
    run/SKILL.md
    ...
    internal/             # agent-only skills
      merge-bean/SKILL.md
      new-bean/SKILL.md
      ...
  hooks/                  # hook scripts and policies
    hook-policy.md
    pre-commit-lint.md
    telemetry-stamp.py
  settings.json           # hook wiring, MCP config
```

**Key detail:** Assets live at the repo root (`agents/`, `commands/`, `skills/`), not under a nested `.claude/` subdirectory.

---

## Recommended Folder Layout (Any Sub-App)

Claude Code discovers assets at fixed paths: `.claude/commands/*.md`, `.claude/skills/*/SKILL.md`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json`. Since assets come from two sources (kit + local), the top-level directories are **assembly directories** containing symlinks into both.

```
my-app/
  .claude/
    kit/                   # Claude-Kit submodule (read-only source)
      agents/
      commands/
      skills/
      hooks/
      settings.json
    local/                 # app-only assets (never shared)
      skills/
      commands/
      agents/
      prompts/
    commands/              # assembled: symlinks → kit + local commands
      deploy.md       → ../kit/commands/deploy.md
      bean-status.md  → ../local/commands/bean-status.md
      internal        → ../kit/commands/internal
    skills/                # assembled: symlinks → kit + local skills
      deploy          → ../kit/skills/deploy
      bean-status     → ../local/skills/bean-status
      internal        → ../kit/skills/internal
    agents/                # assembled: symlinks → kit + local agents
      team-lead.md    → ../kit/agents/team-lead.md
    hooks              → kit/hooks           # direct symlink
    settings.json      → kit/settings.json   # direct symlink
  scripts/
    claude-link.sh         # rebuild assembly symlinks
    claude-sync.sh         # pull + submodule update + relink
    claude-publish.sh      # push kit submodule + parent repo
```

This layout solves the "shared + local" problem:
- `.claude/kit/` is the shared repo (submodule, never edited directly here)
- `.claude/local/` is yours (never shared)
- `.claude/commands/`, `.claude/skills/`, `.claude/agents/` are assembled symlinks so Claude Code discovers everything
- `.claude/hooks` and `.claude/settings.json` symlink directly to kit

---

## Setup Instructions (Sub-App)

### 1) Add Claude-Kit as a submodule
From the sub-app repo root:

```bash
mkdir -p .claude
git submodule add <CLAUDE_KIT_GIT_URL> .claude/kit
git submodule update --init --recursive
```

### 2) Create local folders for app-only assets
```bash
mkdir -p .claude/local/{skills,commands,agents,prompts}
```

### 3) Build assembly symlinks
The link script creates `.claude/commands/`, `.claude/skills/`, `.claude/agents/` with symlinks pointing into both `kit/` and `local/`. It also symlinks `hooks` and `settings.json` from kit.

```bash
./scripts/claude-link.sh
```

The script:
- Clears existing symlinks in each assembly directory
- Links all kit assets (top-level items + `internal/` subdirectory)
- Links all local assets (local wins if a name collides with kit)
- Symlinks `hooks` and `settings.json` from kit

### 4) Commit
```bash
git add .gitmodules .claude/ scripts/
git commit -m "Add Claude-Kit submodule and shared/local .claude layout"
git push
```

---

## Daily Use: Updating (Pull + Submodule)
Use a standard script so you never forget submodules.

### Script: `scripts/claude-sync.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Pulling latest..."
git pull --ff-only

echo "Syncing submodules..."
git submodule sync --recursive
git submodule update --init --recursive

echo "Rebuilding .claude/ symlinks..."
"$SCRIPT_DIR/claude-link.sh"

echo "Sync complete."
```

Run:
```bash
./scripts/claude-sync.sh
```

### Optional: Git config
```bash
git config submodule.recurse true
git config fetch.recurseSubmodules on-demand
```

---

## The Link Script: `scripts/claude-link.sh`

This is the key piece that makes the submodule pattern work with Claude Code's discovery paths.

```bash
#!/usr/bin/env bash
# Rebuild .claude/ assembly symlinks from kit + local
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
CLAUDE_DIR="$REPO_ROOT/.claude"
KIT_DIR="$CLAUDE_DIR/kit"
LOCAL_DIR="$CLAUDE_DIR/local"

if [ ! -d "$KIT_DIR" ]; then
  echo "ERROR: claude-kit submodule not found at $KIT_DIR"
  echo "Run: git submodule update --init --recursive"
  exit 1
fi

# --- Commands ---
mkdir -p "$CLAUDE_DIR/commands"
find "$CLAUDE_DIR/commands" -maxdepth 1 -type l -delete

for f in "$KIT_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  ln -sfn "../kit/commands/$(basename "$f")" "$CLAUDE_DIR/commands/$(basename "$f")"
done
[ -d "$KIT_DIR/commands/internal" ] && \
  ln -sfn ../kit/commands/internal "$CLAUDE_DIR/commands/internal"

for f in "$LOCAL_DIR/commands/"*.md; do
  [ -f "$f" ] || continue
  ln -sfn "../local/commands/$(basename "$f")" "$CLAUDE_DIR/commands/$(basename "$f")"
done

# --- Skills ---
mkdir -p "$CLAUDE_DIR/skills"
find "$CLAUDE_DIR/skills" -maxdepth 1 -type l -delete

for d in "$KIT_DIR/skills"/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  ln -sfn "../kit/skills/$name" "$CLAUDE_DIR/skills/$name"
done
[ -d "$KIT_DIR/skills/internal" ] && \
  ln -sfn ../kit/skills/internal "$CLAUDE_DIR/skills/internal"

for d in "$LOCAL_DIR/skills"/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  ln -sfn "../local/skills/$name" "$CLAUDE_DIR/skills/$name"
done

# --- Agents ---
mkdir -p "$CLAUDE_DIR/agents"
find "$CLAUDE_DIR/agents" -maxdepth 1 -type l -delete

for f in "$KIT_DIR/agents/"*.md; do
  [ -f "$f" ] || continue
  ln -sfn "../kit/agents/$(basename "$f")" "$CLAUDE_DIR/agents/$(basename "$f")"
done
for f in "$LOCAL_DIR/agents/"*.md; do
  [ -f "$f" ] || continue
  ln -sfn "../local/agents/$(basename "$f")" "$CLAUDE_DIR/agents/$(basename "$f")"
done

# --- Hooks & Settings (direct symlinks from kit) ---
ln -sfn kit/hooks "$CLAUDE_DIR/hooks"
ln -sfn kit/settings.json "$CLAUDE_DIR/settings.json"
```

**Important:** Run `claude-link.sh` after any of these events:
- Submodule update (new kit content)
- Adding/removing a local asset
- Initial setup

The script is idempotent — safe to run multiple times.

---

## Editing Shared Assets from a Sub-App (Promotion Workflow)

### The key rule
If you change shared skills/commands/agents, you must commit & push in **two places**:

1) **Claude-Kit repo** (inside `.claude/kit`)
2) **Your sub-app repo** (to bump the kit pointer)

### Step-by-step

#### Step 1 — Edit & test
Edit shared files inside the submodule:
- `.claude/kit/commands/my-command.md`
- `.claude/kit/skills/my-skill/SKILL.md`
- `.claude/kit/agents/my-agent.md`

Run `./scripts/claude-link.sh` to rebuild symlinks if you added new files. Test in your sub-app.

#### Step 2 — Commit & push the kit change (inside submodule)
```bash
cd .claude/kit
git add -A
git commit -m "Improve <skill/command/agent>"
git push
cd ../..
```

#### Step 3 — Commit & push the submodule pointer (in the sub-app)
```bash
git add .claude/kit
git commit -m "Bump Claude-Kit submodule"
git push
```

Now the sub-app repo points to the updated kit SHA.

---

## "Make it hard to forget": Publish script

Git won't automatically push kit commits when you push the parent repo.
So standardize a wrapper:

### Script: `scripts/claude-publish.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KIT_DIR="$REPO_ROOT/.claude/kit"

if [ -d "$KIT_DIR/.git" ] || [ -f "$KIT_DIR/.git" ]; then
  cd "$KIT_DIR"
  if [ -n "$(git status --porcelain)" ] || \
     [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u} 2>/dev/null || echo '')" ]; then
    echo "Pushing Claude-Kit submodule..."
    git push
  else
    echo "Claude-Kit submodule is up to date."
  fi
  cd "$REPO_ROOT"
fi

echo "Pushing parent repo..."
git push
```

Use:
```bash
./scripts/claude-publish.sh
```

---

## What belongs where (Sub-App responsibilities)

### Put in `.claude/local/` (app-only)
- Anything specific to this app's domain
- Experimental skills you don't want shared yet
- App-only agents or prompts

### Put in `.claude/kit/` (shared kit)
- Reusable skills/commands/agents
- Things you want to propagate to other repos/machines
- Hooks and settings shared across all projects

---

## How other repos get your improvements

After you promote a kit change and bump your sub-app pointer:
- Other repos update by running:
```bash
./scripts/claude-sync.sh
```
or manually:
```bash
git submodule update --init --recursive
./scripts/claude-link.sh
```

If Foundry is meant to track "latest kit," it will need to bump its own submodule pointer (or run a "update-to-latest-kit" workflow).

---

## Summary (Sub-App responsibilities)

- Add kit as submodule at `.claude/kit`
- Keep app-only assets in `.claude/local`
- Assembly symlinks in `.claude/commands/`, `.claude/skills/`, `.claude/agents/` make everything discoverable by Claude Code
- Use scripts to:
  - **link** (`claude-link.sh`) — rebuild assembly symlinks
  - **sync** (`claude-sync.sh`) — pull + submodule update + relink
  - **publish** (`claude-publish.sh`) — push kit + parent
- When changing shared assets, always do the **two-commit workflow**:
  - commit/push in kit
  - bump pointer in the parent repo

### Post-adoption checklist

- [ ] `.claude/kit/` submodule present with agents, commands, skills, hooks
- [ ] `.claude/local/` exists for project-specific assets
- [ ] `.claude/commands/`, `.claude/skills/`, `.claude/agents/` contain working symlinks
- [ ] `.claude/hooks` and `.claude/settings.json` symlinked from kit
- [ ] `.gitmodules` tracked
- [ ] `scripts/claude-link.sh`, `claude-sync.sh`, `claude-publish.sh` present and executable
- [ ] Run a quick test: try `/show-backlog` or `/run` to confirm commands work
