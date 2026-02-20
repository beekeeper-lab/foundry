# BEAN-169: SOX Compliance Tech Stack

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-169 |
| **Status** | Done |
| **Priority** | Medium |
| **Created** | 2026-02-20 |
| **Started** | 2026-02-20 22:27 |
| **Completed** | 2026-02-20 22:33 |
| **Duration** | 6m |
| **Owner** | (unassigned) |
| **Category** | App |

## Problem Statement

The Foundry library lacks a SOX (Sarbanes-Oxley) compliance tech stack option. Organizations subject to SOX requirements cannot generate projects with SOX-specific compliance guidance.

## Goal

Add a new tech stack option in the ai-team-library for SOX compliance. Include detailed skill items that a sub-agent should know and references where it can find more information to build this skill.

## Scope

### In Scope
- Create SOX compliance tech stack YAML in the library
- Include SOX-specific skills (internal controls, financial reporting, IT general controls, audit trails, etc.)
- Add references to PCAOB standards, SEC guidance, and compliance resources
- Ensure the stack integrates with the existing library indexer

### Out of Scope
- Modifying the library indexer service itself
- Creating a new persona

## Acceptance Criteria

- [ ] SOX compliance tech stack YAML exists in the library
- [ ] Stack includes relevant skills (internal controls, ITGC, segregation of duties, audit trail, etc.)
- [ ] References to authoritative sources are included (PCAOB, SEC, COSO framework)
- [ ] Library indexer can discover and index the new stack
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Create SOX Compliance Tech Stack | Developer | — | Done |
| 2 | Verify SOX Compliance Tech Stack | Tech-QA | 1 | Done |

> Skipped: BA (default), Architect (default — straightforward library addition)

## Changes

| File | Lines |
|------|-------|
| ai-team-library/stacks/sox-compliance/audit-trail.md | +139 |
| ai-team-library/stacks/sox-compliance/internal-controls.md | +122 |
| ai-team-library/stacks/sox-compliance/itgc.md | +162 |
| ai-team-library/stacks/sox-compliance/references.md | +79 |
| ai-team-library/stacks/sox-compliance/segregation-of-duties.md | +128 |
| ai/beans/BEAN-169-sox-tech-stack/bean.md | +27 -13 |
| ai/beans/BEAN-169-sox-tech-stack/tasks/01-developer-create-sox-stack.md | +27 |
| ai/beans/BEAN-169-sox-tech-stack/tasks/02-tech-qa-verify-sox-stack.md | +26 |
| ai/outputs/tech-qa/review-BEAN-169.md | +60 |
| tests/test_library_indexer.py | +1 |

## Notes

(None)

## Trello

| Field | Value |
|-------|-------|
| **Source** | Trello |
| **Board** | Foundry (ID: 698e9e614a5e03d0ed57f638) |
| **Source List** | Sprint_Backlog |
| **Card ID** | 6998499af76185ce5271df17 |
| **Card Name** | SOX Tech Stack |
| **Card URL** | https://trello.com/c/3isAPLjb/39-sox-tech-stack |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Create SOX Compliance Tech Stack | Developer | 5m | 2,050,490 | 7,519 | $6.34 |
| 2 | Verify SOX Compliance Tech Stack | Tech-QA | 1m | 368,624 | 129 | $0.64 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | 2 |
| **Total Duration** | 6m |
| **Total Tokens In** | 2,419,114 |
| **Total Tokens Out** | 7,648 |
| **Total Cost** | $6.98 |