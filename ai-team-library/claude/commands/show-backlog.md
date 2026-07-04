---
name: show-backlog
description: "Displays the bean backlog in a concise table format showing each bean's ID, a one-sentence summary, and category."
---

# /show-backlog Command

Displays the bean backlog in a concise table format showing each bean's ID, a one-sentence summary, and category.

## Usage

```
/show-backlog [--status <status>] [--category <cat>]
```

- `--status <status>` -- Filter by status: `Unapproved`, `Approved`, `In Progress`, `Done`, `Deferred`, or `open` (shortcut for all non-Done). Default: show all.
- `--category <cat>` -- Filter by category: `App`, `Process`, `Infra`. Case-insensitive. Default: show all.

## See Also

- No paired skill — `/show-backlog` is a thin read-only display of `ai/beans/_index.md`. The full filter/output spec lives in this command.
