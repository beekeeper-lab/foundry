# /telemetry-report Command

Produces an aggregate summary of project telemetry: total time invested, average bean duration, breakdowns by category and owner, and outlier identification.

## Usage

```
/telemetry-report [--category <cat>] [--status <status>] [--since YYYY-MM-DD]
```

- `--category <cat>` -- Filter by category: `App`, `Process`, `Infra`. Case-insensitive.
- `--status <status>` -- Filter by bean status. Default: `Done`. Use `all` for everything.
- `--since YYYY-MM-DD` -- Only include beans created on or after this date.

## See Also

- Skill: `claude/skills/telemetry-report/SKILL.md` — canonical execution spec.
