# BEAN-261: Propagate Missing-Expertise Drop to Agent Headers and Member Files

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-261 |
| **Status** | Done |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | 2026-04-17 18:17 |
| **Completed** | 2026-04-17 18:22 |
| **Duration** | 5m (corrected 2026-07) |
| **Owner** | team-lead |
| **Category** | App |

## Problem Statement

BEAN-247 dropped missing-source expertise from the generated `CLAUDE.md`
Tech Stack table, but the drop did not propagate to other generated
artifacts. In a fresh `small-python-team.yml` generation:

- `.claude/agents/<persona>.md` still lists `**Expertise:** python, clean-code`
- `ai/generated/members/<persona>.md` still references `clean-code` in
  the per-agent expertise context
- `ai/team/composition.yml` still includes `clean-code` in the expertise
  list

External review (2026-04-17) called the remaining references "zombie
headers" — the agent sees `clean-code` in its expertise list but no
`clean-code.md` file exists. This is the same class of integrity defect
BEAN-247 addressed, just in adjacent generated files.

## Goal

Any expertise whose source file is missing is dropped consistently from
**every** generated artifact that references it — agent headers, member
compiled prompts, and the composition snapshot — not just `CLAUDE.md`.
The warning is still emitted.

## Scope

### In Scope
- Update the agent writer / persona section compilation to filter the
  expertise list to only expertise whose source was actually emitted.
- Update `ai/generated/members/<persona>.md` expertise-context sections
  the same way.
- Decide whether `ai/team/composition.yml` should record only
  emitted expertise or retain the original spec (ADR-worthy —
  composition.yml is the user's input; auditing what was dropped is also
  valuable).
- Tests: asserting no agent header lists a missing-source expertise when
  the composition includes it.

### Out of Scope
- Changing the "drop vs hard-fail" policy (that was decided in BEAN-247
  — soft drop with warning is the contract).
- Adding new expertise content (BEAN-248 covers `clean-code` content).

## Acceptance Criteria

- [x] Generated `.claude/agents/<persona>.md` headers list only expertise
      whose source file was written.
- [x] Generated `ai/generated/members/<persona>.md` expertise-context
      blocks reference only expertise whose source file was written.
- [x] The decision for `ai/team/composition.yml` (record-as-input vs
      record-as-emitted) is documented in the bean Notes or an ADR.
- [x] Tests cover the agent header and member file invariants.
- [x] All tests pass (`uv run pytest`).
- [x] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Propagate Expertise Drop to Agent Headers and Member Files | Developer | — | Done |
| 2 | Verify Agent Header / Member File Expertise Invariants | Tech-QA | 01 | Done |

> Skipped: BA (default), Architect (default) — scoped propagation fix following BEAN-247 pattern; behavior is fully specified in the bean.

## Changes

| File | Lines |
|------|-------|
| ai/beans/BEAN-261-propagate-expertise-drop-to-agent-headers/bean.md | ~40 |
| ai/beans/BEAN-261-.../tasks/01-developer-propagate-expertise-drop.md | 60 |
| ai/beans/BEAN-261-.../tasks/02-tech-qa-verify-invariants.md | 48 |
| ai/outputs/tech-qa/BEAN-261-verification.md | 72 |
| foundry_app/services/compiler.py | ~45 |
| foundry_app/services/agent_writer.py | ~15 |
| tests/test_compiler.py | 50 |
| tests/test_agent_writer.py | 35 |

## Notes

**Source.** External review (2026-04-17). Follow-up to BEAN-247 after
review noted the CLAUDE.md fix did not propagate to agent headers.

**Related.** BEAN-247 (initial CLAUDE.md drop), BEAN-248 (add missing
`clean-code` content — addresses the root cause but the resilience fix
here is still needed for any future missing-expertise case).

**Decision — composition.yml.** We keep
`ai/team/composition.yml` as the user's unfiltered input spec (record
what was *requested*, not what was *emitted*). Reasons:
- Re-running generation against the snapshot must produce the same
  spec that the user wrote; filtering would silently amend their
  input.
- The missing-source expertise is already surfaced via the warning
  path in `StageResult.warnings` and via the absent
  `ai/generated/expertise/<id>.md` file — so "what was emitted" is
  auditable from the file tree, not from composition.yml.
- composition.yml is the closest thing to a "saved project file";
  users may edit the source expertise and regenerate, at which point
  the spec would produce the correct artifact without needing to be
  re-added.
The drop is therefore scoped to compiled artifacts only (agent
headers, member files, CLAUDE.md).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Propagate Expertise Drop to Agent Headers and Member Files | Developer | < 1m | 1,769,105 | 0 | $3.25 |
| 2 | Verify Agent Header / Member File Expertise Invariants | Tech-QA | < 1m | 2,119,822 | 2,011 | $4.00 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 1m |
| **Total Tokens In** | 3,888,927 |
| **Total Tokens Out** | 2,011 |
| **Total Cost** | $7.25 |