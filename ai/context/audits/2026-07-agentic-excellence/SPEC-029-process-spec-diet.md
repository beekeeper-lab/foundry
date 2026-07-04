# SPEC-029: Process specification diet: dedupe, split ADRs, enforce-or-drop ceremony

- **Priority:** P2
- **Effort:** M
- **Area:** process
- **Depends on:** SPEC-008 (hook enforcement decides which gates are keepable), SPEC-010 (dispatch decision affects ADR-008 status)
- **Status:** Proposed

## Problem

The process documentation costs more tokens than it returns. Core rules are specified two and three times across files; all 15 ADRs live in one 1,849-line file that any agent must page through to read one decision; status/category tables are duplicated in three places; and several mandatory ceremonies have near-zero adherence in practice (Comprehension Notes in 3 of 342 task files, Example Output in 21 of 342), meaning agents pay to read rules that nothing enforces and nobody follows. Every bean dispatched re-reads this corpus — redundancy here is a per-bean tax.

## Evidence

- `ai/context/bean-workflow.md:44` (`## §6a Context Diet`) and `:457` (`### 8. Context Diet`) — the same policy specified twice in one file; a third copy lives in `ai/context/orchestration-architecture.md`.
- `ai/context/decisions.md` — 1,849 lines, 15 ADRs (`## ADR-001` at :7 through `## ADR-015` at :1800). ADR-010 alone spans :810-1141.
- Status-key/category tables duplicated across `ai/beans/_index.md`, `ai/context/bean-workflow.md`, and `ai/context/vdd-policy.md`.
- Adherence data (process audit over 342 task files / ~294 Done beans): Comprehension Note present in 3/342 (~1%); Example Output in 21/342 (~6%); `Inputs:` absent in 67/342; telemetry blocks copy-pasted defaults where present at all; the Molecularity + Blast-Radius + Bottleneck three-gate stack (`bean-workflow.md:199-289`) is prose ceremony for beans that are almost all trivial 2-task waves.
- Stale ADRs: ADR-008's tmux/spawn-task dispatch is used by 0 recorded beans (all `in-process`); ADR-013's contract graph fired one real handoff; ADR-015 describes a self-measuring cluster whose measurements were never aggregated. All three still read as current, active decisions.

## Proposed change

1. **Single Context-Diet section:** keep one canonical copy in `bean-workflow.md` (merge §6a and §8), replace the `orchestration-architecture.md` copy with a one-line pointer.
2. **Split `decisions.md`** into `ai/context/decisions/ADR-NNN-<slug>.md` (one file per ADR) plus a thin `ai/context/decisions.md` index (number, title, status, one-line summary, link). Update the CLAUDE.md rule "ADRs go in ai/context/decisions.md" to point at the new layout. Update all cross-references (`grep -rn "decisions.md"` across `ai/`, `.claude/`, `ai-team-library/`).
3. **Dedupe tables:** status keys and bean categories get one canonical home (`ai/beans/_index.md` header); other files link instead of copying.
4. **Enforce-or-drop table:** add a normative section to `bean-workflow.md` listing every honor-system gate with an explicit disposition. Recommended dispositions:
   | Gate | Disposition |
   |---|---|
   | Comprehension Gate | **Drop as written** (1% adherence); replace with the dispatch-time input validation that already exists (`validate-task-inputs.py`) |
   | Examples-First | **Fold in** as an optional `## Example Output` section in the task template; not a gate |
   | VDD gate | **Enforce** via SPEC-008 hook |
   | `/handoff` packets | **Enforce** via SPEC-008 hook or drop for the default 2-persona wave |
   | Molecularity / Blast-Radius / Bottleneck checks | **Compress** to a single checklist paragraph; keep as Team-Lead judgment, not per-bean prose recital |
   Each row that says "enforce" must reference the enforcing mechanism; anything unenforced and unfollowed gets deleted, not re-documented.
5. **Update stale ADR statuses:** append status notes to ADR-008 (superseded/pending per SPEC-010 outcome), ADR-013 (partially implemented — core-5 only; extended coverage tracked in SPEC-017), ADR-015 (aspirational — telemetry loop closed by SPEC-009). Use the ADR "Status:" field, do not rewrite history.
6. **Mirror to the library:** apply the same dedupe to `ai-team-library/process/context/bean-workflow.md` so generated projects inherit the leaner spec.

## Out of scope

- Building the enforcement hooks (SPEC-008), telemetry aggregation (SPEC-009), or the dispatch decision (SPEC-010).
- Changing the bean lifecycle states or the beans directory layout.

## Acceptance criteria

- [ ] `manual:` `grep -c "Context Diet" ai/context/bean-workflow.md` shows one section; `orchestration-architecture.md` contains a pointer, not a copy.
- [ ] `file:` `ai/context/decisions/ADR-001-*.md` through `ADR-015-*.md` exist; `ai/context/decisions.md` is an index under ~60 lines.
- [ ] `manual:` no stale references to monolithic `decisions.md` sections remain (`grep -rn "decisions.md#\|decisions.md:" ai/ .claude/ ai-team-library/`).
- [ ] `file-contains:` `ai/context/bean-workflow.md` contains the enforce-or-drop table with a disposition for every gate named above.
- [ ] `manual:` Comprehension Gate as a mandatory step no longer appears in `bean-workflow.md` or the task template.
- [ ] `file-contains:` ADR-008, ADR-013, ADR-015 files carry updated Status lines.
- [ ] `manual:` total line count of `bean-workflow.md` + `orchestration-architecture.md` reduced by ≥20% with no normative rule lost (reviewer judgment).

## Files to touch

- `ai/context/bean-workflow.md`, `ai/context/orchestration-architecture.md`, `ai/context/vdd-policy.md`
- `ai/context/decisions.md` → `ai/context/decisions/` (split)
- `ai/beans/_index.md` (canonical tables), `ai/beans/_bean-template.md` (gate/section changes)
- `CLAUDE.md` (ADR location rule)
- `ai-team-library/process/context/bean-workflow.md`, `ai-team-library/process/beans/_bean-template.md` (mirror)
