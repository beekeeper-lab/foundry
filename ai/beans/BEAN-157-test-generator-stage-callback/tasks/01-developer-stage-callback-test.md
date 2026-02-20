# Task 01: Implement Stage Callback Contract Test

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | 2026-02-19 21:42 |
| **Completed** | 2026-02-19 21:43 |
| **Duration** | 1m |

## Goal

Add a test class `TestStageCallback` in `tests/test_generator.py` that exercises the `stage_callback` parameter of `generate_project()`, verifying the callback contract (invocation count, stage keys, and payload shape).

## Inputs

- `foundry_app/services/generator.py` — the `_run_pipeline` function and `StageCallback` type alias
- `tests/test_generator.py` — existing test patterns, helpers (`_make_spec`, `_make_library_dir`)

## Acceptance Criteria

- [ ] Test passes a mock callback to `generate_project()` and runs the pipeline
- [ ] Test asserts callback fires twice per stage ("running" + "done")
- [ ] Test asserts stage keys match expected stages (scaffold, compile, agent_writer, copy_assets, mcp_config, safety)
- [ ] Test asserts `file_count` on "done" payloads is a non-negative int
- [ ] Test asserts `file_count` on "running" payloads is 0
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)

## Definition of Done

Test class added and all assertions pass. Test follows existing patterns in the file.
