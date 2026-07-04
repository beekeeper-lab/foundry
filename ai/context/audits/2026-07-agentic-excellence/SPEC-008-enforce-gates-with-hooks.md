# SPEC-008: Enforce VDD and handoff gates with hooks, not prose

- **Priority:** P1
- **Effort:** M
- **Area:** kit+process
- **Depends on:** SPEC-005 (telemetry hook shares the same wiring surface); coordinates with SPEC-029 (which gates get *dropped* instead of enforced)
- **Status:** Proposed

## Problem

The three highest-value quality gates in the bean workflow — the VDD merge gate, the typed-handoff gate, and the comprehension gate — are skill/markdown instructions the model is trusted to obey. Practice shows it doesn't: across ~294 Done beans there are exactly **3 VDD reports** (`ai/outputs/tech-qa/vdd-{273,275,277}.md`), **1 handoff packet** (`ai/handoffs/developer-to-tech-qa-BEAN-274-task-02.md`), and **~3 comprehension notes in 342 task files**. Everything the spec calls a "HARD GATE" was silently skipped, because nothing mechanical blocks the skip. Meanwhile the five gates that ARE wired as `settings.json` hooks (branch guard, bash/write safety, task-inputs, telemetry) fire reliably. The lesson is unambiguous: gates that matter must be hooks.

## Evidence

- `ai/context/orchestration-architecture.md:323` — "`/merge-bean` refuses to merge a bean whose VDD report is missing or failing." This refusal lives only in `ai-team-library/claude/skills/merge-bean/SKILL.md:29-32,108-110` (error rows `VDDMissing`/`VDDFail`/`VDDPartial`) — prose an agent can bypass by simply running `git merge` itself.
- `ai-team-library/claude/skills/handoff/SKILL.md:72-95` — "Validate before emitting (HARD GATE …) If no artifact is found for a required type T: BLOCK the handoff." No executor is cited; unlike `/vdd` (which calls `foundry_app.services.vdd`), the handoff gate has no code path. Nothing forces `/handoff` to run at all on a persona transition.
- `.claude/shared/settings.json:3-52` — the only enforced gates: branch guard (inline), `bash_safety.py`, `write_safety.py`, `validate-task-inputs.py`, `telemetry-stamp.py`. No gate touches bean status transitions or merges.
- `ai/context/bean-workflow.md:390-414` — Comprehension Gate specified as mandatory; found in 3 of 342 task files.
- Actual artifacts: `ls ai/outputs/tech-qa/vdd-*.md` → 3 files; `ai/handoffs/` → 1 packet + index, vs. `_index.md` showing 294 Done beans.

## Proposed change

1. **New PreToolUse hook `enforce-bean-gates.py`** (kit: `.claude/shared/hooks/`), matcher `Edit|Write`, modeled on `validate-task-inputs.py`. When a write to `ai/beans/BEAN-*/bean.md` changes `Status` to `Done`, the hook blocks (exit 2) unless:
   - a VDD report `ai/outputs/tech-qa/vdd-<NNN>.md` exists whose aggregate verdict is `PASS` (or `PARTIAL` with an explicit `Manual-Confirmed:` line, mirroring `merge-bean/SKILL.md:110`), and
   - for each persona transition recorded in the bean's task table, a matching packet exists under `ai/handoffs/` (filename pattern from `handoff/SKILL.md:98-101`: `<from>-to-<to>-BEAN-NNN*.md`).
   The hook reuses the parsing helpers already proven in `validate-task-inputs.py` and `telemetry-stamp.py` (bean-file detection, status-diff extraction).
2. **Git-level backstop**: extend the repo's pre-merge protection so `/merge-bean`'s refusal is mechanical — a `PreToolUse` `Bash` matcher rule (added to `bash_safety.py` or a sibling) that blocks `git merge <bean-branch>` / `gh pr merge` when the branch's bean lacks a passing VDD report. Branch→bean resolution: branch names carry the bean id (existing convention, e.g. `BEAN-277-…`).
3. **Escape hatch, audited**: allow `VDD-Waived: <reason ≥ 30 chars>` in the bean's Notes section to pass the hook; the hook appends a `⚠ waived` marker to the bean's Orchestration Telemetry block so SPEC-009's aggregator can count waivers. Ten-character junk must not satisfy it (lesson from `validate-task-inputs.py`'s too-cheap `justified:` hatch).
4. **Comprehension gate: enforce or drop — drop.** Per the evidence (99% skip rate, no observed quality signal), do NOT build a hook for it; SPEC-029 removes it from `bean-workflow.md` or demotes it to optional guidance. Record the decision in `ai/context/decisions.md` as an ADR amendment so the spec and machinery agree.
5. **Wire into both distribution surfaces**: `settings.json` in the kit (for foundry + subtree-mode projects) and `safety_writer._HOOK_PACK_REGISTRY` (for library-copy generated projects), so generated teams get the same gate — coordinate with SPEC-004's single-source-of-truth work.
6. Update `merge-bean/SKILL.md`, `handoff/SKILL.md`, `bean-workflow.md`, and `orchestration-architecture.md` to state that the gate is hook-enforced, and what the waiver mechanism is.

## Out of scope

- Fixing the historical 294 beans (no retroactive VDD).
- The telemetry aggregation that consumes waiver counts (SPEC-009).
- Body-schema validation of handoff packet contents (SPEC-017 territory).

## Acceptance criteria

- [ ] (file:.claude/shared/hooks/enforce-bean-gates.py) Hook script exists in the kit
- [ ] (file-contains:.claude/shared/settings.json::enforce-bean-gates.py) Hook is wired as PreToolUse
- [ ] (test:tests/test_enforce_bean_gates.py) Unit tests: Done-transition blocked without VDD report; allowed with PASS report; allowed with PARTIAL + Manual-Confirmed; waiver accepted only with ≥30-char reason and telemetry marker written; non-bean writes untouched
- [ ] (test:tests/test_enforce_bean_gates.py::test_handoff_packets_required) Done-transition blocked when a wave transition has no matching `ai/handoffs/` packet
- [ ] (file-contains:ai/context/bean-workflow.md::hook-enforced) Workflow doc states the gates are mechanical, not honor-system
- [ ] manual: Attempt to mark a test bean Done without a VDD report in a live session — hook blocks with an actionable message naming the missing artifact

## Files to touch

- `.claude/shared/hooks/enforce-bean-gates.py` (new)
- `.claude/shared/settings.json`
- `foundry_app/services/safety_writer.py` (registry entry; coordinate with SPEC-004)
- `ai-team-library/claude/skills/merge-bean/SKILL.md`, `ai-team-library/claude/skills/handoff/SKILL.md` — note: library edits require the maintainer path, see repo rule "do not modify ai-team-library" (these specs are the sanctioned change request)
- `ai/context/bean-workflow.md`, `ai/context/orchestration-architecture.md`, `ai/context/decisions.md`
- `tests/test_enforce_bean_gates.py` (new)
