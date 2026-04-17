# BEAN-261: Propagate Missing-Expertise Drop to Agent Headers and Member Files

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-261 |
| **Status** | Approved |
| **Priority** | High |
| **Created** | 2026-04-17 |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |
| **Owner** | (unassigned) |
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

- [ ] Generated `.claude/agents/<persona>.md` headers list only expertise
      whose source file was written.
- [ ] Generated `ai/generated/members/<persona>.md` expertise-context
      blocks reference only expertise whose source file was written.
- [ ] The decision for `ai/team/composition.yml` (record-as-input vs
      record-as-emitted) is documented in the bean Notes or an ADR.
- [ ] Tests cover the agent header and member file invariants.
- [ ] All tests pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`).

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | | | | Pending |

## Changes

| File | Lines |
|------|-------|
| — | — |

## Notes

**Source.** External review (2026-04-17). Follow-up to BEAN-247 after
review noted the CLAUDE.md fix did not propagate to agent headers.

**Related.** BEAN-247 (initial CLAUDE.md drop), BEAN-248 (add missing
`clean-code` content — addresses the root cause but the resilience fix
here is still needed for any future missing-expertise case).

## Trello

| Field | Value |
|-------|-------|
| **Source** | Manual |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 |      |       |          |           |            |      |

| Metric | Value |
|--------|-------|
| **Total Tasks** | — |
| **Total Duration** | — |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
