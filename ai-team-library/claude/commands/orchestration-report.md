---
name: orchestration-report
description: "Aggregates the per-bean Orchestration Telemetry blocks (BEAN-278) across recent Done beans and produces a markdown report answering whether the orchestration changes are paying off. Distinct from /telemetry-report (raw cost/duration/tokens); this command layers orchestration-quality metrics — bounces, persona activations, contract violations, escape-hatch trend, dispatch-mode mix — on top."
---

# /orchestration-report

This command is a thin entry point; the canonical process lives in the
`orchestration-report` skill — single source of truth (SPEC-023). The two used to be
maintained as parallel prose copies and drifted.

Read `.claude/skills/orchestration-report/SKILL.md` and execute its process with these arguments:

$ARGUMENTS
