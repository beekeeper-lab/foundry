# Task Taxonomy

A classification system that maps task types to personas, workflow stages, and expected outputs. The taxonomy ensures that every task created by the team has a clear owner, a defined lifecycle, and a predictable deliverable. Use this as a reference when creating task-seeding plans, assigning work during execution, or auditing whether the right persona is handling the right work.

## Task Categories

| Category        | Description                                                        | Primary Persona          | Supporting Personas                          | Typical Outputs                              |
|-----------------|--------------------------------------------------------------------|--------------------------|----------------------------------------------|----------------------------------------------|
| Planning        | Decompose work into tasks, set priorities, define waves            | Team Lead                | BA, Architect                                | Task-seeding plan, status report             |
| Requirements    | Elicit, analyze, and document what the system must do              | BA                       | Team Lead, UX/UI Designer                    | Epic brief, user stories, acceptance criteria|
| Design          | Define system structure, boundaries, APIs, and key decisions       | Architect                | Developer, Security Engineer                 | ADR, design spec, API contract, system context|
| Implementation  | Write production code that satisfies acceptance criteria           | Developer                | Architect, Tech-QA                           | Source code, PR description, dev design decision|
| Testing         | Verify that deliverables meet acceptance criteria and handle edge cases | Tech-QA             | Developer, Security Engineer                 | Test plan, test cases, test report, bug reports|
| Review          | Inspect code for quality, consistency, and adherence to standards  | Code Quality Reviewer    | Architect, Developer                         | Review comments, suggested diffs, ship/no-ship checklist|
| Integration     | Merge work from multiple branches and personas into a cohesive whole| Integrator               | Developer, Tech-QA                           | Merge checklist, conflict resolution notes, release notes|
| Deployment      | Build, release, and operate the system in target environments      | DevOps / Release Engineer| Developer, Security Engineer                 | Release runbook, pipeline config, rollback runbook|
| Documentation   | Produce and maintain project documentation for all audiences       | Technical Writer         | All personas (as subject-matter sources)     | README, runbook, ADR index, API docs, onboarding guide|
| Security        | Identify and mitigate security risks throughout the lifecycle      | Security Engineer        | Architect, Developer, DevOps                 | Threat model, security checklist, hardening checklist|
| Compliance      | Map controls, gather evidence, manage regulatory risk              | Compliance / Risk Analyst| Security Engineer, Team Lead                 | Risk register, control mapping, audit notes, evidence plan|
| Research        | Investigate options, compare alternatives, summarize findings      | Researcher / Librarian   | Architect, BA                                | Research memo, decision matrix, annotated bibliography|
| UX Design       | Define user flows, interaction patterns, and content structure     | UX / UI Designer         | BA, Developer, Technical Writer              | Wireframes, component spec, user flows, accessibility checklist|

## Task Lifecycle States

Every task moves through a defined set of states. Transitions are governed by the stage gates enforced by the Team Lead.

| State       | Description                                                        | Allowed Transitions              |
|-------------|--------------------------------------------------------------------|---------------------------------|
| Pending     | Task is defined but not yet assigned to a persona for execution    | Assigned, Deferred              |
| Assigned    | Task has an owner and is queued for the current or next wave       | In Progress, Blocked, Deferred  |
| In Progress | Active work is underway by the assigned persona                    | In Review, Blocked              |
| In Review   | Work is complete and awaiting review by another persona            | Done, In Progress (rework)      |
| Blocked     | Work cannot proceed due to an unresolved dependency or issue       | Assigned, In Progress, Deferred |
| Done        | Task meets its definition of done and all acceptance criteria pass | (terminal state)                |
| Deferred    | Task is intentionally postponed to a future wave or phase          | Pending, Assigned               |

## Assignment Rules

These guidelines determine which persona receives a given task. The Team Lead is responsible for enforcing these rules during task seeding and re-assignment.

1. **Match by category.** Use the Task Categories table above as the primary routing guide. The Primary Persona column identifies the default owner for each category.
2. **One owner per task.** Every task has exactly one assigned persona. Supporting personas contribute through review or consultation but do not own the deliverable.
3. **Respect boundaries.** Developers do not define requirements (that is the BA's job). The BA does not make architectural decisions (that is the Architect's job). Each persona operates within its defined mission.
4. **Escalate ambiguity.** If a task does not clearly map to a single category, the Team Lead makes the assignment decision and documents the rationale.
5. **Load balance across waves.** Within a single wave, distribute tasks so that no persona is overloaded while others are idle. Use dependencies to sequence work, not arbitrary batching.
6. **Prefer specialists.** When a task touches multiple categories (e.g., a deployment task with security implications), assign it to the primary category owner and list the other persona as a reviewer or consultant.

## Cross-Cutting Concerns

Some work naturally spans multiple personas. These cross-cutting concerns require coordination rather than a single owner.

- **Security review:** Touches Security Engineer (threat model), Architect (design review), Developer (secure coding), and DevOps (hardening). The Security Engineer leads; others contribute within their domain.
- **Compliance evidence gathering:** The Compliance / Risk Analyst defines what evidence is needed, but the evidence itself comes from Developer (code artifacts), Tech-QA (test results), DevOps (deployment logs), and Security Engineer (scan reports).
- **API contract changes:** The Architect owns the contract definition, but the BA validates it against requirements, the Developer implements it, and the Tech-QA verifies it.
- **Release coordination:** The DevOps / Release Engineer owns the release process, but the Integrator prepares the merged branch, the Tech-QA signs off on quality, and the Team Lead approves the go/no-go.
- **Documentation updates:** The Technical Writer owns the documentation, but every persona is responsible for providing accurate source material and reviewing documentation that covers their domain.
- **UX consistency:** The UX / UI Designer defines the patterns, but the Developer implements them, the Code Quality Reviewer checks adherence, and the Tech-QA verifies the user-facing behavior.
