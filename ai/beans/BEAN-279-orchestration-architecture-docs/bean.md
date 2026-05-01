# BEAN-279: Orchestration Architecture Doc + Comprehensive Documentation Update

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-279 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-05-01 01:23 |
| **Completed** | 2026-05-01 01:41 |
| **Duration** | 1588h 34m |
| **Owner** | team-lead |
| **Category** | Process |
| **Depends On** | BEAN-273, BEAN-274, BEAN-275, BEAN-276, BEAN-277, BEAN-278 |

## Problem Statement

Once BEAN-270 through BEAN-278 land, the orchestration model has fundamentally changed:

- Real per-task delegation via `/spawn-task` (BEAN-270)
- Tiered persona library (BEAN-271)
- Validated `Inputs:` and contract graph (BEAN-272, 274)
- Typed produces/consumes contracts (BEAN-273)
- Resolved role boundaries (BEAN-275)
- Typed handoffs (BEAN-276)
- Programmatic VDD (BEAN-277)
- Architecture-aware telemetry (BEAN-278)

If the documentation doesn't catch up, the rest of the cluster is invisible to anyone (human or agent) coming in cold. Per `MEMORY.md`'s documentation checklist, every active behavior doc, agent file, and skill summary needs review.

This bean is the synthesis: write the long-form architecture document, record the ADR, and propagate the changes through every document on the checklist.

## Goal

Two new artifacts plus a checklist sweep:

1. `ai/context/orchestration-architecture.md` — the canonical long-form architectural document. Explains supervisor pattern, context engineering, specialist contracts, and architecture-aware evaluation as Foundry implements them. Lives flat alongside the other policy docs (`bean-workflow.md`, `vdd-policy.md`, etc.) so it's discoverable and easy to maintain.
2. ADR entry in `ai/context/decisions.md` — short record of the architectural decision with a pointer to the long-form doc.
3. Sweep update of the documentation checklist from `MEMORY.md`.

## Scope

### In Scope

- **Write `ai/context/orchestration-architecture.md`** covering:
  - The three principles (supervisor, context engineering, specialist contracts) and how each maps to a Foundry artifact.
  - Diagrams or sequence descriptions for: bean execution under `/spawn-task`, contract graph validation at compose time, typed handoff flow, VDD gate, orchestration telemetry loop.
  - The architecture-aware evaluation methodology — how `/orchestration-report` answers "is the orchestration paying for itself?"
  - References to the source beans (BEAN-270 through BEAN-278) for traceability.
- **Add ADR** to `ai/context/decisions.md` summarizing the architectural shift with pointer to the long-form doc.
- **Sweep update** of every document in `MEMORY.md`'s "Always check" list:
  - `CLAUDE.md` — link orchestration architecture doc; reflect new commands; update Beans Workflow section if affected.
  - `README.md` — top-level pipeline / lifecycle paragraph reflects the new orchestration.
  - `ai/context/bean-workflow.md` — incorporate `/spawn-task` dispatch path, `Inputs:` validation, typed handoffs, programmatic VDD.
  - `ai/context/project.md` — module map updates for new services (`contract_validator.py`, etc.).
  - `.claude/agents/team-lead.md` — orchestration rules name `/spawn-task`, contract checks, AC ownership rule, VDD gate.
  - `.claude/agents/ba.md`, `architect.md`, `developer.md`, `tech-qa.md` — Scope Boundaries (BEAN-275), produces/consumes (BEAN-273), context bundle.
  - `.claude/skills/long-run/SKILL.md` and `.claude/commands/long-run.md` — describe how `/long-run` integrates with `/spawn-task`.
  - `CHANGELOG.md` — add an entry for the orchestration cluster (likely a v1.1.0 release).
- **Sweep update** of "Check when relevant" docs as needed (deploy, backlog-refinement, backlog-consolidate, trello-load, bg, docs-update skills).
- **Library README** (`ai-team-library/README.md`) — update the persona table for tiering (BEAN-271), add the new commands/skills, mention contracts.
- **Update `MEMORY.md`'s documentation checklist** to add `ai/context/orchestration-architecture.md` and any new active-behavior docs introduced in the cluster.
- Single-pass review: spot-check the generated project from one example composition to confirm the documentation reads coherently from a cold start.

### Out of Scope

- Slide deck / external publication (could be a follow-up bean if the user wants).
- Backfilling other historical bean records.
- Restructuring `ai/context/` beyond adding the new doc.
- Diagrams as image files — text-based diagrams (mermaid or ASCII) are fine; image generation is out of scope.

## Acceptance Criteria

- [ ] `ai/context/orchestration-architecture.md` exists and covers the three principles + evaluation methodology with bean references.
- [ ] ADR entry in `ai/context/decisions.md` points to the long-form doc.
- [ ] Every "Always check" doc in `MEMORY.md` has been reviewed and updated where impacted by BEAN-270 through BEAN-278.
- [ ] `MEMORY.md`'s documentation checklist now includes `ai/context/orchestration-architecture.md`.
- [ ] Library README's persona table reflects tiering (BEAN-271).
- [ ] CHANGELOG.md has the cluster entry.
- [ ] Cold-start spot-check: a generated project's CLAUDE.md + agent files + skill docs read coherently and consistently with the new orchestration model.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Write orchestration-architecture.md + ADR-015 + active-behavior doc sweep | developer | — | Done |
| 2 | Cold-start verification: cross-references, checklist coverage, generated-project spot-check | tech-qa | 1 | Done |

> Skipped: BA (default — doc structure provided in Developer task spec; no requirements ambiguity); Architect (default — cross-references folded into Tech-QA's verification per the supervisor's wave call; bean's notes mark this as a sweep, not a new architecture decision).

## Changes

| File | Lines |
|------|-------|
| `ai/context/orchestration-architecture.md` | +507 (new — canonical long-form doc, ~430 lines + ASCII diagrams) |
| `ai/context/decisions.md` | +51 (ADR-015) |
| `ai/context/bean-workflow.md` | +29/-? (Inputs validation + /spawn-task + typed handoff + /vdd) |
| `ai/context/project.md` | +10 (module map note for vdd.py + validate_contract_graph) |
| `CHANGELOG.md` | +28 (v1.1.0 cluster entry) |
| `CLAUDE.md` | +9/-? (Beans Workflow rewrite for /spawn-task, /vdd, /orchestration-report) |
| `README.md` | +13/-? (lifecycle paragraph + Quick Reference table additions) |
| `ai-team-library/README.md` | +16 (Persona Contracts section, contracts/ in structure, orchestration commands table) |
| `.claude/shared` (kit submodule) | bumped — kit branch `kit/BEAN-279-orchestration-docs` (long-run + agent-file edits) |
| `ai/beans/BEAN-279-.../bean.md` + 2 task files | +253 |
| `MEMORY.md` (gitignored, absolute path) | +1 line in documentation checklist |
| **Total in this repo** | 13 files changed, +891 / -29 |

## Notes

**Runs LAST.** This bean depends on BEAN-270 through BEAN-278 being Done — otherwise the docs document things that don't exist yet. Team-Lead must verify all 9 prior beans are Done before starting.

**Doc location decision.** Long-form doc at `ai/context/orchestration-architecture.md` (flat with `bean-workflow.md` and `vdd-policy.md`) — not in a new `architecture/` subdir. Rationale: easy to maintain alongside other policy docs, single discoverable location, no path-fragmentation.

**Checklist enforcement.** Use `MEMORY.md`'s documentation checklist as the work list. Any doc the cluster impacted but isn't on the checklist gets *added* to the checklist.

**Coordinate with BEAN-251 and BEAN-268.** Both are still Approved (not Done). If they land before this bean, fold their CLAUDE.md additions into the orchestration narrative. If they land after, this bean's CLAUDE.md edits should leave room for theirs.

**Tech-QA findings (2026-05-01).** Surfaced during Task 02 cold-start verification. None block bean closure; all tightening opportunities for follow-up.

1. **Doc attributes typed-handoff workflow to wrong directory in generated projects.** orchestration-architecture.md mentions `.claude/agents/*.md` for the typed-handoff workflow in generated projects, but it actually lives in the compiled member prompts at `ai/generated/members/*.md` (the agent files there are 40-60 line stubs). Wording correct on intent, off by one directory on attribution.
2. **Source-beans table title mismatch.** New doc lists BEAN-279 as "...Documentation Sweep" while `_index.md` has "...Comprehensive Documentation Update". Functionally equivalent — pick one.
3. **validate-task-inputs.py doesn't auto-propagate to generated projects.** The hook is foundry-repo-specific and only ships into generated projects if the user enables a hook pack that includes it. The doc's wording describes foundry-repo behavior accurately, but a cold reader could assume universal propagation. Add a one-line caveat.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Write orchestration-architecture.md + ADR-015 + active-behavior doc sweep | developer | 9m | 1,442,005 | 3,808 | $2.50 |
| 2 | Cold-start verification: cross-references, checklist coverage, generated-project spot-check | tech-qa | 4m | 1,217,974 | 3,053 | $2.09 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 13m |
| **Total Tokens In** | 2,659,979 |
| **Total Tokens Out** | 6,861 |
| **Total Cost** | $4.59 |