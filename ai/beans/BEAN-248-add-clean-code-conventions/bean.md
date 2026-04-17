# BEAN-248: Add clean-code Expertise Conventions Content

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-248 |
| **Status** | In Progress |
| **Priority** | Medium |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 19:01 |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Infra |

## Problem Statement

`ai-team-library/expertise/clean-code/` is referenced by `examples/small-python-team.yml` but has no `conventions.md`. The generator warns at every run: `Expertise 'clean-code' missing conventions.md`. Users following the documented "try the sample" path see a warning and a broken reference in their freshly generated project — see BEAN-247.

This bean fixes the *content* side: supply real `clean-code` conventions so the library is complete and the sample composition works end-to-end without warnings. BEAN-247 fixes the *generator* side so future missing sources are handled gracefully; this bean removes the specific instance users hit today.

## Goal

`ai-team-library/expertise/clean-code/conventions.md` exists with real, useful content following the standardized expertise template (Defaults table, Do/Don't, Common Pitfalls, Checklist, code examples where appropriate). A generation run against `small-python-team.yml` emits zero warnings related to `clean-code`.

## Scope

### In Scope
- Create `ai-team-library/expertise/clean-code/conventions.md` following the shape of other expertise files (e.g., `ai-team-library/expertise/python/conventions.md`).
- Content areas: naming, comments/docs, function size/responsibility, error handling, testing, refactoring cadence. Opinionated defaults, not a philosophy essay.
- Keep it language-agnostic — this is cross-cutting advice that complements any language expertise.
- Verify the existing `small-python-team` generation run emits no `clean-code`-related warnings.

### Out of Scope
- Creating content for any other expertise beyond `clean-code`.
- Modifying the compiler's handling of missing sources (BEAN-247).
- Restructuring how expertise highlights are extracted (orthogonal).

## Acceptance Criteria

- [ ] `ai-team-library/expertise/clean-code/conventions.md` exists and is non-empty.
- [ ] Follows the standardized expertise template used by other expertise in the library (Defaults table, Do/Don't sections, Common Pitfalls, Checklist).
- [ ] Regenerating `examples/small-python-team.yml` produces no warnings mentioning `clean-code`.
- [ ] Regenerated `CLAUDE.md` includes `ai/generated/expertise/clean-code.md` as a reference and the file exists on disk.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`) — content-only change, but sanity check.

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Author `ai-team-library/expertise/clean-code/conventions.md` following the standardized expertise template | Developer | — | Pending |
| 2 | Verify acceptance: regenerate `small-python-team`, confirm no `clean-code` warnings, confirm `clean-code.md` on disk + referenced from generated `CLAUDE.md`, run `uv run pytest` and `uv run ruff check foundry_app/` | Tech-QA | 1 | Pending |

> Skipped: BA (default — requirements unambiguous, content-only change), Architect (default — no subsystem, module, or dependency changes).

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| — | — |

## Notes

**Origin.** External review (2026-04-17) spotted the broken `clean-code.md` reference in the generated project. Cross-checked on `test`: the generator emits `Expertise 'clean-code' missing conventions.md` every run.

**Shape reference.** Follow `ai-team-library/expertise/python/conventions.md` for layout and length. The standardized template is documented in `MEMORY.md` and the library README.

**Library-modification exception.** The CLAUDE.md rule "Do not modify files in `ai-team-library/`" is about *unauthorized* edits. Intentional additions via approved beans (BEAN-167..212 are precedent) are allowed.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Author `ai-team-library/expertise/clean-code/conventions.md` following the standardized expertise template | Developer | — | — | — | — |
| 2 | Verify acceptance: regenerate `small-python-team`, confirm no `clean-code` warnings, confirm `clean-code.md` on disk + referenced from generated `CLAUDE.md`, run `uv run pytest` and `uv run ruff check foundry_app/` | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |