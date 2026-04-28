# Task 02: Implement `/spawn-task` Skill, Command, and Persona Wiring

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Materialize the `/spawn-task` command and its execution skill in both the
library (downstream-shipped) and Foundry's own claude-kit. Update Team-Lead
persona docs to name `/spawn-task` as the preferred per-task dispatch
mechanism. Additively integrate `/spawn-task` with `/long-run` so it can be
used without replacing existing in-process role-switching.

This task does **not** invent the dispatch mechanism — it implements what
Task 01's ADR fixed.

## Inputs

- `ai/beans/BEAN-270-spawn-task-command/bean.md` — scope and acceptance
- `ai/beans/BEAN-270-spawn-task-command/tasks/01-architect-spawn-task-adr.md` — ADR pointer
- `ai/context/decisions.md` — the ADR section authored in Task 01
- `ai-team-library/claude/commands/spawn-bean.md` — pattern reference (tmux dispatch)
- `ai-team-library/claude/skills/long-run/SKILL.md` — `/long-run` library version
- `.claude/skills/long-run/SKILL.md` — Foundry's `/long-run` (to integrate `/spawn-task` additively)
- `ai-team-library/personas/team-lead/persona.md` — library Team-Lead source
- `.claude/agents/team-lead.md` — Foundry Team-Lead

## Changes Required

1. **Library skill** at `ai-team-library/claude/skills/spawn-task/SKILL.md`:
   the canonical execution spec covering usage, both execution paths
   (tmux + Agent-tool), telemetry capture, error conditions, escape-hatch
   behavior. Long form (≥80 lines is fine — skill is canonical).
2. **Library command** at `ai-team-library/claude/commands/spawn-task.md`:
   ≤ 30 lines, names the skill, gives usage, points to the skill for
   detail. Conforms to the BEAN-249 rule.
3. **Foundry kit** files at the corresponding `.claude/shared/skills/spawn-task/SKILL.md`
   and `.claude/shared/commands/spawn-task.md` (or `.claude/local/...` per
   the kit's layering rules — pick one consistent location). Run
   `scripts/claude-sync.sh` to regenerate the symlinks.
4. **Library Team-Lead persona** (`ai-team-library/personas/team-lead/persona.md`)
   — add a short `## Per-Task Dispatch` subsection naming `/spawn-task` as
   the preferred mechanism, with one-line rationale.
5. **Foundry Team-Lead** (`.claude/agents/team-lead.md`) — same edit, kept
   in sync via the kit pattern (edit shared source if applicable).
6. **`/long-run` integration** — both the library `SKILL.md` and Foundry's
   shared `SKILL.md`: add a paragraph in Phase 4 ("Wave Execution") that
   `/spawn-task` is the preferred way to execute each task, with the
   in-process role-switching kept as a fallback for tiny tasks. Do not rip
   out existing behavior.

## Acceptance Criteria

- [ ] `ai-team-library/claude/skills/spawn-task/SKILL.md` exists with
      Process, Acceptance, Error Conditions, and a usage example for both
      execution paths.
- [ ] `ai-team-library/claude/commands/spawn-task.md` exists, ≤ 30 lines,
      points to the skill.
- [ ] Foundry's own `.claude/skills/spawn-task/SKILL.md` and
      `.claude/commands/spawn-task.md` are present (after `claude-sync.sh`).
- [ ] Library + Foundry Team-Lead persona docs reference `/spawn-task` as
      preferred per-task dispatch.
- [ ] `/long-run` skills (library + Foundry) reference `/spawn-task` as
      the preferred per-task dispatch with documented fallback.
- [ ] `uv run ruff check foundry_app/` passes (no Python touched but run
      the gate anyway).
- [ ] `uv run pytest` passes — no regressions.

## Definition of Done

- All files above written; line-count rule honored on the command file.
- Symlinks regenerated via `scripts/claude-sync.sh`.
- Tests + lint clean.
- Commit message: `BEAN-270 task 02: spawn-task skill, command, and integration`.
