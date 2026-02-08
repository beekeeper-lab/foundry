# BEAN-041: Library Manager — Template Editor

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-041 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Templates are the deliverable blueprints that personas use — test plans, ADRs, PR descriptions, risk logs, and more. They exist in two locations: per-persona (`personas/{id}/templates/`) and shared (`templates/shared/`). Currently there's no way to browse templates across personas, create new ones, or edit existing ones from within the app. Users who want to customize their team's output formats must manually navigate the file system.

## Goal

Add template management capabilities to the Library Manager screen. Users can browse all templates (both per-persona and shared), edit them using the Markdown Editor Widget, create new templates, and delete templates they no longer need.

## Scope

### In Scope
- Tree view integration: persona template nodes expand to show individual template files; shared templates shown under their own top-level node
- Clicking a template file opens it in the Markdown Editor Widget for editing
- "New Template" action on a persona's templates/ node or on the Shared Templates node: prompts for filename, creates a new `.md` file with a basic template structure (title, metadata table, placeholder fields, checklist, DoD)
- "Delete Template" action: confirmation dialog, removes the file
- Visual distinction between per-persona and shared templates in the tree
- Tree refreshes after create/delete operations

### Out of Scope
- Moving or copying templates between personas (complex UX — defer)
- Template variable validation ({{ placeholder }} syntax checking)
- Template preview with variables resolved
- Bulk operations (import/export template packs)

## Acceptance Criteria

- [ ] Per-persona templates appear under each persona's node in the tree
- [ ] Shared templates appear under a dedicated "Shared Templates" node
- [ ] Users can open and edit any template via the Markdown Editor Widget
- [ ] "New Template" creates a file with the standard template structure
- [ ] "Delete Template" shows confirmation dialog before removing the file
- [ ] Filename validation prevents invalid names and duplicates within the same scope
- [ ] Tree view refreshes after create and delete operations
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover template CRUD operations
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-037 (screen shell & tree) and BEAN-038 (markdown editor widget).
- Template files follow the standardized format: `# title`, Metadata table, `[placeholder]` fields, `- [ ]` checklists, `*italic*` guidance, DoD at bottom. The starter template for "New Template" should follow this convention.
- There are currently 7 shared templates and 10-30 templates per persona, so the tree can get large. Consider lazy-loading template lists.
