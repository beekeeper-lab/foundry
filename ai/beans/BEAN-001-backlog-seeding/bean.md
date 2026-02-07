# BEAN-001: Backlog Seeding Infrastructure

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-001 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

## Problem Statement

The seeder currently creates a flat `seeded-tasks.md` file. When using the beans workflow, we need the seeder to optionally generate per-bean directories with task files instead of (or in addition to) the flat file. This would allow generated projects to start with a structured backlog out of the box.

## Goal

Extend the seeder service to support a `beans` seed mode that creates `ai/beans/` with an index, template, and initial bean directories — matching the structure defined in `bean-workflow.md`.

## Scope

### In Scope
- New seed mode option (`beans`) alongside `detailed` and `kickoff`
- Bean directory structure generation (index, template, bean dirs with tasks/)
- Configurable initial beans via composition spec or a separate beans input file

### Out of Scope
- GUI changes to the wizard (follow-up bean)
- Modification of existing `detailed` or `kickoff` seed modes

## Acceptance Criteria

- [ ] Seeder supports `seed_mode: beans` in `GenerationOptions`
- [ ] Generated beans directory matches the structure in `bean-workflow.md`
- [ ] Existing seed modes (`detailed`, `kickoff`) are unaffected
- [ ] Tests cover the new seed mode
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

This bean is about making Foundry generate the beans structure — the manual beans system (created in this dogfooding setup) serves as the reference implementation.
