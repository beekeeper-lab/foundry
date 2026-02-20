# Task 01: Add Examples-First Principle to Workflow and Agent Docs

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Done |
| **Started** | 2026-02-17 04:08 |
| **Completed** | 2026-02-17 04:08 |
| **Duration** | < 1m |
| **Depends On** | — |

## Goal

Add an "Examples-First" principle to the bean workflow documentation and Developer agent instructions. Ensure task definitions include guidance for providing concrete examples of expected output format.

## Inputs

- `ai/beans/BEAN-150-examples-first/bean.md` — acceptance criteria
- `ai/context/bean-workflow.md` — workflow doc to update
- `.claude/agents/developer.md` — agent instructions to update

## Implementation

1. **`bean-workflow.md` § Decomposition**: Add an "Examples-First Principle" subsection that:
   - States the principle: every task should include or reference a concrete example of the expected output format
   - Adds an `Example Output:` field recommendation to the task file template description
   - Explains when and how to include examples (inline snippet, reference to existing file, or link to a pattern)

2. **`.claude/agents/developer.md` § Operating Principles**: Add a principle:
   - "Examples first" — before starting implementation, look for examples of the expected output in the task file or referenced inputs. If none are provided, flag the gap before writing code.

## Acceptance Criteria

- [x] `bean-workflow.md` documents the examples-first principle in the Decomposition section
- [x] Task file guidance includes a place for examples (Example Output field)
- [x] `.claude/agents/developer.md` references the examples-first principle
- [x] Changes are minimal and consistent with existing document style

## Definition of Done

Workflow docs and developer agent instructions updated with examples-first guidance.
