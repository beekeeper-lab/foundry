# Task 01: Implement `validate-task-inputs` Hook + Tests + Doc Updates

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-04-29 10:52 |
| **Completed** | 2026-04-29 10:57 |
| **Duration** | 5m |

## Goal

Build the validate-task-inputs hook in both the library
(`ai-team-library/claude/hooks/`) and the kit
(`.claude/shared/hooks/`) following the project's existing
PostToolUse-style hook conventions. The hook reads a target task file when
that task transitions to `In Progress` and rejects the dispatch when the
task's `Inputs:` field is missing, empty, or contains only sentinel /
placeholder values. Add the loose-mode escape hatch
`Inputs: NONE (justified: <reason ≥10 chars>)`.

Wire the hook into the library's `claude/settings.json` so generated
projects pick it up. Update the bean template and Team-Lead persona so
the discipline is documented at the source. Cover the validator with
pytest tests (good / bad / escape-hatch).

## Inputs

- `ai/beans/BEAN-272-validate-task-inputs-hook/bean.md` — full scope and acceptance criteria
- `.claude/shared/hooks/telemetry-stamp.py` — existing hook conventions (argv shape, exit codes, JSON envelope handling)
- `ai-team-library/claude/skills/spawn-task/SKILL.md` — Phase 2 integration point (BEAN-270)
- `ai-team-library/claude/settings.json` — hook registration site (or `.claude/shared/settings.json` if that's the registration site)
- `.claude/shared/settings.json` — kit hook registration
- `ai/beans/_bean-template.md` — task subsection example to update
- `ai-team-library/personas/team-lead/persona.md` — task-seeding guidance
- `tests/` — directory for the validator's pytest tests

## Changes Required

1. **Hook script** at `ai-team-library/claude/hooks/validate-task-inputs.py`:
   - Read the target task file path from the hook's input envelope.
   - Parse the `## Inputs` section: take all bullet lines until the next
     `^## ` heading or EOF.
   - Failure conditions: heading missing, no bullets, all bullets are the
     em-dash sentinel `—`, or all bullets are empty after strip.
   - Escape hatch: a single line matching `Inputs: NONE (justified: <reason>)`
     where `<reason>` is ≥ 10 non-whitespace characters → pass.
   - On failure: print a remediation message naming the task file and the
     expected format; exit non-zero (block the dispatch).
   - On pass: exit 0.
   - File header comment + 1-line module docstring; no inline narration.
2. **Mirror to kit** at `.claude/shared/hooks/validate-task-inputs.py`
   (identical content; the kit's submodule is the local execution copy).
3. **Settings registration** — add a PreToolUse hook entry in the relevant
   `settings.json` so an Edit that flips a task's `Status` to `In Progress`
   triggers the validator. Mirror the entry in both library and kit.
4. **Bean template** — update `ai/beans/_bean-template.md`'s task example
   to show a populated `Inputs:` block (3 example bullets with concrete
   paths) and a one-line note about the escape hatch.
5. **Team-Lead persona** — update
   `ai-team-library/personas/team-lead/persona.md` task-seeding guidance
   to require non-empty `Inputs:` for every task. Mirror the same change
   in `.claude/shared/agents/team-lead.md` so Foundry's own team-lead
   carries the rule.
6. **Tests** at `tests/test_validate_task_inputs_hook.py`:
   - `test_pass_with_populated_inputs`
   - `test_fail_when_inputs_section_missing`
   - `test_fail_when_inputs_empty`
   - `test_fail_when_only_sentinel_dashes`
   - `test_pass_with_escape_hatch_short_justification_fails`  (boundary)
   - `test_pass_with_escape_hatch_valid_justification`
   - Optional: `test_remediation_message_names_path`

## Acceptance Criteria

- [ ] Hook script exists at both library and kit locations with identical content.
- [ ] Hook is registered in the kit's `settings.json` so it triggers on
      task-file Edit-to-In-Progress transitions.
- [ ] Hook is also registered in the library `settings.json` (or wherever
      generated projects pick up hooks) so downstream projects get it.
- [ ] Bean template shows a populated `Inputs:` example.
- [ ] Team-Lead persona files (library + kit) require non-empty `Inputs:`.
- [ ] All new tests pass; existing tests still pass (`uv run pytest`).
- [ ] Lint clean (`uv run ruff check foundry_app/`); the hook itself is
      `tests/`-adjacent Python — run ruff on it too via the same command
      if the project's lint scope includes it, otherwise spot-check.
- [ ] `/spawn-task` Phase 2 reference matches the hook's actual module
      name and entry point.

## Definition of Done

- All files written; hook is callable as `python3 <path-to-hook>` with a
  task file path argument or via the registered hook envelope.
- Tests pass; lint clean.
- Commit message: `BEAN-272 task 01: validate-task-inputs hook + tests + docs`.
