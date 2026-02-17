# Analysis: Team Member Participation Decisions

**Bean:** BEAN-138 | **Date:** 2026-02-16 | **Analyst:** developer

---

## 1. Overview

The Foundry AI team uses a natural wave for task decomposition: BA → Architect → Developer → Tech-QA. The Team Lead orchestrates this wave, assigning tasks to each persona in dependency order. However, not every persona is needed for every bean. The current guidance — "skip roles not needed" (bean-workflow.md line 116, team-lead.md line 48) — leaves the decision to Team Lead judgment without explicit criteria.

This document analyzes historical participation patterns across 130+ completed beans, defines a participation decision matrix, provides skip justification templates, and documents exception conditions. The goal is to reduce decomposition ambiguity and improve consistency.

---

## 2. Historical Participation Patterns

### 2.1 Data Source

Analysis of all completed beans (BEAN-001 through BEAN-135) from the backlog index, with detailed task-table inspection of 28 representative beans spanning all three categories.

### 2.2 Observed Patterns by Category

#### App Beans (BEAN-016 through BEAN-129)

| Pattern | Frequency | Example Beans |
|---------|-----------|---------------|
| Developer + Tech-QA only | ~70% | BEAN-016, BEAN-017, BEAN-025, BEAN-054, BEAN-112 |
| Developer only | ~20% | BEAN-049, BEAN-053, BEAN-057, BEAN-081 |
| Team Lead direct (trivial fix) | ~5% | BEAN-059 |
| Full wave (BA + Arch + Dev + QA) | ~5% | None observed in sample |

**Key finding:** BA and Architect were never assigned in the sampled App beans. Skip justifications consistently cite: "Requirements clear in the bean spec" and "No architectural decisions needed."

#### Process Beans (BEAN-006 through BEAN-135)

| Pattern | Frequency | Example Beans |
|---------|-----------|---------------|
| Developer + Tech-QA | ~50% | BEAN-006, BEAN-007, BEAN-010, BEAN-011 |
| Developer only (analysis) | ~30% | BEAN-131, BEAN-132, BEAN-133, BEAN-135 |
| Developer only (docs/config) | ~20% | BEAN-080, BEAN-114 |

**Key finding:** Process beans that modify skill/command files include Tech-QA for verification. Process analysis beans (read-only, no code changes) skip Tech-QA.

#### Infra Beans (BEAN-008, BEAN-009, BEAN-012, BEAN-013)

| Pattern | Frequency | Example Beans |
|---------|-----------|---------------|
| Developer + Tech-QA | 100% | All sampled Infra beans |

**Key finding:** All Infra beans in the sample included Tech-QA, even for configuration and documentation changes. This aligns with the established rule: "Tech QA must never be skipped for App/Infra beans" (bean-132-long-run-analysis.md).

### 2.3 BA and Architect Participation: Why Zero?

Across 130+ completed beans, BA and Architect personas were **never assigned tasks**. This is a striking pattern that merits analysis:

**Structural reasons:**
1. **Bean spec acts as BA output.** The bean template itself (Problem Statement, Goal, Scope, Acceptance Criteria) captures what a BA would produce. By the time a bean reaches "Approved" status, the user has already validated the requirements.
2. **Architectural decisions are pre-made.** Most beans either follow established patterns (service implementation, CRUD, styling) or include architecture sketches in the bean spec (BEAN-010, BEAN-011).
3. **Small scope.** Individual beans are deliberately scoped to be completable in a single session. This granularity eliminates the need for requirements decomposition (BA) or cross-cutting design (Architect).

**When BA/Architect WOULD add value (theoretical):**
- Epic beans spanning multiple components with unclear boundaries
- Beans introducing entirely new subsystems with multiple valid architectural approaches
- Beans with ambiguous acceptance criteria that need user-story elaboration
- Migration or rewrite beans requiring trade-off analysis

---

## 3. Participation Decision Matrix

### 3.1 By Bean Category and Type

| Category | Bean Type | BA | Architect | Developer | Tech-QA |
|----------|-----------|:--:|:---------:|:---------:|:-------:|
| **App** | New feature (service/screen) | Skip | Skip | **Include** | **Include** |
| **App** | Bug fix | Skip | Skip | **Include** | **Include** |
| **App** | Refactoring | Skip | Skip | **Include** | **Include** |
| **App** | UI styling/theming | Skip | Skip | **Include** | Conditional |
| **App** | Test coverage improvement | Skip | Skip | **Include** | Skip |
| **App** | Security hardening | Skip | Skip | **Include** | **Include** |
| **App** | Trivial fix (< 5 min) | Skip | Skip | Skip (TL direct) | Skip |
| **Process** | New skill/command | Skip | Skip | **Include** | **Include** |
| **Process** | Skill/command modification | Skip | Skip | **Include** | **Include** |
| **Process** | Analysis (read-only) | Skip | Skip | **Include** | Skip |
| **Process** | Workflow documentation | Skip | Skip | **Include** | Skip |
| **Process** | Configuration change | Skip | Skip | **Include** | Conditional |
| **Infra** | Git workflow changes | Skip | Skip | **Include** | **Include** |
| **Infra** | Hook/CI changes | Skip | Skip | **Include** | **Include** |
| **Infra** | Deployment changes | Skip | Skip | **Include** | **Include** |

### 3.2 Decision Rules Summary

**Developer: Always included** unless the bean is a trivial fix (< 5 min, single-line change) that the Team Lead can execute directly.

**Tech-QA: Include by default for App and Infra beans.** The established rule is: "Tech QA must never be skipped for App/Infra beans" (from `/long-run` analysis, BEAN-132). Exceptions exist for:
- Pure styling/theming with no logic changes (conditional — include if acceptance criteria are testable)
- Test-only beans where the Developer is already writing/running tests

**Tech-QA: Conditional for Process beans.** Include when the bean creates or modifies executable artifacts (skill files, commands, hooks). Skip when the bean produces analysis documents or documentation-only artifacts.

**BA: Skip by default.** The bean template already serves as the requirements artifact. Include only when requirements are genuinely ambiguous and need elaboration through user-story analysis.

**Architect: Skip by default.** Include only when the bean introduces new subsystems, requires ADR-level decisions, or involves cross-cutting architectural changes.

---

## 4. Conditional Inclusion Criteria

When the matrix says "Conditional" or when the Team Lead is unsure, use these questions:

### 4.1 Should BA Be Included?

Include BA if **all three** are true:
1. The Problem Statement is vague or uses undefined terms
2. The Acceptance Criteria are not testable as written
3. The bean's scope could reasonably be interpreted in multiple contradictory ways

Skip BA if **any one** is true:
- The bean spec already has 3+ concrete, testable acceptance criteria
- The work follows an established pattern (CRUD, service implementation, styling)
- The user has already provided detailed requirements in the bean

### 4.2 Should Architect Be Included?

Include Architect if **any one** is true:
1. The bean introduces a new module, service, or subsystem not in the existing codebase
2. Multiple valid technical approaches exist and the choice has long-term consequences
3. The bean modifies public APIs or data models used by 3+ other modules
4. An ADR (Architecture Decision Record) should be created

Skip Architect if **any one** is true:
- The implementation pattern is already established in the codebase
- The bean follows an existing architectural sketch (included in the spec or a prior ADR)
- The change is isolated to a single module with no cross-cutting concerns

### 4.3 Should Tech-QA Be Included?

Include Tech-QA if **any one** is true:
1. The bean modifies Python code in `foundry_app/` or `tests/`
2. The bean modifies git hooks, CI configuration, or deployment scripts
3. The bean creates executable skill/command files that will be invoked by other skills
4. The acceptance criteria include testable functional requirements

Skip Tech-QA if **all** are true:
- The bean produces only documentation artifacts (markdown analysis, design docs)
- No Python code is created or modified
- No executable configuration is created or modified
- The "test" is simply verifying the document exists and covers required topics

### 4.4 Should Developer Be Skipped?

This is rare. Skip Developer only when:
1. The bean is a trivial fix (typo, single-line config change) that the Team Lead can execute directly in under 5 minutes
2. The bean is purely a BA/Architect deliverable (requirements doc, ADR) with no implementation — note: this pattern hasn't occurred yet in the project

---

## 5. Skip Justification Templates

When skipping a persona, document the reason in the bean.md Tasks section using one of these templates:

### 5.1 BA Skip

```
> BA skipped: [Choose one]
> - Requirements are clear and testable in the bean spec; no ambiguity requiring elaboration.
> - Work follows established pattern ([pattern name]); no user-story analysis needed.
> - Bean scope is self-evident from the Problem Statement; acceptance criteria are concrete.
```

### 5.2 Architect Skip

```
> Architect skipped: [Choose one]
> - Implementation follows established codebase pattern; no architectural decisions required.
> - Architecture sketch provided in the bean spec; design is pre-determined.
> - Change is isolated to [module/file]; no cross-cutting concerns.
> - No new subsystems, APIs, or data models introduced.
```

### 5.3 Tech-QA Skip

```
> Tech QA skipped: [Choose one]
> - No code changes — output is a documentation/analysis artifact only.
> - Process analysis bean — no executable artifacts to test.
> - Developer task includes test writing; separate QA pass would duplicate effort.
```

### 5.4 Combined Skip (Most Common)

```
> BA/Architect skipped: Process analysis bean — no requirements gathering or architecture
> design needed; the task is analysis of existing [workflow patterns/documentation/commands].
> Tech QA skipped: No code changes to test — output is a documentation artifact only.
```

```
> BA/Architect skipped: [Category] bean with clear requirements and established implementation
> pattern; no ambiguity requiring elaboration or architectural decisions.
```

---

## 6. Override and Exception Conditions

### 6.1 Mandatory Overrides

These rules take precedence over the matrix:

| Rule | Source | Description |
|------|--------|-------------|
| **Tech QA mandatory for App/Infra** | BEAN-132 analysis | Tech QA must never be skipped for beans that modify application code or infrastructure. Even if the Developer writes tests, QA provides an independent verification pass. |
| **Developer mandatory for code beans** | Common sense | Any bean that creates or modifies Python code, scripts, or executable config must include the Developer persona. |

### 6.2 Escalation Triggers

Include an additional persona if any of these occur during execution:

| Trigger | Action |
|---------|--------|
| Developer discovers requirements ambiguity during implementation | Add BA task to clarify requirements before continuing |
| Implementation requires choosing between approaches with trade-offs | Add Architect task to evaluate options and produce ADR |
| Developer-written tests miss edge cases that surface later | Add Tech-QA task for independent test review |
| Bug fix reveals a broader design issue | Add Architect task to assess scope of the problem |

### 6.3 Team Lead Direct Execution

The Team Lead may execute a bean directly (no persona tasks) when:
- The bean is a trivial fix completable in under 5 minutes
- The change is a single-line configuration or documentation edit
- Example: BEAN-059 (Theme Wiring Fix, duration < 1m)

Even for Team Lead direct execution, document the decision:
```
> All personas skipped: Trivial fix ([description]); Team Lead executed directly.
```

---

## 7. Participation Patterns by Bean Complexity

### 7.1 Complexity Tiers

| Tier | Characteristics | Typical Team |
|------|----------------|--------------|
| **Trivial** | Single file, < 10 lines changed, < 5 min | Team Lead only |
| **Simple** | Single module, clear pattern, 1-2 hours | Developer |
| **Standard** | Single module with tests, established pattern | Developer + Tech-QA |
| **Complex** | Multiple modules, new patterns, 2+ hours | Developer + Tech-QA (+ Architect if new patterns) |
| **Epic** | New subsystem, cross-cutting, multi-session | BA + Architect + Developer + Tech-QA |

### 7.2 Current Project State

The Foundry project operates primarily in the **Simple** and **Standard** tiers. Bean scoping deliberately keeps work granular (completable in a single session), which is why BA and Architect have never been needed. If the project evolves to include Epic-tier beans, the full wave will become necessary.

---

## 8. Recommendations for Workflow Documentation

1. **Codify the matrix.** The participation decision matrix (Section 3) should be referenced in the Team Lead agent definition and the `/long-run` skill to ensure consistent decomposition.

2. **Require skip justifications.** Every bean.md should include skip notes (using the templates in Section 5) for every persona not assigned a task. This is already common practice but should be formalized.

3. **Add conditional inclusion to `/long-run`.** The `/long-run` skill's decomposition phase should reference these decision rules rather than relying on "skip inapplicable roles."

4. **Track participation metrics.** Future telemetry could track which personas are assigned vs. skipped, enabling data-driven refinement of these rules as the project evolves.

5. **Revisit when scope changes.** If beans start spanning multiple sessions or introducing new subsystems, revisit the BA and Architect skip defaults.

---

## 9. Summary

The Foundry AI team has organically converged on a lean participation model: **Developer + Tech-QA for code beans; Developer only for analysis/documentation beans; Team Lead direct for trivial fixes.** BA and Architect have never been needed because (a) the bean template captures requirements at sufficient granularity, and (b) architectural decisions are either pre-made or follow established patterns.

The critical rule is: **Tech QA must never be skipped for App/Infra beans that modify code.** For Process beans, Tech-QA participation depends on whether the bean produces executable artifacts.

This analysis provides a decision framework that preserves the Team Lead's judgment while reducing ambiguity. The templates and matrix should be treated as defaults — the escalation triggers (Section 6.2) ensure the team can bring in additional personas when execution reveals unexpected complexity.
