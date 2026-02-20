# Task 01: Foundry Kit Architecture Spec

| Field | Value |
|-------|-------|
| **Task ID** | 01 |
| **Owner** | Architect |
| **Depends On** | — |
| **Status** | In Progress |
| **Started** | 2026-02-20 20:40 |
| **Completed** | — |
| **Duration** | — |

## Goal

Produce a comprehensive architecture specification for the Foundry Kit — a shared, versioned configuration baseline that eliminates config drift across projects consuming Claude Code configurations.

## Inputs

- Bean file: `ai/beans/BEAN-166-foundry-kit/bean.md`
- Current `.claude/` directory structure (for understanding what gets shared)
- Existing library structure in `ai-team-library/`
- Trello MCP integration patterns (`.claude/skills/`, `.claude/commands/`)

## Deliverable

A Markdown spec at `ai/outputs/architect/foundry-kit-spec.md` containing four sections:

### A) Options Analysis (at least 4 approaches)
For each approach (git submodule, git subtree, symlink, sync script/rsync/make, and optionally Claude Code plugin packaging):
- Pros and cons
- Failure modes
- Team workflow implications
- Remote server workflow
- Compatibility with existing Foundry scaffolding

### B) Recommended Architecture
- Repos involved (foundry-kit repo, foundry app repo, project repos)
- Folder layout for kit (agents/skills/commands/hooks + docs)
- How Foundry scaffolds new projects (pin version? pull kit? vendor snapshot?)
- How remote machine obtains kit (git clone? pinned tag? automation?)
- How updates flow from "edit in any repo" back to kit (PR process)
- Conflict handling policy + precedence rules (kit vs project override)
- Versioning strategy (tags, semver-ish, changelog)
- Compatibility strategy across Claude Code versions
- Trello integration architecture (where skills live, idempotent card creation, config storage, env parity)
- Mermaid diagrams for architecture and update flow

### C) Implementation Plan
- Step-by-step migration from current state
- Minimum viable scripts/commands (Makefile targets, CLI commands)
- CI checks to detect drift or accidental overrides
- Documentation outline
- Trello test plan (dry-run, sandbox board, rollback)

### D) Examples
- Project consuming kit v0.3.1, overriding /long-run only
- Remote server running 3 repos with same kit version
- /backlog-refinement generating 7 beans and creating/updating 7 Trello cards deterministically
- Emergency hotfix in kit and safe rollout

## Example Output

The spec should follow this structure:

```markdown
# Foundry Kit Architecture Spec

## 1. Options Analysis

### 1.1 Git Submodule
**Pros:** ...
**Cons:** ...
**Failure modes:** ...
**Team workflow:** ...
**Remote workflow:** ...

### 1.2 Git Subtree
...

## 2. Recommended Architecture

### 2.1 Overview
[Mermaid diagram]

### 2.2 Repo Layout
[Directory tree]

...

## 3. Implementation Plan

### 3.1 Migration Steps
1. ...

## 4. Examples

### 4.1 Version Pinning with Override
...
```

## Definition of Done

- [ ] Spec exists at `ai/outputs/architect/foundry-kit-spec.md`
- [ ] Contains options analysis for at least 4 approaches with pros/cons/failure modes
- [ ] Contains recommended architecture with Mermaid diagrams
- [ ] Contains implementation plan with step-by-step migration
- [ ] Contains all 4 required examples
- [ ] Trello integration architecture is documented (idempotency, config, env parity)
- [ ] Spec is opinionated — picks a default and justifies it
