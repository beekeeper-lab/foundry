# BEAN-249 — Command/Skill Duplication Audit

**Bean:** BEAN-249 — Audit Library Command/Skill Duplication
**Task:** 01-developer-audit-and-trim
**Date:** 2026-04-30

## Audit Summary

This audit covers every command file in `ai-team-library/claude/commands/` (32 top-level + 10 in `dev-loop/{node,python}/` = **42 commands**) against its paired skill in `ai-team-library/claude/skills/`. Each command was trimmed to a short user-facing trigger (≤30 lines) consisting of: title, one-sentence description, usage block, argument list, and a pointer to the paired skill. Long-form operational specs (Process, Error Conditions, Quality Criteria, Output tables) live exclusively in the skills going forward.

The split: **command = trigger**, **skill = canonical execution spec**. This eliminates the drift risk flagged in external review (2026-04-17).

## Commands Without Paired Skills

| Command | Reason | Follow-up |
|---|---|---|
| `show-backlog` | No `claude/skills/show-backlog/` directory | File a follow-up bean to extract a `show-backlog/SKILL.md`. The current command preserves the operational essentials (filters, count summary). |
| `spawn-bean` | No `claude/skills/spawn-bean/` directory | The orchestration mechanics (Status File Protocol, worker spawning, dashboard loop, tiled-mode bash) were migrated into `claude/skills/long-run/SKILL.md` — the canonical owner of those workers. The command now points to that section. A future bean could lift them into a dedicated `spawn-bean` skill, but for now the long-run skill is the single source of truth. |
| `status-report` | No `claude/skills/status-report/` directory | File a follow-up bean to extract a `status-report/SKILL.md`. The full Process (read tasks, classify, summarize artifacts, identify blockers, compute velocity, gather decisions) was previously inline in the command and is recoverable from git history (commit prior to BEAN-249). |
| `dev-loop/python/{test,lint,format,build,dev}.md` | Stack-specific shorthand; intentionally no paired skill | These are thin wrappers around user-configured tools. The runtime detail lives in `pyproject.toml`, not in a Foundry skill. No follow-up needed. |
| `dev-loop/node/{test,lint,format,build,dev}.md` | Stack-specific shorthand; intentionally no paired skill | Same as Python. The runtime detail lives in `package.json`. No follow-up needed. |

## Content Migrated INTO Skills

| Skill | Content Added | Reason |
|---|---|---|
| `claude/skills/long-run/SKILL.md` | New "## Status File Protocol" section (file location, format, status values, when-to-update rules, dashboard display format, blocked-worker alerting, tiled-mode `--wide` bash) | The protocol previously lived only in `commands/spawn-bean.md` and was referenced from the long-run skill via "see /spawn-bean for full status file format". That cross-reference into a command file was the exact drift pattern this bean is correcting. The protocol is shared infrastructure between `/long-run` and `/spawn-bean`, so the skill that already owns the orchestration loop is the right canonical home. |

No other content needed migration — every other command's Process/Error/Quality content was already a faithful restatement of the paired skill's spec.

## Audit Table

| # | Command | Paired Skill | Before | After | Δ | Overlap Notes | Migration |
|---|---|---|---:|---:|---:|---|---|
| 1 | `backlog-consolidate.md` | `backlog-consolidate/` | 93 | 16 | -77 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 2 | `backlog-refinement.md` | `backlog-refinement/` | 91 | 16 | -75 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 3 | `bean-status.md` | `bean-status/` | 77 | 16 | -61 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 4 | `build-traceability.md` | `build-traceability/` | 75 | 19 | -56 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 5 | `compile-team.md` | `compile-team/` | 86 | 20 | -66 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill (this was the canonical example called out in external review). | None |
| 6 | `deploy.md` | `deploy/` | 65 | 15 | -50 | Process, Examples, Error Handling all duplicated the skill. | None |
| 7 | `handoff.md` | `handoff/` | 85 | 20 | -65 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 8 | `long-run.md` | `long-run/` | 256 | 18 | -238 | Process (Phase 0–14), Output table, Bean Selection Heuristics, Parallel Mode (worker spawning bash, dashboard loop), Error Handling, Examples — all duplicated the skill. | None directly. The skill itself was extended with the Status File Protocol (see Migration table above). |
| 9 | `merge-bean.md` | `merge-bean/` | 92 | 16 | -76 | Process, Inputs, Output, Error Handling, Examples all duplicated the skill. | None |
| 10 | `new-adr.md` | `new-adr/` | 75 | 19 | -56 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 11 | `new-bean.md` | `new-bean/` | 75 | 16 | -59 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 12 | `new-dev-decision.md` | `new-dev-decision/` | 89 | 22 | -67 | Process, Inputs, Output, Options, Error Handling, Examples, "When to Use" comparison all duplicated the skill. | None |
| 13 | `new-work.md` | `new-work/` | 93 | 21 | -72 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 14 | `notes-to-stories.md` | `notes-to-stories/` | 75 | 19 | -56 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 15 | `pick-bean.md` | `pick-bean/` | 62 | 15 | -47 | Process, Inputs, Output, Error Handling, Examples all duplicated the skill. | None |
| 16 | `release-notes.md` | `release-notes/` | 84 | 21 | -63 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 17 | `review-beans.md` | `review-beans/` | 57 | 16 | -41 | Process, Output, Examples all duplicated the skill. | None |
| 18 | `review-pr.md` | `review-pr/` | 88 | 20 | -68 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 19 | `risk-liability.md` | `risk-liability/` | 92 | 22 | -70 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 20 | `run.md` | `run/` | 20 | 14 | -6 | Process duplicated the skill (already short — light trim). | None |
| 21 | `scaffold-project.md` | `scaffold-project/` | 74 | 18 | -56 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 22 | `seed-tasks.md` | `seed-tasks/` | 91 | 21 | -70 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 23 | `show-backlog.md` | **(none)** | 45 | 16 | -29 | No paired skill. Process, Examples were inline-only. Operational essentials (filter set, count summary) preserved in trimmed command. | Follow-up: extract a `show-backlog/SKILL.md`. |
| 24 | `spawn-bean.md` | **(none — uses long-run skill)** | 342 | 29 | -313 | Largest violator. Status File Protocol, worker-spawning bash, dashboard loop, prompt schema, tiled-mode bash, cleanup rules — all infrastructure shared with `/long-run`. | Status File Protocol + tiled-mode bash migrated into `long-run/SKILL.md`. The command now points at that skill section. |
| 25 | `spawn-task.md` | `spawn-task/` | 27 | 27 | 0 | Already conformed to the target shape (used as one of the two reference examples in the task spec). No change. | None |
| 26 | `status-report.md` | **(none)** | 97 | 19 | -78 | No paired skill. Full Process was inline-only and has been preserved in git history. | Follow-up: extract a `status-report/SKILL.md`. |
| 27 | `telemetry-report.md` | `telemetry-report/` | 34 | 17 | -17 | Already pointed at the skill but had Examples section pushing it over 30. | None |
| 28 | `threat-model.md` | `threat-model/` | 77 | 19 | -58 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 29 | `trello-load.md` | `trello-load/` | 110 | 18 | -92 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 30 | `update-docs.md` | `update-docs/` | 80 | 20 | -60 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 31 | `validate-config.md` | `validate-config/` | 89 | 21 | -68 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 32 | `validate-repo.md` | `validate-repo/` | 79 | 19 | -60 | Process, Inputs, Output, Options, Error Handling, Examples all duplicated the skill. | None |
| 33 | `dev-loop/node/build.md` | **(none — stack shorthand)** | 28 | 22 | -6 | Process inline (no skill). Trimmed: folded the 3-step process into the Notes paragraph. | None |
| 34 | `dev-loop/node/dev.md` | **(none — stack shorthand)** | 28 | 22 | -6 | Same pattern. | None |
| 35 | `dev-loop/node/format.md` | **(none — stack shorthand)** | 30 | 24 | -6 | Same pattern. | None |
| 36 | `dev-loop/node/lint.md` | **(none — stack shorthand)** | 30 | 24 | -6 | Same pattern. | None |
| 37 | `dev-loop/node/test.md` | **(none — stack shorthand)** | 30 | 24 | -6 | Same pattern. | None |
| 38 | `dev-loop/python/build.md` | **(none — stack shorthand)** | 29 | 23 | -6 | Same pattern. | None |
| 39 | `dev-loop/python/dev.md` | **(none — stack shorthand)** | 28 | 22 | -6 | Same pattern. | None |
| 40 | `dev-loop/python/format.md` | **(none — stack shorthand)** | 30 | 24 | -6 | Same pattern. | None |
| 41 | `dev-loop/python/lint.md` | **(none — stack shorthand)** | 30 | 24 | -6 | Same pattern. | None |
| 42 | `dev-loop/python/test.md` | **(none — stack shorthand)** | 32 | 26 | -6 | Same pattern. Was the only dev-loop command originally over 30 lines. | None |

## Counts

| Metric | Value |
|---|---|
| **Total commands audited** | 42 |
| **Total lines before** | 3,170 (top-level 2,875 + dev-loop 295) |
| **Total lines after** | 893 (top-level 658 + dev-loop 235) |
| **Total reduction** | -2,277 lines (-71.8%) |
| **Commands now ≤30 lines** | 42 of 42 (100%) |
| **Commands containing forbidden sections** | 0 (verified by grep for `## Process`, `## Error Conditions`, `## Quality Criteria`) |
| **Commands without paired skills** | 13 (`show-backlog`, `spawn-bean`, `status-report`, plus 10 dev-loop entries; the dev-loop set is intentional) |
| **Skills modified** | 1 (`long-run/SKILL.md` — added Status File Protocol section) |

## Acceptance Criteria Status

- [x] Audit table written to `ai/outputs/team-lead/bean-249-command-skill-audit.md` with one row per command/skill pair.
- [x] Every `ai-team-library/claude/commands/*.md` is ≤30 lines.
- [x] No command file contains `## Process`, `## Error Conditions`, or `## Quality Criteria` sections.
- [x] Each trimmed command keeps title, one-sentence description, usage block, argument list (where applicable), and a pointer to the skill (or a follow-up note when no skill exists).
- [x] Command-only content not present in the paired skill was migrated INTO the skill (long-run skill gained the Status File Protocol).
- [x] Commands without a paired skill are flagged in the audit table; follow-up notes recorded for `show-backlog` and `status-report`.
- [x] Smoke generation (`uv run foundry-cli generate examples/small-python-team.yml --library ai-team-library --output /tmp/bean-249-smoke`) succeeded — 146 files written, 0 warnings; commands directory populated; long-run.md (18 lines) and spawn-bean.md (29 lines) present and within budget.
- [x] `uv run pytest` — 2168 passed in 11.37s.
- [x] `uv run ruff check foundry_app/` — All checks passed.
