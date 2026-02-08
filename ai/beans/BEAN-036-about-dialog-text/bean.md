# BEAN-036: Update About Dialog Text

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-036 |
| **Status** | New |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The About dialog currently shows only a version number and a single-line tagline ("Generate Claude Code project folders from reusable building blocks"). This gives developers no real understanding of what Foundry does, how it works, or why they would use it. A richer summary would help users and contributors understand the application's purpose at a glance.

## Goal

Replace the minimal About text with 2-3 developer-focused paragraphs that explain Foundry's purpose, its library-based approach (personas, technology stacks, templates), and the value it provides to teams using Claude Code.

## Scope

### In Scope
- Update the HTML text in the `_show_about()` method in `foundry_app/ui/main_window.py`
- Write 2-3 paragraphs with a developer-focused tone
- Mention key library concepts: personas, technology stacks, templates
- Keep the version number display
- Keep using `QMessageBox.about()` (no dialog upgrade)

### Out of Scope
- Creating a custom QDialog or dedicated About screen
- Adding links to documentation or external resources
- Changing the Help menu structure

## Acceptance Criteria

- [ ] About dialog displays 2-3 substantive paragraphs (not just a tagline)
- [ ] Text mentions personas, technology stacks, and templates
- [ ] Tone is developer-focused and technical
- [ ] Version number (`__version__`) is still prominently displayed
- [ ] Dialog still uses `QMessageBox.about()` — no new widgets or files
- [ ] No new dependencies introduced
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Draft About text (2-3 paragraphs) | developer | | Pending |
| 2 | Update `_show_about()` in main_window.py | developer | 1 | Pending |
| 3 | Verify dialog renders correctly | tech-qa | 2 | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Current implementation is at `foundry_app/ui/main_window.py` lines ~252-262
- `QMessageBox.about()` supports basic HTML formatting (`<h3>`, `<p>`, etc.)
- The text should convey the "building blocks" philosophy: compose a Claude Code project from a library of reusable personas, stacks, and templates rather than starting from scratch each time
- **Dependency:** BEAN-043 (Add Application Logo) should be done first so the About dialog can include the logo
