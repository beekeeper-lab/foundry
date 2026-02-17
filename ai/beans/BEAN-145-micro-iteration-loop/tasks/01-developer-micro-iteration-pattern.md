# Task 01: Document Micro-Iteration Loop Pattern

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |
| **Started** | 2026-02-17 04:02 |
| **Completed** | 2026-02-17 04:02 |
| **Duration** | < 1m |

## Goal

Add a micro-iteration loop pattern to the bean workflow documentation and Developer agent instructions. The pattern defines when to iterate (test failure, lint failure, AC not met), max iterations before escalating, and how to report iteration results.

## Inputs

- `ai/beans/BEAN-145-micro-iteration-loop/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — workflow doc to update
- `.claude/agents/developer.md` — agent instructions to update

## Implementation

1. **`bean-workflow.md`**: Add a "Micro-Iteration Loop" subsection under Section 5 (Execution) documenting:
   - Entry conditions: test failure, lint failure, acceptance criterion not met
   - Loop steps: diagnose → fix → verify → check exit conditions
   - Exit conditions: all checks pass, or max iterations reached
   - Max iterations: 3 attempts before escalating to Team Lead
   - Reporting: record iteration count and outcome in task file

2. **`developer.md`**: Add a brief reference to the micro-iteration loop in the workflow steps, between step 4 (run tests/lint) and step 5 (self-review).

## Acceptance Criteria

- [ ] Micro-iteration loop pattern is documented in `bean-workflow.md`
- [ ] Pattern specifies entry conditions (when to iterate)
- [ ] Pattern specifies exit conditions (when to stop)
- [ ] Max iteration count is defined with escalation path
- [ ] Developer agent instructions reference the pattern
- [ ] Changes are minimal and do not break existing workflow steps

## Definition of Done

Pattern documented in workflow and referenced in developer agent. No existing steps broken.
