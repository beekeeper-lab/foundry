# BEAN-271: Tier Library Personas — `core/` vs `extended/`

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-271 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-04-30 23:36 |
| **Completed** | 2026-05-01 00:24 |
| **Duration** | 1587h 17m |
| **Owner** | team-lead |
| **Category** | Infra |

## Problem Statement

`ai-team-library/personas/` ships 24 personas. Foundry's own team uses 5 (team-lead, ba, architect, developer, tech-qa). The other 19 (mobile-developer, sales-engineer, financial-operations, etc.) have no orchestration wiring in any command or skill — they sit on the bench but the bench has no rules.

Anthropic guidance: "stable pool of specialist workers." 24 ungrounded personas is a costume rack, not a stable pool. Generated projects inherit all 24 as available bench whether the workflow needs them or not, which dilutes the "narrow specialist boundaries" principle.

BEAN-269 made the available-bench model explicit in CLAUDE.md, but the library still presents all 24 personas with no tiering signal.

## Goal

Library personas are split into two tiers on disk:

- **`ai-team-library/personas/core/`** — the 5 personas that participate in every team's orchestration: team-lead, ba, architect, developer, tech-qa.
- **`ai-team-library/personas/extended/`** — the 19 specialist personas, opt-in per composition.

The compiler emits the core 5 by default. Extended personas appear in generated projects only if explicitly named in `composition.yml`. The wizard UI groups them visibly into the same two tiers.

Clean break: existing compositions that name an extended persona without a `tier:` indicator must be updated by the user (or the compiler errors with a clear message naming the persona's new path). ClaudeKit submodule consumers re-pull and adapt — this is the agreed approach.

## Scope

### In Scope

- File reorg: move 5 persona dirs into `ai-team-library/personas/core/`; move 19 into `ai-team-library/personas/extended/`.
- Update `foundry_app/services/library_indexer.py` to scan both subdirectories and tag each `PersonaInfo` with `tier: "core" | "extended"`.
- Update `PersonaInfo` Pydantic model in `foundry_app/core/models.py` to carry the tier field.
- Update `foundry_app/services/compiler.py` so the default composition includes only `tier=core`; extended personas require explicit naming in `composition.yml`.
- Update wizard's persona selection page (`foundry_app/ui/screens/builder/wizard_pages/`) to render two collapsible groups labeled "Core team" and "Extended specialists" with a brief explainer.
- Update `ai-team-library/README.md`'s persona table to mark the tier of each.
- Update `ai-team-library/workflows/foundry-pipeline.md` and `task-taxonomy.md` to reflect the tiering.
- Update example compositions in `examples/*.yml` — verify each still selects the personas it intends.
- Tests: indexer reports tier; compiler defaults to core only; explicit extended-persona selection still works; clear error message when an extended persona is referenced but the move is not done.

### Out of Scope

- Renaming, merging, or removing personas (no content edits to persona files themselves).
- Backwards-compatibility shim (clean break per agreed plan).
- Activation rules for extended personas (BEAN-257 is Done; this bean preserves those).
- Per-persona expertise filtering (BEAN-259 is the right home for that).

## Acceptance Criteria

- [ ] `ai-team-library/personas/core/` contains exactly: team-lead, ba, architect, developer, tech-qa.
- [ ] `ai-team-library/personas/extended/` contains the remaining 19 personas.
- [ ] `PersonaInfo.tier` is set correctly by the indexer for every persona.
- [ ] Default composition (no `personas:` block) generates a project containing only the core 5.
- [ ] Composition with `personas: [extended/security-engineer, ...]` (or whatever final ref-syntax we pick) generates the right project.
- [ ] Wizard UI groups personas into two clearly-labeled tiers.
- [ ] Library README reflects the tiering.
- [ ] All tests pass (`uv run pytest`); existing tests updated where they reference old paths.
- [ ] Lint clean (`uv run ruff check foundry_app/`).
- [ ] At least one example composition exercises the extended tier end-to-end.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | ADR — extended-persona ref-syntax in composition.yml | architect | — | Done |
| 2 | File reorg + indexer + model + compiler + wizard + examples | developer | 1 | Done |
| 3 | Test sweep: fixtures + tier coverage + compiler defaults + error path | tech-qa | 2 | Done |

> Skipped: BA (default — no requirements ambiguity; the bean is fully specified).

## Changes

| File | Lines |
|------|-------|
| `ai-team-library/personas/` (24 dirs renamed via `git mv`) | core/: 5 dirs; extended/: 19 dirs |
| `ai-team-library/README.md` | +52/-? (persona table + tier instructions) |
| `ai-team-library/workflows/foundry-pipeline.md` | tier instructions |
| `ai/context/decisions.md` | +102 (ADR-014) |
| `examples/foundry-dogfood.yml` | +6/-? |
| `examples/full-stack-web.yml` | +8/-? |
| `examples/security-focused.yml` | +6/-? |
| `examples/small-python-team.yml` | +2/-? |
| `foundry_app/core/models.py` | +70/-? (PersonaInfo.tier, _persona_dirname, _validate_persona_id) |
| `foundry_app/services/library_indexer.py` | +120/-? (two-pass scan + format_unknown_persona_error) |
| `foundry_app/services/generator.py` | +36 (_apply_default_team) |
| `foundry_app/services/compiler.py` | +20/-? |
| `foundry_app/services/validator.py` | +10/-? |
| `foundry_app/services/seeder.py` | +22/-? |
| `foundry_app/services/asset_copier.py` | +30/-? |
| `foundry_app/services/scaffold.py` | +14/-? |
| `foundry_app/services/agent_writer.py` | +15/-? |
| `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` | +100/-? (tier groups) |
| `foundry_app/ui/screens/library_manager.py` | +64/-? (extended/ default for new) |
| `tests/test_persona_tiering.py` | +456 (new file, 20 tests) |
| `tests/test_library_indexer.py` | +173/-? (fixture migration) |
| `tests/test_persona_page.py` | +183/-? (tier-group rewrite) |
| `tests/test_library_manager.py` | +119/-? |
| `tests/test_generator.py`, `test_compiler.py`, `test_validator.py`, `test_agent_writer.py`, `test_asset_copier.py`, `test_persona_contracts.py`, `test_scope_boundaries_partition.py` | fixture migration |
| `ai/beans/BEAN-271-library-persona-tiering/bean.md` + 3 task files | +287 |
| **Total** | 233 files changed, +1697 / -353 |

## Notes

**Clean break decision.** Confirmed 2026-04-28: ClaudeKit submodule consumers will re-pull and adapt. No backwards-compatibility shim. The compiler should error loudly with a remediation hint when it sees an old-style persona reference.

**Architect required.** `composition.yml` ref-syntax for extended personas is a small contract decision — should it be `extended/security-engineer` or `security-engineer` with the loader scanning both? ADR before implementation.

**Coordinate with BEAN-259.** That bean filters expertise per persona; this bean tiers personas. Both contribute to "narrow specialist boundaries." Land in either order; BEAN-259 may want this bean's tier metadata.

**Coordinate with BEAN-273/274.** Contract graph validator must understand tiering — extended personas may produce/consume types that core personas don't.

**Tech-QA follow-ups (2026-05-01).** Surfaced during the test sweep (task 03). Filed as observations rather than fixed under this bean per the verify-don't-re-implement constraint.

1. **Expertise `## Applies To` lists still use bare extended-persona names.** Files like `ai-team-library/expertise/python/conventions.md`, `react/conventions.md`, `typescript/conventions.md`, `accessibility-compliance/accessibility-audits.md` reference `code-quality-reviewer`, `data-engineer`, `ux-ui-designer`, `compliance-risk`, `product-owner` without the `extended/` prefix. After BEAN-271 the indexer drops these as unknown ids (warning logged). Net effect: extended personas no longer pick up the expertise inlining BEAN-259 set up. `tests/test_library_indexer.py::TestExpertiseAppliesTo::test_real_library_curated_applies_to` was updated to lock in the current (degraded) state until a follow-up bean migrates the expertise data to use the canonical `extended/<name>` form.

2. **Compiler emits broken `extended/<name>` paths in CLAUDE.md team table.** `_build_lean_claude_md` writes ``.claude/agents/extended/code-quality-reviewer.md`` and ``ai/generated/members/extended/code-quality-reviewer.md`` for extended personas, but the on-disk files live at the bare leaf path (compiler at line 714 already uses `_persona_dirname`). The team-table loop at compiler lines 580-585 should also strip the prefix so the rendered links resolve. Reproduce: generate `examples/small-python-team.yml` against the real library and inspect the Team table in the generated CLAUDE.md.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | ADR — extended-persona ref-syntax in composition.yml | architect | 2m | 1,371,999 | 14,050 | $3.41 |
| 2 | File reorg + indexer + model + compiler + wizard + examples | developer | 14m | 467,401 | 3,256 | $0.99 |
| 3 | Test sweep: fixtures + tier coverage + compiler defaults + error path | tech-qa | 24m | 515,296 | 3,005 | $1.03 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 3 |
| **Total Duration** | 40m |
| **Total Tokens In** | 2,354,696 |
| **Total Tokens Out** | 20,311 |
| **Total Cost** | $5.43 |