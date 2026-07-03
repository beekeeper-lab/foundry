---
name: new-work
description: "Creates a new work item — the single entry point for bugs, features, chores, spikes, and refactors. Asks the right questions, creates a task spec, drafts the appropriate BA artifact (story or bug report), and seeds initial tasks."
---

# /new-work Command

Creates a new work item — the single entry point for bugs, features, chores, spikes, and refactors. Asks the right questions, creates a task spec, drafts the appropriate BA artifact (story or bug report), and seeds initial tasks.

## Usage

```
/new-work <type> "<goal>" [--urgency <level>] [--constraints <text>] [--areas <list>] [--no-seed] [--assign <persona>]
```

- `type` -- One of: `bug`, `feature`, `chore`, `spike`, `refactor`.
- `goal` -- What this work aims to accomplish (quoted string).
- `--urgency <level>` -- `low`, `normal` (default), `high`, `critical`.
- `--constraints <text>` -- Time, scope, or technical constraints.
- `--areas <list>` -- Comma-separated affected components or modules.
- `--no-seed` -- Create the task spec without seeding tasks.
- `--assign <persona>` -- Override the initial persona assignment.

## See Also

- Skill: `claude/skills/new-work/SKILL.md` — canonical execution spec.
