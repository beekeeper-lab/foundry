# BEAN-277: Programmatic VDD Gate Skill

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-277 |
| **Status** | Approved |
| **Priority** | Medium |
| **Created** | 2026-04-28 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
| **Category** | Process |
| **Depends On** | — |

## Problem Statement

The VDD (Verification-Driven Development) gate today is prose review (`team-lead.md:74-92`): "concrete evidence" reviewed manually by a human (or by Team-Lead reading the bean's acceptance criteria and checking each off in conversation). It works, but:

- It's slow.
- It depends on the reviewer's discipline.
- The evidence isn't structured, so we can't build telemetry on it later (BEAN-278 wants this).
- It blocks `/merge-bean` in spirit but not in code.

`vdd-policy.md` (`ai/context/vdd-policy.md`) defines the policy. There's no command that runs it.

## Goal

A `/vdd` command parses a bean's Acceptance Criteria, runs each "concrete evidence" check programmatically, and emits a structured pass/fail report. `/merge-bean` refuses to merge a bean whose VDD report does not pass.

## Scope

### In Scope

- New library skill `ai-team-library/claude/skills/vdd/SKILL.md` (canonical spec):
  - Parse `bean.md` Acceptance Criteria checklist.
  - For each criterion, identify the evidence type:
    - **Test**: `pytest -k <pattern>` or path → run, capture pass/fail.
    - **Lint**: `ruff check <path>` → run, capture clean/dirty.
    - **File exists / contains**: glob check, optional content match.
    - **Manual** (last resort): emit prompt for human confirmation, recorded in the report.
  - Generate `ai/outputs/tech-qa/vdd-<bean-id>.md` with structured pass/fail per criterion plus aggregate verdict.
- Convention for criteria authors: prefix evidence type when known, e.g., `- [ ] (test:tests/test_foo.py::test_bar) Foo behaves correctly`. Backward-compatible: criteria without prefix default to manual.
- New library command `ai-team-library/claude/commands/vdd.md` (≤30 lines per BEAN-249) — thin trigger.
- Update `ai-team-library/claude/skills/merge-bean/SKILL.md` (or wherever the merge logic lives) to refuse merging if `ai/outputs/tech-qa/vdd-<bean-id>.md` is missing or shows fail.
- Update `ai/context/vdd-policy.md` to reference the new command and the criterion-prefix convention.
- Tests: VDD on a passing bean reports pass; VDD on a failing bean reports fail with specific criterion; merge-bean blocks on missing/failed VDD.

### Out of Scope

- Replacing the prose VDD policy itself (the policy stays; the gate just gets automation).
- Auto-rewriting historical bean ACs to use the new prefix.
- Coverage thresholds, mutation testing, or other test-quality metrics (out of scope; future bean candidate).
- Building the criterion-evidence inference (parser is regex-driven; no LLM in this skill).

## Acceptance Criteria

- [ ] `/vdd <bean-id>` exists and produces `ai/outputs/tech-qa/vdd-<bean-id>.md`.
- [ ] At least three evidence types implemented: test, lint, file-exists. Manual fallback works.
- [ ] `/merge-bean` refuses to merge without a passing VDD report; error message names the bean.
- [ ] Bean template's Acceptance Criteria section is updated to show the evidence-type prefix convention.
- [ ] `vdd-policy.md` references the command.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks populated by Team-Lead. Likely wave: Developer (skill + parser + merge-bean integration), Tech-QA (verification — meta-relevant since this *is* the verification skill). Architect optional.

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Independent.** Doesn't depend on BEAN-273/274/276. Could land first or last in the cluster.

**Dogfood opportunity.** This bean's own AC should use the new evidence-type prefixes — if the parser can verify this bean, the parser works.

**Per BEAN-249**: command ≤30 lines, skill is canonical.

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
