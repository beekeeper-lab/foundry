# SPEC-018: Close workflow ownership gaps: merge, deploy, taxonomy routing

- **Priority:** P1
- **Effort:** S
- **Area:** library
- **Depends on:** none (pairs well with SPEC-017)
- **Status:** Proposed

## Problem

The bean workflow makes merge (and, at release points, deploy) a **mandatory** closure step for every bean — but assigns them to the Merge Captain and DevOps/Release personas, both of which are **opt-in extended personas**. A default core-only team (team-lead, ba, architect, developer, tech-qa) therefore has no owner for a step the workflow says must happen before a bean is closed. The task taxonomy has the same defect more broadly: Integration, Deployment, Security, and Compliance categories route to opt-in personas with no fallback rule, so on most real teams those categories are ownerless and the routing table silently fails.

## Evidence

- `ai-team-library/process/context/bean-workflow.md:141` — "Merge feature branch to `main` using `/merge-bean` (Merge Captain). This step is mandatory — a bean is not fully closed until its branch has been merged."
- `ai-team-library/process/context/bean-workflow.md:147,165` — `/deploy` creates release tags; "the Merge Captain merges the feature branch" — same opt-in owner.
- `ai-team-library/workflows/task-taxonomy.md:15-19` — Integration → Integrator, Deployment → DevOps/Release Engineer, Security → Security Engineer, Compliance → Compliance/Risk Analyst as *Primary Persona*; all four live in `personas/extended/` and are absent from a core-only composition. No fallback column or rule exists.
- `foundry_app/services/validator.py` — no check relates workflow-mandatory steps to team composition; a core-only team validates clean.
- Dogfood reality: in `ai/beans/_index.md` every bean's owner is `team-lead`, i.e. team-lead already performs merges in practice — the spec just never says so.

## Proposed change

1. **Add an explicit fallback-ownership table** to `task-taxonomy.md` (new column "Fallback When Absent") and reference it from `bean-workflow.md`:

   | Category | Primary | Fallback when absent |
   |---|---|---|
   | Integration / merge | Integrator / Merge Captain | **Team Lead** (runs `/merge-bean` itself) |
   | Deployment / release | DevOps / Release Engineer | **Team Lead**, with `/deploy` demoted to a `manual:` step requiring explicit user confirmation |
   | Security | Security Engineer | **Developer** implements + **Tech-QA** verifies; Team Lead escalates to the user for material threat-model decisions |
   | Compliance | Compliance / Risk Analyst | **Escalate to user** — no silent fallback; the bean blocks with a named reason |
   | Review | Code Quality Reviewer | **Tech-QA** |
   | Documentation | Technical Writer | **Developer** (docs land with the change) |
   | Research | Researcher / Librarian | **Architect** |
   | UX Design | UX / UI Designer | **BA** (flows/AC only; no visual design) |

2. **Amend `bean-workflow.md:141-165`** to name the fallback inline: "…using `/merge-bean` (Merge Captain when on the team, otherwise the Team Lead)". Same for the `/deploy` mentions.
3. **Validator advisory:** in `validate_contract_graph` or a new `_check_workflow_ownership`, emit an INFO/WARNING when a composition lacks the primary persona for Integration ("merge falls back to team-lead") and Deployment; keep it non-blocking (consistent with BEAN-292's warning-only stance).
4. **Compiled output:** the generated CLAUDE.md orchestration block (`foundry_app/services/compiler.py:588-604`, `scaffold.py:45-58`) currently name-drops personas not on the team; make it render the fallback owner actually applicable to the composed team (coordinates with SPEC-006/SPEC-007 which fix adjacent bugs in that block).
5. Mirror the taxonomy change into the kit copy if `task-taxonomy.md` is distributed (verify during implementation; the library copy is canonical).

## Out of scope

- Creating contracts for extended personas (SPEC-017).
- Making `/merge-bean` refuse without VDD (SPEC-008).
- Any change to which personas are core vs extended.

## Acceptance criteria

- [ ] `file-contains:` `ai-team-library/workflows/task-taxonomy.md` contains `Fallback When Absent`.
- [ ] `file-contains:` `ai-team-library/process/context/bean-workflow.md` contains `otherwise the Team Lead` (or equivalent explicit fallback wording) at the merge step.
- [ ] `file-contains:` `bean-workflow.md` states the Compliance fallback is escalation to the user, not silent reassignment.
- [ ] `test:` validator emits an ownership advisory for a core-only composition and none for a team including `extended/integrator-merge-captain`.
- [ ] `test:` `uv run pytest` passes.
- [ ] `manual:` generate `examples/small-python-team.yml`; the generated CLAUDE.md orchestration section names no persona absent from the team and states who merges.

## Files to touch

- `ai-team-library/workflows/task-taxonomy.md`
- `ai-team-library/process/context/bean-workflow.md`
- `foundry_app/services/validator.py`
- `foundry_app/services/compiler.py`, `scaffold.py` (orchestration block rendering)
- `tests/` (validator advisory test)
