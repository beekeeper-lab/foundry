# Team Lead Communication Template

Structured output format for Team Lead sessions. Designed to be instantly scannable in a tmux pane at ~100 columns.

---

## Section 1: Header Block

Printed once when a bean is picked. Re-printed every time the task table is updated.

```
===================================================
BEAN-014 | Team Lead Progress Dashboard
---------------------------------------------------
Add structured output template so tmux panes are
instantly scannable during bean processing.
===================================================
```

**Rules:**
- Line 1: `===` separator (51 chars)
- Line 2: Bean ID + `|` + Title (truncate title at 40 chars if needed)
- Line 3: `---` separator
- Lines 4-5: 1-2 sentence summary of what this bean does (wrap at 51 chars)
- Line 6: `===` separator
- Always appears at the top of output, above the task table

---

## Section 2: Task Progress Table

Printed immediately after the header. Re-printed whenever any task's status changes.

```
 #  Task                          Owner       Status
--- ------------------------------ ----------- -----------
 01 Design communication template  team-lead   >> Active
 02 Update team-lead agent         developer   Pending
 03 Update long-run skill          developer   Pending
 04 Template verification          tech-qa     Pending
```

**Column widths (total ~100 chars):**

| Column | Width | Alignment |
|--------|-------|-----------|
| # | 3 | Right |
| Task | 30 | Left (truncate with `...` if longer) |
| Owner | 11 | Left |
| Status | 11 | Left |

**Status values:**

| Status | Display | Meaning |
|--------|---------|---------|
| Pending | `Pending` | Not yet started |
| Active | `>> Active` | Currently being worked on (the `>>` draws the eye) |
| Done | `Done` | Completed successfully |
| Skipped | `Skipped` | Role not needed for this bean |
| Failed | `!! Failed` | Could not complete |

**Re-presentation rules:**
- Reprint header + table whenever a task moves to a new status
- Reprint after every 20 lines of work narration (so scrolling back isn't needed)
- Always reprint before asking the user a question

---

## Section 3: Work Log

Scrolls below the header + table. This is where per-task narration goes.

```
[01:team-lead] Designing communication template...
[01:team-lead] Template written to ai/outputs/team-lead/...
[01:team-lead] Done.

[02:developer] Reading team-lead agent...
[02:developer] Adding template spec to agent...
[02:developer] Done.
```

**Rules:**
- Each line prefixed with `[NN:owner]` so it's clear which task produced it
- Keep narration minimal — 2-5 lines per task, not a play-by-play
- Save detailed output for the actual output files, not the console
- Never let work log text appear above the header + table

---

## Section 4: Completion Summary

Printed once when all tasks are done, just before commit/merge handoff.

```
===================================================
BEAN-014 | DONE
===================================================
Tasks: 4 total, 4 done, 0 failed
Branch: bean/BEAN-014-team-lead-progress-dashboard

Changes:
  - .claude/agents/team-lead.md (updated)
  - .claude/skills/long-run/SKILL.md (updated)
  - ai/outputs/team-lead/bean-014-communication-template.md (new)

Notes:
  Template adds structured header + task table to
  Team Lead output. Works in sequential and parallel
  modes.

Ready for: commit + merge captain
===================================================
```

**Rules:**
- Header: bean ID + `DONE`
- Tasks line: total/done/failed counts
- Branch: feature branch name
- Changes: list of files modified or created (keep brief)
- Notes: 2-3 sentences on what was accomplished, any decisions made
- Ready for: what happens next (commit, merge, manual action)
- This is what the merge captain reads to understand the bean

---

## Output Ordering

The screen should read top-to-bottom as:

1. **Header Block** (fixed — reprinted on updates)
2. **Task Progress Table** (fixed — reprinted on updates)
3. **Work Log** (scrolling — grows downward)
4. **Prompts/Questions** (only when user input needed, always at bottom)

The user should be able to glance at lines 1-8 of any tmux pane and know: which bean, which tasks, what's active.

---

## Width Constraint

All template elements fit within 100 columns. The separator lines are 51 chars. The task table is ~57 chars. No element exceeds 100 chars per line.
