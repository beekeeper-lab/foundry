---
name: handoff
description: "- Invoked by the /handoff slash command (see claude/commands/handoff.md). - Called by any persona when its phase completes and a downstream persona needs to begin. - Suggested automatically by close-loop after verification passes if the task has a downstream dependent."
---

# Skill: Handoff (Typed)

## Description

Creates a **typed**, contract-aware handoff packet when one persona completes
its phase and the next persona picks up. The packet is no longer a free-form
dump — it is the typed intersection of what the **sender produces** and what
the **receiver consumes**, with each artifact spelled out in the
registry-required fields. The skill bridges `close-loop` (which verifies the
sender's work) and the next persona's start (which now has a checkable
schema instead of "read whatever I wrote").

## Trigger

- Invoked by the `/handoff` slash command (see `claude/commands/handoff.md`).
- Called by any persona when its phase completes and a downstream persona
  needs to begin.
- Suggested automatically by `close-loop` after verification passes if the
  task has a downstream dependent.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `from_persona` | string | yes | Persona handing off (e.g., `developer`) |
| `to_persona` | string | yes | Persona receiving (e.g., `tech-qa`) |
| `bean_id` | string | yes | Owning bean (e.g., `BEAN-274`) |
| `task_id` | string | no | Originating task file (e.g., `01-developer-contract-validator.md`) |
| `notes` | text | no | Free-form context the schema does not cover |

## Data sources (read at handoff time)

The skill computes the packet **shape** from three deterministic inputs.
None of these are written by the sender — they are *looked up* from the
library and registry at handoff time.

1. **Sender's `produces:`** —
   `ai-team-library/personas/core/<from>/contracts.yml :: produces`
2. **Receiver's `consumes:`** —
   `ai-team-library/personas/core/<to>/contracts.yml :: consumes`
3. **Artifact-type registry** —
   `ai-team-library/contracts/artifact-types.yml :: types[*]`
   - For each type, `required-fields:` is the per-artifact field set.
   - `pair-fields:` (sibling map) lists per-edge `extras:` to merge in.

These three sources are the same data shape that
`foundry_app/services/library_indexer.py::_load_persona_contracts` already
loads from the library (see lines 100-120 for `ArtifactTypeInfo` and
123-189 for `_load_persona_contracts`). Tech-QA can verify the skill by
checking it consumes the same registry the indexer does — there is no
parallel schema.

## Process

1. **Resolve the contract intersection**
   - Load `from`'s `produces` and `to`'s `consumes`.
   - `intersection = produces ∩ consumes` (preserve `produces` order).
   - If the intersection is empty → **block** with error
     `NoSharedArtifactTypes` (sender produces nothing the receiver consumes
     — wave is misconfigured; escalate to Team Lead).

2. **Compute the packet schema for this edge**
   - For each artifact type `T` in the intersection:
     - `fields(T) = registry.types[T].required-fields`
   - Look up `pair-fields:` for this `(from, to)` edge:
     - If matched, `extras = pair-fields[(from, to)].extras`
     - Else `extras = []`
   - The **packet schema** is `{ T: fields(T) for T in intersection } + extras`.
   - `extras` apply once per packet (not per artifact). They live in a
     dedicated **Edge Extras** section in the rendered packet.

3. **Validate before emitting** (HARD GATE — see Error Conditions)
   - For each artifact type `T` in the intersection, check the sender
     **actually produced** at least one artifact of that type during this
     work cycle. Expected location:
     - `ai/outputs/<from>/` — primary search (recursive). The sender's
       persona-output convention; matches `ArtifactTypeInfo.template-path`
       hint where present.
     - `ai/beans/<bean_id>/` — secondary (e.g., `task-spec`, `bean-spec`,
       embedded `acceptance-criteria`).
     - `ai/context/decisions.md` — for `adr` types (append-only file).
     - The Developer's primary `code-change` artifact lives in the
       working tree itself (not under `ai/outputs/`); accept a referenced
       file under `foundry_app/` or `tests/` as evidence, but the packet
       MUST still cite a developer-authored summary doc under
       `ai/outputs/developer/` (notes file, decision record, or
       comprehension note) so the receiver has a starting point.
   - **If no artifact is found for a required type T**: BLOCK the handoff.
     Emit error `MissingProducedArtifact` naming `T`, the expected
     location(s), and the suggestion to either (a) author the missing
     artifact, or (b) escalate to Team Lead if `T` was claimed in
     `produces:` but is genuinely not part of this work cycle.
   - Do **not** silently downgrade a missing artifact to "TBD" — the
     whole point of the typed packet is to refuse half-baton-passes.

4. **Render the typed packet**
   - File path: `ai/handoffs/<from>-to-<to>-<bean-or-task>.md`
     - `<bean-or-task>` is `BEAN-NNN` for bean-level handoffs and
       `BEAN-NNN-task-NN` for task-scoped ones.
   - Use the **packet template** below. Every artifact type in the
     intersection gets a `### <type-name>` subsection enumerating its
     `required-fields` with concrete values (file path + 1-line summary
     per field, or the field value if the field is a scalar).

5. **Append to the handoff index**
   - Add a row to `ai/handoffs/_index.md` with
     `| Date | From | To | Bean | Packet |` populated from the packet.

6. **Bounce-counter increment** (BEAN-278)
   - When `from_persona == tech-qa` AND `to_persona == developer` AND the
     bean already has at least one `Done`-status `developer`-owned task,
     this handoff is a **bounce** (Tech-QA is sending the work back for
     another pass mid-bean). Locate the bean's Orchestration Telemetry
     block (`## Orchestration Telemetry`), parse the
     `| **Bounces** | N (...) |` row, increment `N` by one (preserving
     the parenthesised hint suffix), and write it back. The counter
     never decrements; over-counts are corrected by manual Team-Lead
     edit, not by automation. If the bean has no Orchestration
     Telemetry block (legacy beans pre-BEAN-278), this step is a silent
     no-op. Note the bounce inline in the packet's `## Notes` section as
     `> Bounce-of: <prior-developer-task-file>` so the audit trail is
     visible from the handoff itself.

7. **Notify the receiver**
   - The packet path is the only thing the sender needs to share. The
     receiver opens it and starts work. No clarifying questions should be
     needed for the contracted-shape items; `notes:` covers the rest.

## Packet template

```markdown
# Handoff: <from> → <to> — <bean-or-task>

| Field | Value |
|-------|-------|
| **From** | <from-persona> |
| **To** | <to-persona> |
| **Bean** | <BEAN-NNN> |
| **Task** | <task-id or —> |
| **Date** | <YYYY-MM-DD> |
| **Packet schema** | <type-1>, <type-2>, … (intersection) |

## Produced artifacts

### <artifact-type-1>

- **<required-field-1>:** <path or value>
- **<required-field-2>:** <path or value>
- …

### <artifact-type-2>
…

## Edge extras

(Present only when `pair-fields` matched this `(from, to)` edge.)

- **<extra-1>:** …
- **<extra-2>:** …

## Start here

The 1-3 files the receiver should open first, in order.

## Notes

Free-form context the schema does not cover. Optional.
```

## How `pair-fields` extras merge with `required-fields`

The artifact-type's `required-fields` describe **what the artifact itself
must contain** (e.g., a `code-change` always has a `summary`,
`what-changed`, `how-to-test`, `files-touched`).

The pair-fields' `extras` describe **what the receiver needs about the
edge that the artifact alone does not say** (e.g., on the
developer→tech-qa edge, Tech-QA needs `test-targets` and `rerun-command`
to start verification immediately — those are not part of the
`code-change` artifact's required fields, but they are required for this
edge).

The merged packet schema is therefore:

```
packet_schema = (union over T in intersection of required-fields[T])
              + extras[(from, to)]
```

`extras` are rendered in a single **Edge Extras** section (not duplicated
per artifact). Field-name collisions between an artifact's required
fields and the edge extras are resolved by **scoping**: artifact fields
appear under the artifact subsection; extras appear under Edge Extras.
The packet renderer never collapses them into a single namespace.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `handoff_packet` | markdown file | Typed packet at `ai/handoffs/<from>-to-<to>-<bean-or-task>.md` |
| `index_row` | table row | Appended row in `ai/handoffs/_index.md` |

## Quality criteria

- The packet's artifact subsections are 1:1 with the contract
  intersection. No extra types, no missing types.
- Every `required-field` for every artifact in the intersection has a
  concrete value (file path, scalar, or short prose). No `TBD` values.
- `pair-fields` extras (when present) appear in their own Edge Extras
  section, not folded into an artifact.
- The packet is self-contained: the receiver can start its phase without
  asking the sender clarifying questions about the contracted items.
- The `_index.md` row is appended (not inserted in arbitrary order) and
  matches the columns `| Date | From | To | Bean | Packet |`.

## Error conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `FromPersonaNotFound` | `from_persona` has no persona directory | Use any persona on the team with a `contracts.yml` (core or `extended/<id>`; SPEC-017 extended contracts to all personas) |
| `ToPersonaNotFound` | `to_persona` has no persona directory | Use any persona on the team with a `contracts.yml` (core or `extended/<id>`) |
| `SamePersona` | `from == to` | A handoff requires two different personas |
| `NoContractsFile` | A persona's `contracts.yml` is missing or unparseable | Restore the persona's `contracts.yml` (validated by `library_indexer._load_persona_contracts`) |
| `NoSharedArtifactTypes` | `produces ∩ consumes == ∅` | Wave is misconfigured for this edge — escalate to Team Lead |
| `MissingProducedArtifact` | Sender did not actually produce an artifact for a required type in the intersection | Either author the missing artifact under `ai/outputs/<from>/` (or the type's conventional location) and re-run, or escalate if the type does not apply to this work cycle |
| `HandoffDirNotWritable` | Cannot write `ai/handoffs/` | Check permissions or scaffold the project |

## Dependencies

- **Close Loop** skill — typically runs before this skill so the sender's
  work is verified before the baton passes.
- **Artifact-type registry** — `ai-team-library/contracts/artifact-types.yml`
  (`types:` for `required-fields`, `pair-fields:` for edge extras).
- **Persona contracts** — `ai-team-library/personas/core/<id>/contracts.yml`
  (`produces:` / `consumes:`).
- **Indexer** — `foundry_app/services/library_indexer.py`
  (`_load_persona_contracts`, `_load_artifact_types`) — same data shape;
  Tech-QA can verify the skill against the indexer for parity.
- **Handoff index** — `ai/handoffs/_index.md` is appended on every emit.
