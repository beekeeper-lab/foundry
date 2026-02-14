# BEAN-117: End-to-End Project Generation Test

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-117 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-13 |
| **Started** | 2026-02-14 |
| **Completed** | 2026-02-14 00:02 |
| **Duration** | < 1m |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

The test suite has strong per-service unit tests and minimal integration tests (e.g., `TestPipelineExecution`) that use mock fixtures, but there is no end-to-end test that runs the full generation pipeline against the **real `ai-team-library`** and verifies the generated project folder is correct and complete. This means regressions in cross-service integration or library content changes could go undetected.

## Goal

A `TestEndToEnd` class in `tests/test_generator.py` that loads `examples/small-python-team.yml`, points at the real `ai-team-library`, runs the full 8-stage pipeline to a `tmp_path`, and verifies both the structural layout and key file contents of the generated project.

## Scope

### In Scope
- New `TestEndToEnd` class added to `tests/test_generator.py`
- Uses `examples/small-python-team.yml` as the composition fixture
- Uses the real `ai-team-library/` (not mocked)
- Runs the full pipeline: validate → scaffold → compile → agent writer → copy assets → MCP config → seed tasks → safety → diff report
- **Structural verification**: all expected directories and files exist and are non-empty (CLAUDE.md, agent files, skills/, commands/, hooks/, settings.local.json, manifest.json)
- **Deep content verification** on key files:
  - CLAUDE.md contains persona-specific sections (team-lead, developer, tech-qa, code-quality-reviewer) and stack content (python, clean-code)
  - manifest.json has valid JSON structure with expected fields (stages, timestamp, composition)
  - Agent .md files reference correct persona names
- Verifies manifest records all pipeline stages that ran

### Out of Scope
- Testing other example compositions (full-stack-web, security-focused, foundry-dogfood) — can be added later
- Overlay mode E2E testing (already covered by `TestOverlayGeneration`)
- GUI/UI integration testing
- Performance benchmarking or timing assertions

## Acceptance Criteria

- [x] `TestEndToEnd` class exists in `tests/test_generator.py`
- [x] Test loads `examples/small-python-team.yml` and parses it into a `CompositionSpec`
- [x] Test uses the real `ai-team-library/` directory (resolved relative to repo root)
- [x] Test runs the full generation pipeline to a `tmp_path` output directory
- [x] Structural checks pass: expected files/dirs exist and are non-empty
- [x] CLAUDE.md contains sections for all 4 personas and 2 stacks from the composition
- [x] manifest.json is valid JSON with pipeline stage records
- [x] Agent .md files are generated for each persona
- [x] All tests pass (`uv run pytest`)
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Existing integration tests to reference: `TestPipelineExecution` (line 796), `TestFullIntegration` in `test_compiler.py` (line 1004), `TestCLIIntegration` in `test_cli.py` (line 332)
- The `small-python-team.yml` composition has 4 personas (team-lead, developer, tech-qa, code-quality-reviewer) and 2 stacks (python, clean-code) with `seed_tasks=true` and `write_manifest=true`
- Source Trello card: "Create a test that goes all the way through and creates a project"

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
