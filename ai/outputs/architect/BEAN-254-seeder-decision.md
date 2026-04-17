# BEAN-254 — Seeder-to-Bean Task Location Decision

## Decision

The Seeder stage emits a single starter bean at `ai/beans/BEAN-001-bootstrap/` with `Status: Approved`, a populated `tasks/` directory, and a BEAN-001 row appended to `ai/beans/_index.md`. `ai/tasks/` remains as an empty scaffold-created directory.

Recorded as **ADR-004** in `ai/context/decisions.md`.

## Rationale

| Criterion | Starter bean (chosen) | Keep orphan `ai/tasks/` |
|-----------|-----------------------|--------------------------|
| Resolves audit complaint | Yes | No |
| Conforms to `bean-workflow.md` | Yes — bean is the declared unit of work | No |
| Day-1 discoverability | Team Lead picks BEAN-001 immediately | `_index.md` is empty |
| Blast radius | Seeder + scaffold only | N/A |

## Structural Contract for Developer

- Bean directory: `ai/beans/BEAN-001-bootstrap/`
- `bean.md` status: `Approved`, priority `Medium`, owner `(unassigned)`, category `App`.
- Task filenames: `NN-<owner>-<slug>.md` — zero-padded, contiguous across personas, kebab-case slug derived from the task description (lowercased, first ~6 words, non-word chars collapsed to `-`).
- `ai/beans/_index.md`: append BEAN-001 row if not present; preserve existing rows on re-run.
- Problem Statement: reference `ai/context/project-charter.md` when it exists in the generated tree; fall back to a generic bootstrap placeholder otherwise.

## Non-Goals

- Do **not** redesign the seeder's task-mapping rules. Same task strings, same counts — only the destination changes.
- Do **not** delete `ai/tasks/` from the scaffold; that's a wider change with library command implications and is out of scope.
- Do **not** create multiple starter beans. One is sufficient.
