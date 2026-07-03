---
name: handoff
description: "Emit a typed handoff packet between two personas. The packet shape is the intersection of the sender's produces: and the receiver's consumes:, with each artifact's required-fields from the registry, plus any edge-specific pair-fields extras."
---

# /handoff

This command is a thin entry point; the canonical process lives in the
`handoff` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/handoff/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
