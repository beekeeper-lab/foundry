# Task 01: Create claude-kit Repo and Set Up Git Subtree

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-21 19:57 |
| **Completed** | — |
| **Duration** | — |

## Goal

Create the `claude-kit` GitHub repository from Foundry's current `.claude/` contents, then convert Foundry's `.claude/` into a git subtree linked to the new repo.

## Inputs

- `.claude/` directory — current contents to extract
- `CLAUDE.md` — needs subtree workflow instructions added
- Bean notes — subtree rationale and alias patterns

## Changes Required

### Step 1: Create claude-kit repo on GitHub

1. Create a new repo `beekeeper-lab/claude-kit` on GitHub (private, no default files)
2. Initialize it locally in a temp directory
3. Copy all `.claude/` contents into the repo root
4. Commit and push to GitHub

### Step 2: Set up subtree in Foundry

1. Add `claude-kit` as a remote in Foundry: `git remote add claude-kit git@github.com:beekeeper-lab/claude-kit.git`
2. Verify the current `.claude/` matches what was pushed to `claude-kit`
3. Set up the subtree relationship using `git subtree add` (or document that the prefix is already in place since `.claude/` was the source)

### Step 3: Test subtree operations

1. Verify `git subtree push --prefix=.claude claude-kit main` works
2. Verify `git subtree pull --prefix=.claude claude-kit main --squash` works
3. Verify Claude Code reads skills, commands, and agents correctly

### Step 4: Document

1. Add subtree workflow section to `CLAUDE.md`
2. Document convenience aliases in bean notes

## Acceptance Criteria

- [ ] `claude-kit` repo exists on GitHub with `.claude/` contents
- [ ] `claude-kit` remote added to Foundry
- [ ] `git subtree push` works
- [ ] `git subtree pull` works
- [ ] Claude Code still reads all skills/commands/agents correctly
- [ ] CLAUDE.md updated with subtree workflow
- [ ] All tests pass
- [ ] Lint clean

## Definition of Done

The `claude-kit` repo is live, the subtree relationship is established, push/pull both work, and the workflow is documented.
