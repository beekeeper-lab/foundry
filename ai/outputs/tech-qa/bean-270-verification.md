# BEAN-270 Verification Report

| Field | Value |
|-------|-------|
| **Bean** | BEAN-270 — `/spawn-task` Persona-Scoped Delegation Command |
| **Verifier** | Tech-QA |
| **Date** | 2026-04-28 |
| **Branch** | `bean/BEAN-270-spawn-task-command` |
| **Verdict** | **PASS** with manual-test follow-up flagged |

## Bean Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `ai-team-library/claude/skills/spawn-task/SKILL.md` exists with usage, tmux-detection logic, both execution paths, telemetry capture, error conditions | **PASS** | File exists. Headings: `## Description`, `## Trigger`, `## Inputs`, `## Usage`, `## Process` (5 phases + prompt schema), `## Outputs`, `## Quality Criteria`, `## Error Conditions`, `## Dependencies`, `## See Also`. tmux detection rule (Phase 3, step 6) is `[ -n "$TMUX" ]`. |
| 2 | `ai-team-library/claude/commands/spawn-task.md` exists, ≤30 lines, points to skill | **PASS** | `wc -l` → 27 lines. `grep -E '^## (Process\|Error Conditions)'` → no match. File names the skill at `claude/skills/spawn-task/SKILL.md` in the See Also section. |
| 3 | Foundry's own `.claude/skills/spawn-task/` and `.claude/commands/spawn-task.md` are populated via the kit sync | **PASS** | After `scripts/claude-sync.sh`: `.claude/skills/spawn-task` → `../local/skills/spawn-task` (symlink). `.claude/commands/spawn-task.md` → `../local/commands/spawn-task.md` (symlink). Both resolve to real content. |
| 4 | Manual test (in tmux): spawns tmux window, executes the task, updates the status file, task Status flips to `Done` | **MANUAL — pending user verification** | Cannot exercise from this autonomous run. Reproduction: enter tmux session, run `/spawn-task developer ai/beans/BEAN-XXX/tasks/01-developer-foo.md` against any in-flight bean's task, observe child window opens, status file at `/tmp/agentic-task-BEAN-XXX-01-developer-foo.status` is written, task file Status advances. |
| 5 | Manual test (not in tmux): same command issues an `Agent` tool call and Status flips to `Done` | **MANUAL — pending user verification** | Cannot exercise from this autonomous run (claude-code does not expose live `/spawn-task` invocation in the same session that defined it). Reproduction: from a non-tmux Claude Code session, run `/spawn-task <task-file>`. The session should issue one `Agent` tool call with `subagent_type=<persona>` and persist the subagent's summary into the task's Telemetry row. |
| 6 | Reminder banner appears when `/spawn-task` runs outside tmux for a high-priority task | **MANUAL — pending user verification** | Banner content is specified verbatim in `SKILL.md` Phase 3 step 7 and ADR-008 decision 3. Reproduction: outside tmux, run `/spawn-task` against a task file whose metadata has `priority: high` (or whose bean has ≥4 unfinished tasks) — banner string `Tip: tmux + /long-run --fast gives this task an isolated worker context...` should print once. |
| 7 | Team-Lead persona files (library + project) name `/spawn-task` as preferred per-task dispatch | **PASS** | Library: `ai-team-library/personas/team-lead/persona.md` has `## Per-Task Dispatch` section with 2 references to `/spawn-task`. Project: `.claude/agents/team-lead.md` (symlink to kit `bean/BEAN-270-spawn-task` branch) has 1 reference in the Skills & Commands table. |
| 8 | All tests pass | **PASS** | `uv run pytest`: 1937 passed, 4 deprecation warnings (pre-existing Qt boilerplate), 0 failures, 10.87s. |
| 9 | Lint clean | **PASS** | `uv run ruff check foundry_app/`: All checks passed! |

## ADR-008 Verification

ADR-008 in `ai/context/decisions.md` was checked for the three load-bearing decisions:

| Decision Point | Status | Evidence |
|----------------|--------|----------|
| Runtime detection rule | **PASS** | "**1. Runtime detection rule.** `/spawn-task` chooses its execution path from a single environment check: `[ -n "$TMUX" ]`." |
| Agent-tool prompt schema | **PASS** | "**2. Agent-tool prompt schema.** Whichever path runs, the prompt has the same five required sections, in this order:" — followed by a 5-row table (Role / Task file / Inputs / Acceptance / Completion contract). |
| Reminder-banner heuristic | **PASS** | "**3. Reminder-banner heuristic.** ... emits a one-line reminder iff (priority: high) OR (bean has ≥4 remaining tasks)." Banner text is quoted verbatim. |

ADR also explicitly enumerates Out of Scope (no retry, no cross-task state, no `/spawn-bean` replacement, deferred BEAN-272 / BEAN-273 integration) and rejects 5 alternatives.

## /long-run Integration

| Surface | Status | Evidence |
|---------|--------|----------|
| Library `ai-team-library/claude/skills/long-run/SKILL.md` | **PASS** | 4 references to `spawn-task`. Phase 4 has a "Preferred dispatch" preamble naming `/spawn-task` and a fallback paragraph for in-conversation role-switching. Step 12 references both paths. |
| Project `.claude/skills/long-run/SKILL.md` (kit symlink) | **PASS** | 4 references to `spawn-task`. Same Phase 4 update as library, mirrored on the kit's `bean/BEAN-270-spawn-task` branch. |

## Static Checks

| Command | Result |
|---------|--------|
| `wc -l ai-team-library/claude/commands/spawn-task.md` | 27 (≤30 required) |
| `grep -E '^## (Process\|Error Conditions)' ai-team-library/claude/commands/spawn-task.md` | no match (correct — these belong in the skill) |
| `uv run pytest` | 1937 passed, 0 failed |
| `uv run ruff check foundry_app/` | All checks passed |

## Findings & Notes

- **Manual tests (criteria 4, 5, 6) deferred to user verification.** The autonomous `/long-run` cannot itself invoke `/spawn-task` and observe the live behavior; the spec is in place and reproducible. This is not a regression — the bean acceptance explicitly framed these as manual tests.
- **Kit submodule pointer bumped.** Foundry's `.claude/shared` now references commit `b815ede` on the kit's `bean/BEAN-270-spawn-task` branch. This branch is pushed but not merged to kit `main` yet — kit-side merge is part of the kit's normal PR cycle.
- **Foundry local-layer files mirror the library files.** This duplication is intentional under the kit's "local overrides shared on collision; both are merged otherwise" rule. When the kit branch merges to its `main`, a follow-up Foundry PR can move the spawn-task files from `.claude/local/` into the kit (or leave them in local — either works because the local layer is a superset).
- **No Python code changed.** The bean is documentation + skill spec + persona doc work; the `pytest`/`ruff` checks ran defensively per the bean's acceptance criteria but found no impact.

## Verdict

**PASS.** All non-manual acceptance criteria verified. Three manual criteria (the actual `/spawn-task` invocation flows) are clearly enumerated above with reproduction steps for the user to exercise post-merge.
