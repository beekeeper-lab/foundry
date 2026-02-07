# BEAN-034: CLI Interface

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-034 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Foundry currently only supports GUI-based generation. Users who prefer the command line or need CI/CD integration have no way to generate projects non-interactively. A CLI interface is needed to invoke the generator with a composition YAML file.

## Goal

Implement a `foundry-cli` command-line interface that supports non-interactive project generation from a composition YAML file, with flags for library path, output directory, overlay mode, dry-run, and force mode.

## Scope

### In Scope
- Implement CLI module (e.g., `foundry_app/cli.py`)
- Command: `foundry-cli generate <composition.yml> [options]`
- Flags: `--library`, `--output`, `--overlay`, `--dry-run`, `--force`, `--strictness`
- Parse and validate composition, report errors clearly
- Call `generate_project()` from generator service
- Display progress and results to stdout
- Exit codes: 0 success, 1 validation error, 2 generation error
- Register `foundry-cli` entry point in `pyproject.toml`
- Comprehensive test suite

### Out of Scope
- Interactive CLI wizard
- Shell completion scripts
- Plugin system

## Acceptance Criteria

- [x] `foundry-cli generate` command works end-to-end
- [x] Loads composition YAML and validates it
- [x] Supports overlay mode, dry-run, and force flags
- [x] Reports progress and results to stdout
- [x] Exit codes follow conventions
- [x] Entry point registered in `pyproject.toml` (was already registered)
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Implement CLI module | Developer | — | Done |
| 2 | Register entry point | Developer | 1 | Done (already registered) |
| 3 | Write tests (19 tests) | Tech-QA | 1 | Done |

## Notes

- Entry points exist in `pyproject.toml` for `foundry` (GUI) — add `foundry-cli` similarly
- Generator API is ready in `foundry_app/services/generator.py`
- Composition I/O in `foundry_app/io/composition_io.py`
- Depends on BEAN-016 (models/IO) and BEAN-032 (generator), both Done
