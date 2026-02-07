# Business Analyst -- Outputs

This document enumerates every artifact the Business Analyst is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. User Story

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | User Story                                         |
| **Cadence**        | Continuous; stories are produced during backlog refinement |
| **Template**       | `personas/ba/templates/user-story.md`              |
| **Format**         | Markdown                                           |

**Description.** A concise specification of a single unit of user-visible
functionality. Each story captures who needs it, what they need, and why it
matters. Stories are the primary input to the development pipeline.

**Quality Bar:**
- Title is a short imperative phrase describing the outcome, not the
  implementation (e.g., "Allow users to reset password via email" not "Add
  password reset endpoint").
- Narrative follows the "As a [role], I want [capability], so that [benefit]"
  structure. All three clauses are present and specific.
- At least two acceptance criteria, written in Given/When/Then format.
- Error and edge case scenarios are covered as separate acceptance criteria,
  not left implicit.
- Story is sized to be completable in a single development cycle.
- Dependencies on other stories, APIs, or data sources are listed explicitly.
- Assumptions are called out in a dedicated section with validation status.

**Downstream Consumers:** Team Lead (for task planning), Developer (for
implementation), Tech QA (for test case derivation), Architect (for design
impact assessment).

---

## 2. Acceptance Criteria Document

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Acceptance Criteria                                |
| **Cadence**        | Attached to every user story; also standalone for complex features |
| **Template**       | `personas/ba/templates/acceptance-criteria.md`     |
| **Format**         | Markdown                                           |

**Description.** A detailed enumeration of the conditions that must be true for
a story or feature to be considered complete. When a feature spans multiple
stories, a standalone acceptance criteria document consolidates the
cross-cutting conditions.

**Quality Bar:**
- Every criterion is independently testable: a reviewer can determine pass/fail
  without subjective judgment.
- Criteria use concrete values, not vague qualifiers. "User sees an error
  message within 2 seconds" not "User is notified promptly."
- Negative cases are explicit: "Given an invalid email, the system displays
  'Invalid email format' and does not submit the form."
- Criteria are ordered by priority: must-have criteria first, then nice-to-have
  (clearly labeled).
- No implementation details. Criteria describe observable behavior, not internal
  mechanisms.

**Downstream Consumers:** Developer (for implementation guidance), Tech QA (for
test case creation), Code Quality Reviewer (for acceptance verification).

---

## 3. Bug Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Bug Report                                         |
| **Cadence**        | As discovered during requirements validation or UAT |
| **Template**       | `personas/ba/templates/bug-report.md`              |
| **Format**         | Markdown                                           |

**Description.** A structured report of a defect discovered during requirements
validation, user acceptance testing, or stakeholder review. Bug reports from the
BA focus on behavior that violates stated requirements or stakeholder
expectations.

**Quality Bar:**
- Includes reproducible steps: numbered, specific, starting from a known state.
- States expected behavior (with reference to the requirement or acceptance
  criterion it violates) and actual behavior.
- Specifies the environment: browser/OS/device if applicable, data conditions,
  user role.
- Severity is assessed: Critical (blocks core workflow), Major (degrades key
  functionality), Minor (cosmetic or low-impact), Trivial (nitpick).
- Includes screenshots or output logs when the defect is visual or produces
  error output.
- Does not prescribe a fix. Describe the problem; let the developer determine
  the solution.

**Downstream Consumers:** Team Lead (for prioritization), Developer (for
resolution), Tech QA (for regression test creation).

---

## 4. Requirements Summary

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Requirements Summary Document                      |
| **Cadence**        | Once per feature or epic; updated as scope evolves |
| **Template**       | None (freeform, but follows structure below)       |
| **Format**         | Markdown                                           |

**Description.** A higher-level document that aggregates the requirements for
a feature or epic. It provides context that individual stories lack: the
business objective, user personas involved, workflow overview, and the
relationship between stories.

**Required Sections:**
1. **Business Objective** -- One paragraph stating the problem being solved and
   the measurable outcome expected.
2. **User Personas** -- Who are the users? What are their goals and
   constraints?
3. **Workflow Overview** -- A step-by-step description of the end-to-end user
   workflow. Use numbered steps, not flowcharts (keep it text-based).
4. **Story Map** -- List of user stories that compose this feature, in
   suggested implementation order, with dependencies noted.
5. **Out of Scope** -- Explicitly state what this feature does not include.
   This prevents scope creep more effectively than any other section.
6. **Open Questions** -- Unresolved items that need stakeholder input, with
   owners and target resolution dates.
7. **Assumptions and Constraints** -- Technical constraints, business rules,
   regulatory requirements, or integration limitations.

**Quality Bar:**
- The business objective includes a success metric, not just a description.
- Every story in the story map traces back to a step in the workflow overview.
- Out of scope section is present and non-empty. If nothing is out of scope,
  the scope is not well-defined.
- Open questions have owners. Unowned questions do not get answered.

**Downstream Consumers:** Team Lead (for sprint planning), Architect (for
system design), Developer (for implementation context), Stakeholders (for
validation and sign-off).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository under the designated docs or requirements directory.
- Use templates when they exist. Templates enforce consistency and prevent
  omission of required sections.
- Cross-reference related artifacts by file path. A user story should link to
  its parent requirements summary. Acceptance criteria should reference the
  story they belong to.
- Version requirements documents. When scope changes, update the document and
  note what changed and why in a changelog section at the bottom.
