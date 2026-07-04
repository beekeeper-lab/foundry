# /status-report Command

Generates a status report summarizing current progress, blockers, and next steps across the team. Scans the project workspace for task states, completed artifacts, and outstanding blockers, then produces a single-document view.

## Usage

```
/status-report [--format <brief|full>] [--cycle <current|all|label>] [--output <path>] [--include-velocity] [--no-velocity] [--dry-run]
```

- `--format <brief|full>` -- `brief` is summary + blockers + next steps only; `full` includes all sections. Default `full`.
- `--cycle <current|all|label>` -- Scope the report. Default `current`.
- `--output <path>` -- Override the output directory (default: `ai/reports/`).
- `--include-velocity` / `--no-velocity` -- Include velocity metrics. Default included.
- `--dry-run` -- Display the report to stdout without writing a file.

## See Also

- No paired skill — `/status-report` is currently spec-only. Follow-up: extract a `claude/skills/status-report/SKILL.md` to mirror other commands. The full execution spec (read tasks, classify, summarize artifacts, identify blockers, compute velocity, gather decisions, generate report) currently lived in this command and has been preserved in the audit notes pending that extraction.
