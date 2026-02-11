# BEAN-010: Parallel Long Run (tmux)

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-010 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-07 |
| **Owner** | team-lead |
| **Category** | Process |

## Problem Statement

The `/long-run` command (BEAN-007) processes beans sequentially — one at a time. For projects with many independent beans, this is slow. Users want to run N beans in parallel, each with its own full team, to accelerate backlog processing.

## Goal

Add a `--fast N` flag to `/long-run` (or a separate `/run-fast` command) that spawns N parallel Claude Code instances in tmux child windows, each processing one bean with a full team. The original window's Team Lead orchestrates which beans go to which windows.

## Scope

### In Scope
- `--fast N` flag on `/long-run` (or `/run-fast N` as a separate command)
- tmux detection: check if the current session is running inside tmux
- If not in tmux: instruct the user to restart Claude Code inside tmux, then re-run
- If in tmux: Team Lead spawns N child tmux windows via `tmux split-window` or `tmux new-window`
- Each child window runs `claude` with instructions to process one specific bean
- Each child window operates on its own feature branch (requires BEAN-008)
- Team Lead in the original window monitors progress
- As a child window completes its bean, Team Lead can assign the next bean to it
- Progress reporting in the main window

### Out of Scope
- Merging completed work (that's BEAN-011)
- Non-tmux parallelism (screen, background processes, etc.)
- Dynamic scaling (adding/removing workers mid-run)
- Cross-bean dependency resolution during parallel execution (beans with dependencies are queued, not parallelized)

## Acceptance Criteria

- [ ] `/long-run --fast N` (or `/run-fast N`) spawns N tmux child windows
- [ ] tmux detection works correctly (reports error with instructions if not in tmux)
- [ ] Each child window runs a Claude Code instance with a full team
- [ ] Each child window works on a separate bean on its own feature branch
- [ ] Team Lead in main window assigns beans to available workers
- [ ] Beans with inter-bean dependencies are not assigned in parallel
- [ ] Progress is reported in the main window as beans complete
- [ ] Command/skill format matches existing patterns
- [ ] Team Lead agent updated to reference the parallel capability

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 01 | Create Parallel Long Run Command & Skill | developer | — | Done |
| 02 | Parallel Long Run Verification | tech-qa | 01 | Done |

> BA and Architect skipped — architecture sketch is already in the bean, and this updates existing command/skill markdown.

## Notes

Depends on: BEAN-007 (Long Run Command), BEAN-008 (Feature Branch Workflow).

**Architecture sketch:**
```
┌─────────────────────────────┐
│  Main tmux window           │
│  Team Lead (orchestrator)   │
│  - Reads backlog            │
│  - Assigns beans to workers │
│  - Monitors progress        │
└──────────┬──────────────────┘
           │ spawns N child windows
     ┌─────┼─────┬─────────┐
     ▼     ▼     ▼         ▼
  ┌─────┐┌─────┐┌─────┐┌─────┐
  │Win 1││Win 2││Win 3││Win N│
  │Bean ││Bean ││Bean ││Bean │
  │-008 ││-009 ││-010 ││-012 │
  │on   ││on   ││on   ││on   │
  │feat/││feat/││feat/││feat/│
  │br 1 ││br 2 ││br 3 ││br N │
  └─────┘└─────┘└─────┘└─────┘
```

Each worker window contains: Team Lead (decompose) → BA → Architect → Developer → Tech-QA → Merge Captain. The Merge Captain is the final stage (see BEAN-011).

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out |
|---|------|-------|----------|-----------|------------|
| 1 | All tasks | team-lead | < 1m | — | — |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 1 |
| **Total Duration** | < 1m |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |

> Duration backfilled from git timestamps (single commit, no merge).
