# Implementation Plan — Agentic Excellence Audit (2026-07)

**Companion to:** [00-INDEX.md](00-INDEX.md). This plan is self-contained: an implementer (Claude Code session, Opus, or the Foundry AI team) can execute it without the original audit conversation. Each spec file contains its own evidence, steps, and VDD-prefixed acceptance criteria.

## Ground rules

1. **One spec = one bean = one branch = one PR.** Promote each spec to a bean via `/backlog-refinement` (bean title = spec title, spec file goes in the bean's `Inputs:`). The spec's acceptance criteria transfer verbatim to the bean's AC.
2. **Never edit on `main`** (branch protection). Parallel work uses one branch/worktree per spec.
3. **Gate every PR** with `uv run pytest` + `uv run ruff check foundry_app/`. Specs touching generation output should regenerate `generated-projects/small-python-team` and eyeball the diff before merge.
4. **Kit changes** (`.claude/shared/`) go through `claude-publish.sh` / the claude-kit repo and must land in **both** trees where content is duplicated (kit copy AND `ai-team-library/claude/` copy) until SPEC-023/026 remove the duplication.
5. **Update this file's checkboxes** as specs merge, so a future session can see progress at a glance.

## Series or parallel?

**Parallel, up to 4 concurrent tracks** — but not arbitrarily. Two constraints:

- **File-collision domains.** Specs cluster around four mostly-disjoint file sets. Within a domain, specs must run in series (they edit the same files); across domains they can run simultaneously in separate worktrees:
  - **Pipeline** (`foundry_app/services/`, `templates/`, `core/models.py`): 001, 004, 006, 011, 012, 013, 016, 022, 027
  - **Kit assets** (`.claude/shared/`, `ai-team-library/claude/`): 002, 005, 007, 008, 014, 015, 023, 024, 25
  - **Library content** (`ai-team-library/personas|expertise|contracts|workflows/`): 003*, 017, 018, 019, 020, 021 (*003 also touches compiler/validator — coordinate with the pipeline track for that slice)
  - **Process/docs** (`ai/context/`, README, samples): 009, 010, 026, 028, 029
- **The serial spine** (true dependencies): `003 → 019 → {012, 020, 021}`, `001 → {006, 011} → 012`, `005 → 008 → 009`, `002 → {007, 023, 024}`, `026-decision → {025, 027}`. Everything else is order-free.

Sequencing intuition: the spine is short (3–4 hops); most of the 29 specs hang off it as parallel leaves.

## Phases

### Phase 0 — Decision gate (do first, cheap)

- [ ] **SPEC-026 (decision half only):** write the ADR — plugin/marketplace distribution vs. keep-and-fix the submodule. **Why first:** the answer decides how much of SPEC-025 (sync-script hardening) is worth doing at all, and shapes SPEC-027. Do NOT implement the migration yet; just decide and record. The contribution-flow script (`kit-contribute`) is worth building under either outcome.

### Phase 1 — Foundations (4 parallel tracks; converts dead content to live)

| Track | Order | Specs | Collision note |
|---|---|---|---|
| A pipeline | series | **001 → 006** | both edit `agent.md.j2`, `agent_writer.py`, `compiler.py` |
| B kit | series | **002 → 007** | 002 adds frontmatter to files 007 then fixes refs in; 007 creates the missing `/vdd`, `/pick-bean`, `/bean-status`, `/orchestration-report`, `/new-work` stubs |
| C expertise | solo | **003** | restructures 19 packs + compiler/validator slice; biggest single item (L) |
| D smalls | any order, parallel | **005, 013, 014, 018** | disjoint files (telemetry hook, seeder, safety hooks, workflow docs) |

**Exit criteria:** regenerated sample project has registering subagents; all 42 packs compile; telemetry durations correct going forward.

### Phase 2 — Enforcement & schema (3–4 parallel tracks)

| Track | Order | Specs | Collision note |
|---|---|---|---|
| A pipeline | series | **004 → 016 → 011** | all touch settings-generation / `models.py`; 011 needs 001 merged |
| B kit hooks | series | **015 → 008** | both wire `settings.json` hook events; 008 also needs 005 (telemetry) and 007 (`/vdd` command) merged |
| C expertise | series | **019 → 012** | 019 needs 003; 012 edits `compiler.py`/`agent_writer.py` — start only after Track A of Phase 1 AND 011 are merged (same files) |
| D library | solo | **017** | contracts.yml × 20 extended personas + handoff skill; large but isolated |

**Exit criteria:** gates are hooks, not prose; permissions differ by posture; agents carry model/tool tiers; member prompts contain relevant expertise within budget.

### Phase 3 — Process modernization (parallel)

- [ ] **010** Native task dispatch (L; retires tmux path + `--dangerously-skip-permissions`, supersedes ADR-008)
- [ ] **009** Feedback loop (needs 005, 008; aggregator + retro + MEMORY.md + one-time backfill)
- [ ] **029** Process spec diet (coordinate with 008's enforce-or-drop decisions; splits `decisions.md`)

These three touch disjoint files and can run concurrently; 029 should merge **after** 008 so the keep/enforce/drop table reflects what actually got enforced.

### Phase 4 — Distribution & content (parallel; scope 025/027 per the 026 decision)

| Track | Order | Specs |
|---|---|---|
| kit | series | **023 → 024** (dedup restructures the same command files 024 rewrites) |
| kit infra | series | **025 → 027** (only the parts the 026 ADR keeps) |
| pipeline | solo | **022** (MCP opt-in; emit root `.mcp.json`) |
| expertise | parallel | **020, 021** (freshness pass; new packs — both need 019's frontmatter contract) |
| distribution | solo | **026 (implementation half)** if the ADR chose migration |

### Phase 5 — Alignment (strictly last)

- [ ] **028** README/output alignment + regenerate both sample projects + CI regeneration-diff job. Last because every output-changing spec above invalidates it.

## If usage/budget runs short — priority order

Do these in order and stop when out of budget; each is independently shippable:

1. **SPEC-001** — generated agents become real subagents (the product's core promise)
2. **SPEC-002** — kit skills/commands/agents become discoverable/invocable
3. **SPEC-003** — 19 dead expertise packs come alive (~87% of authored content)
4. **SPEC-005** — stop writing corrupt telemetry (every day of delay corrupts more data)
5. **SPEC-004** — generator stops discarding hooks; examples get their branch protection back
6. **SPEC-006 + 013** — broken links + VDD-passable seeds (both S, same afternoon)
7. **SPEC-007** — `/vdd` and friends exist; reference rot gets a CI guard
8. **SPEC-008** — the VDD/handoff gates become enforcement
9. **SPEC-014** — safety hooks stop lying and stop false-positives
10. **SPEC-026 decision** — so kit work after the break lands on the right foundation

Everything below this line in the index (011, 012, 015–029) is real value but survives waiting.

## Effort budget

S ×6 (005, 006, 013, 018, 024, 028) · M ×18 · L ×5 (003, 010, 017, 021, 026). At roughly half a focused session per S, one per M, two-to-three per L: **~35 sessions end-to-end**, compressible to **~10–12 calendar sessions** with 3–4 parallel worktree tracks staffed per the phase tables. Phase 1 alone (7 specs) delivers the majority of user-visible improvement.

## Progress

- [ ] Phase 0: 026-decision
- [x] Phase 1 (except 018): ~~001~~ ✅, ~~002~~ ✅ (157 files, script-injected), ~~003~~ ✅ (code path — pack conventions.md authoring deferred to SPEC-019), ~~005~~ ✅ (incl. 69-bean backfill), ~~006~~ ✅, ~~007~~ ✅ (incl. tests/test_reference_integrity.py guard), ~~013~~ ✅, ~~014~~ ✅ (32 hook tests). 018 not started.
- Phase 2 partial: ~~004~~ ✅, ~~008~~ ✅ core slice (vdd-gate.py blocks Done-transition without passing VDD report; handoff-emission warning hook NOT yet done — remaining scope in SPEC-008).
- All on branch `audit/agentic-excellence-2026-07`; kit changes on submodule branch `fix/spec-005-telemetry-integrity` (NOT yet pushed to beekeeper-lab/claude-kit — run claude-publish/PR before merging the parent branch).
- Audit-spec corrections found during implementation: SPEC-006/007's tech-qa "duplicate Scope Boundaries heading" finding was a false positive (BEAN-275 intent; partition tests key on it) — reverted.
- Phase 0 ✅: ~~026~~ done in full for the "regardless" scope — ADR-016 (Accepted, plugin direction staged via hybrid), claude-publish.sh detached-HEAD guard, scripts/kit-contribute.sh (branch+PR with fork fallback), README override policy. Plugin manifest itself = follow-on.
- Also done: ~~018~~ ✅ (fallback table + validator advisories + composition-aware CLAUDE.md orchestration block), ~~011~~ ✅ (model/tools tiering; 25 defaults.yml).
- Also done: ~~016~~ ✅ (regulated_safety + effective_safety + write_permissions stage; postures produce nested deny sets).
- Session 3: ~~012~~ ✅ (retried cleanly — expertise inlined into member prompts, header over-claim fixed), ~~015~~ ✅ (session-start-context/format-on-save/stop-quality-reminder hooks wired kit+library+generated; doc-only hooks bannered), ~~009~~ ✅ (orchestration_report service + CLI, baseline over 295 beans committed, MEMORY.md + scaffold, close-loop retro/cadence), ~~019~~ ✅ (frontmatter on all 42 entry files, indexer frontmatter-first, compile-time stripping, CI guard).
- Remaining: 010 (L), 017 (L), 020, 021 (L), 022, 023, 024, 025, 027, 028, 029.
- (Historical note) **SPEC-012 was started and reverted** — an attempted move of `_extract_expertise_highlights` from agent_writer.py to compiler.py corrupted the file and was rolled back to the SPEC-016 commit. Implementation notes for the next session: (1) inline persona-relevant expertise into `_compile_persona_section` (replace the ADR-012 no-op guard loop at the end with real blocks: Defaults excerpt + pointer to `ai/generated/expertise/<id>.md`, gated by `_expertise_applies_to`, using `_expertise_entry_file`); (2) move the highlights extractor to compiler.py with a careful Edit (not string slicing) and re-import in agent_writer; (3) fix the agent header over-claim (`expertise_names` lists all emitted ids; should list only ids applicable to that persona); (4) update README's member-prompt claim.
- Next: 012 (retry), 015, 009, 019, then 017 (L), 010 (L), remaining P2s (020-025, 027-029).
- [ ] Phase 2: 004, 008, 011, 012, 015, 016, 017, 019
- [ ] Phase 3: 009, 010, 029
- [ ] Phase 4: 020, 021, 022, 023, 024, 025, 026-impl, 027
- [ ] Phase 5: 028
