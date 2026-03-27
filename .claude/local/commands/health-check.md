# /health-check Command

Runs the project health-check suite and produces a table-format report. Detects context bloat, telemetry anomalies, stale artifacts, and cost trends.

## Usage

```
/health-check
/health-check --mode autonomous
```

In autonomous mode (used by `/long-run`), FAIL-level checks auto-create Unapproved beans.

See `.claude/local/skills/health-check/SKILL.md` for the full process specification.
