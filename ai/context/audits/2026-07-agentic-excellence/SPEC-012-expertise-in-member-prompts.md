# SPEC-012: Compile expertise into member prompts with token budgeting

- **Priority:** P1
- **Effort:** M
- **Area:** pipeline
- **Depends on:** SPEC-003 (packs must be compilable at all), SPEC-019 (Applies-To/relevance metadata improves filtering; not gating)
- **Status:** Proposed

## Problem

The README's core promise — member prompts that "merge the persona's identity, outputs contract, invocation prompts, **relevant expertise conventions**, and project context" — is not what the compiler does. Member prompts are persona-only: the expertise-inlining path is an explicit no-op. Meanwhile the *agent* files over-deliver in the wrong way: the same `## Defaults` table is copied verbatim into every agent file the expertise applies to, duplicating identical content across ~10 files in a large team, while each agent's header claims the full expertise list even when only a subset was inlined. The result is the worst of both: members lack expertise, agents carry redundant token load, and headers misreport coverage. One deliberate design is needed.

## Evidence

- `foundry_app/services/compiler.py:436-449` — the forward-compat guard: "Today the persona section embeds no expertise, so the guard is a no-op — but we exercise the lookup here so the path is wired." Expertise is never appended to member prompts.
- README "Component Roles": `ai/generated/members/` described as merging "relevant expertise conventions" — contradicted by the above.
- `foundry_app/services/agent_writer.py:94-140` — `_extract_expertise_highlights` inlines up to `_MAX_EXPERTISE_HIGHLIGHT_LINES` (=15, `:34`) of each pack's `## Defaults` into every applicable agent file; in `generated-projects/drill-deck-base` the identical clean-code/python tables appear in multiple agent files.
- `agent_writer.py:184-186, 282` — the `Expertise:` header line always lists all emitted expertise, even when the inlined sections are filtered per-persona (header over-claims).
- `compiler.py:161-175` — `_expertise_applies_to` returns True when `applies_to` is empty; only 5 of 42 packs set `## Applies To`, so filtering is effectively off (SPEC-019 fixes the metadata).

## Proposed change

1. **Members get relevant expertise, budgeted.** In `_compile_persona_section`, replace the no-op loop with real inlining: for each expertise where `_expertise_applies_to(persona_id, info)` holds, append a compact expertise section to the member prompt. Source: the pack's `## Defaults` table plus `## Do / Don't` (the two highest-signal sections), NOT the full conventions file. Enforce a per-member budget (default ~2,000 words of expertise content, configurable via `GenerationConfig`); when over budget, include Defaults only, then truncate lowest-`order` packs last (order already exists on `ExpertiseSelection`), and emit a compiler warning naming what was cut — no silent truncation.
2. **Agents reference, not copy.** Change `agent_writer` to stop duplicating Defaults tables into every agent file. Each agent's `## Expertise Context` becomes: per-pack one-line summary + pointer to the single canonical compiled file `ai/generated/expertise/<id>.md` (which already exists — `compiler.py:737-742`). Rationale: the agent file is a lean dispatch identity (SPEC-001 gives it frontmatter); the member prompt is the deep context; the expertise file is the shared reference. One copy of every table, three well-defined roles.
3. **Fix the header over-claim.** The agent `Expertise:` line lists only packs that pass the applies-to filter for that persona (`agent_writer.py:184-186`).
4. **Dedup across packs.** When multiple selected packs would inline near-identical guidance (e.g. clean-code error-handling rows duplicated by language packs — see SPEC-020), the compiler does not attempt semantic dedup; instead, document in the README that pack `order` expresses precedence and later packs should not restate earlier ones (authoring rule, enforced editorially via SPEC-020).
5. **Update the README** so the promise and the implementation finally agree, including the budget knob and the three-role content model (member = identity+expertise, agent = registration+pointer, expertise file = canonical reference).

## Out of scope

- Making dead packs compilable (SPEC-003) and pack metadata (SPEC-019).
- Semantic merging/synthesis of overlapping guidance (editorial, SPEC-020).
- Per-task context injection at dispatch time (SPEC-010).

## Acceptance criteria

- [ ] (test:tests/test_compiler.py::test_member_includes_relevant_expertise) Member prompt for developer contains the python pack's Defaults when python is selected
- [ ] (test:tests/test_compiler.py::test_member_expertise_budget) Over-budget composition triggers Defaults-only fallback + warning naming truncated packs
- [ ] (test:tests/test_agent_writer.py::test_agent_references_not_copies) Agent files contain the pointer, not the table; no Defaults table duplicated across two agent files
- [ ] (test:tests/test_agent_writer.py::test_expertise_header_filtered) Header lists only applies-to-filtered packs
- [ ] (file-contains:README.md::budget) README describes the actual merge behavior and budget
- [ ] manual: Regenerate `drill-deck-base`; diff shows smaller agent files, richer member files, and total generated `.claude/` + `ai/generated/` token count not materially worse than before

## Files to touch

- `foundry_app/services/compiler.py` (replace no-op at `:436-449`; budget logic)
- `foundry_app/services/agent_writer.py` (`:94-146`, `:184-186`, `:273-287`)
- `foundry_app/core/models.py` (`GenerationConfig` budget knob)
- `README.md`
- `tests/test_compiler.py`, `tests/test_agent_writer.py`
- `generated-projects/*` (regenerate samples — coordinate with SPEC-028)
