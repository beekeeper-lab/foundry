---
name: merge-bean
description: "Merges a bean's feature branch into the main branch using a safe merge sequence (validate, sync, no-ff merge, push, cleanup). The final stage of the bean execution wave — integrates completed work so other beans can build on it."
---

# /merge-bean Command

Merges a bean's feature branch into the `main` branch using a safe merge sequence (validate, sync, no-ff merge, push, cleanup). The final stage of the bean execution wave — integrates completed work so other beans can build on it.

## Usage

```
/merge-bean <bean-id> [--target <branch>]
```

- `bean-id` -- The bean ID to merge (e.g., `BEAN-011` or just `11`).
- `--target <branch>` -- Target branch to merge into (default: `main`).

## See Also

- Skill: `claude/skills/merge-bean/SKILL.md` — canonical execution spec.
