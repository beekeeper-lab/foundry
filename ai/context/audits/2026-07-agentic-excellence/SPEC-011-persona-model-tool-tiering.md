# SPEC-011: Per-persona model and tool tiering in the composition schema

- **Priority:** P1
- **Effort:** M
- **Area:** pipeline
- **Depends on:** SPEC-001 (generated agents must emit frontmatter for `model:`/`tools:` to land anywhere)
- **Status:** Proposed

## Problem

Every persona in a generated team runs with the same model and unrestricted tools. A first-rate agentic team right-sizes both: the reviewer should not be able to edit source, the BA has no business running Bash, the architect deserves the strongest model while mechanical roles run cheaper tiers. Claude Code subagent frontmatter supports exactly this (`model:`, `tools:`), but neither the composition schema nor the library carries the information, so the pipeline could not emit it even after SPEC-001 adds the frontmatter mechanism. This is the single biggest missed modern capability in the compiled teams — it affects cost, safety, and quality simultaneously.

## Evidence

- `foundry_app/core/models.py:205-226` — `PersonaSelection` fields are `id`, `include_agent`, `include_templates`, `strictness`. No `model`, no `tools`.
- `foundry_app/templates/agent.md.j2` — no frontmatter at all (SPEC-001), hence no model/tools slots.
- `grep -rn '^model:\|^tools:' ai-team-library/personas/` — zero hits across all 24 personas; the library has no per-role defaults to draw from.
- `.claude/shared/agents/*.md` — same gap in the kit's own five agents (kit side handled by SPEC-002; this spec covers the *generated* path and the library defaults both draw from).

## Proposed change

1. **Library: per-persona defaults.** Add a small machine-readable block to each persona (a `defaults.yml` next to `persona.md`, or frontmatter once the library adopts it via SPEC-002's pattern) declaring:
   - `model:` tier — semantic tiers, not model IDs: `strongest` (architect, team-lead), `standard` (developer, tech-qa, ba), `fast` (mechanical/reporting roles like technical-writer status work). The compiler maps tiers → concrete aliases (`opus`/`sonnet`/`haiku`) in ONE place (`foundry_app/services/agent_writer.py`), so model churn is a one-line change, never a library-wide edit.
   - `tools:` posture — named presets rather than raw lists: `full` (developer), `read-review` (code-quality-reviewer, tech-qa review tasks: Read/Grep/Glob/Bash-readonly), `docs-only` (ba, technical-writer: no Bash), `orchestrator` (team-lead: task/agent tools, no source edits). Presets expand to concrete tool lists in `agent_writer.py`.
2. **Schema: composition overrides.** Extend `PersonaSelection` with optional `model: str | None` (tier or concrete alias) and `tools: str | list[str] | None` (preset name or explicit list). Composition wins over library default; absence falls back to the library default; absence of both emits no frontmatter key (inherit session model / all tools) — today's behavior, so existing YAMLs are unaffected.
3. **Pipeline: emit.** `agent_writer.write_agents` resolves persona default + composition override and passes `model`/`tools` into the SPEC-001 frontmatter context. `include_agent: false` must also finally be honored here (currently ignored — `agent_writer.py:227` writes unconditionally).
4. **Validation.** `validator.py` gains: unknown tier/preset name → ERROR (typo protection); explicit tool list containing an unrecognized tool name → WARNING (tool names are harness-defined and evolve; don't hard-fail). Document the known-names list in one constant with a comment dating it.
5. **Docs.** README "Composition schema" section + `examples/*.yml` gain a demonstrative override (e.g. drill-deck pins its reviewer to `read-review`).

## Out of scope

- Kit agents' own frontmatter (SPEC-002).
- Per-task (rather than per-persona) model selection — dispatch-time concern, SPEC-010 territory if ever.
- Cost telemetry by model tier (SPEC-009 aggregator may consume it later).

## Acceptance criteria

- [ ] (test:tests/test_models.py) `PersonaSelection` accepts `model`/`tools` overrides and rejects malformed values
- [ ] (test:tests/test_agent_writer.py) Generated agent frontmatter carries resolved `model:` and expanded `tools:`; library default used when composition silent; composition override wins; neither → keys omitted; `include_agent: false` produces no agent file
- [ ] (file-contains:ai-team-library/personas/core/team-lead/defaults.yml::model) All five core personas carry defaults; extended personas at minimum get a tools posture
- [ ] (test:tests/test_validator.py) Unknown preset errors; unknown tool name warns
- [ ] (file-contains:README.md::tools) Schema documented with an example
- [ ] manual: Generate `small-python-team` and confirm in the output that the reviewer agent cannot Edit (frontmatter tools list) and the architect resolves to the strongest tier

## Files to touch

- `foundry_app/core/models.py`, `foundry_app/services/agent_writer.py`, `foundry_app/services/validator.py`
- `foundry_app/templates/agent.md.j2` (frontmatter slots — lands in SPEC-001)
- `ai-team-library/personas/*/​*/defaults.yml` (new, maintainer path)
- `examples/*.yml`, `README.md`
- `tests/test_models.py`, `tests/test_agent_writer.py`, `tests/test_validator.py`
