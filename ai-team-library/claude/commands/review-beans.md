---
name: review-beans
description: "Generates a filtered Map of Content (MOC) linking to beans by status, then opens Obsidian on the ai/beans/ directory for review."
---

# /review-beans Command

Generates a filtered Map of Content (MOC) linking to beans by status, then opens Obsidian on the `ai/beans/` directory for review.

## Usage

```
/review-beans [--status <status>] [--category <cat>]
```

- `--status <status>` — Filter by status. Default: `unapproved`. Accepts: `unapproved`, `approved`, `in-progress`, `done`, `deferred`, `all`.
- `--category <cat>` — Filter by category: `App`, `Process`, `Infra`. Case-insensitive. Default: all categories.

## See Also

- Skill: `claude/skills/review-beans/SKILL.md` — canonical execution spec.
