# BEAN-005: Compiled Prompt Project Context

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-005 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Compiled member prompts (in `ai/generated/members/`) reference generic project context placeholders. When a project has real context (like Foundry's architecture, module map, and conventions), the compiled prompts should incorporate it so each persona has project-specific guidance without needing to read separate context files.

## Goal

Enhance the compiler to optionally inject project context from `ai/context/project.md` into each compiled member prompt, giving every persona immediate awareness of the project's architecture and conventions.

## Scope

### In Scope
- Compiler reads `ai/context/project.md` during compilation
- Project context is appended or injected into each member prompt
- Configurable: opt-in via composition spec or generation options
- Jinja2 template variable for project context

### Out of Scope
- Dynamic context that changes per-task (that's the persona's job to read)
- Modifying the library's persona source files

## Acceptance Criteria

- [x] Compiled member prompts include project context when `project.md` exists
- [x] Context injection is togglable via `inject_project_context` (default: true)
- [x] Each persona's compiled prompt includes project overview and architecture
- [x] `{{ project_context }}` available as Jinja2 variable in library .md files
- [x] Tests verify context injection with and without `project.md` (10 new tests)
- [x] All tests pass (`uv run pytest`) — 323 total
- [x] Lint clean (`uv run ruff check foundry_app/`) — 0 new issues

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Context Injection Requirements | ba | — | Done |
| 02 | Context Injection Implementation | developer | 01 | Done |
| 03 | Context Injection Verification | tech-qa | 02 | Done |

> Note: Architect task skipped — no architectural decisions needed. The core mechanism already exists; this bean adds a toggle, a Jinja2 variable, and tests.

## Notes

This bean complements the hand-crafted `ai/context/project.md` by making it automatically available inside each persona's compiled prompt, reducing context-switching during task execution.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (single commit, no merge).
