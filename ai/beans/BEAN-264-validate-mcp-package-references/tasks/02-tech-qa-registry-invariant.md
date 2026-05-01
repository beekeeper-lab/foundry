# Task 02: Registry Invariant Tests + Full Regression

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Done |
| **Started** | 2026-04-17 18:20 |
| **Completed** | 2026-04-17 18:20 |
| **Duration** | < 1m |

## Goal

Guarantee that every MCP reference in a generated `mcp.json` exists in
the vetted registry. Catch any future drift at test time.

## Inputs

- `tests/test_mcp_writer.py`
- `foundry_app/services/mcp_writer.py` (already refactored in task 01)
- `ai-team-library/workflows/mcp-registry.yaml`

## Changes Required

1. Update existing tests in `tests/test_mcp_writer.py` to reflect the new
   real package references (e.g. `@modelcontextprotocol/server-filesystem`
   for filesystem, and removal of the docs-server assertions).

2. Add a new invariant test that:
   - Generates an `mcp.json` with representative expertise combinations
     (empty, python, node, react, typescript, multi).
   - Loads the registry YAML directly.
   - Asserts every emitted server name and its `{command, args}` match
     exactly one registry entry.
   - Asserts no server in the output has `@anthropic/` anywhere in its
     args (regression guard against the exact defect this bean fixes).

3. Run full regression:
   - `uv run pytest`
   - `uv run ruff check foundry_app/`

## Acceptance Criteria

- [ ] Tests cover the invariant: generated `mcp.json` has no references
      outside the registry.
- [ ] No test hard-codes `@anthropic/*` as an expected value.
- [ ] `uv run pytest` — all tests pass.
- [ ] `uv run ruff check foundry_app/` — clean.

## Definition of Done

- Invariant test lands and passes.
- Existing tests updated to match new registry contents.
- Full suite green, lint clean.
