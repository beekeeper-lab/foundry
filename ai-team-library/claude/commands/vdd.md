---
name: vdd
description: "Runs the programmatic Verification-Driven Development gate for a bean. Parses the bean's ## Acceptance Criteria section, dispatches each criterion's evidence type (test, lint, file, file-contains, or manual) to the matching runner, and writes a structured pass/fail report at ai/outputs/tech-qa/vdd-<NNN>.md."
---

# /vdd

This command is a thin entry point; the canonical process lives in the
`vdd` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/vdd/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
