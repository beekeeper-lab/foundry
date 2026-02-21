# Claude Kit Adoption Prompt

Paste this into a Claude Code session for any project that should adopt claude-kit.

---

## Prompt

This project needs to adopt **claude-kit** — a shared `.claude/` configuration managed as a git subtree from `beekeeper-lab/claude-kit`. Claude-kit provides a complete AI team workflow: agents, slash commands, skills, hooks, and settings that are shared across all our projects.

### What you're getting

```
.claude/
├── agents/          # AI team personas (team-lead, ba, architect, developer, tech-qa)
├── commands/        # Slash commands (/deploy, /git-status, /long-run, /show-backlog, etc.)
├── skills/          # Skill implementations backing the commands
├── hooks/           # Pre-commit lint, telemetry, task QA hooks
└── settings.json    # Hook wiring, MCP server config (Trello)
```

### Step 1: Check current state

First, check if this project already has a `.claude/` directory:

```bash
ls -la .claude/ 2>/dev/null
git remote -v | grep claude-kit
```

- If `.claude/` exists and `claude-kit` remote exists → you're already set up, just pull latest (skip to Step 4)
- If `.claude/` exists but no `claude-kit` remote → need to replace it with the subtree (Step 2a)
- If `.claude/` doesn't exist → clean install (Step 2b)

### Step 2a: Replace existing .claude/ with subtree

**Back up any project-specific customizations first** — check for local agent files, custom commands, or settings you want to preserve.

```bash
# Remove existing .claude/ and commit the removal
git rm -r .claude/
git commit -m "Remove local .claude/ for claude-kit subtree adoption"

# Add the claude-kit remote
git remote add claude-kit git@github.com:beekeeper-lab/claude-kit.git

# Add the subtree
git subtree add --prefix=.claude claude-kit main --squash
```

### Step 2b: Clean install (no existing .claude/)

```bash
# Add the claude-kit remote
git remote add claude-kit git@github.com:beekeeper-lab/claude-kit.git

# Add the subtree
git subtree add --prefix=.claude claude-kit main --squash
```

### Step 3: Verify

```bash
# Confirm the remote is set
git remote -v | grep claude-kit

# Confirm the directory exists
ls .claude/agents/ .claude/commands/ .claude/skills/

# Confirm settings.json is present
cat .claude/settings.json
```

### Step 4: Pull latest (ongoing)

To get the latest changes from claude-kit at any time:

```bash
git subtree pull --prefix=.claude claude-kit main --squash
```

### Step 5: Push local changes back (if you modify .claude/)

If you make changes to `.claude/` files in this project and want to share them with all other projects:

```bash
git subtree push --prefix=.claude claude-kit main
```

**Important:** Only push changes that should be shared across ALL projects. Project-specific customizations should go elsewhere (e.g., in CLAUDE.md or project-specific config files).

### Step 6: Update CLAUDE.md

Add this section to your project's `CLAUDE.md`:

```markdown
## Claude Kit Subtree

The `.claude/` directory is shared across projects via a git subtree linked to `beekeeper-lab/claude-kit`.

\```bash
# Pull latest changes from claude-kit into this repo
git subtree pull --prefix=.claude claude-kit main --squash

# Push local .claude/ changes back to claude-kit
git subtree push --prefix=.claude claude-kit main
\```

Edits to `.claude/` files are committed normally in this repo. Push them to `claude-kit` when ready to share with other projects.
```

### How subtrees work (quick reference)

- `.claude/` files are **committed normally** in this repo — no special workflow for day-to-day edits
- `git subtree pull` merges upstream changes into your local `.claude/`
- `git subtree push` extracts `.claude/` history and pushes it to the claude-kit repo
- Unlike submodules, subtrees are fully embedded — no `.gitmodules`, no pointer files, works offline
- The subtree relationship is invisible to anyone who clones the repo — they just see a `.claude/` directory

### Post-adoption checklist

- [ ] `.claude/` directory present with agents, commands, skills, hooks
- [ ] `claude-kit` remote configured (`git remote -v`)
- [ ] CLAUDE.md updated with subtree section
- [ ] Trello MCP env vars set if using Trello integration (`TRELLO_API_KEY`, `TRELLO_TOKEN`)
- [ ] Run a quick test: try `/git-status` or `/show-backlog` to confirm commands work
- [ ] Review `settings.json` hooks — the branch protection hook blocks edits on `main`/`master` (disable if your project uses a different workflow)
