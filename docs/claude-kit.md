# Claude Kit — Shared Configuration Management

This repo uses [claude-kit](https://github.com/beekeeper-lab/claude-kit) to share `.claude/` configuration (agents, skills, commands, hooks) across projects via a **git submodule**.

## Architecture

```
.claude/
  kit/                  # Git submodule → beekeeper-lab/claude-kit (read-only source)
    .claude/shared/     # Kit content: agents, commands, skills, hooks, settings.json
  local/                # Project-specific assets (never shared upstream)
    commands/           # App-only commands
    skills/             # App-only skills
    agents/             # App-only agents
  commands/             # Assembly: symlinks → kit + local commands
  skills/               # Assembly: symlinks → kit + local skills
  agents/               # Assembly: symlinks → kit + local agents
  hooks                 # Symlink → kit/.claude/shared/hooks
  shared                # Bridge symlink → kit/.claude/shared (for internal path refs)
  settings.json         # Symlink → kit/.claude/shared/settings.json
```

Claude Code discovers assets at `.claude/{commands,skills,agents,hooks,settings.json}`. The assembly symlinks make content from both kit and local sources visible at these paths. Local assets override kit assets on name collision.

## First-Time Setup

```bash
# After cloning, initialize the submodule and build symlinks
git submodule update --init --recursive
scripts/claude-link.sh

# Install git hooks (also runs on post-checkout)
scripts/claude-sync.sh
```

## Updating the Kit

```bash
# Pull latest kit + rebuild symlinks
scripts/claude-sync.sh
```

Or manually:

```bash
cd .claude/kit
git pull origin main
cd ../..
scripts/claude-link.sh
git add .claude/kit
git commit -m "Bump Claude-Kit submodule"
```

## Editing Shared Assets (Two-Commit Workflow)

When you edit shared config (anything inside `.claude/kit/`):

1. Edit and test inside `.claude/kit/`
2. Run `scripts/claude-link.sh` if you added new files
3. Use `scripts/claude-publish.sh` to push both repos:

```bash
scripts/claude-publish.sh
```

This pushes the submodule first, then bumps the pointer and pushes the parent repo.

## Adding Project-Specific Assets

Put app-only assets in `.claude/local/`:

```bash
# Example: add a project-specific command
echo "..." > .claude/local/commands/my-command.md

# Rebuild symlinks so Claude Code discovers it
scripts/claude-link.sh
```

Local assets are never pushed to claude-kit.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/claude-link.sh` | Rebuild assembly symlinks from kit + local |
| `scripts/claude-sync.sh` | Install git hooks + sync submodule + rebuild symlinks |
| `scripts/claude-publish.sh` | Safe two-step push (submodule first, then repo) |
| `scripts/githooks/post-checkout` | Auto-heal `.claude/` on branch checkout |

### claude-link.sh

The core assembly script. Creates symlinks in `.claude/{commands,skills,agents}` pointing to content in both `kit/.claude/shared/` and `local/`. Also symlinks `hooks`, `settings.json`, and the `shared` bridge. Idempotent — safe to run multiple times.

### post-checkout hook

Automatically installed by `claude-sync.sh`. On every branch checkout, it initializes the submodule if missing and rebuilds symlinks. This ensures worktrees and fresh checkouts always have working `.claude/` content.

## Setup for New Projects

To adopt claude-kit in a new project:

1. Add the submodule: `git submodule add git@github.com:beekeeper-lab/claude-kit.git .claude/kit`
2. Create local dirs: `mkdir -p .claude/local/{commands,skills,agents}`
3. Copy `scripts/claude-link.sh`, `claude-sync.sh`, `claude-publish.sh`, and `githooks/` into your project
4. Run `scripts/claude-link.sh` to create assembly symlinks
5. Run `scripts/claude-sync.sh` to install hooks
6. Commit: `git add .gitmodules .claude/ scripts/ && git commit`
