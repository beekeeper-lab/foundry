# Persona Activation Audit

**Bean:** BEAN-257 — Activation Rules for Remaining Personas
**Date:** 2026-04-17
**Source of truth:** `ai-team-library/personas/<persona>/persona.md` → `## Activated When` section

This audit confirms that every persona shipped in the default library carries an explicit `Activated When` section that the Team Lead consults during decomposition. The bench model (BEAN-269) governs how those rules are applied: the team is an available roster; Developer + Tech-QA are mandatory; every other persona is pulled in only when their activation triggers fire.

## Coverage Matrix

| # | Persona | Activation Stance | Section Present |
|---|---------|-------------------|-----------------|
| 1 | team-lead | **Always-on** coordinator (no opt-out) | ✓ |
| 2 | ba | Opt-in (full mode = always; partial mode = trigger-based) | ✓ |
| 3 | architect | Opt-in (9 structural / decision-bearing triggers) | ✓ |
| 4 | developer | **Mandatory** for any code-touching bean | ✓ |
| 5 | tech-qa | **Mandatory for every bean — no exceptions** | ✓ |
| 6 | code-quality-reviewer | Opt-in (multi-file, hot-spot, convention-drift; scope split with Tech-QA per BEAN-258) | ✓ |
| 7 | ux-ui-designer | Opt-in (new UI surface, redesign, a11y) | ✓ |
| 8 | devops-release | Opt-in (release, deploy, CI/CD, build reproducibility) | ✓ |
| 9 | integrator-merge-captain | Opt-in (multi-branch, conflict, release-train integration) | ✓ |
| 10 | security-engineer | Opt-in (auth, external surface, sensitive data, dependency review) | ✓ |
| 11 | compliance-risk | Opt-in (regulated data, audit trail, consent, cross-border) | ✓ |
| 12 | researcher-librarian | Opt-in (prior-art, vendor eval, RFC research, literature review) | ✓ |
| 13 | technical-writer | Opt-in (user-facing docs, API reference, release notes, migration guide) | ✓ |
| 14 | data-analyst | Opt-in (KPI, A/B test, telemetry interpretation, dashboard) | ✓ |
| 15 | data-engineer | Opt-in (pipeline, schema evolution, ingestion, backfill) | ✓ |
| 16 | database-administrator | Opt-in (migration, index tuning, backup/HA, capacity) | ✓ |
| 17 | legal-counsel | Opt-in (license, IP, contract/ToS, trademark, export-control) | ✓ |
| 18 | mobile-developer | Opt-in (mobile feature, native API, store, parity) | ✓ |
| 19 | platform-sre-engineer | Opt-in (SLO, observability, incident, capacity) | ✓ |
| 20 | product-owner | Opt-in (roadmap impact, prioritization conflict, sunset) | ✓ |
| 21 | customer-success | Opt-in (customer comms, onboarding, support material, escalation) | ✓ |
| 22 | financial-operations | Opt-in (cost-impacting infra, vendor, FinOps maturity) | ✓ |
| 23 | change-management | Opt-in (workflow change, training, cross-team rollout) | ✓ |
| 24 | sales-engineer | Opt-in (demo, POC, RFP response, integration prototype) | ✓ |

**Total:** 24 / 24 personas covered.

## Section Format

Every `Activated When` section follows the BEAN-228/229 pattern:

```markdown
## Activated When

The Team Lead pulls this persona from the bench when **ANY** of the following conditions apply:

1. **<Trigger name>** — <concrete, evaluable description>
...

**Not activated for:**
- <explicit exclusion>
- <explicit exclusion>

**Fallback rule:** <one sentence — when in doubt, do X>
```

Mandatory personas (team-lead, developer, tech-qa) replace the bench-pull preamble with a "mandatory by default" statement and a curated list of exceptions (or "no exclusions" for tech-qa).

## Authoritative Reference

- For Architect and BA, the project-level `.claude/agents/architect.md` and `.claude/agents/ba.md` are the operational reference for the Foundry team. The library `persona.md` files mirror these for downstream projects generated from the library.
- For all other personas, the library `persona.md` `Activated When` section is authoritative. The Team Lead agent doc (`.claude/agents/team-lead.md`) points at these as the source of truth.

## How to Apply

When decomposing a bean:

1. Always include Team Lead, Developer (if code), and Tech-QA on the wave.
2. For Architect and BA, evaluate the engagement rule tables in `.claude/agents/team-lead.md`.
3. For every other persona, open the persona's `persona.md` and check its `Activated When` triggers against the bean scope.
4. Pull each persona from the bench whose triggers fire. Annotate skipped optional personas with `> Skipped: <persona> (<one-line reason>)` in the bean's Tasks section.
5. The bench model is non-negotiable: a persona that does not have an active trigger does not get scheduled "just in case."

## Maintenance

When adding a new persona to the library:

1. Author `persona.md` with all standard sections.
2. **Add an `Activated When` section** between `## Scope` and `## Operating Principles`.
3. Update this audit table with the new persona and stance.
4. If the new persona has activation interaction with another persona (e.g., scope split per BEAN-258), document the boundary in both `persona.md` files.

## Related Beans

- **BEAN-228** — Architect Engagement Rules (precedent)
- **BEAN-229** — BA Engagement Rules (precedent)
- **BEAN-258** — CQR vs Tech-QA scope split (referenced in code-quality-reviewer activation triggers)
- **BEAN-269** — Bench-model orchestration policy (framing applied throughout this work)
