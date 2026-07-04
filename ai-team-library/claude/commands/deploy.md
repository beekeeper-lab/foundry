---
name: deploy
description: "Validates the main branch, runs tests, and creates a version tag. With trunk-based development, all work is already on main via feature branch merges — deploy simply tags a release point."
---

# /deploy

This command is a thin entry point; the canonical process lives in the
`deploy` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/deploy/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
