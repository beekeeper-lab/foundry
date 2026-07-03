---
name: bean-status
description: "Displays the current state of the beans backlog — counts by status, a table grouped by status, and (with --verbose) task-level detail for active beans."
---

# /bean-status Command

Displays the current state of the beans backlog — counts by status, a table grouped by status, and (with `--verbose`) task-level detail for active beans.

## Usage

```
/bean-status [--filter <status>] [--verbose]
```

- `--filter <status>` -- Show only beans with this status: `unapproved`, `approved`, `in-progress`, `done`, `deferred`. Default: show all.
- `--verbose` -- Include task breakdown for In Progress beans.

## See Also

- Skill: `claude/skills/bean-status/SKILL.md` — canonical execution spec.
