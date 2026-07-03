---
name: trello-load
description: "Connects to Trello, pulls cards from a board's Sprint_Backlog list, and feeds each card into /backlog-refinement to create well-formed beans. Cards are moved to In_Progress after refinement."
---

# /trello-load

This command is a thin entry point; the canonical process lives in the
`trello-load` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/trello-load/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
