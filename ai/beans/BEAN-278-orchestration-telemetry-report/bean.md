# BEAN-278: Architecture-Aware Telemetry & `/orchestration-report`

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-278 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-28 |
| **Started** | 2026-05-01 01:03 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | team-lead |
| **Category** | Process |
| **Depends On** | BEAN-274 |

## Problem Statement

Per-task telemetry today (the bean's Telemetry table — duration, tokens, cost) tells us how expensive a bean *was*. It does not tell us whether the *orchestration* is paying for itself.

The architectural review's complementary recommendation: "architecture-aware evaluation. Rather than just testing whether the final output is good, evaluate whether your new orchestrator, context routing, and specialist roles actually improve quality, cost, or reliability enough to justify their added complexity."

Right now we have no answer to:
- Did adding BA on this bean reduce rework?
- Is the supervisor pattern (BEAN-270) cheaper or more expensive per bean than in-process role-switching?
- Are we using the contract validator (BEAN-274) — and when it catches errors, how often?
- Are escape-hatch `Inputs: NONE (justified: ...)` invocations rising? (Signals BEAN-272 may be too strict.)

## Goal

Each bean carries a small Orchestration Telemetry block alongside the existing Telemetry table. A new `/orchestration-report` command aggregates across the backlog and produces a roll-up showing whether the orchestration changes (this whole cluster) are paying off.

## Scope

### In Scope

- Extend `ai/beans/_bean-template.md` with a new section after Telemetry:

  ```markdown
  ## Orchestration Telemetry

  | Field | Value |
  |-------|-------|
  | **Personas activated** | (comma-separated, actual not planned) |
  | **Bounces** | 0 (Tech-QA → Developer kicks) |
  | **Scope changes** | 0 (in-flight scope edits) |
  | **Contract violations** | 0 (BEAN-274 catches at compose time) |
  | **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
  | **Dispatch mode** | (in-process / tmux-worker / mixed) |
  ```

- Update telemetry hook (`.claude/hooks/telemetry-stamp.py`) to populate `Personas activated` and `Dispatch mode` automatically when possible. Other fields are persona-recorded.
- Update `/spawn-task` (BEAN-270) to record the dispatch mode used.
- Update `/spawn-task` and `/handoff` to log Tech-QA→Developer bounces (when Tech-QA opens a new task pointing back at Developer mid-bean) — increments the bean's Bounces counter.
- New library skill `ai-team-library/claude/skills/orchestration-report/SKILL.md`:
  - Aggregates Orchestration Telemetry across all Done beans within a date window.
  - Computes: average bounces by persona-set, average cost-per-bean by persona count, contract violations caught (vs missed and fixed in bounces), escape-hatch trend over time.
  - Outputs `ai/outputs/team-lead/orchestration-report-YYYY-MM-DD.md` with tables and a one-paragraph verdict ("the supervisor pattern reduced average bean cost by N%" / "no measurable improvement; revisit").
- New library command `ai-team-library/claude/commands/orchestration-report.md` (≤30 lines per BEAN-249).
- Tests: telemetry hook populates dispatch mode and personas; report aggregates correctly across fixture beans; report runs end-to-end on the real backlog without errors.

### Out of Scope

- Backfilling Orchestration Telemetry for historical beans (going forward only).
- Real-time dashboards (markdown reports are enough for now).
- Per-task orchestration telemetry (the bean is the unit; per-task is too noisy).
- Cost attribution beyond what task telemetry already captures.

## Acceptance Criteria

- [ ] Bean template carries the Orchestration Telemetry section.
- [ ] Telemetry hook populates `Personas activated` and `Dispatch mode` automatically for new beans.
- [ ] `/spawn-task` and `/handoff` increment Bounces correctly in a manual test.
- [ ] `/orchestration-report` produces a structured report covering at least the last 30 days of Done beans.
- [ ] Report's verdict paragraph is non-trivial (cites at least two metrics with values).
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement orchestration telemetry: template + hook + skill + command + spawn-task/handoff hooks | developer | — | In Progress |
| 2 | Verify orchestration telemetry: hook tests + skill walkthrough + aggregator smoke | tech-qa | 1 | Pending |

> Skipped: BA (default — verdict-paragraph wording is not user-facing requirements; Developer drafts inline); Architect (default — no new subsystem boundary; extends existing telemetry).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Lands last among the working beans.** Most useful after BEAN-270 / 272 / 274 are in place so there's signal to aggregate. Land before BEAN-279 (docs) so the telemetry layer can be documented.

**Honest verdict matters.** If the report shows the supervisor pattern is *more* expensive without a quality offset, that's a signal — not a failure. The whole point of architecture-aware evaluation is to be willing to find out we were wrong.

**Pairs with BEAN-114/116/120** (existing telemetry beans). Those built the cost telemetry layer; this builds the orchestration-quality layer on top.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Implement orchestration telemetry: template + hook + skill + command + spawn-task/handoff hooks | developer | 7m | 1,236,562 | 3,564 | $2.17 |
| 2 | Verify orchestration telemetry: hook tests + skill walkthrough + aggregator smoke | tech-qa | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |