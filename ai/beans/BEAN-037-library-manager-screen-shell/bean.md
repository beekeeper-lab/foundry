# BEAN-037: Library Manager — Screen Shell & Tree Browser

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-037 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

Foundry's library (`ai-team-library/`) contains personas, stacks, templates, workflows, hooks, skills, and commands — all stored as markdown files. Currently, users have no way to browse or manage this content from within the app. They must use an external text editor and know the directory structure. This makes the library opaque and hard to work with, especially for users who didn't create the original content.

## Goal

Add a new top-level "Library Manager" screen to Foundry's main window that provides a tree-based browser for exploring the entire library structure. Users can navigate the hierarchy (Personas, Stacks, Templates, Workflows, Claude Assets) and click any file to view its contents in a read-only preview pane. This screen becomes the foundation for all subsequent editing beans.

## Scope

### In Scope
- New "Library Manager" entry in the main window sidebar navigation
- Tree view widget (QTreeWidget) that scans the configured library path
- Top-level categories in the tree: Personas, Stacks, Shared Templates, Workflows, Claude Commands, Claude Skills, Claude Hooks
- Expanding a category shows its children (directories and files)
- Expanding a directory shows its files recursively
- Clicking a file shows its content in a read-only text pane
- Auto-refresh when the screen is shown (via showEvent)
- Graceful handling when library path is not configured or doesn't exist
- Integration with Catppuccin Mocha theme styling

### Out of Scope
- Editing, creating, or deleting any content (handled by BEAN-038 through BEAN-042)
- Rich markdown rendering (deferred to BEAN-038)
- Drag-and-drop reordering
- Search/filter within the tree (can be added later)

## Acceptance Criteria

- [x] "Library Manager" appears as a screen option in the main window sidebar
- [x] Tree view displays the full library hierarchy with correct nesting
- [x] Clicking a `.md` file in the tree shows its content in the preview pane
- [x] Tree auto-refreshes when the screen is navigated to
- [x] Empty/missing library path shows a helpful message pointing to Settings
- [x] Screen follows existing Catppuccin Mocha theme styling
- [x] All existing tests pass (`uv run pytest`)
- [x] New tests cover tree building logic and screen instantiation
- [x] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create library_manager.py with tree browser + preview pane | developer | — | Done |
| 2 | Add Library entry to main window SCREENS | developer | 1 | Done |
| 3 | Write tests for tree building logic and screen | tech-qa | 1 | Done |
| 4 | Run tests and lint | tech-qa | 1,2,3 | Done |

## Notes

- This is the first bean in the Library Manager feature set. BEAN-038 through BEAN-042 all depend on this screen shell existing.
- The tree scanning logic is directory-driven — it discovers new content types automatically.
- Pure `_build_file_tree()` function is separated from UI for testability.
- Hidden files (starting with `.`) are skipped in the tree.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 11m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 11m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 676s).
