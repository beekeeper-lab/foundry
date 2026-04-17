# Task 02: Verify Agent Header / Member File Expertise Invariants

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Verify that the BEAN-261 developer work fully propagates the
missing-expertise drop to agent headers and member files, and that no
regressions exist in the compiler / agent-writer surface.

## Inputs

- Developer task 01 output (compiler + agent_writer changes)
- `tests/test_compiler.py`, `tests/test_agent_writer.py`
- `foundry_app/services/compiler.py`, `foundry_app/services/agent_writer.py`

## Verification Steps

1. Run the full test suite: `uv run pytest`.
2. Run the linter: `uv run ruff check foundry_app/`.
3. Spot-check the new tests — confirm they actually cover the agent
   header and member file invariants (not just CLAUDE.md).
4. Confirm the composition.yml decision is documented in the bean Notes.
5. Write a short verification note under `ai/outputs/tech-qa/`.

## Acceptance Criteria

- [ ] `uv run pytest` — all tests pass (no regressions).
- [ ] `uv run ruff check foundry_app/` — clean.
- [ ] New tests assert the agent-header invariant.
- [ ] New tests assert the member-file invariant.
- [ ] composition.yml decision documented in bean Notes.
- [ ] Verification note written.

## Definition of Done

- Full test suite green.
- Lint clean.
- Tech-QA verification note recorded.
