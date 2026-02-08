# BEAN-037: Library Manager — Screen Shell & Tree Browser

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-037 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

Foundry's library (`ai-team-library/`) contains personas, stacks, templates, workflows, hooks, skills, and commands — all stored as markdown files. Currently, users have no way to browse or manage this content from within the app. They must use an external text editor and know the directory structure. This makes the library opaque and hard to work with, especially for users who didn't create the original content.

## Goal

Add a new top-level "Library Manager" screen to Foundry's main window that provides a tree-based browser for exploring the entire library structure. Users can navigate the hierarchy (Personas, Stacks, Templates, Workflows, Claude Assets) and click any file to view its contents in a read-only preview pane. This screen becomes the foundation for all subsequent editing beans.

## Scope

### In Scope
- New "Library Manager" entry in the main window sidebar navigation
- Tree view widget (QTreeView or QTreeWidget) that scans the configured library path
- Top-level categories in the tree: Personas, Stacks, Shared Templates, Workflows, Claude (with sub-nodes for Commands, Skills, Hooks)
- Expanding a category shows its children (e.g., Personas > team-lead, developer, ...)
- Expanding a persona shows its files (persona.md, outputs.md, prompts.md, templates/)
- Clicking a markdown file shows its content in a read-only text pane (plain text is fine for now — the Markdown Editor Widget in BEAN-038 will replace this)
- Refresh button or auto-refresh when the screen is shown
- Graceful handling when library path is not configured or doesn't exist
- Integration with the existing library indexer service where applicable

### Out of Scope
- Editing, creating, or deleting any content (handled by BEAN-038 through BEAN-042)
- Rich markdown rendering (deferred to BEAN-038)
- Drag-and-drop reordering
- Search/filter within the tree (can be added later)

## Acceptance Criteria

- [ ] "Library Manager" appears as a screen option in the main window sidebar
- [ ] Tree view displays the full library hierarchy with correct nesting
- [ ] Clicking a `.md` file in the tree shows its content in the preview pane
- [ ] Tree auto-refreshes when the screen is navigated to
- [ ] Empty/missing library path shows a helpful message pointing to Settings
- [ ] Screen follows existing Catppuccin Mocha theme styling
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover tree building logic and screen instantiation
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- This is the first bean in the Library Manager feature set. BEAN-038 through BEAN-042 all depend on this screen shell existing.
- The tree scanning logic should be flexible enough to discover new content types without code changes (directory-driven discovery).
- Consider reusing `build_library_index()` from `library_indexer.py` for the top-level structure, but the tree needs to go deeper (individual files within each item).
