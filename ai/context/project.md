# Project Context: Foundry

## Overview

Foundry generates Claude Code project folders from reusable building blocks. It combines a PySide6 desktop wizard with a headless CLI, both backed by a shared service layer. The library (`ai-team-library/`) contains personas, stack guides, templates, workflows, skills, commands, and hook packs.

**Version:** 1.0.0 | **License:** MIT | **Python:** >=3.11

## Architecture

The generation pipeline runs six stages in order:

```
Validate → Scaffold → Compile → Copy Assets → Seed → Write Manifest
```

Each stage returns a `StageResult(wrote=[], warnings=[])`. The orchestrator (`generator.py`) chains them and assembles a `GenerationManifest`.

## Module Map

```
foundry_app/
  core/
    models.py          # Pydantic models: CompositionSpec, SafetyConfig, GenerationManifest, LibraryIndex
    settings.py        # App settings (JSON-backed)
    logging_config.py  # Structured logging with rotation
    resources.py       # Resource path helpers
  services/
    generator.py       # Pipeline orchestrator — generate_project()
    validator.py       # Pre-generation validation (strictness levels)
    scaffold.py        # Creates directory tree + context files
    compiler.py        # Compiles per-member prompts from persona + stack files
    asset_copier.py    # Copies skills, commands, hooks into .claude/
    seeder.py          # Generates seed tasks (detailed or kickoff mode)
    safety_writer.py   # Writes settings.local.json from SafetyConfig
    library_indexer.py # Builds LibraryIndex from library directory scan
    diff_reporter.py   # Generates diff report for generated files
    agent_writer.py    # Writes agent definition files per persona
    mcp_writer.py      # Generates MCP configuration files
  io/
    composition_io.py  # YAML/JSON read/write for CompositionSpec
  templates/
    agent.md.j2        # Jinja2 template for agent files
  ui/
    main_window.py     # QMainWindow shell
    generation_worker.py # Background thread for pipeline execution
    theme.py           # Dark/light theme support
    icons.py           # Icon management
    screens/
      builder_screen.py    # Wizard host screen
      builder/
        wizard_pages/      # 6-step wizard: Project → Stack → Persona → Architecture → Hooks → Review
      generation_progress.py # Pipeline runner with progress display
      export_screen.py     # Export with pre-flight checklist
      history_screen.py    # Recent projects + logs
      library_manager.py   # Library browser
      settings_screen.py   # App preferences
    widgets/
      branded_empty_state.py # Empty state placeholder
      markdown_editor.py     # Source + preview editor
      spinner_widget.py      # Branded spinner graphic
  cli.py               # CLI entry point (foundry-cli)
  main.py              # GUI entry point (foundry)
```

## Key Patterns

- **Pydantic models** for all data contracts — `CompositionSpec` is the central spec
- **StageResult** pattern — every pipeline stage returns `StageResult` with `wrote` and `warnings`
- **`_write` helper** in scaffold/compiler — writes file, appends path to `StageResult.wrote`
- **Signal/slot** in UI — PySide6 signals for wizard page validation and generation progress
- **`load_composition` / `save_composition`** in `composition_io.py` — YAML round-trip

## Build Gotchas

- `pyproject.toml` uses `packages = ["foundry_app"]` because the PyPI package name (`foundry`) differs from the directory name (`foundry_app`)
- Build backend is `hatchling.build` (not `hatchling.backends`)
- Use `uv sync` to install dependencies, `uv run` to execute

## Test Patterns

- **1811 tests** across all services and core modules
- Fixtures use `tmp_path` for isolated filesystem tests
- Helper functions like `_make_spec()` create minimal `CompositionSpec` instances
- `LIBRARY_ROOT` constant points to `ai-team-library/` for integration tests
- Tests are in `tests/` with files matching `test_*.py`
