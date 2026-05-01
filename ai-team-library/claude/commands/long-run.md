# /long-run Command

Puts the Team Lead in autonomous mode, processing beans from the backlog until the backlog is empty or no actionable beans remain. Supports sequential (default) and parallel (`--fast N`) modes.

## Usage

```
/long-run [--fast N] [--category <cat>]
```

- `--fast N` -- Run N beans in parallel using tmux child windows (requires `$TMUX`).
- `--category <cat>` -- Only process beans matching this category: `App`, `Process`, or `Infra` (case-insensitive).

## See Also

- Skill: `claude/skills/long-run/SKILL.md` — canonical execution spec (sequential and parallel modes, bean selection heuristics, dashboard loop, Status File Protocol).
- `/spawn-bean` — bean-level worker invocation that uses the same workers and protocol.
- `/merge-bean` — invoked by the orchestrator after each worker completes.
