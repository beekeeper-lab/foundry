# Task 03: Update Telemetry Stamp Hook to Write Cost Column

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 01 |
| **Status** | Done |
| **Started** | 2026-02-16 01:03 |
| **Completed** | 2026-02-16 01:03 |
| **Duration** | < 1m |

## Goal

Update `telemetry-stamp.py` to compute and write the Cost column when recording task telemetry in bean.md files.

## Work Items

1. Add a function to read rates from `ai/context/token-pricing.md`
2. Add a `compute_cost()` function: `(tokens_in * input_rate) + (tokens_out * output_rate)`
3. Add a `format_cost()` function: `$X.XX` or `< $0.01`
4. Update telemetry table row format to include 7 columns (add Cost)
5. Update `sync_telemetry_table()` to include Cost column (sentinel value)
6. Update `handle_task_file()` to compute and write Cost when writing tokens
7. Add `sum_telemetry_costs()` for the Total Cost summary field
8. Update `handle_bean_file()` to fill Total Cost on Done

## Acceptance Criteria

- [ ] Pricing is read from config file, not hardcoded
- [ ] Cost is computed when token data is written
- [ ] Total Cost is summed from per-task costs on bean Done
- [ ] Existing telemetry functionality is not broken
- [ ] Lint clean
