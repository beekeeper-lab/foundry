# Health Checks

Detectable conditions and thresholds for the self-healing framework. The `/health-check` skill runs these checks and produces a structured report.

## Check Categories

### 1. Context Bloat

Files that contribute to every agent's context window. Oversized files inflate per-bean token costs.

| Check | Threshold | Severity |
|-------|-----------|----------|
| `CLAUDE.md` line count | >500 lines (combined project + shared) | WARN |
| `MEMORY.md` line count | >200 lines (truncation boundary) | WARN |
| Agent files (`.claude/agents/*.md`) | >300 lines each | WARN |
| `ai/context/bean-workflow.md` | >600 lines | WARN |

**How to check:** Count lines with `wc -l`. Sum project CLAUDE.md + shared CLAUDE.md for combined count.

### 2. Telemetry Anomalies

Beans with telemetry data that suggests measurement errors.

| Check | Threshold | Severity |
|-------|-----------|----------|
| Impossibly low tokens | Bean with <5,000 total input tokens | FAIL |
| Excessive cost | Bean costing >$15 | WARN |
| Missing telemetry | Done bean with all-sentinel telemetry fields | WARN |
| Zero duration | Done bean with Duration = "< 1m" but >5 tasks | WARN |

**How to check:** Parse bean.md Telemetry summary tables. Look for `Total Tokens In`, `Total Cost`, and `Total Duration` fields.

### 3. Stale Artifacts

Outdated items that accumulate over time.

| Check | Threshold | Severity |
|-------|-----------|----------|
| Old memory entries | Memory file >90 days without update | WARN |
| Stuck beans | Bean with status "In Progress" for >7 days | FAIL |
| Orphaned worktrees | `/tmp/foundry-worktree-*` directories | WARN |
| Stale status files | `/tmp/foundry-worker-*.status` files | WARN |

**How to check:** For memory entries, check file modification times. For stuck beans, compare Started timestamp to current date. For worktrees/status files, check if `/tmp` files exist.

### 4. Cost Trends

Aggregate metrics that indicate systemic issues.

| Check | Threshold | Severity |
|-------|-----------|----------|
| Avg bean cost increasing | Trailing 10-bean average > previous 10-bean average by >50% | WARN |
| High average cost | Trailing 10-bean average > $10 | WARN |

**How to check:** Parse the last 20 Done beans' `Total Cost` fields, compute trailing averages.

## Report Format

```
HEALTH CHECK — YYYY-MM-DD
| Check | Status | Detail |
|-------|--------|--------|
| CLAUDE.md size | OK | 179 lines (threshold: 500) |
| MEMORY.md size | OK | 180 lines (threshold: 200) |
| Agent files | OK | max 288 lines (threshold: 300) |
| Telemetry anomalies | WARN | 3 beans with <5K input tokens |
| Stuck beans | OK | 0 beans in-progress >7 days |
| Cost trend | OK | $6.50 avg (trailing 10) |
```

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **OK** | Within threshold | No action needed |
| **WARN** | Approaching or at threshold | Report to user; in autonomous mode, log warning |
| **FAIL** | Exceeds threshold significantly | Report to user; in autonomous mode, create Unapproved bean |

## Auto-Bean Creation

When running in `/long-run` autonomous mode and a FAIL-level check is detected:

1. Create an `Unapproved` bean via `/internal:new-bean`
2. Set the bean's Problem Statement to the check detail
3. Tag the Notes with `source: health-check`
4. Do NOT auto-approve — the user must review and approve

WARN-level checks are logged but do not create beans.
