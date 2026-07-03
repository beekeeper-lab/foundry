# SPEC-009: Close the feedback loop: telemetry aggregation, retros, memory

- **Priority:** P1
- **Effort:** M
- **Area:** process
- **Depends on:** SPEC-005 (Duration data must be trustworthy before aggregating it)
- **Status:** Proposed

## Problem

The process collects per-bean telemetry on every single bean and has consumed it zero times. Nothing in the system learns: no orchestration report has ever been produced, the `MEMORY.md` that the workflow's closure step mandates does not exist anywhere in the repo, there are no retro artifacts, and the escape-hatch counters that exist specifically "to surface over-use" are write-only. The premise of the orchestration cluster — architecture-aware evaluation feeding process improvement — is unrealized. A first-rate agentic factory must feed observed outcomes back into its personas, expertise packs, and process docs.

## Evidence

- No file matching `*orchestration-report*` exists under `ai/` despite `/orchestration-report` being step 8 of the documented lifecycle (`CLAUDE.md` Beans Workflow; `ai/beans/BEAN-278-*/bean.md:111` admits "markdown-only — no Python aggregator yet").
- `ai/context/bean-workflow.md:516` — closure step: "Record findings in `MEMORY.md` (concise entries)…" — `MEMORY.md` does not exist in the repo (verified by search).
- `ai/outputs/team-lead/` contains no telemetry roll-up (4 unrelated files).
- Orchestration Telemetry blocks that DO exist (10 beans: 278, 286–294) all carry identical template defaults (`Bounces 0`, `Scope changes 0`, `Dispatch in-process`) — recorded but never audited, so nobody noticed they were copy-pasted.
- `ai/context/bean-workflow.md:340` — `Inputs: NONE (justified: …)` usage "is counted in orchestration telemetry to surface over-use" — the counter is never read.

## Proposed change

1. **Build the real aggregator**: `foundry_app/services/orchestration_report.py` — parses every `ai/beans/BEAN-*/bean.md` (Status, Started/Completed/Duration, Category, Orchestration Telemetry block, waivers from SPEC-008, `Inputs: NONE` counts from task files) and emits `ai/outputs/team-lead/orchestration-report-<YYYY-MM>.md` with: bean throughput, duration distribution (median/p90 — from corrected SPEC-005 data), dispatch-mode mix, gate-waiver counts, telemetry-completeness rate (how many beans carry a real vs. template-default block), and top anomalies. Expose via CLI (`uv run foundry-cli orchestration-report`) and wire the existing `/orchestration-report` skill to call it — the same pattern BEAN-277 used for `/vdd` → `foundry_app.services.vdd`.
2. **Backfill once**: run the aggregator over the 294 historical beans and commit the baseline report. This also validates the parser against real-world telemetry-block drift (beans 279–285 have no block at all — the report must count absence, not crash).
3. **Create `MEMORY.md`** at repo root (and add it to the generated-project scaffold): a curated, small file with sections per area (process, personas, expertise, kit). Closure step 4 already mandates writing to it; make the instruction satisfiable.
4. **Retro-to-bean pipeline**: extend the `/close-loop` skill (`ai-team-library/claude/skills/internal/close-loop/SKILL.md`) with a lightweight retro step: after marking a bean Done, if any lesson generalizes beyond the bean, append a one-line entry to `MEMORY.md` **and** — when the lesson implicates a persona, expertise pack, or kit asset — draft an Unapproved improvement bean referencing the file to change. This is the mechanism by which the library gets better from experience instead of only from authoring sessions.
5. **Cadence enforcement**: `/close-loop` checks bean-count-since-last-report; every 10th closed bean (configurable), it refuses to complete until `/orchestration-report` has been regenerated. Cheap check: compare max bean number against the newest report's `Generated-through:` header.
6. **Make the report actionable**: the report ends with a "Recommended process changes" section template the Team Lead fills — closing the loop from measurement to decision, with decisions landing as ADR amendments in `ai/context/decisions.md`.

## Out of scope

- Fixing Duration computation itself (SPEC-005).
- Token-cost pricing accuracy (`ai/context/token-pricing.md` refresh can ride along but is not gating).
- Automated persona/expertise editing — the retro step *drafts beans*; humans approve them (existing lifecycle).

## Acceptance criteria

- [ ] (file:foundry_app/services/orchestration_report.py) Aggregator service exists
- [ ] (test:tests/test_orchestration_report.py) Parses beans with a telemetry block, without one, with waiver markers; counts template-default blocks separately from measured ones; produces the report file
- [ ] (file:ai/outputs/team-lead/orchestration-report-*.md) Backfilled baseline report over historical beans is committed
- [ ] (file:MEMORY.md) Memory file exists with the section scaffold
- [ ] (file-contains:ai-team-library/claude/skills/internal/close-loop/SKILL.md::MEMORY.md) Close-loop skill includes the retro + cadence steps
- [ ] (file-contains:foundry_app/services/scaffold.py::MEMORY.md) Generated projects receive the MEMORY.md scaffold
- [ ] manual: Close a test bean end-to-end and observe the retro prompt, memory append, and (on the cadence boundary) the report-refresh refusal

## Files to touch

- `foundry_app/services/orchestration_report.py` (new), `foundry_app/cli.py`
- `tests/test_orchestration_report.py` (new)
- `MEMORY.md` (new), `foundry_app/services/scaffold.py`
- `ai-team-library/claude/skills/internal/close-loop/SKILL.md` (maintainer path)
- `ai/context/bean-workflow.md` (point step 4 at the real file; document cadence)
- `ai/outputs/team-lead/orchestration-report-<baseline>.md` (generated)
