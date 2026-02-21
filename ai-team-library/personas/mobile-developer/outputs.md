# Mobile Developer -- Outputs

This document enumerates every artifact the Mobile Developer is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Mobile Application Code

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Feature/Fix Implementation (iOS, Android, or Cross-Platform) |
| **Cadence**        | Continuous; one or more PRs per assigned task      |
| **Template**       | N/A (follows project conventions and stack conventions) |
| **Format**         | Source code (Swift, Kotlin, TypeScript/React Native, Dart/Flutter) |

**Description.** Working mobile application code that implements the behavior
defined in user stories, design specifications, or bug reports. Code must
function correctly on both target platforms and handle mobile-specific concerns:
offline scenarios, device permissions, lifecycle events, and platform UI conventions.

**Quality Bar:**
- Satisfies all acceptance criteria in the originating story or task.
- Follows the project's coding conventions (see stack `conventions.md`).
- No commented-out code. If code is not needed, delete it.
- No hardcoded configuration values. Use environment-appropriate config mechanisms.
- Functions and methods are short enough to understand without scrolling.
- Naming is intention-revealing.
- Error handling is explicit. Every network call has a failure path. No bare
  exception catches.
- Offline behavior is graceful -- the app does not crash or lose data without
  connectivity.
- Device permissions are requested at the point of use, not at launch.
- Memory usage is appropriate for the target device tier.
- Dependencies added are justified, minimal, and evaluated for binary size impact.

**Downstream Consumers:** Code Quality Reviewer (for review), Tech QA (for
testing), DevOps-Release (for app store builds), future developers (for maintenance).

---

## 2. Unit Tests

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Unit Test Suite                                    |
| **Cadence**        | Accompanies every implementation PR                |
| **Template**       | N/A (follows project test conventions)             |
| **Format**         | Source code (XCTest, JUnit/Espresso, Jest, Flutter Test) |

**Description.** Automated tests that verify individual units of behavior in
isolation. Unit tests cover business logic, data transformations, state management,
and utility functions independent of UI or platform services.

**Quality Bar:**
- Every public function or method with logic has at least one test.
- Tests cover the happy path, at least one error path, and boundary conditions.
- Tests are independent: no test depends on execution order or side effects.
- Test names describe the scenario and expected outcome.
- Tests use meaningful assertions, not just "does not throw."
- No tests hit the network, filesystem, or database -- mock external dependencies.
- Tests run in under 5 seconds for the affected module.
- Aim for 80% line coverage on new code.

**Downstream Consumers:** Code Quality Reviewer (for review), CI pipeline (for
automated verification), future developers (as living documentation).

---

## 3. Widget / UI Tests

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Widget and UI Component Test Suite                 |
| **Cadence**        | Accompanies PRs that modify UI components          |
| **Template**       | N/A (follows project test conventions)             |
| **Format**         | Source code (XCTest UI, Espresso, React Native Testing Library, Flutter Widget Test) |

**Description.** Automated tests that verify UI component rendering and
interaction behavior. Widget tests validate that components display correct
state, respond to user input, and handle edge cases in presentation (empty
states, loading states, error states).

**Quality Bar:**
- Every new UI component has at least one widget test covering its primary state.
- Tests cover key interaction paths (tap, swipe, input).
- Empty, loading, and error states are tested.
- Tests do not depend on network calls or backend state.
- Snapshot tests are updated when intentional visual changes are made.

**Downstream Consumers:** Code Quality Reviewer (for review), Tech QA (for
visual regression checks), CI pipeline (for automated verification).

---

## 4. Integration Tests

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Integration Test Suite                             |
| **Cadence**        | When implementation touches system boundaries      |
| **Template**       | N/A (follows project test conventions)             |
| **Format**         | Source code                                        |

**Description.** Automated tests that verify correct interaction between the
mobile app and external systems: backend APIs, local databases, platform
services (camera, location, notifications), and third-party SDKs.

**Quality Bar:**
- Every API integration point has at least one success path and one error path test.
- Local database interactions are tested against real storage (not mocked).
- Tests clean up after themselves.
- Offline-to-online sync flows are tested.
- Tests use realistic data, including edge cases in format and encoding.
- Integration tests are tagged for separate execution from unit tests.

**Downstream Consumers:** Tech QA (for test coverage assessment), CI pipeline
(for automated verification), DevOps-Release (for deployment confidence).

---

## 5. App Store Build Artifacts

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Release Build (IPA, AAB/APK)                       |
| **Cadence**        | Per release cycle                                  |
| **Template**       | N/A (follows platform build conventions)           |
| **Format**         | Platform-specific binary                           |

**Description.** Signed, release-ready build artifacts for submission to the
Apple App Store and Google Play Store. Includes proper versioning, release
notes input, and compliance with current store guidelines.

**Quality Bar:**
- Build is signed with the correct release certificates.
- Version number and build number are incremented correctly.
- No debug flags, test endpoints, or development configurations remain.
- ProGuard/R8 (Android) or bitcode (iOS) settings are correct for release.
- Binary size is within acceptable limits for the target audience.
- All required app store metadata and screenshots are current.

**Downstream Consumers:** DevOps-Release (for store submission), Team Lead (for
release approval), Tech QA (for final verification).

---

## 6. Pull Request Description

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
   platform or concern if the PR touches multiple areas.
3. **How to Test** -- Step-by-step instructions including target device/simulator,
   OS version, and any setup needed.
4. **Platform Notes** -- Document any platform-specific behavior differences.
5. **Notes for Reviewers** -- Optional. Flag anything unusual, areas where you
   want specific feedback, or known limitations.

**Quality Bar:**
- Summary references the task ID or story title.
- A reviewer who reads only the PR description understands the scope and intent.
- "How to Test" instructions specify devices and OS versions.
- Platform-specific behavior differences are documented.

**Downstream Consumers:** Code Quality Reviewer (primary consumer), Team Lead
(for progress tracking), Tech QA (for testing context).

---

## 7. Device Testing Results

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Device Testing Report                              |
| **Cadence**        | Per feature or release milestone                   |
| **Template**       | `templates/device-testing-matrix.md`               |
| **Format**         | Markdown                                           |

**Description.** Results from testing across the supported device matrix.
Documents which devices and OS versions were tested, what passed, and any
device-specific issues discovered.

**Quality Bar:**
- At least one high-end and one low-end device per platform tested.
- OS version coverage includes the minimum supported version and the latest.
- Performance observations noted (startup time, memory, battery impact).
- Device-specific issues are documented with reproduction steps.

**Downstream Consumers:** Tech QA (for test coverage assessment), Team Lead
(for release confidence), DevOps-Release (for store submission).

---

## 8. Technical Debt Notes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Technical Debt Annotation                          |
| **Cadence**        | As encountered during implementation               |
| **Template**       | None (issue tracker format)                        |
| **Format**         | Issue/ticket                                       |

**Description.** When implementation reveals pre-existing code quality issues,
missing tests, platform deprecations, or suboptimal patterns that are out of
scope for the current task, the Mobile Developer documents them as technical
debt items for future prioritization.

**Quality Bar:**
- Describes the problem specifically: file, function, and what is wrong.
- States the risk of leaving it unaddressed (including platform deprecation timelines).
- Suggests a remediation approach with rough effort estimate.
- Does not mix debt documentation with the current PR.

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
- Platform-specific code is clearly separated from shared code.
- Device testing results reference specific device models and OS versions.
