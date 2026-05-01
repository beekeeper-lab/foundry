# Integrator / Merge Captain -- Outputs

This document enumerates every artifact the Integrator / Merge Captain is
responsible for producing, including quality standards and who consumes each
deliverable.

---

## 1. Integration Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Integration Plan                                   |
| **Cadence**        | One per integration cycle or major merge campaign  |
| **Template**       | `personas/integrator-merge-captain/templates/integration-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A sequenced plan for merging multiple branches or changesets
into the integration branch. The integration plan identifies what will be
merged, in what order, what dependencies exist between branches, and what risks
each merge carries.

**Quality Bar:**
- Every branch scheduled for integration is listed with its source persona,
  purpose, and readiness status.
- Merge sequence is explicitly ordered and justified (foundational changes
  before dependent ones, low-risk before high-risk).
- Dependencies between branches are identified: "feature/export depends on
  feature/data-service and must merge after it."
- Risk assessment per merge includes: estimated conflict areas, complexity
  (Low/Medium/High), and rollback difficulty.
- The plan includes a validation step after each merge (build, test) before
  proceeding to the next.

**Downstream Consumers:** Team Lead (for scheduling and priorities), Developer
(for branch freeze coordination), DevOps-Release (for CI pipeline alignment),
Tech QA (for integration test scheduling).

---

## 2. Merge Checklist

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Merge Checklist                                    |
| **Cadence**        | One per merge operation                            |
| **Template**       | `personas/integrator-merge-captain/templates/merge-checklist.md` |
| **Format**         | Markdown                                           |

**Description.** A step-by-step checklist executed during each merge operation
to ensure nothing is missed. The checklist covers pre-merge verification,
conflict resolution, post-merge validation, and stakeholder notification. It
serves as both a process guide and an audit trail.

**Quality Bar:**
- Pre-merge checks include: source branch is up to date, CI is passing,
  contributing developer has confirmed readiness.
- Each conflict resolution is documented inline with the file path, the nature
  of the conflict, and the resolution decision.
- Post-merge validation confirms: build passes, all existing tests pass, no
  new warnings introduced.
- Every checkbox has a binary pass/fail state -- no ambiguous items.
- The checklist records who performed the merge and the timestamp of completion.

**Downstream Consumers:** Team Lead (for integration status tracking), Developer
(for confirmation their work was merged correctly), Code Quality Reviewer (for
post-merge review context).

---

## 3. Release Notes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Release Notes                                      |
| **Cadence**        | One per release or integration milestone           |
| **Template**       | `personas/integrator-merge-captain/templates/release-notes.md` |
| **Format**         | Markdown                                           |

**Description.** A reader-friendly summary of everything that changed in the
integrated deliverable. Release notes communicate what is new, what changed,
what was fixed, and what was removed -- without requiring the reader to parse
individual commit messages or merge records.

**Quality Bar:**
- Organized into clear categories: Added, Changed, Fixed, Removed, Deprecated.
- Each entry is a plain-language description understandable by someone who did
  not participate in the development.
- Every entry traces to at least one task ID, PR number, or branch name.
- Breaking changes are called out in a dedicated section with migration
  instructions.
- The release notes cover all merges since the previous release -- no gaps.

**Downstream Consumers:** Technical Writer (for user-facing documentation),
DevOps-Release (for deployment context), Team Lead (for stakeholder
communication), Business Analyst (for requirements traceability).

---

## 4. Cutover Plan

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Cutover Plan                                       |
| **Cadence**        | One per major release or environment migration     |
| **Template**       | `personas/integrator-merge-captain/templates/cutover-plan.md` |
| **Format**         | Markdown                                           |

**Description.** A detailed plan for transitioning from the current integrated
state to the release state, including the sequence of operations, rollback
procedures, and verification steps. The cutover plan ensures that the final
handoff from integration to deployment is controlled and reversible.

**Quality Bar:**
- Step-by-step cutover sequence with explicit ordering and estimated duration
  per step.
- Rollback procedure for each step is documented and tested before cutover
  begins.
- Go/no-go criteria are defined for each phase of the cutover.
- Communication plan specifies who is notified at each stage (start,
  completion, rollback).
- Verification steps confirm that the cutover result matches expected state
  (build hash, test results, feature flags).

**Downstream Consumers:** DevOps-Release (for deployment execution), Team Lead
(for go/no-go decision), Tech QA (for post-cutover verification), Developer
(for rollback support).

---

## 5. Conflict Resolution Notes

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Conflict Resolution Notes                          |
| **Cadence**        | One per merge that involves non-trivial conflicts  |
| **Template**       | `personas/integrator-merge-captain/templates/conflict-resolution-notes.md` |
| **Format**         | Markdown                                           |

**Description.** Detailed documentation of how merge conflicts were resolved,
including the intent of both sides, the resolution strategy chosen, and any
implications for future work. These notes preserve the reasoning so that future
integrators and developers understand why the code looks the way it does after
the merge.

**Quality Bar:**
- Each conflict is documented with: file path, line range, description of what
  each side changed, and why.
- The resolution strategy is stated explicitly: "kept both changes interleaved,"
  "chose side A because side B is superseded," or "rewrote to accommodate both."
- Contributing developers were consulted before resolving semantic conflicts.
- If a conflict reveals a design gap, this is flagged for the Architect with
  a specific description of the overlap.

**Downstream Consumers:** Developer (for understanding resolution decisions),
Architect (for design gap identification), Code Quality Reviewer (for review
context), future Integrators (for historical reference).

---

## 6. Post-Integration Status Report

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Post-Integration Status Report                     |
| **Cadence**        | One per integration cycle completion               |
| **Template**       | None (follows structure below)                     |
| **Format**         | Markdown                                           |

**Description.** A summary report delivered after an integration cycle
completes, providing the team with a clear picture of what merged successfully,
what is pending, what had issues, and what risks remain.

**Required Sections:**
1. **Integration Summary** -- Total branches merged, total conflicts resolved,
   cycle duration, and comparison to the integration plan.
2. **Successfully Merged** -- List of branches merged with confirmation of
   build and test status for each.
3. **Pending** -- Branches not yet merged with reason (not ready, blocked,
   deferred) and expected timeline.
4. **Issues Encountered** -- Conflicts that required escalation, regressions
   found, and deviations from the integration plan.
5. **Risks and Recommendations** -- Outstanding risks, recommended actions,
   and items requiring Team Lead attention.

**Quality Bar:**
- Every branch from the integration plan is accounted for -- none are silently
  omitted.
- Build and test status is reported with specific evidence (CI run URL or test
  result summary), not just "passed."
- Issues are described with enough detail for the Team Lead to make decisions
  without further investigation.
- The report is delivered within one working day of integration cycle
  completion.

**Downstream Consumers:** Team Lead (for status and decision-making), Developer
(for awareness of integration state), Tech QA (for regression awareness),
DevOps-Release (for deployment readiness assessment).

---

## Output Format Guidelines

- All deliverables are written in Markdown and committed to the project
  repository or filed in the project's documentation structure.
- Integration plans and cutover plans are stored in `docs/integration/` and
  named with the cycle or release identifier (e.g., `integration-plan-v2.1.md`).
- Conflict resolution notes are stored alongside the merge records they
  document, or in `docs/integration/conflicts/`.
- Release notes follow a consistent naming convention tied to the version or
  milestone (e.g., `release-notes-v2.1.md`).
- Post-integration status reports are delivered to the Team Lead directly and
  archived for future reference.
- All outputs reference specific branch names, commit hashes, or PR numbers
  for traceability.
