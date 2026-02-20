# Changelog

All notable changes to Foundry are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

**App**
- BEAN-036..052: Industrial theme restyle — sidebar, wizard cards, forms, progress screens, typography, icons, accessibility polish
- BEAN-058..061: Branded spinner, theme wiring fix, sidebar navigation modernization, menu bar removal
- BEAN-062..064: Settings screen — core paths, generation & safety defaults, appearance & advanced
- BEAN-065..067: Wire screens into main window, builder wizard screen, compiler & asset copier pipeline wiring
- BEAN-068: Agent writer service for persona + stack team member files
- BEAN-069: Workflow hook packs (Git & Az)
- BEAN-070: MCP config generation
- BEAN-071: Skills & commands copier enhancement
- BEAN-075..078: Auto-detect library root, sidebar nav restyle, wizard validation feedback, empty-state messaging
- BEAN-081..108: Library Manager CRUD for all asset types (personas, stacks, templates, workflows, commands, skills, hooks)
- BEAN-111: Wire generate button to pipeline with progress
- BEAN-117..119: End-to-end project generation test, team persona agent verification, full agentic infrastructure export
- BEAN-124..129: Hook-selective asset copier, MCP config (Obsidian & Trello), native Claude Code hooks, scaffold skills directory, generation progress UI missing stages, seeder templates for all 13 personas
- BEAN-156: AI code review anti-patterns documentation
- BEAN-157: Test generator stage callback contract

**Process**
- BEAN-072..074: Obsidian review skill, approval gate wiring, bean workflow docs update
- BEAN-079..080: Obsidian MCP integration, bean & task telemetry automation
- BEAN-114..116: Telemetry backfill from git history, live telemetry capture fix, telemetry summary report command
- BEAN-120..122: Telemetry table population & duration tracking, token usage capture via JSONL, structured Trello linkage
- BEAN-130: Telemetry cost estimation
- BEAN-142: Verification-Driven Development (VDD) policy
- BEAN-143..153: Agent behavior improvements — downstream gate, bottleneck check, micro-iteration loop, rule extractor, molecularity gate, comprehension gate, hard reset protocol, examples-first, context diet, blast radius budget, continuous assignment loop

**Infra**
- BEAN-154..155: Trello integration tests and lifecycle E2E test
- /bg command for background tmux execution
- Trello MCP server configuration
- Deploy skill documentation review phase
- Command reorganization into three tiers (user / internal / deprecated)

### Changed
- BEAN-131..141: Command and workflow analysis — backlog-refinement, long-run, show-backlog, backlog-consolidate, deploy, trello-load, team member assignment analysis and recommendations, Trello-bean lifecycle mapping, token usage optimization
- Default wave model: Developer → Tech-QA (mandatory). BA and Architect are opt-in with documented triggers.

### Fixed
- BEAN-053: P0 bug fixes
- BEAN-055: Wire real services & clean up dead code
- BEAN-109..110: Library Manager missing CRUD test coverage, sidebar nav button contrast
- BEAN-112..113: Path traversal hardening, input bounds & error sanitization
- BEAN-115: Live telemetry capture fix
- BEAN-123: Project slug output folder test
- Telemetry fix for parallel mode token capture

### Infrastructure
- BEAN-054: Security hardening
- BEAN-056..057: Robustness improvements, test coverage gaps
- Test suite growth: 195 → 1811 tests across 38 modules

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
- 6-step project wizard: Project, Stack, Persona, Architecture, Hooks, Review/Generate
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
