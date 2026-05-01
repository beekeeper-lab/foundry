# Orchestration Architecture

> **Audience:** anyone — human or agent — walking in cold to Foundry's
> bean execution model.
>
> **Status:** active. The model described here is implemented across
> BEAN-270 through BEAN-278 (the orchestration cluster). Cross-references
> at the bottom point at every active-behavior doc, ADR, agent file, and
> skill that participates.

Foundry treats a bean as a *unit of work executed by a team of
specialists*. The orchestration model says **how** that team is
assembled, **how** work is dispatched between specialists, and **how**
we know it is paying off.

The model rests on three principles. They were adopted as a cluster
because they only work together: the supervisor pattern is convention
unless you also engineer the context, and the context discipline is
unenforceable unless you also pin down what each specialist owes the
next.

```
┌───────────────────────── Three Principles ──────────────────────────┐
│                                                                     │
│   1. Supervisor Pattern  ──┐                                        │
│      (BEAN-270)            │                                        │
│                            ├─→  4. Architecture-Aware Evaluation   │
│   2. Context Engineering  ─┤      (BEAN-278)                       │
│      (BEAN-272/273/274)    │                                        │
│                            │                                        │
│   3. Specialist Contracts  ┘                                        │
│      (BEAN-271/273/275/276)                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Three Principles

### 1. Supervisor Pattern (BEAN-270, `/spawn-task`)

**Principle.** Each task in a wave is executed by a fresh specialist
worker — not by the orchestrator playing the role inline. The
specialist sees only the task's `Inputs:` plus the persona's own
context bundle. The orchestrator never accumulates role baggage.

**Mechanism.** The `/spawn-task` skill (`ai-team-library/claude/
skills/spawn-task/SKILL.md`, ADR-008 in `ai/context/decisions.md`)
is the single entry point for per-task dispatch. It auto-detects the
runtime:

- **In tmux** (`$TMUX` set): spawn a tmux child window in a git
  worktree. Process-isolated. Parallelizable. The pattern
  `/spawn-bean` already used for whole-bean dispatch, narrowed to a
  single task.
- **Not in tmux**: invoke the `Agent` tool with
  `subagent_type=<persona>`. Fresh subagent context inside the same
  Claude session.

```
                   Team-Lead (orchestrator)
                            │
              /spawn-task <task-file>
                            │
              ┌─────────────┴─────────────┐
              │                           │
         in tmux?                    not in tmux?
              │                           │
              ▼                           ▼
   tmux window + worktree           Agent(subagent_type=…)
   (process-isolated worker)        (in-process subagent)
              │                           │
              └─────────────┬─────────────┘
                            │
                  Worker reads ONLY:
                  • the task file
                  • files in Inputs:
                  • the persona's bundle
                  (NOT the bean folder,
                   NOT the orchestrator's
                   transcript)
                            │
                            ▼
                  Status file / Agent return
                            │
                            ▼
                   Team-Lead resumes
```

**What it replaces.** Before BEAN-270, "delegation" was prose: the
orchestrator wrote task files, then played Developer, then played
Tech-QA, all in one window. The supervisor pattern was convention
only. After BEAN-270, the supervisor is a real boundary.

**Reminder banner.** When `/spawn-task` runs *outside* tmux against
either a high-priority task or a bean with ≥4 remaining tasks, it
emits a one-line banner recommending tmux + `/long-run --fast`.
Larger bodies of work should not be supervised in-process if a
process-isolated alternative exists.

**Fallback.** In-conversation role-switching — the orchestrator
reading the task and executing it in the same window — survives as a
fallback for tiny tasks where dispatch overhead is not worth it. It
is **not** the default. See team-lead.md and
`.claude/skills/long-run/SKILL.md` Phase 4 for the dispatch hierarchy.

### 2. Context Engineering (BEAN-272, BEAN-273, BEAN-274)

**Principle.** Specialists read only what they need; the workflow
*enforces* that discipline at the dispatch boundary; the team can
only be assembled if every consumed artifact has a producer on the
team.

The principle has three teeth, one each from BEAN-272/273/274.

**Tooth A — Inputs validation at dispatch (BEAN-272).**
Every task file declares `Inputs:` (file paths the persona must
read). The hook
`ai-team-library/claude/hooks/validate-task-inputs.py` runs on the
task-status transition to `In Progress` and on every `/spawn-task`
dispatch. Empty, missing, or placeholder `Inputs:` blocks the
transition with a remediation message. One escape hatch:
`Inputs: NONE (justified: <≥10 chars>)`. Tracked in BEAN-278's
orchestration telemetry as `Inputs escape-hatch invocations` so the
team can spot if the hatch is being abused.

```
   Worker dispatch
        │
        ▼
   Read task file
        │
        ▼
   validate-task-inputs.py
        │
        ├─ Inputs populated  ─→ proceed
        ├─ Inputs: NONE (just) ─→ proceed; +1 to escape-hatch counter
        └─ empty / placeholder ─→ BLOCK; print remediation
```

**Tooth B — Produces/consumes contracts on personas (BEAN-273).**
Each core persona owns a sibling `contracts.yml` next to its
`persona.md` (e.g. `ai-team-library/personas/core/developer/
contracts.yml`). The file declares the artifact types the persona
*produces* and *consumes*. A registry at
`ai-team-library/contracts/artifact-types.yml` names every type
(currently 15: `bean-spec`, `task-spec`, `user-story`,
`acceptance-criteria`, `scope-definition`, `risk-register`, `adr`,
`design-spec`, `dev-decision`, `code-change`, `test-suite`,
`traceability-matrix`, `vdd-report`, `handoff-packet`,
`merge-summary`). Format and required fields per type live in the
registry; ADR-013 locks the contract location, the loader, and the
compiler-emission shape.

The compiler emits a flattened `contracts:` block at the bottom of
every generated `ai/team/composition.yml` so the contract graph is
addressable without reloading the library at runtime.

**Tooth C — Compose-time contract graph validation (BEAN-274).**
At project-generation time, `validate_contract_graph()` in
`foundry_app/services/validator.py` runs between validate and
scaffold. For each `consumes:` declaration on every persona, it
checks that *some* persona on the team declares the matching
`produces:`. Modes:

| Mode | Unsatisfied consume | Orphan produce |
|---|---|---|
| **Standard generation** (new project) | hard fail; remediation hint names the missing type and a producer to add | warning |
| **Overlay** (re-generation over existing project) | warning logged + recorded in `GenerationManifest` | warning |

The wizard's persona-selection page (`foundry_app/ui/screens/
builder/wizard_pages/persona_page.py`) shows a real-time team
coherence indicator (green/yellow/red) reflecting the same checks.

```
  Standard generation                   Overlay (re-generation)
  ───────────────────                   ──────────────────────
  Validate                              Validate
       │                                     │
       ▼                                     ▼
  validate_contract_graph                validate_contract_graph
       │                                     │
   unsatisfied ?                         unsatisfied ?
       │                                     │
       ├─ no  → Scaffold                     ├─ no  → Scaffold
       └─ yes → ABORT (clear error)          └─ yes → WARN + record in
                                                       GenerationManifest;
                                                       proceed
```

### 3. Specialist Contracts (BEAN-271, BEAN-273, BEAN-275, BEAN-276)

**Principle.** Each persona is a narrow specialist with explicit
boundaries — what it owns, what it does not author, what it produces
for downstream, what it consumes from upstream.

**Tiered library (BEAN-271).** Personas live in two on-disk tiers:
`ai-team-library/personas/core/` (the default 5 — team-lead, ba,
architect, developer, tech-qa) and `ai-team-library/personas/
extended/` (the 19 specialists, opt-in per composition).
`composition.yml` references core personas by bare name and extended
personas with the `extended/` tier prefix (e.g.
`extended/security-engineer`). See ADR-014 for the reference syntax
decision.

The tiering says: a "stable pool of specialist workers" requires a
visible default and a visible specialist bench. Generated projects
get the core 5 unless they ask for more.

**Acceptance-criteria ownership (BEAN-275).** Every core persona
file (library + Foundry kit) carries a "Scope Boundaries"
subsection. Two rules:

1. **AC ownership.** BA owns `acceptance-criteria` when on the wave.
   Team-Lead owns it by default (when BA is not activated).
   Developer, Architect, and Tech-QA *verify against* AC; they
   never author it. Mid-bean AC edits require Team-Lead approval
   plus a Notes-section entry on the bean.
2. **ADR vs dev-decision.** Blast-radius rule. **ADR** (Architect via
   `/internal:new-adr`): decision affects ≥3 modules, an external
   interface, a cross-cutting concern, or a future-irreversible
   commitment. **dev-decision** (Developer via
   `/internal:new-dev-decision`): local to one module, no external
   surface, reversible. When a Developer hits the threshold, they
   pause and request Architect activation rather than write a
   dev-decision unilaterally.

These rules used to be implicit and contradicted across persona
files (BA, Team-Lead, Developer, Architect, and Tech-QA all
"touched" AC). After BEAN-275 they are explicit and partition
cleanly.

**Typed handoffs (BEAN-276).** `/handoff <from> <to>` reads the
sender's `produces:`, the receiver's `consumes:`, computes the
intersection, and emits a typed packet with the artifact registry's
required fields per type. Plus a `pair-fields:` map in the registry
for sender/receiver pairs that need extras beyond the per-artifact
required fields (e.g., Developer→Tech-QA wants `test-targets`).
Missing required fields block the handoff. Every `/handoff` call
appends a row to `ai/handoffs/_index.md` for traceability.

The contract graph (BEAN-273) supplies the *shape* of every
handoff; BEAN-276 supplies the *enforcement*.

## Architecture-Aware Evaluation (BEAN-278)

The architectural review that prompted this cluster came with a
pointed warning: rather than just testing whether the final output
is good, evaluate whether the orchestrator, context routing, and
specialist roles **actually improve quality, cost, or reliability
enough to justify their added complexity**. Otherwise the
orchestration is theatre.

`/orchestration-report` is the answer. The skill lives at
`ai-team-library/claude/skills/orchestration-report/SKILL.md`.

**Per-bean instrumentation.** The bean template
(`ai/beans/_bean-template.md`) carries an Orchestration Telemetry
block alongside the existing per-task Telemetry table:

```markdown
## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | (comma-separated, actual not planned) |
| **Bounces** | 0 (Tech-QA → Developer kicks) |
| **Scope changes** | 0 (in-flight scope edits) |
| **Contract violations** | 0 (BEAN-274 catches at compose time) |
| **Inputs escape-hatch invocations** | 0 (BEAN-272's NONE-justified) |
| **Dispatch mode** | (in-process / tmux-worker / mixed) |
```

The PostToolUse telemetry hook (`.claude/hooks/telemetry-stamp.py`)
auto-populates `Personas activated` and `Dispatch mode`. Other
fields are persona-recorded. `/spawn-task` records the dispatch
mode it used; `/spawn-task` and `/handoff` increment Bounces when
Tech-QA opens a new task pointing back at Developer mid-bean.

**Aggregation.** `/orchestration-report` rolls up the per-bean
blocks across a date window:

- Average bounces by persona-set.
- Average cost-per-bean by persona count.
- Contract violations caught (BEAN-274) vs. missed and fixed via
  bounces.
- Escape-hatch trend over time.
- A one-paragraph verdict citing at least two metrics with values
  ("the supervisor pattern reduced average bean cost by N%" / "no
  measurable improvement; revisit").

**Honest verdict matters.** If the report shows the supervisor
pattern is *more* expensive without a quality offset, that is a
signal — not a failure. The whole point of architecture-aware
evaluation is to be willing to find out we were wrong.

Output lands at `ai/outputs/team-lead/orchestration-report-
YYYY-MM-DD.md`. Backfilling is **out of scope**: only beans created
after BEAN-278 landed carry the new section, so early reports will
have small samples.

## Programmatic VDD Gate (BEAN-277)

The Verification-Driven Development gate (`ai/context/vdd-policy.md`)
used to be prose review. After BEAN-277, `/vdd <bean-id>` parses the
bean's Acceptance Criteria checklist, runs each "concrete evidence"
check programmatically, and emits
`ai/outputs/tech-qa/vdd-<bean-id>.md` with structured pass/fail per
criterion plus an aggregate verdict.

Evidence types:

- **`test:`** — `pytest -k <pattern>` or path → run, capture
  pass/fail.
- **`lint:`** — `ruff check <path>` → run, capture clean/dirty.
- **`file:`** — glob existence check, optional content match.
- **`manual`** (default when no prefix) — emits a prompt for human
  confirmation, recorded in the report.

Convention for AC authors: prefix evidence type when known —
`- [ ] (test:tests/test_foo.py::test_bar) Foo behaves correctly`.
Backward-compatible: criteria without a prefix default to manual.

`/merge-bean` refuses to merge a bean whose VDD report is missing or
shows fail. The gate is no longer trust-based.

## Bean Lifecycle Under This Architecture

The bean lifecycle (`ai/context/bean-workflow.md`) has not changed —
Unapproved → Approved → In Progress → Done. What changed is what
happens *inside* In Progress.

```
  ┌───────────────────────────────────────────────────────────────┐
  │  Unapproved ─→ Approved (human)                               │
  │     │                                                          │
  │     ▼                                                          │
  │  Approved ─→ In Progress (Team-Lead via /pick-bean)            │
  │     │                                                          │
  │     ▼                                                          │
  │ ┌─ In Progress ───────────────────────────────────────────┐   │
  │ │                                                          │   │
  │ │  Decompose into tasks                                    │   │
  │ │     • each task has Inputs:                              │   │
  │ │     • Tech-QA mandatory; BA/Architect opt-in (rules)    │   │
  │ │                                                          │   │
  │ │  ┌─ For each task in dependency order ─────┐             │   │
  │ │  │                                          │             │   │
  │ │  │ /spawn-task <task-file>     ◄─ BEAN-270 │             │   │
  │ │  │      │                                  │             │   │
  │ │  │      ▼                                  │             │   │
  │ │  │ validate-task-inputs hook   ◄─ BEAN-272 │             │   │
  │ │  │      │                                  │             │   │
  │ │  │      ▼                                  │             │   │
  │ │  │ Specialist worker                       │             │   │
  │ │  │   • reads task Inputs only              │             │   │
  │ │  │   • produces typed artifact             │             │   │
  │ │  │     (per contracts.yml)  ◄── BEAN-273   │             │   │
  │ │  │      │                                  │             │   │
  │ │  │      ▼                                  │             │   │
  │ │  │ /handoff <from> <to>        ◄─ BEAN-276 │             │   │
  │ │  │   • typed packet, pair-fields           │             │   │
  │ │  │   • appended to handoffs/_index.md      │             │   │
  │ │  └──────────────────────────────────────────┘             │   │
  │ │                                                          │   │
  │ │  /vdd <bean-id>             ◄────── BEAN-277             │   │
  │ │      │                                                   │   │
  │ │      ▼                                                   │   │
  │ │  vdd-<bean-id>.md report                                 │   │
  │ │                                                          │   │
  │ │  Orchestration Telemetry      ◄── BEAN-278               │   │
  │ │     populated automatically + persona-recorded            │   │
  │ │                                                          │   │
  │ └──────────────────────────────────────────────────────────┘   │
  │     │                                                          │
  │     ▼                                                          │
  │  /merge-bean                                                   │
  │     • REFUSES if VDD report missing or failing  ◄── BEAN-277  │
  │     │                                                          │
  │     ▼                                                          │
  │  Done                                                          │
  └───────────────────────────────────────────────────────────────┘
```

**Compose-time gates (run at project-generation time, not
bean-execution time):**

| Gate | Bean | Condition |
|---|---|---|
| Contract graph coherence | BEAN-274 | Every `consumes:` matched by a `produces:` on the team |
| Standard mode hard-fail | BEAN-274 | New generations cannot ship with an unsatisfied consume |
| Overlay mode warn-and-proceed | BEAN-274 | Re-generation over an existing project does not break |

**Per-task gates (run on every task dispatch):**

| Gate | Bean | Condition |
|---|---|---|
| `Inputs:` populated | BEAN-272 | Block dispatch if empty/missing/placeholder |
| Escape-hatch tracked | BEAN-272 | `Inputs: NONE (justified: …)` allowed; counted |

**Per-handoff gate (run on every `/handoff`):**

| Gate | Bean | Condition |
|---|---|---|
| Required artifact fields present | BEAN-276 | Block handoff if a required field is missing |

**Per-bean gate (run before `/merge-bean`):**

| Gate | Bean | Condition |
|---|---|---|
| Programmatic VDD | BEAN-277 | `/merge-bean` refuses to merge without a passing `vdd-<bean-id>.md` |

## What This Architecture Does and Does Not Promise

**Promises.**

- Each specialist sees only what its task declared it needs.
- Each handoff carries the fields the receiver was promised.
- A team that cannot internally satisfy its own consumes never
  reaches scaffold.
- A bean whose AC has not been programmatically verified does not
  merge.
- The cost of all of the above is measured per-bean and aggregated
  per-cycle, so the team can tell whether the orchestration is
  paying for itself.

**Does not promise.**

- That artifact *content* is correct. The contract graph
  (BEAN-273/274) checks that some persona produces a type, not that
  the produced artifact is well-formed against its schema. The
  programmatic VDD (BEAN-277) closes part of this gap on a
  per-criterion basis.
- That extended-tier personas have full contract coverage. BEAN-273
  declared contracts only for the core 5; extended personas are a
  follow-up.
- That every prose document and handoff template inside a generated
  project enforces the typed shape — `/handoff` does at runtime; the
  generated agent files include the typed-handoff workflow but the
  enforcement lives in the skill, not the agent prose.

## Cross-References

**Active-behavior docs**

- `ai/context/bean-workflow.md` — full lifecycle: status values,
  approval gate, decomposition, comprehension gate, micro-iteration
  loop, branch strategy.
- `ai/context/vdd-policy.md` — the policy that BEAN-277's `/vdd`
  command automates. The policy stays prose; the gate gets
  automation.
- `CLAUDE.md` — project entry point; references this doc and the
  cluster's commands.
- `README.md` — top-level pipeline + lifecycle paragraph; orchestration
  model summary lives in the AI Team & Beans Workflow section.
- `ai/context/project.md` — module map; `validate_contract_graph()`
  and `vdd.py` are services.

**ADRs (in `ai/context/decisions.md`)**

- **ADR-008** — `/spawn-task` per-task dispatch mechanism (BEAN-270).
- **ADR-013** — Persona produces/consumes contracts: format,
  registry, loader, compiler emission (BEAN-273).
- **ADR-014** — Extended-persona reference syntax in
  `composition.yml` (BEAN-271).
- **ADR-015** — Orchestration Architecture as a coordinated cluster
  (this doc; pointer at the bottom of decisions.md).

**Agent files (`.claude/agents/`)**

- `team-lead.md` — orchestration rules, participation decisions, AC
  ownership rule, ADR-threshold escalation, `/spawn-task` as the
  preferred per-task dispatch.
- `ba.md` — Scope Boundaries: BA owns `acceptance-criteria` when on
  the wave.
- `architect.md` — Scope Boundaries: ADR ownership, dev-decision
  threshold.
- `developer.md` — Scope Boundaries: dev-decision boundary, escalation
  to Architect at the ADR threshold.
- `tech-qa.md` — Scope Boundaries: verifies against AC, never
  authors; `/vdd` is the programmatic gate.

**Skills & commands** (canonical specs in
`ai-team-library/claude/skills/<name>/SKILL.md`; commands are
≤30-line triggers per BEAN-249)

- `/spawn-task` — per-task dispatch (BEAN-270).
- `/handoff` — typed handoff (BEAN-276).
- `/vdd` — programmatic VDD gate (BEAN-277).
- `/orchestration-report` — architecture-aware aggregator
  (BEAN-278).
- `/long-run` — autonomous backlog processor; uses `/spawn-task` for
  per-task dispatch in Phase 4.

**Source beans**

| Bean | Title |
|---|---|
| BEAN-270 | `/spawn-task` Persona-Scoped Delegation Command |
| BEAN-271 | Tier Library Personas — `core/` vs `extended/` |
| BEAN-272 | Validate Task `Inputs:` at Dispatch (Pre-Execution Hook) |
| BEAN-273 | Persona `produces:` / `consumes:` Contracts |
| BEAN-274 | Compose-Time Contract Graph Validator |
| BEAN-275 | Resolve Acceptance Criteria & ADR Boundary Ownership |
| BEAN-276 | Role-Aware Handoff Schemas |
| BEAN-277 | Programmatic VDD Gate Skill |
| BEAN-278 | Architecture-Aware Telemetry & `/orchestration-report` |
| BEAN-279 | Orchestration Architecture Doc + Documentation Sweep (this doc) |
