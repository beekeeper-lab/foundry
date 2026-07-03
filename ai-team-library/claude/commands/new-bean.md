---
name: new-bean
description: "Creates a new bean in the backlog with the correct ID, directory structure, and index entry. Auto-assigns the next sequential BEAN-NNN ID, populates bean.md from the template, and appends to _index.md."
---

# /new-bean Command

Creates a new bean in the backlog with the correct ID, directory structure, and index entry. Auto-assigns the next sequential `BEAN-NNN` ID, populates `bean.md` from the template, and appends to `_index.md`.

## Usage

```
/new-bean "<title>" [--priority <level>]
```

- `title` -- Short descriptive title for the bean (quoted string).
- `--priority <level>` -- Priority: `Low`, `Medium`, `High`. Default: `Medium`.

## See Also

- Skill: `claude/skills/new-bean/SKILL.md` — canonical execution spec.
