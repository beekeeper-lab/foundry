# BEAN-027: Compiler Service

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-027 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The generation pipeline needs a compiler stage that reads library source files (persona markdown, stack convention docs) and merges them into a single, deterministic `CLAUDE.md` file. Without this, generated projects have no AI team constitution.

## Goal

Implement `foundry_app/services/compiler.py` with a `compile_project()` function that:
1. Reads persona files (persona.md, outputs.md, prompts.md) from the library
2. Reads stack convention files (conventions.md) from the library
3. Performs Jinja2-style template variable substitution ({{ project_name }}, {{ stacks }})
4. Assembles a single CLAUDE.md with deterministic section ordering
5. Returns a StageResult listing the written file and any warnings

## Scope

### In Scope
- Reading persona source files from the library
- Reading stack convention files from the library
- Template variable substitution (project_name, stacks)
- Deterministic ordering (personas by spec order, stacks by `order` field)
- Writing compiled CLAUDE.md to output directory
- Overlay-safe (overwrites existing CLAUDE.md)
- Warning on missing optional files
- Error on missing required files
- Comprehensive test suite (60+ tests)

### Out of Scope
- Copying agent files (.claude/agents/) — that's BEAN-028 (Asset Copier)
- Copying template files — that's BEAN-028
- Hook/settings compilation — that's BEAN-030 (Safety Writer)
- Pipeline orchestration — that's BEAN-032

## Acceptance Criteria

- [x] `compile_project()` function exists in `foundry_app/services/compiler.py`
- [x] Reads persona.md, outputs.md, prompts.md for each selected persona
- [x] Reads conventions.md for each selected stack
- [x] Substitutes `{{ project_name }}` and `{{ stacks | join(", ") }}` placeholders
- [x] Produces deterministic output (same inputs = identical CLAUDE.md)
- [x] Returns StageResult with `wrote` and `warnings` populated correctly
- [x] Raises or warns appropriately for missing library files
- [x] Overlay-safe: works on existing output directories
- [x] All tests pass (`uv run pytest`) — 466/466
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement compiler.py service | developer | — | Done |
| 2 | Write comprehensive test suite | tech-qa | 1 | Done |
| 3 | Run tests and lint, fix issues | developer | 2 | Done |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Follows the same pattern as scaffold.py: takes CompositionSpec + output_dir, returns StageResult
- Additionally needs LibraryIndex and library_root to locate source files
- Template variables use Jinja2 `{{ }}` syntax found in library persona files
