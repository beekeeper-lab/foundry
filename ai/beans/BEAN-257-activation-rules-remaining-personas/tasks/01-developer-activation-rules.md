# Task 01: Add "Activated When" Sections to All Library Personas

| Field         | Value     |
| ------------- | --------- |
| **Owner**     | developer |
| **Depends On** | —         |
| **Status**    | Done |
| **Started**   | 2026-04-17 19:35 |
| **Completed** | 2026-04-17 19:55 |
| **Duration**  | 20m |

## Goal

Add an "Activated When" section to every persona file in `ai-team-library/personas/*/persona.md`, following the BEAN-228/229 pattern already used in `.claude/agents/architect.md` and `.claude/agents/ba.md`. The section must read as **selection criteria from a bench** (per BEAN-269), not as scheduled participation. Update `.claude/agents/team-lead.md` to point at these library sections as the authoritative source. Add an audit note confirming coverage.

## Inputs

- `.claude/agents/architect.md` and `.claude/agents/ba.md` — reference format ("When You Are Activated" sections)
- `.claude/agents/team-lead.md` — Participation Decisions and per-persona engagement rules
- `ai-team-library/personas/*/persona.md` — 24 persona files to update
- `ai/context/bean-workflow.md` — wave model (Developer + Tech-QA mandatory; others opt-in)
- BEAN-269 wording (in this bean's Notes): bench model — team is an available bench, Developer + Tech-QA mandatory, others opt-in

## Section Format

Add a top-level `## Activated When` section near the top of each `persona.md` (after `## Mission` / `## Scope`, before `## Operating Principles`). Use this shape:

```markdown
## Activated When

The Team Lead pulls this persona from the bench when **ANY** of the following conditions apply:

1. **<Trigger name>** — <concrete, evaluable description>
2. **<Trigger name>** — <concrete, evaluable description>
...

**Not activated for:**
- <explicit exclusion>
- <explicit exclusion>

**Fallback rule:** <one sentence — when in doubt, do X>
```

For **Developer** and **Tech-QA**, replace the bench-pull preamble with a mandatory-default statement (e.g., "Activated by default on every bean that touches code…"), and still list the few cases where the persona is *not* needed.

## Per-Persona Triggers (audit & draft)

Apply the bench-model framing — selection from an available roster, not scheduled participation — to all 24 personas:

| Persona | Activation Stance |
|---------|-------------------|
| team-lead | Always-on coordinator; activated for every bean (codify) |
| ba | Already covered by `.claude/agents/ba.md`; mirror in library |
| architect | Already covered by `.claude/agents/architect.md`; mirror in library |
| developer | **Mandatory** for any bean that produces code; not activated for pure-content beans where Tech-QA can verify alone |
| tech-qa | **Mandatory** for every bean (no exceptions) |
| code-quality-reviewer | PR review on multi-file or risky changes; complexity hot-spots; performance concerns. Disambiguates vs. Tech-QA per BEAN-258 |
| ux-ui-designer | New UI surface, visual redesign, accessibility work, interaction flow changes |
| devops-release | Release cuts, deploy automation, CI/CD pipeline changes, environment config |
| integrator-merge-captain | Multi-branch merges, conflict resolution, release-train integration |
| security-engineer | New external surface, auth/authn changes, dependency security review, secret-handling code |
| compliance-risk | Regulatory-flagged scope (PII, financial data, audit-trail requirements) |
| researcher-librarian | Domain-knowledge gathering, prior-art surveys, citation work |
| technical-writer | User-facing docs, API reference, onboarding material, tutorials |
| data-analyst | Metrics analysis, A/B test review, telemetry interpretation |
| data-engineer | Pipeline/ETL changes, schema evolution, ingestion work |
| database-administrator | Schema migrations, index/perf tuning, backup/recovery design |
| legal-counsel | License review, contract obligations, IP concerns, terms-of-service |
| mobile-developer | Mobile-app feature work (iOS/Android/RN) |
| platform-sre-engineer | Reliability work, SLO/SLI definition, incident review, capacity planning |
| product-owner | Roadmap-impacting beans, prioritization conflicts, multi-stakeholder trade-offs |
| customer-success | Customer-facing comms, onboarding flows, feedback synthesis |
| financial-operations | Cost-impacting decisions, budget review, FinOps tagging |
| change-management | Org-process changes, training/comms for shipped behavior |
| sales-engineer | Demo flows, pre-sales technical specs, integration prototypes |

Tailor the trigger list to each persona's actual scope — don't copy-paste boilerplate.

## Steps

1. Read `.claude/agents/architect.md` and `.claude/agents/ba.md` "When You Are Activated" sections — these are the format reference.
2. For each of the 24 personas in `ai-team-library/personas/*/persona.md`, add an `## Activated When` section using the format above with persona-tailored triggers, exclusions, and fallback.
3. Update `.claude/agents/team-lead.md` Participation Decisions to add a one-line note: "For personas not covered above (security, devops-release, ux-ui, etc.), see the `Activated When` section in each persona's `persona.md` in the configured library."
4. Add a coverage audit note to `ai/context/team-lead.md` (or create one if missing) listing all 24 personas and confirming each has an `Activated When` section.
5. Run `uv run pytest` and `uv run ruff check foundry_app/` — must be clean.

## Acceptance Criteria

- [ ] All 24 persona files in `ai-team-library/personas/*/persona.md` contain an `## Activated When` section
- [ ] Each section follows the bench-model framing (selection from a roster, not scheduled participation)
- [ ] Developer + Tech-QA explicitly marked mandatory; others opt-in with concrete triggers
- [ ] `.claude/agents/team-lead.md` references the library sections as authoritative for personas it doesn't already cover
- [ ] Audit note exists confirming coverage for all 24 personas
- [ ] `uv run pytest` passes
- [ ] `uv run ruff check foundry_app/` passes

## Definition of Done

All 24 library persona files carry a tailored `Activated When` section, the team-lead agent points at them as authoritative, and the audit note confirms full coverage. Tests + lint clean.
