---
name: handoff
description: "Emit a typed handoff packet between two personas. The packet shape is the intersection of the sender's produces: and the receiver's consumes:, with each artifact's required-fields from the registry, plus any edge-specific pair-fields extras."
---

# /handoff Command

Emit a **typed** handoff packet between two personas. The packet shape is the
intersection of the sender's `produces:` and the receiver's `consumes:`,
with each artifact's `required-fields` from the registry, plus any
edge-specific `pair-fields` extras.

## Usage

```
/handoff <from-persona> <to-persona> --bean <BEAN-ID> [--task <task-file>] [--notes <text>]
```

- `from-persona` — Persona handing off (e.g., `developer`).
- `to-persona` — Persona receiving (e.g., `tech-qa`).
- `--bean <BEAN-ID>` — Owning bean (e.g., `BEAN-274`). Required.
- `--task <task-file>` — Originating task file inside the bean. Optional.
- `--notes <text>` — Free-form context the typed schema does not cover.

The skill blocks the handoff if the sender has not produced an artifact for
a required type in the intersection — see `MissingProducedArtifact` in the
skill spec.

## See also

- Skill: `claude/skills/handoff/SKILL.md` — canonical execution spec.
- Registry: `contracts/artifact-types.yml` — `types:` and `pair-fields:`.
- Index: `ai/handoffs/_index.md` — every emitted packet appended here.
