# Team Lead -- Outputs

This document enumerates every artifact the Team Lead is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Status Report

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| **Deliverable**    | Cycle Status Report                               |
| **Cadence**        | End of every sprint/cycle, or on-demand for escalations |
| **Template**       | `personas/team-lead/templates/status-report.md`   |
| **Format**         | Markdown                                          |

**Description.** A concise summary of what was accomplished, what is in
progress, what is blocked, and what is planned next. Intended for stakeholders
who need a five-minute read, not a deep dive.

**Quality Bar:**
- Every in-progress item has an estimated completion date or explicit "unknown."
- Every blocked item names the specific blocker and who owns resolution.
- Risks section includes likelihood and impact, not just a list of worries.
- Metrics section includes at least: tasks completed, tasks added, tasks
  deferred, and cycle velocity trend.
- No stale data: report reflects state as of the reporting timestamp.

**Downstream Consumers:** Stakeholders, Architect (for planning), Business
Analyst (for scope tracking).

---

## 2. Task Seeding Plan

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| **Deliverable**    | Task Seeding Plan                                 |
| **Cadence**        | Start of every sprint/cycle                       |
| **Template**       | `personas/team-lead/templates/task-seeding.md`    |
| **Format**         | Markdown                                          |

**Description.** The breakdown of cycle objectives into discrete, assignable
tasks. Each task entry includes the target persona, objective, inputs required,
acceptance criteria, dependencies, and priority rank.

**Quality Bar:**
- Every task has exactly one assigned persona. Shared ownership is not allowed;
  if collaboration is needed, create separate tasks with explicit handoff
  points.
- Acceptance criteria are testable: a reviewer can unambiguously determine
  pass/fail.
- Dependencies are stated as "blocked by Task X" with the specific output
  needed, not vague references to other work streams.
- Priority ordering is a strict rank (1, 2, 3...), not tiers (P1, P1, P1...).
- No task takes more than one cycle. If an objective is too large, decompose
  it into multiple tasks.

**Downstream Consumers:** All personas (for their assignments), Code Quality
Reviewer (for review planning), DevOps-Release (for release scoping).

---

## 3. Integration Summary

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| **Deliverable**    | Integration Summary                               |
| **Cadence**        | After each integration milestone                  |
| **Template**       | None (freeform, but follows structure below)      |
| **Format**         | Markdown                                          |

**Description.** Documents how outputs from multiple personas were composed
into a working whole. Captures integration decisions, conflicts resolved during
integration, and any rework triggered.

**Required Sections:**
1. **Components Integrated** -- List of artifacts merged, with source persona
   and review status.
2. **Integration Decisions** -- Any choices made during integration that were
   not specified in the original task (e.g., ordering of operations, conflict
   resolution between competing approaches).
3. **Rework Triggered** -- If integration surfaced issues requiring a persona
   to revise their output, document what was sent back and why.
4. **Verification** -- How the integrated result was verified (smoke test,
   persona review, automated checks).
5. **Open Issues** -- Anything deferred or known-imperfect in the integration.

**Quality Bar:**
- Every component in the integration is traceable to a completed, reviewed task.
- No "magic" steps: a reader should be able to reproduce the integration from
  this document alone.
- Rework items are tracked back into the task pipeline, not left as footnotes.

**Downstream Consumers:** Architect (for system coherence), DevOps-Release
(for release readiness), Code Quality Reviewer (for audit trail).

---

## 4. Team Charter

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| **Deliverable**    | Team Charter                                      |
| **Cadence**        | Once at project kickoff; updated when team composition changes |
| **Template**       | None (follows structure below)                    |
| **Format**         | Markdown                                          |

**Description.** The foundational document that establishes who is on the team,
what each persona is responsible for, how decisions are made, and what the
shared working agreements are.

**Required Sections:**
1. **Project Objective** -- One paragraph stating what the team exists to
   deliver and the primary success metric.
2. **Team Roster** -- Table of active personas, their domain, and their
   primary deliverables (link to each persona's `outputs.md`).
3. **Decision Framework** -- Who decides what (mirrors the Decision Rights
   table from the Team Lead persona, extended for project-specific decisions).
4. **Working Agreements** -- Shared norms: review turnaround time, definition
   of done, communication channels, escalation path.
5. **Cycle Structure** -- Length of sprints/cycles, ceremony schedule (planning,
   review, retro), reporting cadence.
6. **Risk Register** -- Initial risks identified at kickoff with owners and
   mitigation plans.

**Quality Bar:**
- Every persona on the roster has acknowledged their role (or been confirmed
  by the Team Lead as active).
- Working agreements are specific enough to be enforceable. "We will
  communicate well" is not a working agreement. "Review turnaround is 4 hours
  maximum" is.
- The charter is stored in the project root and linked from the README or
  project index.

**Downstream Consumers:** All team personas, stakeholders, any new persona
joining the team mid-project.

---

## 5. Retrospective Notes

| Field              | Value                                             |
|--------------------|---------------------------------------------------|
| **Deliverable**    | Cycle Retrospective                               |
| **Cadence**        | End of every sprint/cycle                         |
| **Template**       | None (freeform)                                   |
| **Format**         | Markdown                                          |

**Description.** A structured reflection on what went well, what did not, and
what the team will change. The critical output is not the reflection itself but
the concrete improvement actions committed for the next cycle.

**Required Sections:**
1. **What Worked** -- Practices or decisions that should continue.
2. **What Did Not Work** -- Specific pain points with root cause analysis.
3. **Improvement Actions** -- Each action has an owner, a target cycle, and
   measurable success criteria.

**Quality Bar:**
- At least one improvement action is committed per cycle. Zero actions means
  the retrospective was performative.
- Improvement actions from the previous cycle are reviewed: were they done?
  Did they help?
- Blame-free language. Name processes and artifacts, not personas.

**Downstream Consumers:** Team Lead (for process improvement), all personas
(for shared learning).
