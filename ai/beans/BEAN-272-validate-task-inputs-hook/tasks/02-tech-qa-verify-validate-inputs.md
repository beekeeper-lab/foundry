# Task 02: Verify BEAN-272 Acceptance Criteria

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Independently verify every acceptance criterion in BEAN-272 and Task 01.
Produce a verification report at
`ai/outputs/tech-qa/bean-272-verification.md` listing each criterion with
PASS / FAIL / MANUAL plus concrete evidence (file path, command output
excerpt, line range). Stop the bean if any criterion fails.

Specifically exercise the validator end-to-end in three modes — populated
Inputs, missing/empty Inputs, escape-hatch — by invoking the hook script
directly with crafted task-file fixtures and asserting exit code +
remediation message. The pytest run already covers this, but the
verification report names the test names that exercise each criterion.

The `/spawn-task` integration is verified by inspecting the SKILL.md's
Phase 2 reference: confirm the hook path in the skill matches the hook
file actually shipped, so the integration is real not aspirational.

## Inputs

- `ai/beans/BEAN-272-validate-task-inputs-hook/bean.md`
- `ai/beans/BEAN-272-validate-task-inputs-hook/tasks/01-developer-validate-inputs-hook.md`
- `ai-team-library/claude/hooks/validate-task-inputs.py`
- `.claude/shared/hooks/validate-task-inputs.py`
- `ai-team-library/claude/settings.json`
- `.claude/shared/settings.json`
- `ai/beans/_bean-template.md`
- `ai-team-library/personas/team-lead/persona.md`
- `.claude/shared/agents/team-lead.md`
- `ai-team-library/claude/skills/spawn-task/SKILL.md`
- `tests/test_validate_task_inputs_hook.py`

## Acceptance Criteria

- [ ] Verification report exists at `ai/outputs/tech-qa/bean-272-verification.md`.
- [ ] Each of the 9 bean acceptance criteria gets a PASS/FAIL/MANUAL row
      with evidence.
- [ ] Hook script is byte-identical between library and kit (or
      intentionally divergent with the divergence documented).
- [ ] Hook is registered in both library and kit settings (grep evidence).
- [ ] `/spawn-task` skill's Phase 2 reference matches the hook's actual
      file path.
- [ ] Bean template shows a populated `Inputs:` example.
- [ ] Both Team-Lead persona docs require non-empty `Inputs:`.
- [ ] `uv run pytest` passes — captured tail in the report.
- [ ] `uv run ruff check foundry_app/` passes — captured in the report.

## Definition of Done

- Report committed with a clear PASS / FAIL verdict.
- Any failures specific enough to fix without re-investigating.
