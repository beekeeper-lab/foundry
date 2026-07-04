# ADR-015: Orchestration Architecture as a Coordinated Cluster

| Field | Value |
|-------|-------|
| **Date** | 2026-05-01 |
| **Status** | Accepted |
| **Bean** | BEAN-279 |
| **Deciders** | Architect (cluster), Team-Lead (synthesis) |

> **Practice note (2026-07 audit, SPEC-029):** the cluster's mechanisms were largely aspirational in practice — 3 VDD reports and 1 handoff packet across ~294 Done beans, telemetry collected but never aggregated. The 2026-07 audit implementation (SPEC-005/008/009) converted the load-bearing gates to hooks and built the aggregator; read this ADR as intent, with enforcement status tracked in bean-workflow.md's Gate Enforcement Status table.

## Context

BEAN-270 through BEAN-278 changed how Foundry's bean execution works. Each individual bean made a sound, contained decision (some with their own ADRs — ADR-008 for `/spawn-task` dispatch, ADR-013 for produces/consumes contracts, ADR-014 for extended-persona reference syntax), but the architectural review that prompted the cluster framed them as **one coordinated change** rather than nine independent ones. The supervisor pattern (BEAN-270) is convention without contracts (BEAN-273) and Inputs validation (BEAN-272). Specialist contracts (BEAN-273) are unenforced without compose-time validation (BEAN-274) and typed handoffs (BEAN-276). And the whole stack pays for itself only if its cost is measurable (BEAN-278).

This ADR records the cluster-level decision to keep the long-form architectural narrative in one canonical document and to treat that document as the single source of truth for "what this orchestration model does and what it does not promise." Without that anchor, anyone — human or agent — coming in cold has to reconstruct the model by reading nine bean files.

## Decision

**1. Adopt the three-principles + evaluation framing as the canonical model.** Foundry's bean execution is described as: (1) supervisor pattern, (2) context engineering, (3) specialist contracts, with (4) architecture-aware evaluation as the feedback loop that keeps the first three honest. Each of BEAN-270..278 maps to exactly one of those four slots. New beans that touch orchestration must declare which slot they affect.

**2. Long-form home is `ai/context/orchestration-architecture.md`.** Flat alongside `bean-workflow.md`, `vdd-policy.md`, and `project.md`. Not nested under a new `architecture/` subdirectory. **Rationale:** the file lives next to the other policy docs so a single `ls ai/context/` discovers it. A new subdirectory fragments the policy surface; the existing flat structure already organizes ~16 docs without trouble. The long-form covers the three principles, the evaluation methodology, the bean lifecycle under the new model, and a cross-reference index.

**3. ADR responsibilities split.** Per-decision ADRs (ADR-008, ADR-013, ADR-014) carry the *contract* for a single bean's structural choice. This ADR (ADR-015) carries the *connective tissue* — why the cluster lands as a cluster, what each bean contributes to the joint model, and where a cold reader should start. ADR-008/013/014 are the wire format; ADR-015 is the system diagram.

**4. Documentation checklist anchor.** `MEMORY.md`'s documentation checklist gains `ai/context/orchestration-architecture.md` as a permanent "Always check" entry. Future orchestration-touching beans must update this doc in the same commit they land their behavior change. Doc rot in this file is the leading indicator the cluster is drifting out of sync with implementation.

## Consequences

**Positive.**
- A cold reader (human or agent) has one document to read to understand the orchestration model. The cross-reference index at the bottom of the long-form doc fans out to per-bean detail when needed.
- Future beans that touch orchestration declare which principle they extend, making it easier to spot when a fourth principle is being introduced (signal: rewrite the cluster framing) versus when an existing principle is being deepened (signal: extend the relevant section).
- The architecture-aware evaluation slot (BEAN-278's `/orchestration-report`) is now first-class in the model. If the report shows the cluster is not paying off, the architecture itself is up for revision.

**Negative.**
- One more "always check" doc in the documentation checklist. Mitigated: the doc lives where every other policy doc lives, so the cost is visibility, not navigation.
- The three-principles framing is a synthesis chosen by this ADR — it is not the only possible framing. Risk: it freezes a particular vocabulary. Mitigation: the framing maps cleanly onto the Anthropic supervisor-pattern guidance the cluster was built against, so divergence would be a real signal that Foundry's model has moved beyond that template.

## Alternatives Rejected

1. **Per-bean ADRs only; no cluster-level ADR.** Rejected. The per-bean ADRs document per-bean structural choices but do not document why the bundle exists as a bundle. A cold reader who reads ADR-008, ADR-013, and ADR-014 in isolation gets three good local decisions and no joined-up picture of the supervisor pattern + context engineering + specialist contracts as one design.
2. **Long-form doc inside `ai/context/architecture/orchestration.md`** (new subdirectory). Rejected per Decision 2 — fragments the flat policy surface for no readability win.
3. **Embed the long-form narrative directly inside `bean-workflow.md`.** Rejected. `bean-workflow.md` describes the lifecycle (status values, approval gate, comprehension gate). The orchestration architecture describes how specialists are dispatched, contracted, and evaluated *during* In Progress. Different concerns; mixing them would bloat `bean-workflow.md` past readable size.
4. **Stop at `MEMORY.md` notes.** Rejected. `MEMORY.md` is per-user persistent memory, gitignored from the foundry repo. The orchestration architecture is a project-level commitment that needs to live in the repo where every contributor sees it.

## Reversibility

Mostly reversible. Rolling back this ADR means deleting `ai/context/orchestration-architecture.md`, removing the entry from `MEMORY.md`'s checklist, and reverting the cross-reference adds in CLAUDE.md, README.md, the agent files, and the `/long-run` skill/command. Per-bean ADRs (ADR-008/013/014) and the BEAN-270..278 implementations stay; this ADR's reversal only removes the synthesis layer. The cost is rebuilding the joint model in a reader's head from nine separate beans — the very cost this ADR was written to avoid.

## Pointer

Long-form architectural document: **`ai/context/orchestration-architecture.md`**.

