---
name: orchestration-report
description: "Aggregates the per-bean Orchestration Telemetry blocks (BEAN-278) across recent Done beans and produces a markdown report answering whether the orchestration changes are paying off. Distinct from /telemetry-report (raw cost/duration/tokens); this command layers orchestration-quality metrics — bounces, persona activations, contract violations, escape-hatch trend, dispatch-mode mix — on top."
---

# /orchestration-report Command

Aggregates the per-bean Orchestration Telemetry blocks (BEAN-278) across
recent Done beans and produces a markdown report answering whether the
orchestration changes are paying off. Distinct from `/telemetry-report`
(raw cost/duration/tokens); this command layers orchestration-quality
metrics — bounces, persona activations, contract violations, escape-hatch
trend, dispatch-mode mix — on top.

## Usage

```
/orchestration-report [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--out PATH] [--include-incomplete]
```

- `--since YYYY-MM-DD` — Lower bound on the bean's Completed date. Default: 30 days ago.
- `--until YYYY-MM-DD` — Upper bound on the bean's Completed date. Default: today.
- `--out PATH` — Override the output file path. Default: `ai/outputs/team-lead/orchestration-report-YYYY-MM-DD.md`.
- `--include-incomplete` — Include beans with a partly-populated Orchestration Telemetry block.

## See Also

- Skill: `claude/skills/orchestration-report/SKILL.md` — canonical execution spec.
- Companion: `/telemetry-report` — raw cost/duration/token aggregations.
- BEAN-278 — bean spec defining the Orchestration Telemetry layer.
