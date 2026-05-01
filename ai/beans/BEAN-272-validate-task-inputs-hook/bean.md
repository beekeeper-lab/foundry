# BEAN-272: Validate Task `Inputs:` at Dispatch (Pre-Execution Hook)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-272 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-28 |
| **Started** | 2026-04-29 10:51 |
| **Completed** | 2026-04-29 10:59 |
| **Duration** | 1549h 52m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Every persona file (`developer.md:76-84`, `tech-qa.md:100-107`) carries a "Context Diet" rule: read only what the task's `Inputs:` field lists. The architectural review found that the rule is voluntary — many task files omit `Inputs:` entirely, and nothing fails when they do. Personas then default to "read the bean folder + context files," which dumps unrelated context into the worker.

Context engineering only works if the discipline is enforced at the boundary. Right now it's prose-described and ignored half the time.

## Scope

### In Scope

- New hook at `ai-team-library/claude/hooks/validate-task-inputs.py` that:
  - Triggers on the task-status transition to `In Progress` (or, equivalently, when a worker is dispatched via `/spawn-task`).
  - Parses the task file's `Inputs:` field.
  - Fails (blocks the dispatch / status change) when `Inputs:` is missing, empty, or contains only `—` / placeholder values.
  - Emits a remediation message naming the task file and the expected format.
- Same hook copied to Foundry's `.claude/hooks/` via the kit.
- Integration with `/spawn-task` (BEAN-270): `/spawn-task` calls this validator before dispatching.
- Loose mode escape hatch: a task can declare `Inputs: NONE (justified: <reason>)` for the rare task that genuinely needs no specific input (e.g., "scan the repo for X"). The validator allows this when the justification is non-empty and ≥10 chars.
- Update `ai/beans/_bean-template.md` task subsection example to include a populated `Inputs:` block.
- Update `ai-team-library/personas/team-lead/persona.md` task-seeding guidance to require non-empty `Inputs:` for every task.
- Tests for the validator (good/bad/escape-hatch cases).

### Out of Scope

- Validating that the input *files* exist (separate concern; covered loosely by `/spawn-task`).
- Validating that consumed types are produced (BEAN-274's contract graph).
- Auto-suggesting Inputs (out of scope; future bean candidate).
- Retroactively updating historical task files (Done beans stay as-is per repo convention).

## Acceptance Criteria

- [ ] Hook script exists at both library and Foundry kit locations.
- [ ] Hook is registered in `ai-team-library/claude/settings.json` (or wherever hooks register today) so generated projects pick it up.
- [ ] Task with empty/missing `Inputs:` cannot move to `In Progress`; remediation message is clear.
- [ ] Task with `Inputs: NONE (justified: ...)` proceeds.
- [ ] `/spawn-task` (BEAN-270) refuses to dispatch when validation fails.
- [ ] Bean template shows a populated `Inputs:` example.
- [ ] Team-Lead persona doc requires non-empty `Inputs:` for every task.
- [ ] Tests cover the validator end-to-end.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | validate-task-inputs hook + tests + doc updates | Developer | — | Done |
| 02 | Verify acceptance criteria | Tech-QA | 01 | Done |

> Skipped: BA (default — requirements concrete), Architect (default — single hook, follows existing telemetry-stamp.py conventions).

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Pairs with BEAN-270.** The hook is most useful when wired to `/spawn-task`'s dispatch path. Land BEAN-270 first or in the same wave so the integration is real, not aspirational.

**Existing hooks pattern.** Look at `.claude/hooks/telemetry-stamp.py` (per `MEMORY.md`) for the project's conventions on PostToolUse hook implementation. The validator is structurally similar but PreToolUse / pre-dispatch.

**Escape-hatch wording.** The `Inputs: NONE (justified: ...)` form must be uncommon — if it shows up frequently, that signals the validator is too strict, not that the loose escape is too lenient. Add a metric in BEAN-278 to count its use.

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 01 | validate-task-inputs hook + tests + doc updates | Developer | — | — | — | — |
| 02 | Verify acceptance criteria | Tech-QA | — | — | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1549h 52m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |