# /new-dev-decision Command

Records a lightweight developer decision — implementation-level choices that matter but don't warrant a full ADR (library choices, algorithm approaches, error handling strategies, performance tradeoffs).

## Usage

```
/new-dev-decision "<title>" [--context <text>] [--chosen <text>] [--alternatives <list>] [--tags <list>] [--work <id>] [--output <dir>]
```

- `title` -- Short title for the decision (required).
- `--context <text>` -- Why the decision was needed (prompted if omitted).
- `--chosen <text>` -- What was decided and why (prompted if omitted).
- `--alternatives <list>` -- Comma-separated alternatives considered.
- `--tags <list>` -- Comma-separated tags (e.g., `performance,caching`).
- `--work <id>` -- Related work item ID.
- `--output <dir>` -- Override the output directory (default: `ai/outputs/developer/decisions/`).

## See Also

- Skill: `claude/skills/new-dev-decision/SKILL.md` — canonical execution spec.
- `/new-adr` — for architectural decisions affecting system boundaries or multiple components.
