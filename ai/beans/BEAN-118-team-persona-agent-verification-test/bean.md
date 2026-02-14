# BEAN-118: Team Persona Agent Verification Test

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-118 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-13 |
| **Started** | 2026-02-14 |
| **Completed** | 2026-02-14 00:05 |
| **Duration** | < 1m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

When a project is generated, the Agent Writer service creates agent `.md` files for each persona selected in the composition. However, there is no test that verifies the generated team is correct — that every persona selected in the composition spec results in a corresponding agent file with the right content. A mismatch (missing agent, extra agent, wrong persona reference) would go undetected.

## Goal

A test that generates a project from a composition spec, then inspects the generated team directory to confirm there is exactly one agent file per selected persona, each referencing the correct persona name and containing expected agent configuration.

## Scope

### In Scope
- New test class in `tests/test_agent_writer.py` (or `tests/test_generator.py` alongside the E2E test)
- Verify agent file count matches persona count from the composition
- Verify each agent file references the correct persona name
- Verify agent files are non-empty and well-structured
- Test against `examples/small-python-team.yml` (4 personas: team-lead, developer, tech-qa, code-quality-reviewer)

### Out of Scope
- Testing agent file content beyond persona name verification (detailed prompt content)
- Testing the Agent Writer service internals (already covered by unit tests)
- GUI/UI testing of persona selection

## Acceptance Criteria

- [x] Test exists that loads a composition spec with multiple personas
- [x] Test runs the agent writer (or full pipeline) and produces agent files in the output directory
- [x] Test asserts one agent `.md` file per persona in the composition
- [x] Test asserts each agent file contains the correct persona name reference
- [x] Test asserts no extra or missing agent files relative to the composition
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Source: Trello card 'Create a test that inspects the Team when the project is created. Confirm there is a team member for each persona that is selected in the workflow.'
- Card URL: https://trello.com/c/BPdUaOAq
- Related: BEAN-117 (E2E Project Generation Test) — these could share fixtures

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 |      |       |          |           |            |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
