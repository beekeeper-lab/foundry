# UX / UI Designer -- Outputs

This document enumerates every artifact the UX / UI Designer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. User Flows

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | User Flows                                         |
| **Cadence**        | One per feature or user-facing workflow             |
| **Template**       | `personas/ux-ui-designer/templates/user-flows.md`  |
| **Format**         | Markdown with text-based diagrams                  |

**Description.** A step-by-step mapping of how a user moves through the system
to accomplish a goal. User flows identify every decision point, branch, and
terminal state -- covering the happy path, error recovery, empty states, and
alternative paths.

**Quality Bar:**
- Every flow has a named starting state and one or more named ending states.
- Decision points are explicit: "If the user has no saved items, show empty
  state. If the user has items, show the list."
- Error states are included for every action that can fail (form submission,
  API call, file upload) with the recovery path specified.
- Empty states and loading states are documented, not left as implicit.
- Flows are validated against the Business Analyst's user stories to confirm
  all acceptance criteria are reachable.
- Each step identifies what the user sees and what action they can take --
  not just a label like "Login page."

**Downstream Consumers:** Developer (for implementation sequencing), Tech QA
(for test scenario derivation), Business Analyst (for requirements validation).

---

## 2. Textual Wireframes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Textual Wireframes                                 |
| **Cadence**        | One per screen or significant UI component         |
| **Template**       | `personas/ux-ui-designer/templates/wireframes-text.md` |
| **Format**         | Markdown with ASCII layout descriptions            |

**Description.** Structured text descriptions of screen layouts that define the
information hierarchy, component placement, and content for each view. In a
text-based AI team, textual wireframes replace visual mockups as the primary
medium for communicating layout and structure to developers.

**Quality Bar:**
- Every user-facing screen referenced in the user flows has a corresponding
  wireframe.
- Content hierarchy is clear: the reader can identify what is most prominent,
  what is secondary, and what is tertiary.
- Interactive elements (buttons, links, form fields) are labeled with their
  exact text and described with their behavior on interaction.
- Placeholder content uses realistic data (names, dates, quantities) rather
  than "Lorem ipsum" or "Text here."
- Each wireframe cross-references the user flow step(s) it corresponds to.
- Annotations explain layout decisions that are not self-evident from the
  wireframe alone.

**Downstream Consumers:** Developer (for implementation), Tech QA (for visual
verification), Technical Writer (for content alignment).

---

## 3. Component Specification

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Component Specification                            |
| **Cadence**        | One per reusable UI component or complex widget    |
| **Template**       | `personas/ux-ui-designer/templates/component-spec.md` |
| **Format**         | Markdown                                           |

**Description.** A detailed behavioral specification for a UI component,
defining every state it can be in, every interaction it supports, and the
content it displays. Component specs are the contract between the designer
and the developer -- they eliminate ambiguity about how a component should
behave.

**Quality Bar:**
- All states are enumerated: default, hover, focus, active, disabled, error,
  loading, and empty. No state is left to developer interpretation.
- Each state includes: what the user sees, what interactions are available,
  and what transitions to the next state.
- Content specifications include exact label text, placeholder text, error
  messages, and tooltip text.
- Keyboard interaction is specified: Tab order, Enter/Space behavior, Escape
  behavior, and arrow key navigation where applicable.
- Accessibility attributes are specified: ARIA roles, labels, and
  live-region behavior.

**Downstream Consumers:** Developer (for implementation), Tech QA (for
state-by-state testing), Code Quality Reviewer (for implementation
verification against spec).

---

## 4. Content Style Guide

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Content Style Guide                                |
| **Cadence**        | One per project; updated as content patterns evolve |
| **Template**       | `personas/ux-ui-designer/templates/content-style-guide.md` |
| **Format**         | Markdown                                           |

**Description.** The authoritative reference for all user-facing text in the
product: labels, button text, error messages, confirmation dialogs, empty-state
messages, tooltips, and microcopy. The content style guide ensures that the
product speaks with one voice and that users encounter consistent language
patterns throughout.

**Quality Bar:**
- Terminology is canonicalized: for each concept, one term is designated and
  alternatives are listed as "do not use" (e.g., "Use 'Delete' not 'Remove'
  for permanent actions").
- Error message patterns are defined with a formula: what went wrong + what
  the user can do about it (e.g., "Unable to save changes. Check your
  connection and try again.").
- Tone guidelines are specific: "Use sentence case for buttons. Use active
  voice. Address the user as 'you.'"
- Examples are provided for every pattern: correct and incorrect usage
  side-by-side.
- The guide covers at minimum: button labels, form labels, error messages,
  success messages, empty states, loading states, and confirmation dialogs.

**Downstream Consumers:** Developer (for UI text implementation), Technical
Writer (for documentation consistency), Business Analyst (for requirements
language alignment), Researcher / Librarian (for terminology standardization).

---

## 5. Accessibility Checklist

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Accessibility Checklist                            |
| **Cadence**        | One per feature; updated as WCAG guidelines evolve |
| **Template**       | `personas/ux-ui-designer/templates/accessibility-checklist.md` |
| **Format**         | Markdown                                           |

**Description.** A feature-specific checklist of accessibility requirements
derived from WCAG guidelines and the project's accessibility targets. The
checklist translates abstract accessibility standards into concrete, testable
criteria that developers can implement and testers can verify.

**Quality Bar:**
- Each item is a specific, testable criterion: "All form inputs have an
  associated `<label>` element" not "Forms are accessible."
- Items are organized by WCAG principle: Perceivable, Operable,
  Understandable, Robust.
- Each item references the specific WCAG success criterion it addresses
  (e.g., "WCAG 2.1 SC 1.1.1 Non-text Content").
- Keyboard navigation requirements are specified: every interactive element is
  reachable via Tab, activatable via Enter/Space, and dismissable via Escape.
- Screen reader expectations are stated: what the screen reader should
  announce for each interactive element and state change.
- The checklist has pass/fail status for each item to track progress.

**Downstream Consumers:** Developer (for accessible implementation), Tech QA
(for accessibility testing), Compliance / Risk Analyst (for regulatory
compliance verification).

---

## 6. UX Acceptance Criteria

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | UX Acceptance Criteria                             |
| **Cadence**        | One set per user story or feature with UI impact   |
| **Template**       | `personas/ux-ui-designer/templates/ux-acceptance-criteria.md` |
| **Format**         | Markdown                                           |

**Description.** Testable conditions that define when a feature's user
experience meets the design specification. UX acceptance criteria bridge the
gap between the designer's intent and the tester's verification -- they specify
what "done" looks like from the user's perspective.

**Quality Bar:**
- Every criterion has a clear pass/fail condition: "When the user submits the
  form with an empty required field, an inline error message appears below the
  field within 200ms" not "Form validation works."
- Criteria cover: happy path, error paths, empty states, loading states, and
  edge cases (long text, special characters, rapid repeated actions).
- Responsive behavior criteria are included for each supported viewport size.
- Criteria reference the specific wireframe, component spec, or user flow they
  verify.
- Accessibility criteria from the accessibility checklist are included or
  cross-referenced, not treated as a separate concern.
- Criteria are written in a format that Tech QA can execute without needing
  to consult the designer.

**Downstream Consumers:** Tech QA (for test case derivation and execution),
Developer (for implementation verification), Business Analyst (for acceptance
sign-off).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository.
- User flows and wireframes are stored in `docs/ux/` with descriptive
  filenames (e.g., `user-flow-checkout.md`, `wireframe-dashboard.md`).
- Component specifications are stored in `docs/ux/components/` and named
  after the component (e.g., `component-spec-search-bar.md`).
- The content style guide lives in `docs/ux/content-style-guide.md` and is
  referenced by all documentation and implementation involving user-facing text.
- Accessibility checklists are stored alongside the feature they apply to
  or in `docs/ux/accessibility/`.
- UX acceptance criteria are attached to their corresponding user story in
  the issue tracker or stored in `docs/ux/acceptance/`.
- Text-based diagrams (ASCII, Mermaid) are used for all flow diagrams to
  keep them diffable and renderable in standard Markdown viewers.
