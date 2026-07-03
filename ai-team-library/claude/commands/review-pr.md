---
name: review-pr
description: "Performs a structured, checklist-driven code review covering readability, correctness, maintainability, convention consistency, test coverage, and security. Produces a clear verdict (ship / ship with comments / request changes) with actionable line-level feedback."
---

# /review-pr Command

Performs a structured, checklist-driven code review covering readability, correctness, maintainability, convention consistency, test coverage, and security. Produces a clear verdict (ship / ship with comments / request changes) with actionable line-level feedback.

## Usage

```
/review-pr [diff-or-pr] [--skip-checks] [--checklist <path>] [--output <path>] [--self-review] [--security-only]
```

- `diff-or-pr` -- A diff file, directory of changed files, PR number, or PR URL. Defaults to the current branch's uncommitted changes.
- `--skip-checks` -- Skip test and lint prerequisite checks.
- `--checklist <path>` -- Custom review checklist.
- `--output <path>` -- Override the output directory (default: `ai/outputs/code-quality-reviewer/`).
- `--self-review` -- Self-review mode: same rigor, author-facing language.
- `--security-only` -- Only run the security checks.

## See Also

- Skill: `claude/skills/review-pr/SKILL.md` — canonical execution spec.
