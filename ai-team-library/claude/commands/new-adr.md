# /new-adr Command

Creates a new Architecture Decision Record documenting a significant technical decision with context, options, tradeoffs, rationale, and consequences.

## Usage

```
/new-adr "<decision title>" [--context <text-or-file>] [--related <item-ids>] [--output <dir>] [--template <path>]
```

- `decision title` -- Short title for the decision (required).
- `--context <text-or-file>` -- Provide context inline instead of being prompted.
- `--related <ids>` -- Comma-separated story/task/issue IDs related to this decision.
- `--output <dir>` -- Override the ADR output directory (default: `ai/context/decisions/`).
- `--template <path>` -- Custom ADR template (default: Architect's ADR template).

## See Also

- Skill: `claude/skills/new-adr/SKILL.md` — canonical execution spec.
