# Changelog

All notable changes to Foundry are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-02-06

### Added

**Core Pipeline**
- Full generation pipeline: Validate, Scaffold, Compile, Seed, Manifest, Diff Report
- Generator service orchestrating all pipeline stages with logging
- Scaffold service creating CLAUDE.md, README.md, agent files, project context, output directories
- Compiler service producing compiled member prompts from persona + stack + project context
- Jinja2 template rendering in compiler with graceful fallback on syntax/undefined errors
- Seeder service generating starter task lists based on persona dependency waves
- Diff reporter comparing successive generation runs (new/removed files, stage changes)
- Manifest tracking with JSON persistence and composition snapshots

**Data Layer**
- Pydantic models: CompositionSpec, GenerationManifest, LibraryIndex, AppSettings, and more
- YAML composition IO with CompositionIOError custom exception and specific error handling
- JSON manifest IO with validation and descriptive error messages
- Settings persistence at ~/.config/foundry/settings.json with corruption recovery

**Validation**
- Pre-generation validation: composition completeness, library persona/stack existence, template references
- Three strictness modes: light (fatal only), standard (errors + warnings), strict (all promoted)
- Post-generation validation: CLAUDE.md, agent definitions, compiled member prompts
- Export validation: self-contained check, symlink detection

**GUI (PySide6)**
- Main window with three-pane layout: navigation tree, content area, inspector panel
- 5-step project wizard: Identity, Stacks, Personas, Hooks, Review/Generate
- Composition editor with synchronized Form and YAML views
- Generate screen with pipeline runner, progress display, and manifest inspector
- Export screen with pre-export checklist, copy/move modes, and git init option
- History screen with recent projects, generation logs, and manifest viewer tabs
- Settings screen for all app preferences
- Library browsers: Persona, Stack, Template (cross-cut), Hooks, Workflows, Skills/Commands
- Markdown editor widget for inline library file editing

**CLI**
- `foundry-cli generate` — full pipeline with strictness override
- `foundry-cli validate` — pre-generation checks only
- `foundry-cli export` — copy/move with optional git init and pre-export validation
- `foundry-cli info` — display manifest metadata
- `foundry-cli diff` — display diff report

**Library**
- 13 personas: team-lead, ba, architect, developer, tech-qa, code-quality-reviewer, devops-release, security-engineer, compliance-risk, researcher-librarian, technical-writer, ux-ui-designer, integrator-merge-captain
- 11 tech stacks: python, python-qt-pyside6, react, typescript, node, java, dotnet, sql-dba, devops, security, clean-code
- Each persona includes: persona.md, outputs.md, prompts.md, templates/
- Jinja2 variables in library files: {{ project_name }}, {{ stacks | join(", ") }}, {{ strictness }}
- 4 example compositions: small-python-team, full-stack-web, security-focused, foundry-dogfood
- 5 hook packs: hook-policy, pre-commit-lint, post-task-qa, security-scan, compliance-gate
- Skills and commands for Claude Code integration

**Infrastructure**
- Structured logging with RotatingFileHandler (~/.local/share/foundry/logs/)
- Settings validation helpers for library and workspace paths
- Export service with copy/move/git-init (pure business logic, no Qt dependency)
- Library indexer with JSON cache
- CI workflow (.github/workflows/ci.yml) with Python 3.11+3.12 matrix
- 195 tests across 16 test files
