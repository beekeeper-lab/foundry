# BEAN-039: Library Manager — Persona Editor

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-039 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Personas are the core building block of Foundry's library — each one defines an AI team member's role, outputs, prompts, and templates. Currently, creating or modifying a persona requires manually creating directories and markdown files with the correct structure. There's no in-app way to manage personas, making it error-prone and inaccessible to users unfamiliar with the library layout.

## Goal

Add persona management capabilities to the Library Manager screen. Users can edit existing persona files (persona.md, outputs.md, prompts.md), create new personas with properly scaffolded directories, and delete personas they no longer need. All editing uses the shared Markdown Editor Widget from BEAN-038.

## Scope

### In Scope
- Context menu or toolbar actions on persona nodes in the tree: "New Persona", "Delete Persona"
- Clicking a persona file (persona.md, outputs.md, prompts.md) opens it in the Markdown Editor Widget for editing
- "New Persona" action: prompts for persona ID (slug), creates the directory structure with starter files:
  - `personas/{id}/persona.md` (from a starter template)
  - `personas/{id}/outputs.md` (from a starter template)
  - `personas/{id}/prompts.md` (from a starter template)
  - `personas/{id}/templates/` (empty directory)
- Starter templates contain the expected markdown structure with placeholder content
- "Delete Persona" action: confirmation dialog ("Delete persona '{id}' and all its files? This cannot be undone."), then removes the entire persona directory
- Tree refreshes after create/delete operations
- Validation: persona ID must be a valid slug (lowercase, hyphens, no spaces), must not collide with existing persona

### Out of Scope
- Editing persona templates (handled by BEAN-041)
- Renaming a persona (complex due to references — defer to a future bean)
- Persona preview/testing (running a persona in a sandbox)
- Bulk operations (multi-select delete, import/export)

## Acceptance Criteria

- [ ] Users can open and edit persona.md, outputs.md, and prompts.md via the Markdown Editor Widget
- [ ] "New Persona" creates a properly structured persona directory with starter files
- [ ] New persona ID is validated (slug format, no duplicates)
- [ ] "Delete Persona" shows a confirmation dialog before deleting
- [ ] Delete removes the entire persona directory and all contents
- [ ] Tree view refreshes after create and delete operations
- [ ] Starter templates contain meaningful placeholder content (not empty files)
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover persona creation, deletion, and validation logic
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-037 (screen shell & tree) and BEAN-038 (markdown editor widget).
- The 13 existing personas provide good reference for what starter templates should contain.
- Consider whether the persona.md starter template should include the standard sections (Mission, Scope, Operating Principles, etc.) pre-filled with guidance text.
