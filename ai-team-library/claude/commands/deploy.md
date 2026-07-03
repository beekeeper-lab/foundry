---
name: deploy
description: "Validates the main branch, runs tests, and creates a version tag. With trunk-based development, all work is already on main via feature branch merges — deploy simply tags a release point."
---

# /deploy Command

Validates the `main` branch, runs tests, and creates a version tag. With trunk-based development, all work is already on `main` via feature branch merges — deploy simply tags a release point.

## Usage

```
/deploy [--tag <version>]
```

- `--tag <version>` -- Optional. Tag the current commit with a version (e.g., `v1.2.0`). If omitted, auto-generates from date: `deploy-YYYY-MM-DD`.

## See Also

- Skill: `claude/skills/deploy/SKILL.md` — canonical execution spec.
