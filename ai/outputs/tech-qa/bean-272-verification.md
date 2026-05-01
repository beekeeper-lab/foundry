# BEAN-272 Verification Report

| Field | Value |
|-------|-------|
| **Bean** | BEAN-272 — Validate Task `Inputs:` at Dispatch (Pre-Execution Hook) |
| **Verifier** | Tech-QA |
| **Date** | 2026-04-29 |
| **Branch** | `bean/BEAN-272-validate-task-inputs-hook` |
| **Verdict** | **PASS** |

## Bean Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Hook script exists at both library and Foundry kit locations | **PASS** | `ai-team-library/claude/hooks/validate-task-inputs.py` and `.claude/shared/hooks/validate-task-inputs.py` exist. `diff -q` reports identical content. |
| 2 | Hook is registered in `ai-team-library/claude/settings.json` so generated projects pick it up | **PASS** | `ai-team-library/claude/settings/settings.json` PreToolUse on `Edit\|Write` — 1 matching `validate-task-inputs` reference. |
| 3 | Task with empty/missing `Inputs:` cannot move to `In Progress`; remediation message is clear | **PASS** | End-to-end script invocation Case 1 (missing Inputs): exit=2; stderr names the task path and the expected format. Case 4 (sentinel-only `—` bullets): exit=2 with sentinel-specific message. |
| 4 | Task with `Inputs: NONE (justified: ...)` proceeds | **PASS** | End-to-end Case 3: exit=0 with a 50-char justification. pytest `test_main_passes_with_escape_hatch` covers the same path. Boundary: `test_validate_fail_with_escape_hatch_too_short` confirms <10 char reasons fail. |
| 5 | `/spawn-task` (BEAN-270) refuses to dispatch when validation fails | **PASS** | `ai-team-library/claude/skills/spawn-task/SKILL.md` Phase 2 ("Inputs Validation (BEAN-272 hook integration point)") explicitly states the hook is invoked before dispatch and aborts on failure. The skill's Phase 2 step 4 names the hook by file path: `hooks/validate-task-inputs.py`. |
| 6 | Bean template shows a populated `Inputs:` example | **PASS** | `ai/beans/_bean-template.md` task-decomposition note includes an `## Inputs` block with two concrete bullet examples and the escape-hatch syntax. |
| 7 | Team-Lead persona doc requires non-empty `Inputs:` for every task | **PASS** | Library: `ai-team-library/personas/team-lead/persona.md` has a `### Task Inputs are Mandatory` subsection inside `## Per-Task Dispatch`. Kit (project-side via symlink): `.claude/shared/agents/team-lead.md` task-file checklist line for `Inputs:` flagged "Required and non-empty" with escape-hatch wording. |
| 8 | Tests cover the validator end-to-end | **PASS** | `tests/test_validate_task_inputs_hook.py`: 35 test cases — pure-function (path matching, bullet parsing, sentinel detection, escape-hatch), full-text validation (populated, missing, empty, all-sentinel, escape-hatch valid/short), and `main()` JSON-envelope behavior (non-task-file passthrough, non-`In Progress` passthrough, blocking with remediation, populated-pass, escape-hatch pass, invalid JSON tolerance, non-Edit-tool passthrough, Write tool support). |
| 9 | All tests pass (`uv run pytest`) | **PASS** | `1972 passed, 4 warnings in 11.12s`. The 4 warnings are pre-existing Qt deprecation notices unrelated to this bean. |
| 10 | Lint clean (`uv run ruff check foundry_app/`) | **PASS** | `All checks passed!` (run includes `ai-team-library/claude/hooks/validate-task-inputs.py`). |

## End-to-End Script Invocations

Manual hook invocations against crafted task fixtures at `/tmp/btest-272b/ai/beans/BEAN-999-test/tasks/01-dev-foo.md`. JSON envelope passed via stdin. Each case produced the expected exit code and stderr output.

| Case | Inputs Block | Expected | Got |
|------|-------------|----------|-----|
| 1 | (no `## Inputs` heading) | exit 2 + remediation | exit 2 + "missing `## Inputs` section" |
| 2 | populated bullets | exit 0 | exit 0 |
| 3 | `Inputs: NONE (justified: <51-char reason>)` | exit 0 | exit 0 |
| 4 | bullets `- —` only | exit 2 + sentinel remediation | exit 2 + "contains only sentinel placeholders" |
| 5 | Status flipping to `Done` (not In Progress) | exit 0 (passthrough) | exit 0 |

## /spawn-task Integration

`ai-team-library/claude/skills/spawn-task/SKILL.md` Phase 2 (lines 65–73) declares the integration:

```
### Phase 2: Inputs Validation (BEAN-272 hook integration point)

4. Parse the task's `Inputs:` section ... If the validate-task-inputs
   hook (`hooks/validate-task-inputs.py` from BEAN-272) is registered,
   invoke it. On failure, the hook's remediation message is the
   user-facing error and dispatch is aborted.
5. Escape hatch — `Inputs: NONE (justified: <reason ≥10 chars>)` proceeds.
```

This matches the hook's actual file name and behavior. Integration is real, not aspirational.

## Static Checks

| Command | Result |
|---------|--------|
| `diff -q` between library and kit hooks | identical |
| `wc -l ai-team-library/claude/hooks/validate-task-inputs.py` | 158 lines |
| `grep -c "validate-task-inputs" ai-team-library/claude/settings/settings.json` | 1 (registered) |
| `grep -c "validate-task-inputs" .claude/shared/settings.json` | 1 (registered) |
| `uv run pytest` | 1972 passed |
| `uv run ruff check foundry_app/ ai-team-library/claude/hooks/validate-task-inputs.py` | clean |

## Findings & Notes

- **Kit submodule pointer** advances to `bean/BEAN-272-validate-inputs` (commit `a1a15b1`), which itself was branched from the BEAN-270 kit branch tip. Kit-side merge to its `main` is part of the kit's normal PR cycle — same posture as BEAN-270. Foundry consumes the change immediately via the submodule pointer.
- **No Python production code changed** in `foundry_app/`. The hook is a standalone script consumed at the Claude Code runtime layer, not a foundry module. The 35 new tests live alongside `test_telemetry_stamp.py` and use the same `importlib`-loaded module pattern.
- **Hook does not validate file existence in the Inputs list.** That's deliberate per the bean's "Out of Scope" — covered loosely by `/spawn-task` and properly by BEAN-274's contract graph.
- **Hook ignores writes when bean status flips, not task status flips.** The path filter (`is_task_file`) requires the file path to be a task file, so editing `bean.md` or `_index.md` to flip a status is not affected.

## Verdict

**PASS.** All ten acceptance criteria verified with concrete evidence. End-to-end behavior matches the spec across positive, negative, sentinel, escape-hatch, and passthrough paths.
