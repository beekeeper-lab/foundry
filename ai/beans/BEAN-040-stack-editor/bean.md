# BEAN-040: Library Manager — Stack Editor

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-040 |
| **Status** | New |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Technology stack files define coding conventions, testing practices, security guidelines, and other standards for each tech stack. Like personas, managing these requires knowledge of the directory structure and manual file creation. Users should be able to add new stacks (e.g., for a framework or language not yet covered) and edit existing convention files without leaving the app.

## Goal

Add stack management capabilities to the Library Manager screen. Users can edit existing stack convention files, create new stacks with a starter directory, add or remove individual files within a stack, and delete entire stacks. All editing uses the shared Markdown Editor Widget from BEAN-038.

## Scope

### In Scope
- Context menu or toolbar actions on stack nodes: "New Stack", "Delete Stack"
- Context menu on individual stack files: "New File", "Delete File"
- Clicking a stack file opens it in the Markdown Editor Widget for editing
- "New Stack" action: prompts for stack ID (slug), creates the directory with a starter `conventions.md` file
- "New File" action within a stack: prompts for filename, creates a new `.md` file with a basic template
- "Delete Stack" action: confirmation dialog, removes the entire stack directory
- "Delete File" action: confirmation dialog, removes the individual file
- Tree refreshes after create/delete operations
- Validation: stack ID must be a valid slug, no duplicates; filenames must end in `.md`

### Out of Scope
- Renaming stacks or files (defer to a future bean)
- Reordering files within a stack (order is alphabetical)
- Stack file validation against a schema (convention files are free-form markdown)
- Bulk operations

## Acceptance Criteria

- [ ] Users can open and edit any stack markdown file via the Markdown Editor Widget
- [ ] "New Stack" creates a directory with a starter conventions.md
- [ ] "New File" within a stack creates a new markdown file with basic template content
- [ ] "Delete Stack" shows confirmation dialog before deleting the entire directory
- [ ] "Delete File" shows confirmation dialog before deleting an individual file
- [ ] Stack ID and filename validation prevents invalid names and duplicates
- [ ] Tree view refreshes after all create and delete operations
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover stack CRUD operations and validation
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-037 (screen shell & tree) and BEAN-038 (markdown editor widget).
- The 11 existing stacks show the common file patterns: conventions.md, testing.md, security.md, performance.md, packaging.md, etc. The starter template for a new file should follow the standardized format (Defaults table, Do/Don't, Common Pitfalls, Checklist, code examples).
- Stack files are simpler than personas (flat list of .md files, no required structure), so this bean should be smaller than BEAN-039.
