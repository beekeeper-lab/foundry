---
name: notes-to-stories
description: "Converts unstructured notes (meeting notes, feature requests, brainstorming output) into properly formatted user stories with testable acceptance criteria, flagged open questions, and identified risks."
---

# /notes-to-stories Command

Converts unstructured notes (meeting notes, feature requests, brainstorming output) into properly formatted user stories with testable acceptance criteria, flagged open questions, and identified risks.

## Usage

```
/notes-to-stories <notes-file-or-text> [--template <path>] [--existing <dir>] [--output <dir>] [--format <brief|full>]
```

- `notes-file-or-text` -- Path to a notes file, or inline text.
- `--template <path>` -- Custom story template (default: BA persona template).
- `--existing <dir>` -- Directory of existing stories for deduplication (default: `ai/outputs/ba/`).
- `--output <dir>` -- Override output directory (default: `ai/outputs/ba/user-stories/`).
- `--format <brief|full>` -- `brief` produces inline stories; `full` produces individual files. Default `full`.

## See Also

- Skill: `claude/skills/notes-to-stories/SKILL.md` — canonical execution spec.
