# BEAN-252 — BA Charter Content Spec

| Field | Value |
|-------|-------|
| **Bean** | BEAN-252 |
| **Date** | 2026-04-17 |

See `ai/beans/BEAN-252-project-purpose-charter/tasks/02-ba-charter-content.md` for the full per-section content specification.

## Handoff to Developer

The spec in task 02 is the source of truth for `_render_project_charter(spec)`. Copy the heading text, block-quoted prompts, and TODO placeholders verbatim. The Tech-QA tests will assert on:

- Presence of all five H2 headings (`Purpose`, `Audience`, `Success Criteria`, `Non-Goals`, `Constraints`).
- The greppable `Status: TODO` token in the header.
- Description echo (italicized line under H1) for both `description=None` and `description="..."`.
- Overlay safety: re-running scaffold over an existing charter does not modify it.
