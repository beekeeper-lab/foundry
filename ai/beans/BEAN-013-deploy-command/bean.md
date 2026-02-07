# BEAN-013: Deploy Command

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-013 |
| **Status** | New |
| **Priority** | Low |
| **Created** | 2026-02-07 |
| **Owner** | (unassigned) |

## Problem Statement

There is no defined process for promoting work from the `test` integration branch to `main`. After beans are completed and merged to `test`, someone needs to review the accumulated changes, verify quality, and merge to `main`. This should be a deliberate, gated process — not an ad-hoc git merge.

## Goal

Create a `/deploy` command that safely promotes `test` → `main` with a full quality gate: run tests, code quality review, security review, generate release notes summarizing all included beans, and present to the user for approval before executing the merge.

## Scope

### In Scope
- `/deploy` command and skill
- Pre-merge quality gate:
  - Run full test suite against `test` branch
  - Code quality review (using code-quality-reviewer persona)
  - Security review (using security-engineer persona)
  - All reviews produce written reports in `ai/outputs/`
- Release notes generation:
  - Identify all beans merged to `test` since the last deploy to `main`
  - Summarize each bean (title, what changed, files affected)
  - Generate a concise release summary
- User approval gate:
  - Present the release notes, review summaries, and test results
  - Wait for explicit user "go" before merging
- Safe merge: `test` → `main` with `--no-ff`, then push
- Post-merge: tag the release (optional, if user wants versioning)

### Out of Scope
- CI/CD pipeline triggers
- Automated deployment to environments
- Rollback mechanisms
- Version bumping in source files
- Changelog file generation (the release notes are console output, not committed)

## Acceptance Criteria

- [ ] `/deploy` command and skill created
- [ ] Tests run against `test` branch before merge
- [ ] Code quality review performed by code-quality-reviewer persona
- [ ] Security review performed by security-engineer persona
- [ ] Release notes generated listing all beans since last deploy
- [ ] User presented with summary and asked for explicit approval
- [ ] Merge only proceeds after user says "go"
- [ ] Safe merge: `test` → `main` with `--no-ff`, push to remote
- [ ] Command/skill format matches existing patterns
- [ ] Team Lead agent updated with `/deploy` reference

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| | | | | |

> Tasks are populated by the Team Lead during decomposition.
> Task files go in `tasks/` subdirectory.

## Notes

Depends on: BEAN-012 (Enforce Feature Branch Workflow).

The `/deploy` process is deliberately separate from the bean lifecycle. Beans flow: feature branch → `test`. Deploys flow: `test` → `main`. The user controls when deploys happen — they are not automatic.

**Quality gate personas:**
- **code-quality-reviewer** — Reviews code style, patterns, complexity, maintainability
- **security-engineer** — Reviews for vulnerabilities, OWASP top 10, secrets exposure
- Both produce reports in `ai/outputs/<persona>/`

**Release notes format:**
```
Release: test → main
Date: YYYY-MM-DD
Beans included:
  - BEAN-012: Enforce Feature Branch Workflow
  - BEAN-013: Deploy Command
  - BEAN-014: ...

Summary:
  <2-3 sentence high-level summary>

Reviews:
  Code Quality: PASS (see ai/outputs/code-quality-reviewer/deploy-YYYY-MM-DD.md)
  Security: PASS (see ai/outputs/security-engineer/deploy-YYYY-MM-DD.md)
  Tests: 248 passed, 0 failed
```
