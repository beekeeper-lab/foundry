# Task 01 — Architect: Seeder-to-Bean Task Location Decision

| Field | Value |
|-------|-------|
| **Owner** | Architect |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-04-17 18:46 |
| **Completed** | 2026-04-17 18:46 |
| **Duration** | < 1m |

## Goal

Decide whether the Seeder still produces `ai/tasks/<persona>/` files or moves those tasks inside a starter bean's `tasks/` directory. Record the decision as an ADR.

## Inputs

- `ai/beans/BEAN-254-bootstrap-bean-for-seeded-tasks/bean.md`
- `foundry_app/services/seeder.py`
- `foundry_app/services/scaffold.py`
- `ai/context/bean-workflow.md`

## Decision

**Choice: Seeder emits a starter bean at `ai/beans/BEAN-001-bootstrap/`** with `Status: Approved`, a populated `tasks/` directory holding the same set of tasks the Seeder produces today, and an `ai/beans/_index.md` entry for BEAN-001.

### Rationale

| Criterion | Starter bean (chosen) | Keep `ai/tasks/` |
|-----------|-----------------------|-------------------|
| Resolves audit complaint | Yes — tasks now live inside a tracked bean | No — orphan tasks persist |
| Conforms to declared workflow | Yes — bean is the unit of work per `bean-workflow.md` | No — bypasses the workflow |
| Discoverable at day 1 | Yes — Team Lead picks BEAN-001 immediately | No — `_index.md` is empty |
| Blast radius | Small — seeder + scaffold only | N/A |
| Forward compatibility | Extra task mappings just add task files | Deepens the orphan problem |

### Structural Shape

```
ai/
  beans/
    _index.md                       # BEAN-001 row appended
    BEAN-001-bootstrap/
      bean.md                       # Status: Approved
      tasks/
        01-team-lead-*.md
        02-ba-*.md
        ...
  tasks/                            # remains as an empty scaffold-created dir
```

- `ai/tasks/` is no longer written to by the seeder. It stays as an empty scaffold directory so downstream library commands (`seed-tasks`, `new-work`, `release-notes`) that document task-file paths continue to have a target to write into. Keeping the directory also avoids breaking `validate-repo`'s structural path list without a cross-cutting change.
- The starter bean's `Problem Statement` references `ai/context/project-charter.md` (emitted by BEAN-252) when the charter file is present in the generated tree; otherwise it falls back to a generic bootstrap placeholder.
- Task filenames follow the existing naming convention: `NN-<owner>-<slug>.md` where `NN` is zero-padded (`01`, `02`, …) and `slug` is a kebab-case extract of the task description.

### ADR

Recorded as **ADR-004** in `ai/context/decisions.md`.

## Deliverables

- `ai/outputs/architect/BEAN-254-seeder-decision.md` — decision note and rationale.
- `ai/context/decisions.md` — ADR-004 entry appended.

## Acceptance Criteria

- [x] Decision recorded with rationale.
- [x] File layout for the starter bean is specified unambiguously so Developer can implement without re-deciding.
- [x] ADR appended to `ai/context/decisions.md`.
