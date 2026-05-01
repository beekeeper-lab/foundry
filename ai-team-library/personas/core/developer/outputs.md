# Developer -- Outputs

This document enumerates every artifact the Developer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Implementation Code

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Feature/Fix Implementation                         |
| **Cadence**        | Continuous; one or more PRs per assigned task      |
| **Template**       | N/A (follows project conventions and stack conventions) |
| **Format**         | Source code in the project's language(s)            |

**Description.** Working code that implements the behavior defined in user
stories, design specifications, or bug reports. This is the Developer's primary
output and the team's primary product.

**Quality Bar:**
- Satisfies all acceptance criteria in the originating story or task.
- Follows the project's coding conventions (see stack `conventions.md`).
- No commented-out code. If code is not needed, delete it. Version control
  preserves history.
- No hardcoded configuration values. Use environment variables, config files,
  or constants with meaningful names.
- Functions and methods are short enough to understand without scrolling. If a
  function exceeds 40 lines, consider decomposition.
- Naming is intention-revealing: a reader can understand what a variable,
  function, or class does from its name alone.
- Error handling is explicit. Every external call has a failure path. No bare
  exception catches.
- Dependencies added are justified and minimal. Do not add a library for
  something that takes 10 lines to implement.

**Downstream Consumers:** Code Quality Reviewer (for review), Tech QA (for
testing), DevOps-Release (for deployment), future developers (for maintenance).

---

## 2. Unit Tests

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Unit Test Suite                                    |
| **Cadence**        | Accompanies every implementation PR                |
| **Template**       | N/A (follows project test conventions)             |
| **Format**         | Source code (test framework specific to the stack) |

**Description.** Automated tests that verify individual units of behavior in
isolation. Unit tests are the first line of defense against regressions and
the fastest feedback loop for correctness.

**Quality Bar:**
- Every public function or method with logic has at least one test.
- Tests cover the happy path, at least one error path, and boundary conditions.
- Tests are independent: no test depends on the execution order or side effects
  of another test.
- Test names describe the scenario and expected outcome:
  `test_calculate_total_applies_discount_when_quantity_exceeds_threshold`.
- Tests use meaningful assertions, not just "does not throw." Assert on the
  specific expected output.
- No test hits the network, filesystem, or database. Use mocks, stubs, or
  fakes for external dependencies.
- Tests run in under 5 seconds total for the affected module. Slow tests are
  marked appropriately for separate execution.
- Aim for 80% line coverage on new code. Measure branch coverage as the more
  meaningful metric.

**Downstream Consumers:** Code Quality Reviewer (for review), CI pipeline (for
automated verification), future developers (as living documentation).

---

## 3. Integration Tests

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Integration Test Suite                             |
| **Cadence**        | When implementation touches system boundaries      |
| **Template**       | N/A (follows project test conventions)             |
| **Format**         | Source code                                        |

**Description.** Automated tests that verify the correct interaction between
components or between the system and external dependencies (databases, APIs,
message queues). Integration tests complement unit tests by catching issues that
arise at boundaries.

**Quality Bar:**
- Every API endpoint has at least one integration test covering the success
  path and one covering an error path.
- Database interactions are tested against a real database instance (using
  containers or an in-memory equivalent), not mocked.
- Tests clean up after themselves: no test leaves state that affects other
  tests.
- Tests use realistic data, not trivial placeholders. Edge cases in data
  format, encoding, and size should be represented.
- Integration tests are tagged or separated so they can be run independently
  from unit tests (they are slower and require infrastructure).
- External service interactions use contract tests or recorded fixtures where
  live calls are impractical.

**Downstream Consumers:** Tech QA (for test coverage assessment), CI pipeline
(for automated verification), DevOps-Release (for deployment confidence).

---

## 4. Pull Request Description

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | PR Description                                     |
| **Cadence**        | One per pull request                               |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown (in the PR body)                          |

**Description.** The narrative accompanying a pull request. A good PR
description enables efficient review by explaining what changed, why it changed,
and how to verify it.

**Required Sections:**
1. **Summary** -- One to three sentences explaining the change and its purpose.
   Link to the originating task or story.
2. **What Changed** -- Bulleted list of the significant changes. Group by
   component or concern if the PR touches multiple areas.
3. **How to Test** -- Step-by-step instructions a reviewer can follow to verify
   the change works. Include any setup needed (environment variables, seed data,
   etc.).
4. **Notes for Reviewers** -- Optional. Flag anything unusual, areas where you
   want specific feedback, or known limitations of the current approach.

**Quality Bar:**
- Summary references the task ID or story title.
- A reviewer who reads only the PR description understands the scope and intent
  of the change.
- "How to Test" instructions are complete enough that a reviewer can execute
  them without asking questions.
- The PR description is updated if the implementation changes during review.

**Downstream Consumers:** Code Quality Reviewer (primary consumer), Team Lead
(for progress tracking), Tech QA (for testing context).

---

## 5. Technical Debt Notes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technical Debt Annotation                          |
| **Cadence**        | As encountered during implementation               |
| **Template**       | None (issue tracker format)                        |
| **Format**         | Issue/ticket                                       |

**Description.** When implementation reveals pre-existing code quality issues,
missing tests, or suboptimal patterns that are out of scope for the current
task, the Developer documents them as technical debt items for future
prioritization.

**Quality Bar:**
- Describes the problem specifically: file, function, and what is wrong.
- States the risk of leaving it unaddressed.
- Suggests a remediation approach with rough effort estimate.
- Does not mix debt documentation with the current PR. Debt is tracked
  separately, not embedded as TODO comments.

**Downstream Consumers:** Team Lead (for backlog prioritization), Architect
(for systemic pattern identification).

---

## Output Format Guidelines

- Code follows the stack-specific conventions document (`stacks/<stack>/conventions.md`).
- Tests follow the same conventions as production code: same linting, same
  formatting, same naming rules.
- PR descriptions are written as if the reviewer has no prior context about the
  change.
- All outputs are committed to the project repository. No deliverables live
  outside version control.
