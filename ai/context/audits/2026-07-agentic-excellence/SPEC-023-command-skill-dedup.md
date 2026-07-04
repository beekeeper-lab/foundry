# SPEC-023: Collapse kit command/skill duplication to a single source

- **Priority:** P2
- **Effort:** M
- **Area:** kit
- **Depends on:** SPEC-002
- **Status:** Proposed

## Problem

Roughly fifteen kit capabilities exist twice: a skill (`skills/<name>/SKILL.md`) and a same-named command (`commands/<name>.md`) that is a thick prose duplicate rather than a thin dispatcher. Two sources of truth guarantee drift — and drift has already happened (the command copies of `git-status`/`deploy` reference the stale `.claude/kit` submodule path). Every future edit must be made twice or the pair silently diverges.

## Evidence

- Duplicated pairs (command file + skill dir with overlapping content): `backlog-consolidate`, `backlog-refinement`, `bg`, `commands`, `deploy`, `docs-update`, `generate-image`, `generate-screen`, `long-run`, `review-beans`, `run`, `telemetry-report`, `trello-add`, plus the `internal/` set (`build-traceability`, `compile-team`, `handoff`, `merge-bean`, `new-adr`, `new-bean`, `new-dev-decision`, `notes-to-stories`, `review-pr`, `scaffold-project`, `seed-tasks`, `trello-load`, `validate-config`, `validate-repo`).
- `.claude/shared/commands/git-status.md:26-34,96-118,151` and `.claude/shared/skills/deploy/SKILL.md:146-148` — operate on `.claude/kit`, but `.gitmodules` mounts the kit at `.claude/shared`; concrete drift artifact (also tracked in SPEC-007).
- `.claude/shared/commands/deploy.md` vs `.claude/shared/skills/deploy/SKILL.md` — the same multi-phase release process restated in both files.
- Command-only entries with no skill twin: `bug`, `chore`, `feature`, `implement`, `test-gen`, `tools`, `git-status`, `show-backlog`, `status-report`, `internal/spawn-bean`.

## Proposed change

1. **Adopt a decision rule** and record it in the kit README:
   - **Skill** = a workflow the model should be able to invoke on its own (or that carries scripts/reference files). The SKILL.md body is the single source of truth.
   - **Command** = a user-typed entry point only. A command that fronts a skill must be a ≤10-line stub: frontmatter (`description`, `argument-hint` — from SPEC-002) plus one instruction: "Invoke the `<name>` skill with `$ARGUMENTS`."
2. **For each duplicated pair:** keep the skill, reduce the command to a stub (preserving any command-only content by merging it into the skill first). Where the command adds nothing a user needs to type (e.g. `generate-image` — the skill auto-triggers), delete the command outright.
3. **For `internal/` pairs:** internal skills are invoked by other skills/agents, not typed by users — delete the `commands/internal/*.md` duplicates entirely unless a specific user-typed entry point is documented.
4. **Reassess command-only entries:** migrate `git-status`, `show-backlog`, `status-report` to skills with command stubs (they are model-invocable status workflows); leave `bug`/`chore`/`feature`/`test-gen` as commands (they are user-initiated planning entry points; content fixed separately in SPEC-024).
5. **Add a drift guard:** a small CI/check script (can live in the kit's `scripts/`) that fails when a `commands/<name>.md` body exceeds a size threshold while a `skills/<name>/` twin exists — enforcing the stub rule mechanically.

## Out of scope

- Adding frontmatter itself (SPEC-002).
- Fixing the `.claude/kit` path and other dangling references (SPEC-007).
- Rewriting `bug`/`feature`/`chore`/`test-gen` content (SPEC-024).
- The library's copies under `ai-team-library/claude/` — apply the same rule there in a follow-up once the kit pattern is proven.

## Acceptance criteria

- [ ] `file-contains:` kit README documents the command-vs-skill decision rule.
- [ ] `manual:` for every name present in both `commands/` and `skills/`, the command is a ≤10-line stub or has been deleted.
- [ ] `file:` `.claude/shared/commands/internal/` contains no file duplicating a `skills/internal/<name>/SKILL.md` workflow.
- [ ] `test:` (kit check script) no command stub references a skill that does not exist, and no oversized command shadows a skill.
- [ ] `manual:` `/deploy` and `/long-run` still work end-to-end via their stubs in a synced project.

## Files to touch

- `.claude/shared/commands/*.md`, `.claude/shared/commands/internal/*.md` (kit repo — via kit PR flow)
- `.claude/shared/skills/*/SKILL.md` (merge command-only content in)
- `.claude/shared/README.md`, `.claude/shared/scripts/` (drift-guard check)
- `ai-team-library/claude/` follow-up tracked separately
