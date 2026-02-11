# BEAN-038: Library Manager — Markdown Editor Widget

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-038 |
| **Status** | New |
| **Priority** | High |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The Library Manager screen (BEAN-037) provides read-only browsing of library files. To enable editing, we need a reusable markdown editor component that all subsequent editor beans (BEAN-039 through BEAN-042) can share. Building this as a standalone widget ensures consistent editing UX across all content types and avoids duplicating editor logic in each bean.

## Goal

Create a reusable split-pane markdown editor widget: plain text editing on the left with a live-rendered markdown preview on the right. The widget handles file I/O, dirty state tracking, and save/revert operations. Once built, it replaces the read-only preview pane in the Library Manager screen.

## Scope

### In Scope
- Split-pane widget: QPlainTextEdit (monospace, left) + QTextBrowser (rendered HTML, right)
- Live markdown preview that updates as the user types (with a short debounce to avoid lag)
- Markdown-to-HTML rendering using the `markdown` Python package (or similar lightweight library)
- Save button that writes content back to the original file path
- Revert button that reloads the file from disk, discarding unsaved changes
- Dirty state tracking: visual indicator (e.g., asterisk in tab/title) when content has been modified
- Unsaved changes warning if the user navigates away while dirty
- Syntax highlighting for markdown (basic: headers, bold, italic, code blocks, lists) — nice to have but not required
- Integration into the Library Manager screen as the file viewer/editor pane
- Resizable splitter between editor and preview panes

### Out of Scope
- WYSIWYG editing (this is a plain-text-with-preview editor, not a rich text editor)
- Image embedding or media preview
- Git integration (tracking changes, diffing)
- Collaborative editing
- Template variable resolution in the preview ({{ placeholders }} show as-is)

## Acceptance Criteria

- [ ] Split-pane editor displays with text editor on the left and rendered preview on the right
- [ ] Editing text in the left pane updates the preview in the right pane in near-real-time
- [ ] Save button writes the file to disk
- [ ] Revert button reloads the file from disk and discards unsaved changes
- [ ] Dirty indicator shows when content has been modified since last save/load
- [ ] Navigating away from a dirty file prompts the user (or auto-saves — decide during implementation)
- [ ] The widget is a reusable QWidget subclass that can be instantiated by any screen
- [ ] `markdown` package (or equivalent) added to project dependencies if not already present
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover widget instantiation, dirty tracking, and save/revert logic
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-037 (screen shell must exist for integration).
- The `markdown` Python package is lightweight and well-maintained. Alternatives: `mistune` (faster), `markdown-it-py` (CommonMark compliant). Choose based on what's simplest to integrate.
- Preview rendering should use CSS that matches the Catppuccin Mocha theme for visual consistency.
- Consider a toggle to hide the preview pane for users who prefer full-width editing.

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (commit→merge, 98s).
