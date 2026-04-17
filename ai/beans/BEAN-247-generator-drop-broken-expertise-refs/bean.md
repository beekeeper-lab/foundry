# BEAN-247: Drop Broken Expertise References from Generated CLAUDE.md

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-247 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

A freshly generated project's `CLAUDE.md` contains references to expertise files that the generator never wrote. Concretely, when `small-python-team.yml` is generated, the compiler lists `ai/generated/expertise/clean-code.md` in the references section, but the file is never emitted because `ai-team-library/expertise/clean-code/` has no `conventions.md`. The generator prints a warning ("Expertise 'clean-code' missing conventions.md") and continues silently.

External review (2026-04-17) flagged this as an integrity failure: a generated project shipping with broken internal references erodes trust in the framework. BEAN-243 eliminated `{{ ... }}` leakage from generated files; this bean closes the adjacent class of defect — *referenced-but-never-written* paths in compiled documentation.

## Goal

A generated project contains zero references to files that were not actually emitted. If an expertise source is missing, either:

1. The expertise is omitted from CLAUDE.md's reference list (preferred — a warning is still emitted to `warnings`), **or**
2. The build fails in strict mode so the issue is surfaced at generation time rather than discovered by a reader.

## Scope

### In Scope
- `foundry_app/services/compiler.py`: when `_compile_expertise_section` returns `None` (source missing), do not write a file **and** do not list the expertise in whatever section of CLAUDE.md currently produces the `ai/generated/expertise/<id>.md` reference.
- Keep the existing warning so the missing source is still surfaced.
- Optional strict-mode switch: if `spec.generation.strict_references` (new field) is true, fail the build when any referenced artifact was not emitted. Default false to preserve current behavior.
- Unit tests that assert the reference line is absent for a missing-source expertise.
- BEAN-242's structural test extended (or a peer test added) to scan CLAUDE.md for `ai/generated/expertise/<id>.md` references and assert each referenced file exists on disk.

### Out of Scope
- Adding the missing `clean-code` conventions content (BEAN-248).
- Redesigning CLAUDE.md layout.
- Per-persona reference checking (separate concern — file this as a follow-up bean if needed).

## Acceptance Criteria

- [ ] When an expertise source is missing, the generated `CLAUDE.md` does not list `ai/generated/expertise/<id>.md` as a reference path.
- [ ] The existing warning is still emitted via `StageResult.warnings`.
- [ ] A new test (in `tests/test_compiler.py` or `tests/test_generator.py`) asserts every `ai/generated/expertise/*.md` reference in the generated CLAUDE.md corresponds to a file on disk.
- [ ] Manual verification: regenerate `small-python-team.yml` → `CLAUDE.md` no longer lists `clean-code.md` under references, and no broken links remain.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Origin.** External review (2026-04-17): "Your CLAUDE.md references `ai/generated/expertise/clean-code.md` ... I did not find `clean-code.md`. A generated project should not ship with broken internal references."

**Relationship to BEAN-248.** BEAN-248 fixes the *content* side (add the missing `conventions.md`). This bean fixes the *generator* side so the same class of bug cannot recur when another expertise is added without full content.

**Related prior beans.** BEAN-242 (integration test contract), BEAN-243 (Jinja placeholder leak), BEAN-244 (composition.yml + README.md emission).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
