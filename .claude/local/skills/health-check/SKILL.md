# Skill: Health Check

## Description

Runs all health checks defined in `ai/context/health-checks.md` and produces a table-format report. Can be called standalone or by other skills (e.g., `/long-run`).

## Trigger

- Invoked by the `/health-check` slash command.
- Called programmatically by `/long-run` at the start of each cycle.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| health_checks | Markdown file | Yes | `ai/context/health-checks.md` — check definitions |
| mode | String | No | `interactive` (default) or `autonomous`. In autonomous mode, FAIL-level checks create Unapproved beans. |

## Process

### Phase 1: Context Bloat Checks

1. **CLAUDE.md size** — Count lines in `CLAUDE.md` and `.claude/shared/CLAUDE.md`. Sum them. Threshold: 500 lines.
2. **MEMORY.md size** — Count lines in the project memory's `MEMORY.md`. Threshold: 200 lines.
3. **Agent file sizes** — Count lines in each `.claude/agents/*.md`. Threshold: 300 lines each.
4. **Bean workflow size** — Count lines in `ai/context/bean-workflow.md`. Threshold: 600 lines.

### Phase 2: Telemetry Anomaly Checks

5. **Parse recent Done beans** — Read `ai/beans/_index.md`. For each Done bean, read its `bean.md` Telemetry summary section.
6. **Low token check** — Flag beans with `Total Tokens In` < 5,000.
7. **High cost check** — Flag beans with `Total Cost` > $15.
8. **Missing telemetry** — Flag Done beans where all telemetry summary fields are sentinel (`—`).
9. **Zero duration anomaly** — Flag Done beans with `Duration` = "< 1m" but >5 tasks.

### Phase 3: Stale Artifact Checks

10. **Old memory entries** — Check modification dates of files in the project memory directory. Flag files >90 days old.
11. **Stuck beans** — Flag beans with status "In Progress" where Started date is >7 days ago.
12. **Orphaned worktrees** — Check for `/tmp/foundry-worktree-*` directories.
13. **Stale status files** — Check for `/tmp/foundry-worker-*.status` files.

### Phase 4: Cost Trend Checks

14. **Compute trailing averages** — From the last 20 Done beans with valid cost data, compute:
    - Last 10-bean average cost
    - Previous 10-bean average cost
15. **Increasing cost trend** — Flag if current average is >50% higher than previous.
16. **High average cost** — Flag if current 10-bean average > $10.

### Phase 5: Report

17. **Render report** — Print a table with columns: Check, Status (OK/WARN/FAIL), Detail.
18. **Auto-bean creation (autonomous mode only)** — For each FAIL-level check:
    - Create an Unapproved bean via `/internal:new-bean`
    - Problem statement = check detail
    - Notes include `source: health-check`
    - Do NOT auto-approve

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| report | Console text | Table-format health check report |
| beans | Markdown files | (Autonomous mode only) Unapproved beans for FAIL-level issues |

## Quality Criteria

- All checks produce a deterministic result (OK, WARN, or FAIL) with detail.
- Report is concise — one row per check.
- No false positives for newly created beans (exclude In Progress beans < 1 day old from stuck check).
- Autonomous bean creation is conservative (FAIL only, never auto-approve).

## Error Conditions

| Error | Cause | Resolution |
|-------|-------|------------|
| `NoBeanIndex` | `_index.md` not found | Report error and skip telemetry/stale checks |
| `ParseError` | Bean telemetry section malformed | Log warning, skip that bean, continue |

## Dependencies

- `ai/context/health-checks.md` — check definitions and thresholds
- `ai/beans/_index.md` — bean index for telemetry and stale checks
- Individual bean files for telemetry data
- Project memory directory for stale memory checks
