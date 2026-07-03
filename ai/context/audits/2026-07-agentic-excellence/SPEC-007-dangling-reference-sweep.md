# SPEC-007: Repo-wide dangling reference sweep

- **Priority:** P0
- **Effort:** M
- **Area:** kit+library
- **Depends on:** none
- **Status:** Proposed

## Problem

The kit and library are dense with cross-references — commands referencing commands, agents referencing skills, contracts referencing template files — and a large share of them dangle. Agents are told to run commands that don't exist (`/vdd` is referenced nine times and is central to the merge gate story; there is no `/vdd` command file anywhere). Shared agents reference commands that exist only in Foundry's project-local layer, so every downstream repo inherits instructions it cannot execute. Ops tooling still points at the pre-rename submodule path `.claude/kit`, so `/git-status`'s submodule section always reports "not configured" and `/deploy` never syncs the kit. The library's artifact-type registry points at template paths that all broke when personas were tiered under `core/`. Five persona outputs and the pipeline doc still reference the retired `stacks/` directory layout.

Each item is small; together they mean an agent following its own instructions hits dead ends constantly, and the class of rot will keep recurring without a mechanical check.

## Evidence

- **Stale submodule path:** `.claude/shared/commands/git-status.md:26-33` and `.claude/shared/skills/deploy/SKILL.md:146-148` operate on `.claude/kit`; `.gitmodules` mounts the kit at `.claude/shared`.
- **Missing commands:** `/vdd` (9 refs, e.g. `.claude/shared/agents/team-lead.md:34`, `long-run.md:48`), `/orchestration-report` (`team-lead.md:35`), `/pick-bean` (`team-lead.md:22`, `spawn-bean.md:171,221`), `/bean-status` (`team-lead.md:23`, `spawn-bean.md:412`), `/new-work` (`team-lead.md:29`) — no backing file in shared or local.
- **Namespace mismatch:** `/close-loop` referenced ~27× un-namespaced; the skill lives at `skills/internal/close-loop/` (resolves as `/internal:close-loop`).
- **Shared→local leakage:** `team-lead.md:25,329` references `/spawn-task` and `/health-check`, which exist only in `.claude/local/` (Foundry-only) yet ship in the shared agent to every project.
- **Registry template paths:** `ai-team-library/contracts/artifact-types.yml:73,88,100,143,160,175,189,204,215,229` — all `personas/<id>/templates/...`, missing the `core/` tier; actual files are `personas/core/<id>/templates/...`.
- **Retired `stacks/` layout:** `ai-team-library/workflows/foundry-pipeline.md:101`; `personas/core/developer/outputs.md:174`; `personas/extended/{mobile-developer:234,data-analyst:182,data-engineer:174,sales-engineer:213}/outputs.md`.
- **Tier-less cross-refs:** `personas/core/tech-qa/persona.md:48` → `personas/code-quality-reviewer/persona.md` (needs `extended/`); `personas/extended/code-quality-reviewer/persona.md:56` → `personas/tech-qa/persona.md` (needs `core/`).
- **Inconsistent persona-path validation between skills:** `ai-team-library/claude/skills/spawn-task/SKILL.md:62-63,196-197,238` validates untiered `personas/<persona>/persona.md`; `claude/skills/handoff/SKILL.md:38-40,234` uses tiered paths. At most one is correct.

## Proposed change

1. **Fix the submodule path:** replace `.claude/kit` with `.claude/shared` in `git-status.md` and `deploy/SKILL.md` (kit + any library copies).
2. **Resolve missing commands** — for each, pick create-or-repoint:
   - `/vdd` and `/orchestration-report`: create thin command files delegating to the existing skills (`skills/vdd`, telemetry-report skill) so agent instructions become executable.
   - `/pick-bean`, `/bean-status`, `/new-work`: either create thin commands over the corresponding team-lead skill flows or rewrite the references to the commands that actually exist (`/show-backlog`, `/review-beans`). Decide per reference; no reference may remain pointing at nothing.
3. **`/close-loop` namespace:** either move the skill out of `internal/` or update all ~27 references to the namespaced form. Prefer moving it (it's invoked constantly; the `internal/` grouping buys nothing).
4. **De-localize shared agents:** move `/spawn-task` (and `/health-check` if generally useful) into the shared kit, or rewrite shared-agent references to describe the capability without naming a local-only command. ADR-008 makes `/spawn-task` core to the process — promoting it to shared is the coherent choice.
5. **Library path fixes:** add `core/` to every non-null `template-path` in `artifact-types.yml`; replace `stacks/<stack>/conventions.md` with `expertise/<id>/conventions.md` in the five outputs.md files; update `foundry-pipeline.md` terminology and extension-point path; fix the two tier-less persona cross-refs; align `spawn-task/SKILL.md` persona paths to the tiered convention used by `handoff/SKILL.md`.
6. **Recurrence guard:** add `tests/test_reference_integrity.py` that (a) extracts backtick-quoted repo-relative paths from library contracts/personas/workflows and kit commands/skills/agents and asserts existence; (b) extracts `/command` tokens from kit agents/skills and asserts a backing command or skill file exists (with an allowlist for prose false-positives). Run in CI with the normal suite.

## Out of scope

- Command↔skill content deduplication (SPEC-023).
- Generated-output link correctness (SPEC-006).
- Creating real enforcement for `/vdd` at merge time (SPEC-008) — here we only make the command resolvable.

## Acceptance criteria

- [ ] `test: tests/test_reference_integrity.py` — passes; deliberately breaking a template-path fails it.
- [ ] `file-contains: .claude/shared/commands/git-status.md` — no occurrence of `.claude/kit`.
- [ ] `file: .claude/shared/commands/vdd.md` — exists (thin delegate), or all `/vdd` references repointed.
- [ ] `file-contains: ai-team-library/contracts/artifact-types.yml` — every non-null template-path starts `personas/core/` or `personas/extended/` or `ai/`.
- [ ] `manual:` grep for `stacks/` in `ai-team-library/` returns only historical/changelog mentions.
- [ ] `test: uv run pytest` — full suite passes.

## Files to touch

- `.claude/shared/commands/git-status.md`, `.claude/shared/skills/deploy/SKILL.md`, `.claude/shared/agents/team-lead.md`, new thin commands under `.claude/shared/commands/`
- `.claude/local/commands/spawn-task.md` (promote to shared)
- `ai-team-library/contracts/artifact-types.yml`, `ai-team-library/workflows/foundry-pipeline.md`, five `outputs.md` files, `personas/core/tech-qa/persona.md`, `personas/extended/code-quality-reviewer/persona.md`, `ai-team-library/claude/skills/spawn-task/SKILL.md` (library-change approval)
- `tests/test_reference_integrity.py` (new)
