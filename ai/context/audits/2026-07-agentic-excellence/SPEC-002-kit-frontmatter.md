# SPEC-002: Kit-wide frontmatter for skills, commands, and agents

- **Priority:** P0
- **Effort:** M
- **Area:** kit
- **Depends on:** none
- **Status:** Proposed

## Problem

Nothing in ClaudeKit or the library's `claude/` tree carries YAML frontmatter. Every skill starts `# Skill: X`, every command `# /x Command`, every agent with a plain H1. Claude Code's discovery is frontmatter-driven: skills need `name:`/`description:` to be registered for model-driven auto-invocation (the rich `## Trigger` sections in the media skills are stranded in the body where the router never sees them); commands need `description:`/`argument-hint:`/`allowed-tools:` to show usefully in the `/` menu, hint their `$ARGUMENTS`, and scope tools; agents need `name:`/`description:` to be discoverable at all.

This is a latent functional break, not cosmetics: `long-run.md:125`, `spawn-bean.md:125`, and `.claude/local/commands/spawn-task.md` launch workers with `claude --agent team-lead`, but with no `name: team-lead` frontmatter in `agents/team-lead.md` that flag has nothing to resolve against. The kit's core orchestration path depends on agents the harness likely never registers.

Two trees must be updated in lockstep: the kit submodule (`.claude/shared/`) and the library copy (`ai-team-library/claude/`) are separate file sets, and the asset copier distributes the library copy into generated projects in library-copy mode.

## Evidence

- Zero files matching `^---$` as line 1 across `.claude/shared/{skills,commands,agents}` and `ai-team-library/claude/` (verified by scan, 2026-07-03).
- Counts: `.claude/shared/skills` 30 `.md` (24 SKILL.md), `.claude/shared/commands` 37, `.claude/shared/agents` 5, `ai-team-library/claude/skills` 36, `ai-team-library/claude/commands` 44.
- `.claude/shared/skills/generate-image/SKILL.md:1` — `# Skill: Generate Image`; its `## Trigger` block (~line 12) holds exactly the content that belongs in a frontmatter `description:`.
- `.claude/shared/commands/bug.md:196` — consumes `$ARGUMENTS` with no `argument-hint`.
- `.claude/shared/commands/long-run.md:125`, `.claude/shared/commands/internal/spawn-bean.md:125` — `claude ... --agent team-lead` against agents with no `name:` field.
- `.claude/shared/agents/team-lead.md:1` — `# Team Lead`, no frontmatter.

## Proposed change

1. **Skills (kit + library):** prepend frontmatter to every `SKILL.md`:
   - `name:` = skill directory name.
   - `description:` = distilled from the existing `## Description` plus `## Trigger`/when-to-use text — one dense paragraph covering what it does and when to invoke it (this is what the router matches on). Keep the body; delete body sections that became redundant.
   - Exclude `_media_lib` (not a skill; see SPEC-025 for stopping its sync).
2. **Commands (kit + library):** prepend frontmatter to every command:
   - `description:` (one line, imperative), `argument-hint:` for every command consuming `$ARGUMENTS` (bug, feature, chore, implement, test-gen, bg, spawn-bean, …), `allowed-tools:` where scope is clear (e.g. `/git-status` and `/show-backlog` read-only: `Bash(git *), Read, Grep`), `model:` only where a cheap model is clearly sufficient (e.g. `/commands`, `/show-backlog` → haiku), and `disable-model-invocation: true` for operator-only commands (`/deploy`, `/long-run`, `/merge-bean`).
3. **Agents (kit):** prepend `name:` (exact string used by `--agent` call sites: `team-lead`, `ba`, `architect`, `developer`, `tech-qa`), `description:` (delegation-routing sentence from each agent's activation rules), and `tools:` where restriction is safe (ba: no Bash write access; tech-qa: read + Bash for test runs). Do not set `model:` in this spec.
4. **Consistency check:** add a small validation script (`scripts/check-kit-frontmatter.sh` or a pytest) asserting every SKILL.md/command/agent in both trees parses YAML frontmatter with the required keys — so new assets can't regress.
5. Publish via the normal kit flow (`scripts/claude-publish.sh`) so downstream repos pick it up.

## Out of scope

- Deduplicating command↔skill twins (SPEC-023) — but sequence this spec first; dedup is easier when frontmatter marks which side is canonical.
- Generated-agent frontmatter (SPEC-001).
- Rewriting wrong-stack command bodies (SPEC-024).

## Acceptance criteria

- [ ] `test: tests/test_kit_frontmatter.py` — every `SKILL.md`, command `.md`, and agent `.md` in `.claude/shared/` and `ai-team-library/claude/` starts with valid YAML frontmatter containing `name`+`description` (skills, agents) or `description` (commands).
- [ ] `file-contains: .claude/shared/agents/team-lead.md` — frontmatter `name: team-lead`.
- [ ] `file-contains: .claude/shared/skills/generate-image/SKILL.md` — frontmatter `description:` mentions trigger conditions (generate/create/illustrate an image).
- [ ] `manual:` in a synced checkout, `/` menu shows descriptions and argument hints for bug/feature/chore; a `claude --agent team-lead` invocation resolves.
- [ ] `manual:` kit change published to claude-kit and submodule pointer bumped.

## Files to touch

- `.claude/shared/skills/*/SKILL.md` (24), `.claude/shared/commands/**/*.md` (37), `.claude/shared/agents/*.md` (5)
- `ai-team-library/claude/skills/*/SKILL.md` (35+), `ai-team-library/claude/commands/**/*.md` (44)
- `scripts/check-kit-frontmatter.sh` or `tests/test_kit_frontmatter.py` (new)
