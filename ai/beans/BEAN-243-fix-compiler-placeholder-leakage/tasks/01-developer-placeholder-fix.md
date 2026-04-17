# Task 01: Root-Cause Placeholder Fix + Warning Extension

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 16:38 |
| **Completed** | 2026-04-17 16:38 |
| **Duration** | < 1m |

## Goal

Fix placeholder leakage at the root cause in the compile pipeline so `.claude/agents/*.md` and `ai/generated/members/*.md` contain no unresolved Jinja expressions. Extend the existing unresolved-placeholder warning to scan agent files as well.

## Inputs

- `foundry_app/services/compiler.py`
- `foundry_app/services/agent_writer.py`
- `foundry_app/templates/agent.md.j2`
- `ai-team-library/personas/<persona>/persona.md` (contain `{{ project_name }}`, `{{ expertise | join(", ") }}`, `{{ strictness }}`)
- BEAN-242 integration test — drives this fix.

## Root Cause

Two independent gaps:

1. **compiler.py** — `_build_context` only included `project_name` and `expertise`. It did not include `strictness`, which is a **per-persona** value on `PersonaSelection`. When a persona template used `{{ strictness }}` (e.g., `code-quality-reviewer`), `_substitute` had nothing to replace it with and left the literal `{{ strictness }}` in `ai/generated/members/<persona>.md`.
2. **agent_writer.py** — the agent writer extracted raw strings from persona.md (mission, role description, operating principles, expertise highlights) and embedded them into the outer Jinja template as variable values. Jinja does **not** recursively render expressions that appear inside variable values, so any `{{ project_name }}` text inside the extracted mission leaked through into `.claude/agents/<persona>.md`.

## Fix

- `compiler.py` — Added `_build_persona_context(spec, persona_sel)` which extends the shared context with the persona's `strictness.value`. `compile_project` now builds a per-persona context before calling `_compile_persona_section`, so every persona's `{{ strictness }}` resolves to its own value.
- `agent_writer.py` — Before extracting mission/role/key rules, the raw `persona.md` text is piped through `_substitute(text, _build_persona_context(spec, persona_sel))`. Expertise `conventions.md` is run through `_substitute(text, _build_context(spec))` (shared context). Every extracted fragment is already fully substituted before entering the Jinja template.
- `agent_writer.py` — After rendering, the service scans every written agent file and appends a warning to `StageResult.warnings` for any remaining `{{ ... }}` markers, so a regression is never silent.
- `tests/test_compiler.py` — New `TestBuildPersonaContext` and `TestCompilePersonaRendering` classes assert per-persona strictness and confirm no unresolved placeholders are left in compiled member files.
- `tests/test_agent_writer.py` — New `TestAgentPlaceholderRendering` class asserts the two behaviors: `{{ project_name }}`, `{{ strictness }}`, and `{{ expertise | join(...) }}` all resolve in the output; unknown variables surface as warnings.

## Acceptance Criteria

- [x] Root cause documented above.
- [x] Fix is at the root cause (per-persona context + pre-extraction substitution), not post-hoc string replacement.
- [x] Unit tests at compiler and agent-writer layers assert full rendering.
- [x] Placeholder warning now scans `.claude/agents/*.md` as well.
- [x] Regenerated `small-python-team` project contains zero unresolved `{{`, `}}`, `{%`, `%}`.
- [x] BEAN-242 placeholder assertion passes.
- [x] All tests pass except the remaining intentional BEAN-244 red (`test_validate_repo_structural_paths_exist`).
- [x] `uv run ruff check foundry_app/` clean.

## Verification

- `uv run pytest` → 1 failed (the BEAN-244-scoped structural test, intentional), 1793 passed.
- `uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean243-check-new` then `grep -rn '{{' /tmp/bean243-check-new | grep -v '.git/'` → zero matches.
- `uv run ruff check foundry_app/` → All checks passed.

## Definition of Done

- All files changed committed on feature branch.
- Tests and lint pass per the AC above.
