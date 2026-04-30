# BEAN-259 Verification Report

**Date:** 2026-04-30
**Persona:** tech-qa
**Bean:** BEAN-259 — Persona-Scoped Expertise Inclusion
**Branch:** `bean/BEAN-259-persona-scoped-expertise-inclusion`
**ADR under verification:** ADR-012 (decisions.md L1531–1612)

## Summary

All 12 verification checks PASS. The compiler now filters expertise per persona based on each expertise's `## Applies To` section (Mechanism A in the bean). Backward-compat default (empty list = applies to all) is preserved. The lean `CLAUDE.md` Tech Stack table and standalone `ai/generated/expertise/<id>.md` files are intentionally unfiltered, matching the ADR's filter contract.

## Verification Matrix

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | ADR present and consistent | PASS | `ai/context/decisions.md` L1531 starts `## ADR-012: Per-Expertise Persona Relevance for Compile-Time Filtering`; **Bean** field on L1537 = `BEAN-259`; ADR specifies Mechanism A, `## Applies To` heading, `ExpertiseInfo.applies_to: list[str]` default `[]`, helper name `_expertise_applies_to`. Implementation matches every clause. |
| 2 | Library metadata on 4 files | PASS | `python/conventions.md` L6 (5 personas), `typescript/conventions.md` L6 (4 personas), `react/conventions.md` L6 (5 personas), `accessibility-compliance/accessibility-audits.md` L6 (5 personas). All present with non-empty bulleted persona lists. |
| 3 | Pydantic model | PASS | `foundry_app/core/models.py` L565: `applies_to: list[str] = Field(default_factory=list, …)` with ADR-012 reference in the description. |
| 4 | Indexer + filter helper | PASS | `library_indexer.py` L95 `_parse_expertise_applies_to`, L171 wired into `build_library_index`, L178 `_validate_expertise_applies_to` drops bogus persona IDs with a warning at L200. `compiler.py` L158 `_expertise_applies_to(persona_id, expertise_info) -> bool` returns True when `applies_to` is empty or `persona_id in applies_to`. |
| 5 | Filter applied in agent_writer | PASS | `agent_writer.py` L193 `all_expertise_sections` now stores `{"name", "highlights", "info"}` (each entry retains source `ExpertiseInfo`). L266–270 the per-persona Jinja context's `expertise_sections` list is rebuilt inside the `for persona_sel in spec.team.personas` loop and filtered through `_expertise_applies_to(persona_sel.id, entry["info"])`. The shared list is no longer passed to the template; ADR clause (filter contract #2) satisfied. |
| 6 | Lean CLAUDE.md not filtered | PASS | Generated `examples/full-stack-web.yml` to a fresh tmp dir. `CLAUDE.md` Tech Stack table lists all 4 selected expertise (React, Typescript, Node, Clean Code) regardless of any persona's `applies_to`. |
| 7 | Standalone expertise files not filtered | PASS | `ai/generated/expertise/` for full-stack-web contains `clean-code.md`, `node.md`, `react.md`, `typescript.md` — every selected expertise that has a `conventions.md`. (`accessibility-compliance` has no `conventions.md` so it is not emitted as a standalone file in any composition; that is pre-existing behavior, not a BEAN-259 regression.) |
| 8 | Forward filter — React/TS+Python | PASS | Generated a tech-qa verification composition (python+typescript+react+a11y, full team incl. ux-ui-designer). Counts in `.claude/agents/`: <br>• `devops-release.md`: tsconfig=0, ruff=0, react-as-content=0 (single `react` token is in the `**Expertise:**` header line, not filtered content). <br>• `ux-ui-designer.md`: tsconfig=0, ruff=0; legitimate React content present (ux-ui-designer is in react.applies_to). <br>• `developer.md`: tsconfig=2, ruff=1, React present. ADR test cases 1, 2, 3 all hold. |
| 9 | Backward compat — small-python-team | PASS | Generated `examples/small-python-team.yml`; exit 0; layout = `.claude/agents/`, `ai/generated/{members,expertise}/`. Personas in scope: team-lead, developer, tech-qa, code-quality-reviewer (all 4 are in python.applies_to). Developer's agent file has `ruff` (Python content intact). Generation succeeded with the curated metadata in place; no regression for personas inside `applies_to`. |
| 10 | Token / size reduction ≥20% | PASS | `uv run python scripts/measure_bean_259_savings.py` → RESULT: PASS. Per-persona reductions: ba 55.6%, devops-release 59.6%, security-engineer 56.2%, ux-ui-designer 38.9%. Architect/developer/tech-qa unchanged (in every applies_to). Largest non-Developer reduction: devops-release at 59.6% — far above 20%. |
| 11 | Test suite + lint | PASS | `uv run pytest` → **2194 passed** in 11.65s (above the 2189–2194 reported by developer; 2169+ baseline + ~25 new BEAN-259 tests). `uv run ruff check foundry_app/` → "All checks passed!" |
| 12 | ADR test cases (smoke) | PASS | `uv run pytest -k "applies_to or filter or savings or scope" --tb=short -q` → 48 passed, 2146 deselected. Includes ADR-012 cases 1–6 (test_agent_writer.py L795/805/818/853/866/895) and the unit test class `TestExpertiseAppliesTo` in test_compiler.py L2208. |

## Detailed Findings

### Filter behavior on the verification composition

For a composition with python+typescript+react+accessibility-compliance and a 7-persona team (developer, tech-qa, architect, devops-release, ux-ui-designer, ba, security-engineer):

| Persona | tsconfig | ruff | react (word) | Notes |
|---|---|---|---|---|
| developer | 2 | 1 | 5 | In every applies_to — full content. |
| ux-ui-designer | 0 | 0 | 4 | Only react.applies_to includes ux-ui-designer; python/typescript stripped as expected. |
| devops-release | 0 | 0 | 1 (header only) | Stripped from all 3 language expertise; the lone `react` is in the project's overall `**Expertise:**` line. |
| ba | — | — | — | Reductions visible via measurement script; ba not in any language applies_to. |

ADR-012 test cases 1, 2, 3 all hold against the generated artifacts.

### Measurement script result

```
Persona                     Before B    After B        Δ B       %
architect                       4331       4331          0    0.0%
ba                              4023       1787       2236   55.6%
developer                       4499       4499          0    0.0%
devops-release                  3749       1513       2236   59.6%
security-engineer               3979       1743       2236   56.2%
tech-qa                         4211       4211          0    0.0%
ux-ui-designer                  4019       2457       1562   38.9%

Largest reduction (non-Developer): devops-release = 59.6%
RESULT: PASS
```

Architect/developer/tech-qa show 0% because they appear in every selected expertise's `applies_to` list — the curated metadata covers them everywhere, so their content is unchanged. That matches the ADR's design intent ("Developer is unaffected by design").

### Test coverage cross-check

The targeted run picks up:

- `test_compiler.py::TestExpertiseAppliesTo` — pure unit tests for the filter helper (empty list / persona present / persona absent).
- `test_compiler.py::TestExpertiseAppliesToCompilerIntegration` — end-to-end in-tree compose with `## Applies To` markdown.
- `test_agent_writer.py` — ADR-012 cases 1–6 spelled out by name (lines 795/805/818/853/866/895).
- `test_library_indexer.py` — `_parse_expertise_applies_to` happy-path and `_validate_expertise_applies_to` warning path (bogus persona IDs).

## Verdict

**OVERALL: PASS**

All 9 acceptance criteria from `bean.md` L43–51 are satisfied:

- [x] ADR-012 recorded with chosen Mechanism A and rationale.
- [x] Library metadata (`## Applies To`) on 4 expertise files.
- [x] Compiler (`_expertise_applies_to`) and agent_writer (per-persona-loop filter) respect the metadata.
- [x] `small-python-team.yml` regenerates successfully; developer prompt retains Python content.
- [x] React/TS composition: devops-release/ux-ui-designer member prompts contain no `tsconfig` and no `ruff`; developer prompt contains both.
- [x] Token reduction: devops-release 59.6% / security-engineer 56.2% / ba 55.6% / ux-ui-designer 38.9% — all ≥20%.
- [x] Tests cover the filter end-to-end for ≥2 personas (and in fact for all listed personas plus pure-unit coverage on the helper).
- [x] `uv run pytest` → 2194 passed.
- [x] `uv run ruff check foundry_app/` → All checks passed.

No required fixes. Ready for Team Lead close-out.
