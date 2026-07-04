# Agentic Excellence Audit — 2026-07

**Scope:** the quality of what Foundry produces — generated projects, the agentic process, the AI teams, and the commands/skills/hooks distributed via ClaudeKit. Python app quality was audited only where it determines output quality.

**Method:** five parallel deep audits (persona/process library, expertise packs, ClaudeKit `.claude/shared` assets, generation pipeline + sample outputs, agentic process vs. ~294 real completed beans), synthesized into 29 specs. Each spec is self-contained and implementable independently unless a dependency is noted.

**How to act on these:** each spec can be promoted to a bean via `/backlog-refinement` (suggested bean title = spec title). Priorities: **P0** = shipped functionality is broken or silently inert; **P1** = the agentic process/teams are materially weaker than designed; **P2** = content quality, coverage, and maintainability.

## Headline findings

1. **Generated `.claude/agents/*.md` are not valid Claude Code subagents** — no YAML frontmatter, so they never register. The product's core promise doesn't function. Same gap across every kit skill, command, and agent.
2. **19 of 42 expertise packs compile to nothing** (no `conventions.md` — the only file the compiler reads), including every compliance and cloud pack. ~87% of authored expertise lines are unreachable by any generation path. The validator does not catch it.
3. **The quality gates are honor-system prose, not machinery** — across ~294 completed beans: 1 handoff packet, 3 VDD reports, ~3 comprehension notes, 0 telemetry roll-ups. The two hooks that ARE enforced include a data-corrupting Duration bug (branch-age instead of Started→Completed).
4. **The generator degrades its own inputs** — it overwrites the library's good `settings.json` hooks with an often-empty file; the flagship examples select `hook-policy`, which renders zero hooks silently; extended personas ship broken links; seeded acceptance criteria can never pass `/vdd`.
5. **The ClaudeKit loop is one-directional and fragile** — only Foundry can push upstream; local overrides fork files permanently; `claude-sync.sh` is destructive and non-atomic; a plugin/marketplace distribution would replace most of it.

## Spec index

### P0 — Broken or silently inert functionality

| Spec | Title | Area | Effort |
|---|---|---|---|
| [SPEC-001](SPEC-001-generated-agent-frontmatter.md) | Generated agents: emit valid Claude Code subagent frontmatter | pipeline | M |
| [SPEC-002](SPEC-002-kit-frontmatter.md) | Kit-wide frontmatter for skills, commands, and agents | kit | M |
| [SPEC-003](SPEC-003-expertise-compile-contract.md) | Expertise compilation contract: no silently dead packs | expertise | L |
| [SPEC-004](SPEC-004-hook-generation-reconciliation.md) | Hook generation reconciliation: hook-policy no-op, settings.json overwrite, render validation | pipeline | M |
| [SPEC-005](SPEC-005-telemetry-integrity.md) | Telemetry integrity: fix Duration computation and checkpoint race | kit | S |
| [SPEC-006](SPEC-006-extended-persona-path-bugs.md) | Fix extended-persona path bugs in compiler and agent writer | pipeline | S |
| [SPEC-007](SPEC-007-dangling-reference-sweep.md) | Repo-wide dangling reference sweep | kit+library | M |

### P1 — Make the agentic process real

| Spec | Title | Area | Effort |
|---|---|---|---|
| [SPEC-008](SPEC-008-enforce-gates-with-hooks.md) | Enforce VDD and handoff gates with hooks, not prose | kit+process | M |
| [SPEC-009](SPEC-009-close-the-feedback-loop.md) | Close the feedback loop: telemetry aggregation, retros, memory | process | M |
| [SPEC-010](SPEC-010-native-task-dispatch.md) | Rebuild task dispatch on the native Claude Code task system | process | L |
| [SPEC-011](SPEC-011-persona-model-tool-tiering.md) | Per-persona model and tool tiering in the composition schema | pipeline | M |
| [SPEC-012](SPEC-012-expertise-in-member-prompts.md) | Compile expertise into member prompts with token budgeting | pipeline | M |
| [SPEC-013](SPEC-013-seeder-vdd-ready-acs.md) | Seeder emits VDD-verifiable acceptance criteria | pipeline | S |
| [SPEC-014](SPEC-014-safety-hook-hardening.md) | Safety hook hardening: false positives, defense in depth, honest claims | kit | M |
| [SPEC-015](SPEC-015-quality-gate-hooks.md) | Implement or de-scope the documented quality-gate hooks | kit | M |
| [SPEC-016](SPEC-016-safetyconfig-to-permissions.md) | Wire SafetyConfig to generated permissions or remove it | pipeline | M |
| [SPEC-017](SPEC-017-contracts-for-extended-personas.md) | Extend typed contracts to extended personas | library | L |
| [SPEC-018](SPEC-018-workflow-ownership-gaps.md) | Close workflow ownership gaps: merge, deploy, taxonomy routing | library | S |

### P2 — Content quality, coverage, maintainability

| Spec | Title | Area | Effort |
|---|---|---|---|
| [SPEC-019](SPEC-019-expertise-frontmatter.md) | Expertise pack frontmatter and structural normalization | expertise | M |
| [SPEC-020](SPEC-020-expertise-freshness.md) | Expertise freshness and cross-pack contradiction pass | expertise | M |
| [SPEC-021](SPEC-021-new-expertise-packs.md) | New expertise packs: LLM/agent-app development and modern web | expertise | L |
| [SPEC-022](SPEC-022-mcp-opt-in.md) | MCP servers become composition-driven and opt-in | pipeline+kit | M |
| [SPEC-023](SPEC-023-command-skill-dedup.md) | Collapse kit command/skill duplication to a single source | kit | M |
| [SPEC-024](SPEC-024-fix-wrong-stack-commands.md) | Replace wrong-stack bug/feature/chore/test-gen commands | kit | S |
| [SPEC-025](SPEC-025-claude-sync-robustness.md) | claude-sync.sh robustness and portability | kit | M |
| [SPEC-026](SPEC-026-kit-distribution-evolution.md) | Kit distribution evolution: plugin path and contribution loop | kit | L |
| [SPEC-027](SPEC-027-unify-distribution-modes.md) | Unify subtree and library-copy distribution modes | pipeline | M |
| [SPEC-028](SPEC-028-readme-output-alignment.md) | Align README and sample projects with actual output | docs | S |
| [SPEC-029](SPEC-029-process-spec-diet.md) | Process specification diet: dedupe, split ADRs, enforce-or-drop ceremony | process | M |

## Suggested sequencing

1. **Wave 1 (unblocks everything):** SPEC-001, 002, 003 — frontmatter + expertise compile contract. These convert existing authored content from inert to live.
2. **Wave 2 (correctness):** SPEC-004, 005, 006, 007, 013 — the generator stops degrading its inputs; telemetry becomes trustworthy.
3. **Wave 3 (process):** SPEC-008, 009, 010 — gates become machinery; the loop learns; dispatch goes native.
4. **Wave 4 (power):** SPEC-011, 012, 014–018.
5. **Wave 5 (polish/coverage):** SPEC-019–029. SPEC-026 (plugin distribution) deserves an ADR before implementation.
