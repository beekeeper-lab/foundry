---
name: trello-load
description: "Connects to Trello, pulls cards from a board's Sprint_Backlog list, and feeds each card into /backlog-refinement to create well-formed beans. Cards are moved to In_Progress after refinement."
---

# /trello-load Command

Connects to Trello, pulls cards from a board's Sprint_Backlog list, and feeds each card into `/backlog-refinement` to create well-formed beans. Cards are moved to In_Progress after refinement.

## Usage

```
/trello-load [--dry-run] [--board <id>]
```

No arguments required — the command prompts for board selection interactively.

- `--dry-run` -- Show which cards would be processed without creating beans or moving cards.
- `--board <id>` -- Skip board selection and use the specified board ID directly.

## See Also

- Skill: `claude/skills/trello-load/SKILL.md` — canonical execution spec.
