# BEAN-139: Team Member Assignment Recommendations

**Date:** 2026-02-16 | **Analyst:** developer | **Category:** Process
**Companion to:** BEAN-137 (assignment analysis), BEAN-138 (participation decisions)

---

## 1. Executive Summary

BEAN-137 revealed that the Foundry AI team's five-persona model has converged to a two-persona execution pipeline (Developer + Tech-QA) for 97% of beans. BEAN-138 codified this into a participation decision matrix with skip templates. This document translates those findings into **10 specific, implementable recommendations** — concrete changes to agent definitions, workflow files, skill templates, and team configuration.

The recommendations are ordered by priority and grouped into three tiers:
- **High priority (R1–R4):** Structural changes that reduce overhead on every bean
- **Medium priority (R5–R7):** Quality and consistency improvements
- **Low priority (R8–R10):** Future-proofing and optimization

---

## 2. High Priority Recommendations

### R1: Make Developer + Tech-QA the Default Decomposition Template

**What to change:** Update `bean-workflow.md` Section 4 (Decomposition) and the Team Lead agent (`team-lead.md` line 47) to define `Developer → Tech-QA` as the **default task template**, with BA and Architect as **opt-in exceptions** rather than skipped-by-default members of a full wave.

**Why:** Currently, the workflow describes a BA → Architect → Developer → Tech-QA wave (bean-workflow.md line 115) and instructs the Team Lead to "skip personas that aren't needed" (line 116). In practice, BA is skipped 98% of the time and Architect 97% (BEAN-137 §4). This inverts the cognitive default — the Team Lead must actively decide to skip two personas on every single bean, then document why. Flipping the default eliminates this repetitive overhead.

**Expected impact:**
- Eliminates ~2 skip-justification lines per bean (saved on every decomposition)
- Reduces Team Lead decomposition decision time
- Aligns documentation with actual practice (removes mismatch between defined and actual model)

**Suggested changes:**
1. `ai/context/bean-workflow.md` §4 line 115: Change "Follow the natural wave: BA → Architect → Developer → Tech-QA" to "Default decomposition: Developer → Tech-QA. Add BA or Architect only when their inclusion criteria (see below) are met."
2. `.claude/agents/team-lead.md` line 47: Change "Follow the natural wave: BA → Architect → Developer → Tech-QA (skip roles not needed)" to "Default wave: Developer → Tech-QA. Include BA when requirements are ambiguous (§4.1 criteria). Include Architect when design decisions are needed (§4.2 criteria)."
3. Add inclusion criteria (from BEAN-138 §4.1 and §4.2) directly into bean-workflow.md as a subsection of Decomposition.

**Implementation:** Single Process bean modifying 2 files.

---

### R2: Embed the BEAN-138 Participation Matrix in the Team Lead Agent

**What to change:** Add a condensed version of BEAN-138's participation decision matrix (§3.1) directly into `.claude/agents/team-lead.md` under a new "## Participation Decisions" section, positioned after the decomposition workflow.

**Why:** The Team Lead agent is the sole decision-maker for persona assignment. Currently, the participation criteria exist only in `ai/outputs/team-lead/bean-138-team-member-participation-decisions.md` — an output document that the Team Lead has no instruction to consult. Embedding the matrix in the agent definition ensures it's part of every decomposition context window.

**Expected impact:**
- Consistent decomposition decisions across all future beans
- No need to separately load BEAN-138 output during decomposition
- Skip justifications become more formulaic and faster to write

**Suggested addition to `team-lead.md`:**
```markdown
## Participation Decisions

Default team for decomposition: Developer + Tech-QA.

| Condition | Add Persona |
|-----------|-------------|
| Requirements are ambiguous; 3+ interpretations possible | BA |
| New subsystem, cross-cutting API change, or ADR needed | Architect |
| App/Infra bean with any code changes | Tech-QA (mandatory) |
| Process bean producing executable artifacts | Tech-QA |
| Process bean producing documentation only | Skip Tech-QA |
| Trivial fix (< 5 min, single-line) | Team Lead direct; skip all |
```

**Implementation:** Single Process bean modifying 1 file.

---

### R3: Redefine the BA Persona as a Requirements Reviewer

**What to change:** Transform `.claude/agents/ba.md` from an active requirements-authoring role to a **requirements review** role that validates bean definitions before they enter the execution pipeline.

**Why:** BEAN-137 Finding 1 shows the BA has not been assigned a task since BEAN-005 (130 beans ago). The bean template and `/backlog-refinement` skill have fully absorbed the BA's requirements-gathering function — requirements are captured during bean creation, not during execution. However, there is a gap: no one formally validates that bean requirements are complete, unambiguous, and testable before the Team Lead picks them. Repurposing the BA to fill this gap gives the persona a useful function without adding a new agent.

**Current BA role (from `ba.md`):**
- Elicit, analyze, and document requirements
- Write user stories with Given/When/Then
- Define scope boundaries
- Identify risks, assumptions, dependencies

**Proposed BA role:**
- Review bean definitions during `/backlog-refinement` for completeness
- Validate that acceptance criteria are testable (can Tech-QA verify them?)
- Flag scope ambiguities before beans are approved
- Remain available for full requirements analysis on rare complex beans

**Expected impact:**
- Gives the BA persona a function that's actually used
- Improves bean quality upstream (before execution, not during)
- Reduces rework from vague acceptance criteria

**Suggested changes to `ba.md`:**
1. Rename role to "Requirements Reviewer" in the header description
2. Add "## Primary Function" section: Review and validate bean definitions
3. Keep existing "What You Do" as secondary (complex-bean) function
4. Add trigger: "Activated during `/backlog-refinement` when bean specs need validation"

**Implementation:** Single Process bean modifying 1 file. Could also update `/backlog-refinement` skill to include a BA review step.

---

### R4: Add Team Lead Direct-Execution Quality Gate

**What to change:** Add a mandatory lint+test verification step to beans where the Team Lead implements directly, documented in `team-lead.md` and `bean-workflow.md`.

**Why:** BEAN-137 Finding 5 shows the Team Lead bypasses all specialist personas (including Tech-QA) for ~6% of beans. While efficient for trivial work, this skips the quality gate. BEAN-138 §6.3 acknowledges this but doesn't enforce a verification step. Even a minimal `uv run pytest && uv run ruff check foundry_app/` after Team Lead implementation ensures no regressions slip through.

**Expected impact:**
- Maintains quality gate coverage at 100% (currently ~94% due to Team Lead direct implementations)
- Minimal overhead for truly trivial fixes (< 30 seconds to run tests)
- Prevents the "trivial fix that breaks something" failure mode

**Suggested changes:**
1. `.claude/agents/team-lead.md`: Add rule: "When implementing a bean directly (without delegating to Developer/Tech-QA), you MUST run `uv run pytest` and `uv run ruff check foundry_app/` before marking the bean Done."
2. `ai/context/bean-workflow.md` §7 (Closure): Add: "If the Team Lead implemented directly, test and lint verification is still required."

**Implementation:** Single Process bean modifying 2 files.

---

## 3. Medium Priority Recommendations

### R5: Define Explicit Architect Trigger Criteria in the Architect Agent

**What to change:** Add a "## When You Are Activated" section to `.claude/agents/architect.md` that lists the specific conditions under which the Architect should be included in task decomposition.

**Why:** BEAN-137 Finding 2 shows the Architect activates for only 3% of beans. The current agent definition describes what the Architect does but not when they should be brought in. The Team Lead must rely on judgment for every bean. Explicit triggers reduce ambiguity and ensure the Architect is included when genuinely needed (and not included when not).

**Suggested triggers (derived from BEAN-137 §10.2 and BEAN-138 §4.2):**
```markdown
## When You Are Activated

The Team Lead includes you in task decomposition when ANY of these conditions apply:

1. **New subsystem:** The bean creates a new module, service, or package not in the existing codebase
2. **Cross-cutting change:** The bean modifies public APIs or data models used by 3+ modules
3. **Technology decision:** The bean introduces a new external dependency or framework
4. **Format mapping:** The bean requires translating between two different configuration/data formats
5. **ADR needed:** The change has long-term consequences that warrant a documented decision record

You are NOT activated for:
- Beans following established implementation patterns
- Single-module changes with no cross-cutting concerns
- Bug fixes, styling, or configuration changes
- Analysis or documentation beans
```

**Expected impact:**
- Team Lead can quickly evaluate whether Architect is needed using a checklist
- Architect is consistently included for genuinely complex design work
- Reduces the chance of missing an Architect review on a bean that actually needs one

**Implementation:** Single Process bean modifying 1 file.

---

### R6: Strengthen Tech-QA's Shift-Left Capability

**What to change:** Add a new optional task type to the Tech-QA agent: "Pre-implementation acceptance criteria review." This task would run *before* the Developer starts, reviewing the bean's acceptance criteria for testability.

**Why:** BEAN-137 §10.4 recommends shift-left testing. Currently, Tech-QA always runs after Developer (post-implementation verification). Adding an optional pre-implementation review step means:
- Untestable acceptance criteria are caught before Developer invests time
- Test stubs can be written before implementation (TDD-style)
- Tech-QA is engaged earlier, reducing back-and-forth after implementation

**Current Tech-QA flow:** Developer completes → Tech-QA verifies
**Proposed flow (optional):** Tech-QA reviews criteria → Developer implements → Tech-QA verifies

**Suggested changes to `tech-qa.md`:**
1. Add "## Pre-Implementation Review (Optional)" section
2. Contents: Read bean's acceptance criteria, flag any that are untestable, write test stubs in `tests/` if applicable
3. Add to Team Lead decomposition guidance: "For Standard and Complex tier beans, consider adding a pre-implementation Tech-QA task to review acceptance criteria."

**Expected impact:**
- Earlier detection of untestable acceptance criteria
- Potential for TDD-style development on complex beans
- No overhead on simple beans (optional activation)

**Implementation:** Single Process bean modifying 2 files (`tech-qa.md`, `team-lead.md`).

---

### R7: Standardize Skip Justification as Inline Tags

**What to change:** Replace the current multi-line skip justification blocks with single-line inline tags in the bean.md Tasks table.

**Why:** BEAN-138 §5 provides skip justification templates, but they're verbose (2-3 lines each). For the typical bean that skips BA and Architect, this adds 4-6 lines of boilerplate to every bean.md. Since the participation matrix (R2) will be embedded in the Team Lead agent, detailed justifications become redundant. A single-line tag is sufficient for audit trail.

**Current format:**
```markdown
> BA/Architect skipped: Process analysis bean — no requirements gathering or architecture
> design needed; the task is analysis of existing workflow patterns.
> Tech QA skipped: No code changes to test — output is a documentation artifact only.
```

**Proposed format:**
```markdown
> Skipped: BA (default), Architect (default), Tech-QA (no-code-changes)
```

**Skip tag vocabulary:**
| Tag | Meaning |
|-----|---------|
| `default` | Persona is not in the default wave; no special reason needed |
| `no-code-changes` | Bean produces documentation only; no executable artifacts to test |
| `trivial-fix` | Team Lead direct execution; too small for specialist |
| `included:requirements-ambiguity` | BA included because criteria need elaboration |
| `included:design-decision` | Architect included because ADR needed |

**Expected impact:**
- Reduces boilerplate by ~4 lines per bean
- Faster decomposition
- Still maintains audit trail via standard tags

**Implementation:** Single Process bean updating documentation. Optionally update existing beans retroactively.

---

## 4. Low Priority Recommendations

### R8: Track Persona Utilization Metrics in Telemetry

**What to change:** Extend the bean telemetry table to include a "Personas Used" field, enabling data-driven tracking of which personas are engaged over time.

**Why:** BEAN-137 relied on manual inspection of task tables to calculate utilization rates. BEAN-141 showed only 2.8% of beans have telemetry data. Adding a simple "Personas Used" field to the telemetry summary (e.g., `Developer, Tech-QA`) would enable automated tracking of participation patterns and validate whether the recommendations in this document are having the intended effect.

**Suggested change to `_bean-template.md`:**
Add to the Telemetry summary table:
```markdown
| **Personas Used** | — |
```

**Expected impact:**
- Enables future analysis without manual task-table inspection
- Low overhead (single field populated during bean closure)
- Provides feedback loop for participation decision effectiveness

**Implementation:** Single Process bean modifying 1 template file.

---

### R9: Create a "Complexity Assessment" Step in Decomposition

**What to change:** Add a brief complexity assessment to the Team Lead's decomposition workflow that maps to BEAN-138's complexity tiers (Trivial/Simple/Standard/Complex/Epic) and automatically determines the participation model.

**Why:** BEAN-138 §7.1 defines five complexity tiers, each with a typical team composition. Currently, the Team Lead must mentally map bean characteristics to tiers and then to team composition. Making this a deliberate step (even just a one-line annotation in the Tasks section) ensures consistent tier assignment and makes the participation decision traceable.

**Proposed addition to bean.md template:**
```markdown
## Tasks

**Complexity:** [Trivial | Simple | Standard | Complex | Epic]

| # | Task | Owner | Depends On | Status |
```

**Tier → Team mapping (from BEAN-138 §7.1):**
| Tier | Default Team |
|------|-------------|
| Trivial | Team Lead only |
| Simple | Developer |
| Standard | Developer + Tech-QA |
| Complex | Developer + Tech-QA (+ Architect if new patterns) |
| Epic | BA + Architect + Developer + Tech-QA |

**Expected impact:**
- Makes decomposition decisions explicit and auditable
- Provides data for future analysis of bean complexity distribution
- Minimal overhead (single word added to Tasks section)

**Implementation:** Single Process bean modifying 1 template file and documentation.

---

### R10: Update the `/long-run` Skill to Reference Participation Rules

**What to change:** Update the `/long-run` skill to reference the embedded participation matrix (R2) during its decomposition phase, rather than relying on generic "skip inapplicable roles" guidance.

**Why:** `/long-run` is the primary autonomous execution pathway. It processes beans from pick through closure without user intervention. If it doesn't reference the participation rules during decomposition, it may produce inconsistent skip decisions across long autonomous runs. By referencing the Team Lead agent's embedded matrix, `/long-run` inherits consistent behavior.

**Suggested change:** In the `/long-run` skill's decomposition step, add:
```
Reference the Participation Decisions section in the Team Lead agent for persona inclusion/exclusion criteria.
```

**Expected impact:**
- Consistent participation decisions during autonomous runs
- No behavioral change for manual (non-`/long-run`) decomposition (already covered by R2)

**Implementation:** Single Process bean modifying 1 skill file.

---

## 5. Summary: Recommendation Roadmap

| # | Recommendation | Priority | Files Changed | Depends On |
|---|---------------|----------|---------------|------------|
| R1 | Default to Developer + Tech-QA wave | High | bean-workflow.md, team-lead.md | — |
| R2 | Embed participation matrix in Team Lead agent | High | team-lead.md | — |
| R3 | Redefine BA as Requirements Reviewer | High | ba.md | R1 |
| R4 | Add Team Lead direct-execution quality gate | High | team-lead.md, bean-workflow.md | — |
| R5 | Define Architect trigger criteria | Medium | architect.md | R1 |
| R6 | Strengthen Tech-QA shift-left capability | Medium | tech-qa.md, team-lead.md | — |
| R7 | Standardize skip justifications as inline tags | Medium | bean-workflow.md, _bean-template.md | R1, R2 |
| R8 | Track persona utilization in telemetry | Low | _bean-template.md | — |
| R9 | Add complexity assessment to decomposition | Low | _bean-template.md, bean-workflow.md | R2 |
| R10 | Update /long-run to reference participation rules | Low | long-run skill | R2 |

**Estimated implementation effort:** Each recommendation is a single Process bean, typically modifying 1-2 files with no code changes. The full set could be batched into 3-4 beans (grouping by file affected) or executed individually.

**Suggested implementation order:**
1. R1 + R2 (same bean — core workflow change)
2. R4 (independent — quality gate)
3. R3 + R5 (same bean — agent role adjustments)
4. R6 + R7 (same bean — Tech-QA and template updates)
5. R8 + R9 + R10 (same bean — template and skill updates)

---

## 6. Persona-by-Persona Impact Summary

### Team Lead
- **R1:** Default decomposition changes from 4-persona wave to 2-persona wave
- **R2:** Participation matrix embedded in agent definition
- **R4:** Must run tests/lint when implementing directly
- **R9:** Adds complexity tier annotation to decomposition
- **Net effect:** Faster, more consistent decomposition; slight additional obligation for direct implementations

### BA
- **R3:** Role redefined from "requirements author" to "requirements reviewer"
- **R1:** No longer in the default wave; inclusion requires explicit trigger
- **Net effect:** Shifts from dormant-but-defined to active-when-triggered; more likely to actually be used

### Architect
- **R5:** Explicit activation triggers added to agent definition
- **R1:** No longer in the default wave; inclusion requires explicit trigger
- **Net effect:** Clearer contract for when Architect is needed; reduces ambiguity

### Developer
- **No direct changes.** Developer is already the execution backbone and will continue to be.
- **R6:** May benefit from pre-implementation Tech-QA criteria review (fewer rework cycles)
- **Net effect:** No change in workload or responsibilities

### Tech-QA
- **R6:** Optional pre-implementation review step added
- **R7:** Skip justifications become simpler when Tech-QA is excluded
- **R4:** Indirectly benefits from Team Lead quality gate (ensures all beans get at least basic verification)
- **Net effect:** Expanded scope (optional shift-left); role otherwise unchanged

---

## 7. Cross-Reference to Prior Analysis

| BEAN-137 Finding | This Document's Response |
|-----------------|-------------------------|
| §8.1: BA effectively retired | R3: Redefine as Requirements Reviewer |
| §8.2: Architect is event-driven | R5: Define explicit trigger criteria |
| §8.3: Developer is execution bottleneck | No change (structural reality of single-agent model) |
| §8.4: Tech-QA consistently gates quality | R6: Strengthen with shift-left option |
| §8.5: Team Lead bypasses wave for small work | R4: Add quality gate for direct implementations |
| §8.6: Skip reasons are consistent | R7: Standardize as inline tags |
| §10.1: Formalize two-persona model | R1: Make Developer + Tech-QA the default |
| §10.2: Define Architect triggers | R5: Explicit activation criteria |
| §10.3: Consider retiring BA | R3: Repurpose rather than retire |
| §10.4: Strengthen Tech-QA independence | R6: Pre-implementation review option |
| §10.5: Audit Team Lead direct implementation | R4: Mandatory test/lint verification |

| BEAN-138 Section | This Document's Response |
|-----------------|-------------------------|
| §3: Participation matrix | R2: Embed in Team Lead agent |
| §5: Skip justification templates | R7: Simplify to inline tags |
| §6: Override and exception conditions | R4: Formalize Team Lead quality gate |
| §7: Complexity tiers | R9: Add complexity annotation to template |
| §8: Workflow documentation recommendations | R10: Update /long-run skill |
