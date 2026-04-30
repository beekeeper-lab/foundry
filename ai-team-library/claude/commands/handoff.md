# /handoff Command

Creates a structured handoff packet between personas — bundles artifacts, decisions, assumptions, next steps, and risks so the next persona can pick up where the previous one left off without context loss.

## Usage

```
/handoff <from-persona> <to-persona> [--work <id>] [--artifacts <paths>] [--notes <text>] [--output <path>]
```

- `from-persona` -- The persona completing their phase.
- `to-persona` -- The persona picking up next.
- `--work <id>` -- Work item ID to scope the handoff (e.g., `WRK-003`).
- `--artifacts <paths>` -- Comma-separated artifact paths (auto-detected if omitted).
- `--notes <text>` -- Free-form context to include in the handoff.
- `--output <path>` -- Override the output directory (default: `ai/handoffs/`).

## See Also

- Skill: `claude/skills/handoff/SKILL.md` — canonical execution spec.
