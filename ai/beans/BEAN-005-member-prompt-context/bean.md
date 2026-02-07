# BEAN-005: Compiled Prompt Project Context

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-005 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

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

- [ ] Compiled member prompts include project context when `project.md` exists
- [ ] Context injection is togglable (default: on when `project.md` exists)
- [ ] Each persona's compiled prompt includes the project overview and architecture
- [ ] Tests verify context injection with and without `project.md`
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

This bean complements the hand-crafted `ai/context/project.md` by making it automatically available inside each persona's compiled prompt, reducing context-switching during task execution.
