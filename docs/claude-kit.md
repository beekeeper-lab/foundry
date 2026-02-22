# Claude Kit — Shared Configuration Management

This repo uses [claude-kit](https://github.com/beekeeper-lab/claude-kit) to share `.claude/` configuration (agents, skills, commands, hooks) across projects. Two integration patterns are supported: **git subtree** and **git submodule**.

## Patterns

### Git Subtree (current default)

The `.claude/` directory is a git subtree linked to the `claude-kit` remote. Content lives directly in `.claude/`.

```bash
# Add the remote (first time)
git remote add claude-kit git@github.com:beekeeper-lab/claude-kit.git

# Pull latest changes from claude-kit
git subtree pull --prefix=.claude claude-kit main --squash

# Push local .claude/ changes back to claude-kit
git subtree push --prefix=.claude claude-kit main
```

### Git Submodule

The `.claude/kit/` directory is a git submodule pointing to the claude-kit repo.

```bash
# Add the submodule (first time)
git submodule add git@github.com:beekeeper-lab/claude-kit.git .claude/kit

# Update after pull
git submodule update --init --recursive
```

## Two-Commit Workflow

When you edit shared config files (anything inside `.claude/` or `.claude/kit/`), changes must be pushed in two steps to keep repos in sync:

### Subtree pattern

1. Commit changes normally in the consuming repo (they're already in-tree)
2. Push shared changes to claude-kit: `git subtree push --prefix=.claude claude-kit main`
3. Push the consuming repo: `git push`

### Submodule pattern

1. Commit and push inside `.claude/kit/`: `cd .claude/kit && git add . && git commit && git push`
2. Commit the updated submodule pointer in the consuming repo: `git add .claude/kit && git commit`
3. Push the consuming repo: `git push`

### Use `claude-publish.sh` instead

The `scripts/claude-publish.sh` script handles both patterns automatically:

```bash
scripts/claude-publish.sh
```

It detects which pattern is in use, pushes `.claude/` changes first, and only pushes the main repo if that succeeds.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/claude-sync.sh` | Install git hooks + sync `.claude/` content |
| `scripts/claude-publish.sh` | Safe two-step push (`.claude/` first, then repo) |
| `scripts/githooks/post-checkout` | Auto-heal `.claude/` on branch checkout |

### claude-sync.sh

Run after cloning or when hooks need updating:

```bash
scripts/claude-sync.sh
```

This will:
- Copy all hooks from `scripts/githooks/` into `.git/hooks/`
- Sync `.claude/` content (subtree pull or submodule update)

### post-checkout hook

Automatically installed by `claude-sync.sh`. On every branch checkout, it:
- Detects if `.claude/` content is missing or empty
- In submodule mode: runs `git submodule update --init --recursive`
- In subtree mode: warns and suggests running `claude-sync.sh`
- Runs `claude-sync.sh` if available

This ensures worktrees and fresh checkouts always have `.claude/` content.

## Setup for New Projects

To adopt these scripts in a new claude-kit consuming project:

1. Copy `scripts/githooks/` and `scripts/claude-sync.sh` and `scripts/claude-publish.sh` into your project
2. Run `scripts/claude-sync.sh` to install the hooks
3. Commit the scripts to your repo
