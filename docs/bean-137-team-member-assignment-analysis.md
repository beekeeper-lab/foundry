# BEAN-137: Team Member Assignment Analysis

**Date:** 2026-02-16
**Analyst:** developer (Process analysis bean)
**Data source:** All 135 completed beans in `ai/beans/_index.md`, agent definitions in `.claude/agents/`, task tables in `bean.md` files

---

## 1. Overview

The Foundry AI team defines five personas — Team Lead, BA, Architect, Developer, and Tech-QA — each with distinct responsibilities documented in `.claude/agents/`. This analysis examines how these personas are actually assigned to bean tasks across the entire backlog history (BEAN-001 through BEAN-135), quantifying utilization rates, skip patterns, and the gap between defined roles and actual usage.

**Key finding:** The team operates a **Developer-centric execution model** where BA and Architect are almost entirely bypassed. Developer and Tech-QA carry the workload, with Team Lead serving as orchestrator and occasional direct implementer.

---

## 2. Defined Roles vs Actual Utilization

### 2.1 Persona Role Definitions (from `.claude/agents/`)

| Persona | Defined Role | Key Outputs |
|---------|-------------|-------------|
| **Team Lead** | Orchestrate work, decompose beans, route to specialists, enforce stage gates | Task decompositions, progress dashboards, coordination |
| **BA** | Translate business needs into requirements, write user stories with Given/When/Then criteria, define scope boundaries | User stories, scope definitions, risk registers |
| **Architect** | Own architectural decisions, create ADRs, design API contracts and component boundaries | ADRs, design specs, interface definitions |
| **Developer** | Implement features and fixes, write tests alongside code, make implementation-level decisions | Code changes, unit tests, decision records |
| **Tech-QA** | Ensure deliverables meet acceptance criteria, design test strategies, perform code reviews | Traceability matrices, QA reports, test results |

### 2.2 Actual Utilization Summary

| Persona | Beans Assigned | Tasks Assigned | Utilization Rate | Last Active |
|---------|---------------|----------------|-----------------|-------------|
| **Developer** | ~80+ beans | ~150+ tasks | ~100% of decomposed beans | BEAN-135 (current) |
| **Tech-QA** | ~55+ beans | ~65+ tasks | ~70% of decomposed beans | BEAN-130 |
| **Team Lead** (direct) | ~8 beans | ~25 tasks | ~6% (as implementer) | BEAN-079 |
| **Architect** | 4 beans | 4 tasks | ~3% | BEAN-126 |
| **BA** | 3 beans | 3 tasks | ~2% | BEAN-005 |

---

## 3. Assignment Patterns by Bean Category

### 3.1 App Category (Application Changes) — 103 beans

**Dominant pattern:** Developer (implementation) → Tech-QA (verification)

Typical decomposition for an App bean:
```
Task 1: Implement feature/fix          → Developer
Task 2: Write/update tests             → Tech-QA (depends on T1)
Task 3: Run full test suite & lint     → Tech-QA (depends on T2)
```

**Exceptions:**
- BEAN-002 (Generator Overlay): Full wave — BA → Architect → Developer → Tech-QA. This was the most complex early bean, requiring requirements gathering and design.
- BEAN-004 (Safety Source Dirs): Full wave — BA → Architect → Developer → Tech-QA. Involved new Pydantic model design.
- BEAN-028 (Asset Copier Service): Architect → Developer → Tech-QA. Required interface design before implementation.
- BEAN-126 (Native Claude Code Hooks): Architect → Developer → Tech-QA. Required design mapping between hook pack format and native hook format.

**BA in App beans:** 2 out of 103 (1.9%)
**Architect in App beans:** 4 out of 103 (3.9%)
**Developer in App beans:** ~100% (universal)
**Tech-QA in App beans:** ~85% (skipped only when Team Lead did everything directly)

### 3.2 Process Category (Workflow/Skills/Analysis) — 25 beans

**Two sub-patterns emerged:**

**Pattern A — Process Implementation** (e.g., BEAN-006, 007, 010, 080, 120-122):
```
Task 1-N: Implement skill/workflow changes → Developer
Task N+1: Verify tests and lint            → Tech-QA
```

**Pattern B — Process Analysis** (BEAN-131, 132, 133, 135):
```
Task 1: Read source and write analysis doc → Developer
Task 2: Review against acceptance criteria → Team Lead (optional)
```

**BA in Process beans:** 1 out of 25 (4%) — only BEAN-005
**Architect in Process beans:** 0 out of 25 (0%)
**Tech-QA in Process beans:** ~60% (skipped for analysis-only beans)

### 3.3 Infra Category (Git/CI/Deployment) — 7 beans

**Pattern:** Developer → Tech-QA (same as App)

Examples: BEAN-008 (Feature Branch Workflow), BEAN-009 (Push Hook Refinement), BEAN-012 (Enforce Branch Workflow), BEAN-013 (Deploy Command)

**BA in Infra beans:** 0 out of 7 (0%)
**Architect in Infra beans:** 0 out of 7 (0%)

---

## 4. Skip Patterns and Documented Reasons

### 4.1 BA Skip Analysis

**Skip rate: ~98%** (3 assignments out of 135 beans)

The BA was assigned tasks only in BEAN-002, BEAN-004, and BEAN-005 — all within the first five beans of the project. After BEAN-005, the BA has never been assigned a task.

**Documented skip reasons (representative sample):**

| Bean | Skip Reason |
|------|------------|
| BEAN-001 | "Requirements are clear in the bean" |
| BEAN-003 | "No requirements ambiguity" |
| BEAN-006 | "Requirements are clear in the bean" |
| BEAN-010 | "Architecture sketch is already in the bean" |
| BEAN-128 | "No requirements ambiguity or design decisions for this simple list addition" |
| BEAN-131-135 | "Process analysis bean — no requirements gathering needed" |

**Root cause analysis:** The bean template itself serves as the requirements document. By the time a bean reaches execution, the Problem Statement, Goal, Scope, and Acceptance Criteria are already defined. The BA's role of "translating business needs into requirements" is performed upstream during bean creation (usually by the Team Lead or user during `/backlog-refinement`).

### 4.2 Architect Skip Analysis

**Skip rate: ~97%** (4 assignments out of 135 beans)

The Architect was assigned tasks in BEAN-002, BEAN-004, BEAN-028, and BEAN-126. Three of these were in the first 28 beans. The most recent assignment was BEAN-126 (Native Claude Code Hooks), which required mapping between two different format systems.

**Documented skip reasons:**

| Bean | Skip Reason |
|------|------------|
| BEAN-001 | "Implementation follows the existing seeder pattern" |
| BEAN-003 | "No architectural decisions. This bean creates markdown command/skill files, not Python code" |
| BEAN-011 | "Architecture sketch is already in the bean" |
| BEAN-128 | "No architecture decisions needed — this is a list addition" |
| BEAN-131-135 | "No system design decisions — this is a read-only analysis" |

**Root cause analysis:** The application architecture stabilized early (around BEAN-016 through BEAN-032 which established the core service layer). After that, most work is implementation within established patterns. When design decisions are needed, they tend to be embedded in the bean definition itself rather than requiring a separate design phase.

### 4.3 Tech-QA Skip Analysis

**Skip rate: ~15-30%** (significantly lower than BA/Architect)

Tech-QA is skipped only in specific circumstances:
1. **Analysis-only beans** (BEAN-131-135): "No code changes to test — output is documentation artifact only"
2. **Team Lead direct implementation** (BEAN-059, 075-079): Team Lead did both implementation and verification
3. **Some CRUD beans** (BEAN-081-108): Developer ran tests directly as part of implementation

### 4.4 Developer Skip Analysis

**Skip rate: ~0%** — Developer is assigned to every decomposed bean without exception.

The Developer is the only persona that has never been skipped. Even analysis beans assign the "analysis and write document" task to the Developer persona.

---

## 5. Team Lead as Direct Implementer

An unexpected pattern: the Team Lead occasionally bypasses the specialist personas entirely and implements beans directly. This occurred in approximately 8 beans:

| Bean | What Team Lead Did | Why |
|------|-------------------|-----|
| BEAN-059 | Theme wiring fix (2 tasks) | Trivial 2-line fix |
| BEAN-075 | Auto-detect library root (4 tasks) | Small feature, self-contained |
| BEAN-076 | Sidebar nav button restyle (1 task) | UI tweak |
| BEAN-077 | Wizard nav validation feedback (5 tasks) | Widget state management |
| BEAN-078 | Wizard empty-state messaging (5 tasks) | UI labels and visibility toggles |
| BEAN-079 | Obsidian MCP integration (7 tasks) | Infrastructure setup, not code |
| BEAN-014 | Progress dashboard design (1 task) | Template design, not code |
| BEAN-131 | Analysis review (1 task) | Verification of analysis output |

**Pattern:** Team Lead implements directly when the bean is:
- A trivial fix (1-2 lines)
- Infrastructure/configuration (no code review needed)
- UI tweaks within the Team Lead's recent context
- Template/document design tasks

---

## 6. Task Count Distribution

### 6.1 Tasks Per Bean by Category

| Category | Avg Tasks | Min | Max | Typical Pattern |
|----------|-----------|-----|-----|-----------------|
| App (implementation) | 2-4 | 1 | 7 | Developer(1-5) + Tech-QA(1-2) |
| App (CRUD batch) | 1-3 | 1 | 3 | Developer(1-2) + Tech-QA(0-1) |
| Process (implementation) | 3-5 | 2 | 5 | Developer(2-4) + Tech-QA(1) |
| Process (analysis) | 1-2 | 1 | 2 | Developer(1) + Team Lead(0-1) |
| Infra | 2 | 2 | 2 | Developer(1) + Tech-QA(1) |

### 6.2 Task Ownership Distribution (Estimated)

| Persona | Total Tasks | % of All Tasks |
|---------|-------------|----------------|
| Developer | ~150+ | ~60-65% |
| Tech-QA | ~65+ | ~25-28% |
| Team Lead (direct) | ~25 | ~8-10% |
| Architect | 4 | ~1.5% |
| BA | 3 | ~1.2% |

---

## 7. Evolution Over Time

The assignment pattern has evolved through three distinct phases:

### Phase 1: Full Wave (BEAN-001 through BEAN-005)
- All four specialist personas were utilized
- BA → Architect → Developer → Tech-QA pipeline followed
- Established the workflow but proved heavyweight for most beans

### Phase 2: Developer + Tech-QA (BEAN-006 through BEAN-130)
- BA and Architect dropped from routine usage
- Skip reasons documented consistently
- Developer handles all implementation; Tech-QA handles verification
- Team Lead occasionally does direct implementation for trivial beans

### Phase 3: Lean Analysis (BEAN-131 through BEAN-135+)
- Analysis beans use Developer-only (no Tech-QA)
- Minimal task decomposition (1-2 tasks per bean)
- Fastest execution model

**Transition triggers:**
- Phase 1→2: Realization that bean definitions already contain sufficient requirements and the architecture had stabilized
- Phase 2→3: Batch of analysis beans where code verification was not applicable

---

## 8. Key Findings

### Finding 1: The BA Persona is Effectively Retired
The BA has not been assigned a task since BEAN-005 (bean #5 of 135). The bean template and `/backlog-refinement` skill have absorbed the BA's requirements-gathering function. Requirements are captured during bean creation, not during execution.

### Finding 2: The Architect Persona is Event-Driven
The Architect activates only when genuine design decisions are needed (4 out of 135 beans = 3%). The last activation was BEAN-126, which required mapping between two different configuration formats. This is appropriate — not every change needs architectural review.

### Finding 3: Developer is the Execution Bottleneck
Developer is assigned to 100% of decomposed beans and ~60-65% of all tasks. This creates a sequential dependency: nothing moves forward without Developer completing tasks. In a single-agent model this is fine, but it means the Developer persona's instructions carry outsized influence on output quality.

### Finding 4: Tech-QA Consistently Gates Quality
Tech-QA is assigned to ~70-85% of beans, always as the final verification step. This creates a clean quality gate: Developer implements, Tech-QA verifies. The pattern is well-established and appears effective (248 tests in the suite).

### Finding 5: Team Lead Bypasses the Wave for Small Work
When the Team Lead implements beans directly (BEAN-059, 075-079), it bypasses all specialist personas. This is efficient for trivial work but creates a precedent where quality gates (Tech-QA) may be skipped.

### Finding 6: Skip Reasons Are Consistent and Documented
Every persona skip includes a documented reason in the bean.md file. The reasons are formulaic but accurate. This is good practice — it creates an audit trail for why personas were excluded.

---

## 9. Comparison: Defined vs Actual Team Model

| Aspect | Defined Model | Actual Model |
|--------|--------------|--------------|
| **Team size** | 5 personas (lead + 4 specialists) | Effectively 2-3 active personas |
| **Pipeline** | BA → Architect → Developer → Tech-QA | Developer → Tech-QA |
| **Requirements** | BA writes user stories from business needs | Bean template captures requirements at creation |
| **Design** | Architect creates ADRs and design specs | Developer makes design decisions inline |
| **Verification** | Tech-QA performs independent code review | Tech-QA runs tests and lint |
| **Orchestration** | Team Lead coordinates only | Team Lead coordinates AND sometimes implements |

---

## 10. Recommendations

### 10.1 Formalize the Two-Persona Execution Model
The actual workflow is Developer + Tech-QA for the vast majority of beans. Rather than documenting BA/Architect skip reasons on every bean, consider formalizing this as the **default** with BA and Architect as **opt-in** for beans that need them.

### 10.2 Define Architect Trigger Criteria
Since the Architect activates so rarely, define explicit criteria for when architectural review is required. Suggested triggers:
- New service or module creation
- Cross-module interface changes
- New external dependency introduction
- Data model schema changes affecting 3+ modules

### 10.3 Consider Retiring or Repurposing the BA
The BA's defined outputs (user stories, scope definitions) are produced by the bean creation process itself. Options:
- **Retire**: Remove BA from the agent roster; document that requirements live in bean definitions
- **Repurpose**: Transform BA into a "Requirements Reviewer" that validates bean definitions before approval
- **Preserve**: Keep BA dormant for future beans with genuine requirements ambiguity

### 10.4 Strengthen Tech-QA Independence
Tech-QA currently runs after Developer with a dependency on their output. Consider:
- Having Tech-QA review the bean's acceptance criteria before Developer starts (shift-left)
- Tech-QA writing test stubs before Developer implements (TDD-style)

### 10.5 Audit Team Lead Direct Implementation
When Team Lead implements directly, quality gates may be skipped. Consider requiring at least a lint/test verification step even for Team Lead-implemented beans.

---

## 11. Data Quality Notes

- **Coverage:** This analysis examined all 135 beans in `_index.md` with task table data from `bean.md` files
- **Counting method:** Task owners were extracted from the `## Tasks` table in each `bean.md`; telemetry tables were excluded from task counts
- **Approximate counts:** Some beans (particularly BEAN-038 through BEAN-070) have minimal task table data, so counts may slightly underrepresent Developer and Tech-QA assignments
- **Team Lead telemetry rows** show "All tasks | team-lead" for most beans, which reflects orchestration overhead, not direct implementation

---

## 12. Summary

The Foundry AI team's five-persona model has naturally converged on a **lean two-persona execution pipeline** (Developer + Tech-QA) for 97% of beans. BA and Architect served their purpose in the project's first five beans and during rare architectural decisions, but the bean template system and stable architecture have made them largely unnecessary for routine work. This is not a failure — it's an efficient adaptation. The team should formalize this reality rather than continuing to document skip reasons on every bean.
