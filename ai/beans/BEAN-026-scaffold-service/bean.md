# BEAN-026: Scaffold Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-026 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generation pipeline needs a service that creates the base directory structure for a generated project. Before the compiler can write CLAUDE.md, before the asset copier can place templates, and before the seeder can create tasks, the target directory tree must exist. Without a dedicated scaffold service, each downstream service would need to handle directory creation itself, leading to duplicated logic and inconsistent structures.

## Goal

Implement a scaffold service that takes a CompositionSpec and creates the full directory skeleton for a Claude Code project. The service creates directories only — file content is written by downstream services (compiler, asset copier, safety writer).

## Scope

### In Scope
- `foundry_app/services/scaffold.py` — the scaffold service module
- `scaffold_project(spec, output_dir)` function that creates the directory tree
- Directory structure: `.claude/agents/`, `.claude/commands/`, `.claude/hooks/`, `ai/context/`, `ai/outputs/<persona>/`, `ai/beans/`, `ai/tasks/`
- Returns a `StageResult` with all directories/files created
- Handles overlay mode: skip existing directories, create only missing ones
- Unit tests covering all directory creation paths

### Out of Scope
- Writing file content (CLAUDE.md, agent files, templates) — that's compiler/copier
- Safety config file generation — that's BEAN-030
- Task seeding — that's BEAN-029

## Acceptance Criteria

- [x] `scaffold_project()` creates the full directory tree from a CompositionSpec
- [x] Creates `.claude/` subdirectories (agents, commands, hooks)
- [x] Creates `ai/` subdirectories (context, outputs, beans, tasks)
- [x] Creates per-persona output directories under `ai/outputs/`
- [x] Returns StageResult listing all paths created
- [x] Handles existing directories gracefully (overlay mode)
- [x] Handles empty persona/stack lists
- [x] Unit tests cover happy path, edge cases, and overlay behavior
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement scaffold service | developer | — | Done |
| 2 | Write unit tests | tech-qa | 1 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on BEAN-016 (models). Used by BEAN-032 (Generator Orchestrator). The scaffold service is the first stage of the generation pipeline — it creates the directory skeleton that all subsequent stages populate.
