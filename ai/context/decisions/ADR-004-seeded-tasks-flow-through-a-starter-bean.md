# ADR-004: Seeded Tasks Flow Through a Starter Bean

| Field | Value |
|-------|-------|
| **Date** | 2026-04-17 |
| **Status** | Accepted |
| **Bean** | BEAN-254 |
| **Deciders** | Architect |

## Context

External audit (2026-04-17) flagged that seeded tasks were orphaned: `ai/tasks/_index.md` listed tasks assigned to personas, but `ai/beans/_index.md` was empty and no task was linked to a bean. The declared unit of work is the bean (per `ai/context/bean-workflow.md`), so tasks that live in `ai/tasks/` bypass the very system that is supposed to track them. A Team Lead's first action on a newly generated project is meant to be *picking a bean* from the backlog — but there was no starter bean for them to pick.

## Decision

The Seeder stage emits a single starter bean, `BEAN-001-bootstrap`, under `ai/beans/`. The bean is created with `Status: Approved` so the Team Lead can claim it immediately. Its `tasks/` directory holds the same set of per-persona tasks the Seeder used to write into `ai/tasks/_index.md`, one task per file, named `NN-<owner>-<slug>.md`. `ai/beans/_index.md` is appended with a BEAN-001 row. The bean's Problem Statement references `ai/context/project-charter.md` (emitted by BEAN-252) when that file is present, falling back to a generic "bootstrap" placeholder otherwise.

`ai/tasks/` remains as an empty scaffold-created directory so downstream library commands that write task files (`seed-tasks`, `new-work`, `release-notes`) still have a target, and so `validate-repo`'s structural path list is unaffected.

## Consequences

**Positive:**
- Seeded work enters through the bean workflow — no orphan tasks.
- Team Lead's day-1 action has a target (`BEAN-001`) that can be picked without any setup.
- Tasks are now first-class bean artifacts, so telemetry, status changes, and outputs all flow through the bean directory contract the rest of the workflow already speaks.
- Strictly additive — no existing generated projects lose files, because the new write location is a parallel tree (`ai/beans/BEAN-001-bootstrap/`).

**Negative:**
- Two task file shapes coexist in the library (the old `ai/tasks/NNN-{slug}.md` layout referenced by `seed-tasks.md` / `new-work.md` commands, and the new bean-scoped `NN-<owner>-<slug>.md` layout). These command docs describe downstream library commands the generated project runs later — they can migrate independently.

## Alternatives Rejected

1. **Leave `ai/tasks/_index.md` as-is:** Does not solve the audit's complaint. Rejected.
2. **Delete `ai/tasks/` entirely:** Larger blast radius — the library's `seed-tasks` / `new-work` / `release-notes` commands reference that path. Keeping the empty directory costs one `mkdir` and preserves the contract.
3. **Emit one starter bean per persona:** Multiplies the backlog with beans that share a single goal (bootstrap). A single bean whose `tasks/` directory enumerates per-persona work mirrors the normal bean → tasks decomposition pattern exactly.

