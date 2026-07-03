---
name: backlog-consolidate
description: "Detects and resolves duplicates, overlaps, contradictions, missing dependencies, and merge opportunities across recently created beans. Designed for post-refinement cleanup after running multiple /backlog-refinement sessions in parallel."
---

# /backlog-consolidate Command

Detects and resolves duplicates, overlaps, contradictions, missing dependencies, and merge opportunities across recently created beans. Designed for post-refinement cleanup after running multiple `/backlog-refinement` sessions in parallel.

## Usage

```
/backlog-consolidate [--status <status>] [--dry-run]
```

- `--status <value>` — Filter which beans to analyze. Default: `Unapproved`. Also accepts `open` (Unapproved + Approved + In Progress), `all`, or any single status value.
- `--dry-run` — Show findings and proposed changes without applying them.

## See Also

- Skill: `claude/skills/backlog-consolidate/SKILL.md` — canonical execution spec.
