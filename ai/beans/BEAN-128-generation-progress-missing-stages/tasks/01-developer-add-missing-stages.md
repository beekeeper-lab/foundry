# Task 01: Add Missing Pipeline Stages to Progress UI

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Status** | Pending |
| **Depends On** | — |

## Goal

Add `agent_writer` and `mcp_config` entries to `PIPELINE_STAGES` in `generation_progress.py` so the progress screen shows all 8 pipeline stages in the correct order.

## Inputs

- `foundry_app/ui/screens/generation_progress.py` — the progress screen with `PIPELINE_STAGES`
- `foundry_app/services/generator.py` — the pipeline that emits stage callbacks

## Acceptance Criteria

- [ ] `PIPELINE_STAGES` contains 8 entries in order: scaffold, compile, agent_writer, copy_assets, mcp_config, seed_tasks, safety, diff_report
- [ ] Stage IDs match the keys used in `_run_stage()` calls in generator.py
- [ ] Labels are descriptive: "Write agent files", "Write MCP config"

## Definition of Done

Code change committed, stage list correct, labels match generator stage keys.
