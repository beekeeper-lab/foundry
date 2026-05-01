# Task 01: Implement Orchestration Telemetry — Template, Hook, Skill, Command, /spawn-task & /handoff Hooks

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 01:05 |
| **Completed** | 2026-05-01 01:12 |
| **Duration** | 7m |

## Goal

Add a per-bean Orchestration Telemetry block to the bean template,
extend the telemetry-stamp hook to populate `Personas activated` and
`Dispatch mode` automatically, teach `/spawn-task` to record dispatch
mode and Tech-QA→Developer bounces, teach `/handoff` to count bounces,
and ship a new library `/orchestration-report` skill+command that
aggregates the new fields across recent Done beans.

## Inputs

- `ai/beans/BEAN-278-orchestration-telemetry-report/bean.md` — bean
  spec. Read **Scope — In Scope**, **Acceptance Criteria**, **Notes**.
  The exact Orchestration Telemetry block format is in the In Scope
  section; copy it verbatim into the template.
- `ai/beans/_bean-template.md` (96 lines) — append the new section
  immediately after the existing Telemetry section (after line 96).
- `.claude/hooks/telemetry-stamp.py` (1337 lines) — extend to
  populate `Personas activated` and `Dispatch mode`. **Read targeted
  sections only**:
  - The function that finds and updates the existing Telemetry table
    (search for "Telemetry" / "Total Tokens" / similar anchors).
  - `ensure_metadata_field` (per MEMORY.md, exists for idempotent
    additions). Reuse it.
  - The session-resolution helper (`find_session_jsonl` per MEMORY.md).
  - **Do not refactor the hook**. Add only what the bean requires.
- `ai-team-library/claude/skills/spawn-task/SKILL.md` (202 lines) —
  add: a `Dispatch mode:` line that the worker writes to the bean's
  Orchestration Telemetry block when dispatch happens, and a
  bounce-counter step (Tech-QA opening a downstream task pointing back
  at Developer mid-bean increments the bean's `Bounces` counter).
- `ai-team-library/claude/skills/handoff/SKILL.md` (just rewritten by
  BEAN-276) — add a one-paragraph bounce-counter step (when a
  Tech-QA→Developer handoff is opened mid-bean, increment the bean's
  `Bounces` counter).
- The data shape: `Personas activated` should be the comma-separated
  set of persona ids that actually executed at least one task in the
  bean. Source the data from the existing per-task Telemetry rows
  (the hook already populates the Owner column).
- `Dispatch mode`: `in-process` (Agent-tool path), `tmux-worker`
  (worktree path), or `mixed`. Source from a per-task marker the
  worker writes (or, if the worker can't write it, infer from
  presence of a `/tmp/agentic-task-*` worktree at task-completion
  time — best-effort).
- New skill location:
  `ai-team-library/claude/skills/orchestration-report/SKILL.md`.
  Aggregates Orchestration Telemetry across all Done beans within a
  date window (default: 30 days). Computes: average bounces by
  persona-set, average cost-per-bean by persona count, contract
  violations caught, escape-hatch trend. Outputs
  `ai/outputs/team-lead/orchestration-report-YYYY-MM-DD.md`.
- New library command:
  `ai-team-library/claude/commands/orchestration-report.md` (≤30
  lines per BEAN-249).

## Acceptance Criteria

- [ ] `ai/beans/_bean-template.md` carries the Orchestration
      Telemetry section verbatim from the bean's In Scope spec, after
      the existing Telemetry block.
- [ ] `.claude/hooks/telemetry-stamp.py` populates `Personas activated`
      and `Dispatch mode` automatically when a bean's status flips to
      `Done`. Idempotent (re-running doesn't duplicate). Other fields
      (Bounces, Scope changes, Contract violations, Escape-hatch
      invocations) are persona-recorded — the hook may stamp them with
      `0` as the default if not already present, but should not
      overwrite a non-zero persona-recorded value.
- [ ] `ai-team-library/claude/skills/spawn-task/SKILL.md` describes
      how the worker writes its dispatch mode to the bean's
      Orchestration Telemetry block on task completion.
- [ ] `ai-team-library/claude/skills/spawn-task/SKILL.md` and
      `ai-team-library/claude/skills/handoff/SKILL.md` both describe
      the bounce-counter increment for Tech-QA→Developer hand-back
      mid-bean.
- [ ] `ai-team-library/claude/skills/orchestration-report/SKILL.md`
      exists with the standard skill structure (Description, Trigger,
      Inputs, Process, Outputs, Quality Criteria, Error Conditions,
      Dependencies). It must specify how the report is computed
      (which beans are scanned, the date-window default, the
      aggregations performed, the verdict-paragraph template).
- [ ] `ai-team-library/claude/commands/orchestration-report.md` is
      ≤30 lines (per BEAN-249) — thin trigger only.
- [ ] Lint clean: `uv run ruff check foundry_app/`.

## Definition of Done

- All listed files added/modified.
- Telemetry hook unit-tested manually on a fixture bean (don't
  destroy real telemetry; either set `dryrun` or test against a
  copy).
- Lint clean.
- Status set to `Done`.

## Notes

**The telemetry hook is 1337 lines and historically tricky.** Per
MEMORY.md (`BEAN-235/236/237` telemetry beans). Add only what's
required; do not refactor. Reuse `ensure_metadata_field` and
`find_session_jsonl` rather than reinventing.

**No backfill.** New Orchestration Telemetry only applies to Done
beans going forward. Existing beans without the block stay as-is.
The hook should silently skip beans whose Telemetry section doesn't
have the new Orchestration Telemetry block.

**Dispatch-mode fallback.** If `/spawn-task` cannot reliably mark
its dispatch mode (e.g., the worker exited before writing), the
orchestrator's view (presence/absence of `/tmp/agentic-task-*`
worktrees at completion time, OR the bean's mode of-record stamped
on bean-pick) is acceptable as a fallback. Document the rule in
the SKILL.md.

**Out of scope:**
- Backfilling Orchestration Telemetry for historical beans.
- Real-time dashboards.
- Per-task orchestration telemetry (the bean is the unit).
- Cost attribution beyond what task telemetry already captures.

**Skill placement.** The orchestration-report skill goes in
`ai-team-library/` (the canonical library) per ADR-009 — not in
`.claude/skills/` directly. Foundry's own `.claude/skills/` will
pick it up via the symlink layer (`scripts/claude-sync.sh`).
