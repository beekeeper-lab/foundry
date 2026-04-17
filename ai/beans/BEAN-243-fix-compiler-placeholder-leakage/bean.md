# BEAN-243: Fix Compiler Placeholder Leakage in Agents and Members

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-243 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 16:31 |
| **Completed** | 2026-04-17 16:39 |
| **Duration** | 1267h 32m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generator leaves Jinja expressions unrendered in portions of the generated project. Verified today on `test` branch by regenerating `examples/small-python-team.yml`:

- `.claude/agents/team-lead.md`, `developer.md`, `tech-qa.md`, `code-quality-reviewer.md` — each contains unresolved `{{ project_name }}`, `{{ expertise | join(", ") }}`, and/or `{{ strictness }}`.
- `ai/generated/members/code-quality-reviewer.md` — unresolved `{{ strictness }}` (generator already warns about this one at generation time).

The generator's placeholder-detection warning system covers `ai/generated/members/` files but does NOT cover `.claude/agents/` files, and it issues warnings without failing the build or actually fixing the leakage.

An agent file that appears compiled is actually half-rendered. A human or Claude reading these sees `**{{ project_name }}**` instead of the actual project name. The team-lead, developer, tech-qa, and code-quality-reviewer agents all read these strings as literal template placeholders during live sessions — this is a framework-integrity failure.

Per-service unit tests pass because they test rendering steps in isolation, not the full assembled output. The integration test from BEAN-242 is the driver for this fix.

## Goal

The generation pipeline fully resolves all Jinja expressions in every generated file. No `{{`, `}}`, `{%`, or `%}` leaks through to the output tree. The fix targets the **root cause** — likely the step that concatenates raw fragments from persona/expertise source files without running them through the Jinja environment with the full composition context — rather than post-hoc string substitution.

## Scope

### In Scope
- Identify the compile-pipeline step(s) that concatenate raw fragments without rendering them. Likely suspects: `foundry_app/services/compiler.py`, `foundry_app/services/agent_writer.py`, or the step that assembles `ai/generated/members/<persona>.md`.
- Ensure every fragment that may contain Jinja expressions is rendered with the full composition context (`project_name`, `strictness`, `expertise` list, etc.).
- Extend the generator's existing placeholder-detection warning system to cover `.claude/agents/*.md` as well, so any future leakage is surfaced.
- Unit tests at the compiler and/or agent-writer layer asserting full rendering.
- Fix leakage in both `.claude/agents/*.md` and `ai/generated/members/*.md`.
- BEAN-242's placeholder assertion goes green after this ships.

### Out of Scope
- Changing the template syntax or engine.
- Redesigning the agent file format.
- Emission of `composition.yml` or `README.md` (BEAN-244).
- Generation progress UX fixes (BEAN-245).

## Acceptance Criteria

- [x] Root cause identified and documented (per-persona context missing `strictness` in compiler; agent_writer embedded raw persona fragments into Jinja template variables without recursive render).
- [x] Fix applied at the root cause (per-persona context + pre-extraction substitution).
- [x] Unit tests at the compiler and agent-writer layer assert full rendering.
- [x] Generator's placeholder-warning now scans `.claude/agents/*.md` (in `agent_writer.py` post-write scan).
- [x] Regenerated `small-python-team` project contains zero unresolved `{{`/`}}`/`{%`/`%}` — verified via `grep -rn '{{' /tmp/bean243-check-new | grep -v '.git/'` → 0 matches.
- [x] BEAN-242 placeholder assertion passes.
- [x] All tests pass except the intentional BEAN-244 structural red (1 failed / 1793 passed).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Root-Cause Fix + Warning Extension | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

> Skipped: BA (default — criteria clear), Architect (default — localized fix, no new subsystem).

## Changes

| File | Lines |
|------|-------|
| `ai/beans/BEAN-243-fix-compiler-placeholder-leakage/bean.md` | ±41 |
| `ai/beans/BEAN-243-fix-compiler-placeholder-leakage/tasks/01-developer-placeholder-fix.md` | +59 |
| `ai/beans/BEAN-243-fix-compiler-placeholder-leakage/tasks/02-tech-qa-verification.md` | +76 |
| `foundry_app/services/agent_writer.py` | +35 |
| `foundry_app/services/compiler.py` | +33 |
| `tests/test_agent_writer.py` | +102 |
| `tests/test_compiler.py` | +78 |

Totals: 7 files changed, +399 / -25.

## Notes

**Depends on:** BEAN-242 (integration test exists first as failing test, drives this fix).

**Specific evidence of leakage** (observed today, 2026-04-17, on `test` branch by regenerating `examples/small-python-team.yml`):

- `.claude/agents/team-lead.md` — `{{ project_name }}`
- `.claude/agents/developer.md` — `{{ project_name }}`, `{{ expertise | join(", ") }}`
- `.claude/agents/tech-qa.md` — `{{ project_name }}`
- `.claude/agents/code-quality-reviewer.md` — `{{ project_name }}`, `{{ strictness }}`
- `ai/generated/members/code-quality-reviewer.md` — `{{ strictness }}` (generator warns about this one)

**Likely root cause hypothesis** (for the executor): the persona library files (`personas/<persona>/persona.md`, `outputs.md`, `prompts.md`) contain Jinja expressions. When the pipeline assembles the final agent file (`.claude/agents/`) or compiled member file (`ai/generated/members/`), it may be reading those fragments verbatim and concatenating them without running through a full Jinja `Environment.from_string(...).render(context)` pass. The existing placeholder-warning system detects this for `ai/generated/members/` (partial coverage) — extend both the detection and the fix to cover `.claude/agents/` too.

**Downstream verification:**

| System | Impact | Verification Command |
|--------|--------|---------------------|
| Tests  | compiler/agent-writer tests updated; BEAN-242 green | `uv run pytest tests/test_compiler.py tests/test_agent_writer.py tests/test_generator.py` |
| Lint   | `foundry_app/` changes | `uv run ruff check foundry_app/` |
| Manual | Regenerate and grep | `uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean243-check && grep -rn '{{' /tmp/bean243-check \| head` |

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Root-Cause Fix + Warning Extension | Developer | — | — | — | — |
| 2 | Tech-QA Verification | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1267h 32m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |