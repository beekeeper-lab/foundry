---
name: validate-config
description: "Checks configuration hygiene and detects exposed secrets — hardcoded credentials, missing config variables, untracked .env files, and cross-environment inconsistencies."
---

# /validate-config

This command is a thin entry point; the canonical process lives in the
`validate-config` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/validate-config/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
