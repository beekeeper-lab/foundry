# Tech QA -- Outputs

This document enumerates every artifact the Tech QA Engineer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Test Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Test Plan                                          |
| **Cadence**        | One per feature or epic; updated as scope evolves  |
| **Template**       | `personas/tech-qa/templates/test-plan.md`          |
| **Format**         | Markdown                                           |

**Description.** A structured document that defines the test strategy for a
feature or epic. The test plan identifies what will be tested, how it will be
tested, what the entry and exit criteria are, and what risks exist in the
testing approach.

**Required Sections:**
1. **Scope** -- What features, components, or behaviors are covered by this
   plan. Equally important: what is explicitly out of scope.
2. **Test Strategy** -- The types of testing to be performed (unit, integration,
   end-to-end, performance, security) and the rationale for each.
3. **Entry Criteria** -- Conditions that must be met before testing begins
   (e.g., feature is code-complete, environment is provisioned, test data is
   available).
4. **Exit Criteria** -- Conditions that define when testing is complete (e.g.,
   all critical test cases pass, no open Critical/Major defects, coverage
   target met).
5. **Test Environment** -- Required infrastructure, configuration, test data,
   and any external service dependencies.
6. **Risks and Mitigations** -- Testing risks (e.g., unstable environment,
   missing test data, third-party dependency) with mitigation strategies.

**Quality Bar:**
- Scope is traceable to specific user stories or acceptance criteria.
- Strategy choices are justified, not just listed. "We use integration tests
  for the payment flow because it involves three external services" is useful.
  "We will do integration testing" is not.
- Exit criteria are measurable. "All tests pass" is measurable. "Quality is
  acceptable" is not.
- The plan is reviewed by the Developer and Team Lead before testing begins.

**Downstream Consumers:** Team Lead (for planning), Developer (for test
infrastructure support), DevOps-Release (for environment provisioning).

---

## 2. Test Cases

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Test Case Suite                                    |
| **Cadence**        | Continuous; cases are written as acceptance criteria are finalized |
| **Template**       | `personas/tech-qa/templates/test-case.md`          |
| **Format**         | Markdown or test framework code                    |

**Description.** Individual test cases that verify specific behaviors of the
system. Each test case is a single, atomic verification of one expected behavior
under defined conditions.

**Quality Bar:**
- Each test case has: a unique identifier, a descriptive title, preconditions,
  test steps, expected result, and actual result (when executed).
- Test cases trace back to specific acceptance criteria. Every acceptance
  criterion has at least one test case. Complex criteria have multiple cases
  covering variations.
- Negative test cases are present for every positive case: what happens when
  the input is invalid, the service is unavailable, the user lacks permission?
- Boundary conditions are tested explicitly: zero, one, maximum, just above
  maximum, empty string, null, Unicode, special characters.
- Test cases are independent. No test case depends on the output or side
  effects of another test case.
- Automated test cases follow the Arrange-Act-Assert pattern and have
  intention-revealing names.

**Downstream Consumers:** Developer (for bug reproduction), Code Quality
Reviewer (for acceptance verification), future QA (for regression).

---

## 3. Bug Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Defect Report                                      |
| **Cadence**        | As defects are discovered                          |
| **Template**       | `personas/tech-qa/templates/bug-report.md`         |
| **Format**         | Markdown or issue tracker format                   |

**Description.** A structured report of a defect discovered during testing.
The bug report provides enough information for a developer to reproduce, diagnose,
and fix the issue without a conversation.

**Quality Bar:**
- **Title** is a concise description of the symptom: "Checkout returns 500 when
  quantity is 0" not "Bug in checkout."
- **Steps to Reproduce** are numbered, specific, and start from a known state.
  A developer following these steps will see the defect on the first attempt.
- **Expected Result** states what should happen, with reference to the
  acceptance criterion or specification that defines the correct behavior.
- **Actual Result** states what actually happened, including error messages,
  status codes, or screenshots.
- **Environment** specifies: OS, browser (if applicable), API version,
  database state, test data used.
- **Severity** is assessed:
  - Critical: system crash, data loss, security vulnerability, complete feature
    failure.
  - Major: feature partially broken, workaround exists but is unacceptable.
  - Minor: cosmetic issue, minor UX problem, non-critical edge case.
  - Trivial: typo, alignment, negligible impact.
- **Priority** is suggested (the Team Lead makes the final call).
- Attachments (logs, screenshots, network traces) are included when they aid
  diagnosis.

**Downstream Consumers:** Developer (for resolution), Team Lead (for
prioritization), BA (for requirement clarification if the expected behavior
is ambiguous).

---

## 4. Quality Metrics Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Quality Metrics Report                             |
| **Cadence**        | End of every sprint/cycle                          |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A summary of quality indicators for the cycle, providing the
team and stakeholders with an objective view of the system's current quality
posture.

**Required Sections:**
1. **Test Execution Summary** -- Total tests, passed, failed, blocked, skipped.
   Broken down by test type (unit, integration, e2e).
2. **Coverage Report** -- Line coverage and branch coverage for new and modified
   code. Trend compared to the previous cycle.
3. **Defect Summary** -- New defects found, defects resolved, defects still
   open. Breakdown by severity.
4. **Defect Trends** -- Are defects increasing or decreasing cycle over cycle?
   Are they being found earlier or later in the pipeline?
5. **Risk Assessment** -- Areas of the codebase with low coverage, high defect
   density, or insufficient testing. Recommended actions.

**Quality Bar:**
- Numbers are accurate and sourced from CI/CD pipeline data, not estimates.
- Trends include at least two data points (current and previous cycle).
- Risk assessment includes specific recommendations, not just observations.
- The report is reviewed in the cycle retrospective.

**Downstream Consumers:** Team Lead (for process decisions), Architect (for
systemic quality patterns), Stakeholders (for release confidence).

---

## Output Format Guidelines

- Test plans and test cases are committed to the project repository alongside
  the code they test.
- Automated test cases follow the project's stack conventions for test
  organization and naming.
- Bug reports are filed in the project's issue tracker with consistent labels
  for severity and component.
- Quality metrics are sourced from automated tooling wherever possible. Manual
  data collection introduces error and lag.
- All test artifacts use the templates referenced above when they exist.
  Templates ensure consistency and prevent omission of required information.
