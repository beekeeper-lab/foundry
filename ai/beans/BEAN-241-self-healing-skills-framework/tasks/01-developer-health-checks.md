# Task 01: Health-Check Framework

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-03-27 11:49 |
| **Completed** | 2026-03-27 14:55 |
| **Duration** | 3h 6m |

## Goal

Create the health-check definition document and `/health-check` skill that detects systemic issues in the project.

## Inputs

- Bean scope from BEAN-241
- `ai/context/bean-workflow.md` — for understanding bean structure
- `.claude/skills/` — for skill structure patterns

## Implementation

1. **Create `ai/context/health-checks.md`** — Define all detectable conditions:
   - Context bloat: CLAUDE.md >500 lines, MEMORY.md >200 lines, agent files >300 lines
   - Telemetry anomalies: Beans with <5K input tokens, beans costing >$15, beans with N/A telemetry
   - Stale artifacts: Memory entries >90 days old, beans stuck In Progress >7 days
   - Cost trends: Average bean cost increasing over trailing 10-bean window

2. **Create `/health-check` skill** at `.claude/local/skills/health-check/SKILL.md`:
   - Runs all checks and produces a table-format report
   - Each check has: name, status (OK/WARN/FAIL), detail
   - Non-interactive — can be called by other skills

3. **Create command** at `.claude/local/commands/health-check.md`:
   - Brief command summary that invokes the skill

4. **Update `/long-run` SKILL.md** to call health checks at the start of each cycle:
   - In interactive mode: print warnings
   - In autonomous mode: auto-create Unapproved beans for FAIL-level issues

5. **Update Team Lead agent** to reference health checks before starting bean batches

## Acceptance Criteria

- [ ] `ai/context/health-checks.md` defines all check categories with thresholds
- [ ] `/health-check` skill exists and produces structured report
- [ ] Context bloat check correctly measures file sizes
- [ ] Telemetry anomaly check identifies beans with suspect data
- [ ] Stale artifact check finds old memory entries and stuck beans
- [ ] `/long-run` calls health checks at start of each cycle
- [ ] Health check report is concise (table format)
- [ ] All tests pass
- [ ] Lint clean

## Definition of Done

- All files created/updated, tests pass, lint clean
