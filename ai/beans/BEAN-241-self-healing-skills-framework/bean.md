# BEAN-241: Self-Healing Skills Framework

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-241 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-03-27 |
| **Started** | 2026-03-27 11:48 |
| **Completed** | 2026-03-27 14:56 |
| **Duration** | 8m |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

Our skills and long-run processes operate in isolation without awareness of systemic health issues. When context windows grow too large, CLAUDE.md accumulates bloat, MEMORY.md exceeds useful size, or telemetry shows anomalous patterns — no one notices until a human reviews manually. In an autonomous team where agents run beans through `/long-run`, problems compound silently: an oversized CLAUDE.md inflates every bean's token cost, a stale memory entry causes repeated mistakes, or a broken telemetry pipeline goes unnoticed for dozens of beans.

Skills should be able to detect these issues, report them, and — when running autonomously — create beans to fix them.

## Goal

A health-check framework that skills can call to detect and respond to systemic issues. When running in conversation, it recommends fixes. When running in `/long-run` isolation, it auto-creates beans for issues that need human review.

## Scope

### In Scope
- Create a health-check module at `ai/context/health-checks.md` that defines detectable conditions and thresholds:
  - **Context bloat:** CLAUDE.md >500 lines, MEMORY.md >200 lines (truncation boundary), agent files >300 lines
  - **Telemetry anomalies:** Beans with <5K input tokens, beans costing >$15, beans with `N/A` telemetry
  - **Stale artifacts:** Memory entries >90 days old without updates, beans stuck "In Progress" >7 days
  - **Cost trends:** Average bean cost increasing over trailing 10-bean window
- Add a `/health-check` skill that runs all checks and produces a report
- Update `/long-run` skill to run health checks at the start of each processing cycle:
  - In interactive mode: print warnings and recommendations
  - In autonomous mode: auto-create `Unapproved` beans via `/internal:new-bean` for issues exceeding thresholds, tagged with `source: health-check`
- Update the Team Lead agent to check health status before starting a new bean batch

### Out of Scope
- Auto-fixing issues (the framework detects and reports, humans approve fixes)
- Monitoring external systems (Trello, Git hosting, etc.)
- Real-time alerting or notifications beyond stderr/console output
- Changes to the telemetry-stamp hook itself (covered by BEAN-235-238)

## Acceptance Criteria

- [ ] `ai/context/health-checks.md` defines all check categories with thresholds
- [ ] `/health-check` skill exists and produces a structured report
- [ ] Context bloat check correctly measures CLAUDE.md, MEMORY.md, and agent file sizes
- [ ] Telemetry anomaly check identifies beans with suspect data
- [ ] Stale artifact check finds old memory entries and stuck beans
- [ ] `/long-run` calls health checks at the start of each cycle
- [ ] In autonomous mode, health issues exceeding thresholds create `Unapproved` beans
- [ ] Auto-created beans have clear problem statements derived from the check results
- [ ] Health check report is concise (table format, not verbose prose)
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Health-Check Framework | Developer | — | Done |
| 2 | Tech-QA Verification | Tech-QA | 01 | Done |

## Changes

> Auto-populated by `/merge-bean` with the git diff summary.

| File | Lines |
|------|-------|
| .claude/local/commands/health-check.md | +14 |
| .claude/local/skills/health-check/SKILL.md | +86 |
| .claude/shared (submodule) | +11 |
| ai/beans/BEAN-241-self-healing-skills-framework/bean.md | +29 -17 |
| ai/beans/BEAN-241-self-healing-skills-framework/tasks/01-developer-health-checks.md | +58 |
| ai/beans/BEAN-241-self-healing-skills-framework/tasks/02-tech-qa-verification.md | +38 |
| ai/beans/_index.md | +1 -1 |
| ai/context/health-checks.md | +88 |

## Notes

This is the "immune system" for the autonomous team. Without it, issues discovered manually (like the telemetry accuracy problems that prompted this bean batch) go undetected for weeks. The framework should be lightweight — a few file-size checks and telemetry scans, not a complex monitoring system.

Example health check output:
```
HEALTH CHECK — 2026-03-27
| Check | Status | Detail |
|-------|--------|--------|
| CLAUDE.md size | WARN | 520 lines (threshold: 500) |
| MEMORY.md size | OK | 180 lines (threshold: 200) |
| Telemetry coverage | WARN | 33/229 beans have data (14%) |
| Suspect telemetry | FAIL | 10 beans with <5K input tokens |
| Stuck beans | OK | 0 beans in-progress >7 days |
| Cost trend | OK | $5.20 avg (trailing 10) |
```

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Health-Check Framework | Developer | 3h 6m | 2,767,953 | 4,503 | $6.06 |
| 2 | Tech-QA Verification | Tech-QA | < 1m | 194,412 | 583 | $0.36 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 3h 6m |
| **Total Tokens In** | 2,962,365 |
| **Total Tokens Out** | 5,086 |
| **Total Cost** | $6.42 |