# Task 01: Source Directory Requirements

| Field | Value |
|-------|-------|
| **Owner** | ba |
| **Status** | Done |
| **Depends On** | — |

## Goal

Refine the acceptance criteria for configurable source directories. Define the exact user stories, edge cases, and scope boundaries so the Architect and Developer have unambiguous requirements.

## Inputs

- `ai/beans/BEAN-004-safety-source-dirs/bean.md` — problem statement and initial AC
- `foundry_app/services/safety.py` — current hardcoded rules (lines 56-59)
- `foundry_app/core/models.py` — current FileSystemPolicy model (lines 72-74)
- `foundry_app/ui/screens/builder/wizard_pages/safety_page.py` — current Safety page

## Acceptance Criteria

- [ ] User stories written in Given/When/Then format covering: single custom dir, multiple dirs, default fallback, wizard UI interaction
- [ ] Edge cases documented (empty list, overlapping patterns, invalid patterns)
- [ ] Scope boundary clarified: what's configurable vs what stays hardcoded
- [ ] Output written to `ai/outputs/ba/bean-004-source-dirs-requirements.md`

## Definition of Done

Requirements doc exists with user stories, edge cases, and scope boundary. Downstream personas (Architect, Developer) can implement without asking clarifying questions.
