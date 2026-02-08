# BEAN-042: Library Manager — Claude Assets & Workflows Editor

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-042 |
| **Status** | New |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The library's `claude/` directory contains hook packs, skill definitions, and command files that configure Claude Code behavior in generated projects. The `workflows/` directory contains reference documents (pipeline description, task taxonomy) that get included in generated output. These are all markdown files that users may want to customize — for example, adding a new skill, tweaking a hook pack's rules, or updating the task taxonomy with project-specific task types. Currently, there's no in-app way to manage these files.

## Goal

Add editing capabilities for Claude integration assets (hooks, skills, commands) and workflow reference documents in the Library Manager screen. Users can edit existing files, create new ones, and delete files they no longer need. All editing uses the shared Markdown Editor Widget from BEAN-038.

## Scope

### In Scope
- Tree view integration: Claude assets shown under a "Claude" node with sub-nodes for Commands, Skills, and Hooks; Workflows shown under a "Workflows" node
- Clicking any file opens it in the Markdown Editor Widget for editing
- "New Command", "New Skill", "New Hook Pack", "New Workflow" actions: prompt for filename, create a `.md` file with appropriate starter content
- "Delete" action on any file: confirmation dialog, removes the file
- Starter templates:
  - Commands: basic command structure with description and usage
  - Skills: skill definition with trigger, inputs, process, outputs sections
  - Hook packs: hook definition with event triggers and actions
  - Workflows: basic reference document structure
- Tree refreshes after create/delete operations

### Out of Scope
- Hook pack testing or validation (verifying hooks actually work)
- Skill dependency resolution
- Command/skill import from external sources
- Visual hook flow editor (would be a separate feature entirely)

## Acceptance Criteria

- [ ] Claude assets (commands, skills, hooks) appear correctly nested under a "Claude" node in the tree
- [ ] Workflow documents appear under a "Workflows" node
- [ ] Users can open and edit any file via the Markdown Editor Widget
- [ ] "New" actions create files with appropriate starter content for each type
- [ ] "Delete" actions show confirmation dialog before removing files
- [ ] Filename validation prevents invalid names and duplicates
- [ ] Tree view refreshes after create and delete operations
- [ ] All existing tests pass (`uv run pytest`)
- [ ] New tests cover CRUD operations for each asset type
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

- Depends on BEAN-037 (screen shell & tree) and BEAN-038 (markdown editor widget).
- This is the lowest priority editor bean since hooks/skills/commands change less frequently than personas and stacks.
- The existing 16 commands, 16 skills, and 5 hook packs provide good reference for starter template content.
- Workflow files (foundry-pipeline.md, task-taxonomy.md) are meta-documentation — editing them is straightforward since they have no structural requirements.
