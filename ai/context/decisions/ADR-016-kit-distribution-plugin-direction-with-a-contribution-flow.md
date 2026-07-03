# ADR-016: Kit Distribution — Plugin Direction with a Contribution Flow

| Field | Value |
|-------|-------|
| **Date** | 2026-07-03 |
| **Status** | Accepted |
| **Bean** | SPEC-026 (2026-07 agentic excellence audit) |
| **Deciders** | Gregg (direction), Claude (analysis) |

## Context

ClaudeKit distributes shared agentic assets (commands, skills, agents, hooks,
settings) to every beekeeper-lab repo via a git submodule at `.claude/shared`
plus `claude-sync.sh` symlink generation. The model is one-directional and
lossy: only Foundry may push upstream (`.claude/shared/README.md`), downstream
projects have no scripted contribution path, `claude-publish.sh` breaks on the
detached HEAD every submodule checkout produces, and the only local-adaptation
mechanism is whole-file override — which permanently forks the file away from
upstream improvements. Meanwhile Claude Code's plugin/marketplace system now
natively versions and distributes exactly this asset set, with install/update
semantics, making most of the bespoke sync apparatus redundant. SPEC-002
(frontmatter everywhere) removed the main packaging blocker.

## Options considered

- **A. Plugin + marketplace.** Package claude-kit as a Claude Code plugin
  (manifest bundling commands/skills/agents/hooks/MCP); beekeeper-lab hosts a
  marketplace repo. Consumers install/update with explicit versions;
  `claude-sync.sh`'s symlink layer, settings merge, and git-hook installer are
  deleted. Local `.claude/` files naturally layer over plugin content.
- **B. Keep submodule, fix the loop.** Apply SPEC-025 hardening and add
  contribution tooling. Lowest migration cost; keeps every known fragility
  (non-atomic sync, GNU-only symlinks, whole-file forks, manual pointer bumps).
- **C. Hybrid.** Plugin for the stable layer (safety hooks, media skills,
  generic commands); submodule/plain files for the fast-moving orchestration
  layer projects adapt per-repo.

## Decision

**Target Option A, staged through C.** The stable layer (media skills,
safety hooks, generic workflow commands/skills) is packaged as a plugin
first; the orchestration layer (agents, bean-workflow skills) follows once
per-project adaptation patterns are understood — what projects genuinely
customize stays project-local in `.claude/` regardless of mechanism.
Regardless of stage, the contribution flow ships now: `kit-contribute.sh`
creates a branch from kit `origin/main`, handles detached HEAD, and opens a
PR against beekeeper-lab/claude-kit — replacing the push-rights-only
`claude-publish.sh` path for downstream contributors. Override policy:
**patch upstream** is the default for fixes; **fork locally** requires a
`LOCAL-OVERRIDES.md` ledger entry so drift is visible.

## Consequences

- Version pinning becomes explicit (plugin version) instead of implicit
  (submodule SHA); consumers stop needing post-merge sync hooks.
- Foundry's generator gains a third distribution path during migration
  (SPEC-027 must define the canonical post-generation `.claude` contract so
  subtree, library-copy, and plugin modes converge on the same result).
- Air-gapped installs are unchanged (plugin source is still a git repo).
- Migration sequencing: (1) contribution flow + publish guard now; (2) plugin
  manifest for the stable layer; (3) one pilot consumer repo; (4) remaining
  repos + delete sync apparatus; (5) orchestration layer once stable.
- Rollback: the submodule path keeps working throughout; abandoning the
  migration strands only the plugin manifest.
