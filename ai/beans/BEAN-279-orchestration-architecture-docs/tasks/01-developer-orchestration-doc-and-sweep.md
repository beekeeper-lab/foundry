# Task 01: Write `orchestration-architecture.md` + ADR-015 + Documentation Sweep

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-05-01 01:25 |
| **Completed** | 2026-05-01 01:34 |
| **Duration** | 9m |

## Goal

Synthesize the BEAN-270..278 orchestration cluster into:

1. A canonical long-form architectural document at
   `ai/context/orchestration-architecture.md`.
2. An ADR (ADR-015) in `ai/context/decisions.md` with a pointer to
   the long-form doc.
3. A sweep update of every active-behavior document so they reflect
   what BEAN-270..278 changed.

## Inputs

- `ai/beans/BEAN-279-orchestration-architecture-docs/bean.md` — bean
  spec with the full sweep checklist in **Scope — In Scope**.
- The 9 cluster bean files (read just the headers + Goal + In Scope
  for each — do not read every detail; you need synthesis-level
  understanding):
  - `ai/beans/BEAN-270-spawn-task-command/bean.md`
  - `ai/beans/BEAN-271-library-persona-tiering/bean.md`
  - `ai/beans/BEAN-272-validate-task-inputs-hook/bean.md` (find via `ls ai/beans | grep 272`)
  - `ai/beans/BEAN-273-persona-contracts/bean.md` (find via grep)
  - `ai/beans/BEAN-274-contract-graph-validator/bean.md`
  - `ai/beans/BEAN-275-acceptance-criteria-ownership/bean.md` (find)
  - `ai/beans/BEAN-276-role-aware-handoff-schemas/bean.md`
  - `ai/beans/BEAN-277-vdd-gate-skill/bean.md` (find)
  - `ai/beans/BEAN-278-orchestration-telemetry-report/bean.md`
- Existing ADRs as style reference: read just the headings of recent
  ADRs (ADR-013 / ADR-014) in `ai/context/decisions.md` — the next
  number is **ADR-015**.

## Long-form doc structure (target ~250-400 lines)

```
# Orchestration Architecture

## Three Principles
### 1. Supervisor Pattern (BEAN-270, /spawn-task)
### 2. Context Engineering (BEAN-272 Inputs validation, BEAN-273/274 contracts)
### 3. Specialist Contracts (BEAN-271 tiering, BEAN-273 produces/consumes, BEAN-276 typed handoffs)

## Architecture-Aware Evaluation (BEAN-278)
How `/orchestration-report` answers "is the orchestration paying for itself?"

## Bean Lifecycle Under This Architecture
Sequence: bean-pick → /spawn-task → contract validation at compose
time → typed handoff between persona tasks → /vdd at bean close.

## Cross-References
Pointers (one-line each) to: bean-workflow.md, vdd-policy.md,
ADR-008/013/014/015, agent files, /spawn-task & /handoff &
/orchestration-report skills.
```

Use text-based diagrams (mermaid or ASCII) — no image generation.

## "Always check" docs to sweep (from MEMORY.md)

For each, read it, identify what BEAN-270..278 changed about the
behavior it documents, and edit the impacted sections only:

- `CLAUDE.md` — link orchestration-architecture.md; reflect the new
  /spawn-task and /orchestration-report commands; update Beans
  Workflow section if affected.
- `README.md` — top-level pipeline / lifecycle paragraph reflects
  the new orchestration model.
- `ai/context/bean-workflow.md` — incorporate /spawn-task dispatch,
  Inputs validation, typed handoffs, programmatic VDD.
- `ai/context/project.md` — module map updates for new files
  (validator.py extensions, contract_validator if any).
- `.claude/agents/team-lead.md` — orchestration rules name
  /spawn-task, contract checks, AC ownership rule, VDD gate.
- `.claude/agents/{ba,architect,developer,tech-qa}.md` — Scope
  Boundaries (BEAN-275), produces/consumes (BEAN-273), context
  bundle.
- `.claude/skills/long-run/SKILL.md` and
  `.claude/commands/long-run.md` — describe how /long-run
  integrates with /spawn-task.
- `CHANGELOG.md` — add a v1.1.0 entry for the orchestration cluster.

## "Check when relevant" — only if directly impacted

- `ai-team-library/README.md` — persona table reflects tiering
  (BEAN-271); add /orchestration-report and /spawn-task to the
  commands list; mention contracts.
- The MEMORY.md documentation checklist itself — add
  `ai/context/orchestration-architecture.md`.

## Acceptance Criteria

- [ ] `ai/context/orchestration-architecture.md` exists and covers
      the three principles + evaluation methodology with bean references.
- [ ] ADR-015 entry in `ai/context/decisions.md` points to the
      long-form doc.
- [ ] Every "Always check" doc above has been reviewed and updated
      where impacted by BEAN-270..278.
- [ ] `MEMORY.md`'s documentation checklist now includes
      `ai/context/orchestration-architecture.md`.
- [ ] Library README's persona table reflects tiering (BEAN-271).
- [ ] `CHANGELOG.md` has the cluster entry.
- [ ] `uv run pytest` passes (full suite).
- [ ] `uv run ruff check foundry_app/` clean.

## Definition of Done

- All listed files added/modified.
- Lint clean; tests pass.
- Status set to `Done`.

## Notes

**Do not over-edit.** Many docs already touch the right concepts —
your job is to make the references consistent with the cluster's
final state, not to rewrite the docs.

**Out of scope:**
- Slide decks / external publication.
- Backfilling other historical bean records.
- Restructuring `ai/context/` beyond adding the new doc.
- Diagrams as image files (text-based diagrams only).

**MEMORY.md is in `~/.claude/projects/...` (project memory)** — not
in the foundry repo. Update the documentation checklist section in
that file. Use the Edit tool with the absolute path; the file is
gitignored from the foundry repo's perspective.

**Context discipline.** Read each doc before editing it; do not
edit blind. But don't re-read docs already in your context. Use
targeted reads (offset/limit, grep-then-read).

**One commit at the end** — message:
`BEAN-279 task 01: orchestration-architecture.md + ADR-015 + active-behavior doc sweep`
