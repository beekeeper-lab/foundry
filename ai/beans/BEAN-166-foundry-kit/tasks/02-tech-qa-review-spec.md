# Task 02: Review Foundry Kit Architecture Spec

| Field | Value |
|-------|-------|
| **Task ID** | 02 |
| **Owner** | Tech-QA |
| **Depends On** | 01 |
| **Status** | Pending |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Review the Foundry Kit Architecture Spec for completeness, accuracy, and alignment with acceptance criteria. Verify all required sections are present and the recommendations are sound.

## Inputs

- Spec: `ai/outputs/architect/foundry-kit-spec.md`
- Bean file: `ai/beans/BEAN-166-foundry-kit/bean.md` (acceptance criteria)

## Review Checklist

1. **Options analysis completeness** — At least 4 approaches with pros/cons/failure modes for each
2. **Mermaid diagrams** — Present and render correctly (valid Mermaid syntax)
3. **Implementation plan** — Step-by-step migration path exists
4. **Examples** — All 4 required examples present:
   - Version pinning + override
   - Multi-repo remote server
   - Trello batch card creation
   - Emergency hotfix rollout
5. **Trello integration** — Idempotency, config storage, and env parity documented
6. **Opinionated recommendation** — A clear default is chosen and justified
7. **Practical feasibility** — Recommendations are implementable with current tooling
8. **No contradictions** — Internal consistency across sections

## Example Output

A review report at `ai/outputs/tech-qa/review-BEAN-166.md`:

```markdown
# BEAN-166 Review: Foundry Kit Architecture Spec

## Verdict: PASS / FAIL

## Checklist
- [x] Options analysis: 4+ approaches with pros/cons
- [x] Mermaid diagrams: valid syntax
...

## Issues Found
(None / list of issues)

## Recommendations
(Optional suggestions for improvement)
```

## Definition of Done

- [ ] Review report exists at `ai/outputs/tech-qa/review-BEAN-166.md`
- [ ] All acceptance criteria from bean.md verified against spec content
- [ ] Any issues found are documented with specific references
- [ ] Verdict is PASS (or issues documented for rework)
