# Task 02 — BA: Charter Section Content Guidance

| Field | Value |
|-------|-------|
| **Owner** | BA |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 18:17 |
| **Completed** | 2026-04-17 18:17 |
| **Duration** | < 1m |

## Goal

Define the prose guidance for each of the five charter sections so a persona reading the file knows what kind of content belongs where. The guidance lives inside the scaffolded file as block-quoted prompts under each heading — visible to the human filling in the charter, deletable once the section is complete.

## Inputs

- `ai/beans/BEAN-252-project-purpose-charter/tasks/01-architect-decision-and-template.md` (skeleton)
- `ai/beans/BEAN-252-project-purpose-charter/bean.md` (acceptance criteria)

## Section Content Specification

Each section has: a heading, a one-line block-quoted prompt explaining what to write, and a TODO placeholder. The block quote stays in the file until the user replaces or removes it.

### 1. Purpose

> What does this project do, in one paragraph? Lead with the *outcome* (what changes for the user/business when this exists), not the implementation. A reader should understand the project's reason for existing in 30 seconds.

`TODO: Replace this paragraph with a one-paragraph statement of purpose.`

### 2. Audience

> Who is this for? Name the primary user (role, context, what they're trying to accomplish) and any secondary stakeholders. If multiple audiences, distinguish them — different audiences usually imply different success criteria.

`TODO: Describe the primary audience and any secondary stakeholders.`

### 3. Success Criteria

> What does "done" look like? List 3–5 outcome-shaped criteria the team can point at to say "yes, we shipped what we set out to ship." Avoid implementation criteria (e.g., "uses Postgres") — describe the change in the world, not the components used.

- [ ] `TODO: Outcome criterion 1`
- [ ] `TODO: Outcome criterion 2`
- [ ] `TODO: Outcome criterion 3`

### 4. Non-Goals

> What is this project explicitly *not* doing? Non-goals are as important as goals — they prevent scope creep and tell the team where to push back. Include things that a reasonable reader might assume are in scope but are not.

- `TODO: Non-goal 1`
- `TODO: Non-goal 2`

### 5. Constraints

> What boundaries does the project operate within? Include technical constraints (must run on X, must integrate with Y), organizational constraints (deadline, budget, team size), and regulatory/compliance constraints. If the project has no hard constraints, note that explicitly.

- `TODO: Constraint 1`
- `TODO: Constraint 2`

## Header Block

A two-line block at the top of the file makes the unfilled state visible and tells personas how to use the file:

```markdown
> **Status:** TODO — fill in this charter before the team begins substantive work.
> Personas should read this file first when opening the project.
```

The `Status: TODO` token is greppable so the Team Lead can detect unfilled charters with a one-liner.

## Description Echo

If `spec.project.description` is non-empty, surface it under the H1 as a single italicized line:

```markdown
*<description>*
```

If empty, surface a TODO line:

```markdown
*TODO: Add a one-line project description in the composition spec.*
```

This ensures the existing description (when present) is not duplicated work, and the absence (when missing) is explicit.

## Definition of Done

- [x] All five sections have block-quoted guidance prompts
- [x] Each section has a clearly marked TODO placeholder
- [x] Header status admonition specified (greppable token)
- [x] Description echo behavior specified for both present and absent cases
- [x] Handoff to developer: spec is concrete enough to implement directly without further design questions
