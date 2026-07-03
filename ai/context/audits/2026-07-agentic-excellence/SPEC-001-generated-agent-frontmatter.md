# SPEC-001: Generated agents: emit valid Claude Code subagent frontmatter

- **Priority:** P0
- **Effort:** M
- **Area:** pipeline
- **Depends on:** none
- **Status:** Proposed

## Problem

Foundry's headline promise is that generated projects contain working Claude Code sub-agents. They don't. The agent template emits a plain Markdown file starting with an H1 — no YAML frontmatter — and Claude Code only registers a `.claude/agents/*.md` file as a delegatable subagent when it carries `name:` and `description:` frontmatter. Every generated agent file is therefore invisible to the harness: no auto-routing by description, no `--agent <name>` resolution, no tool scoping, no per-agent model selection. The README's "Component Roles" table explicitly claims "Claude Code loads these as sub-agent definitions," which is currently false.

Separately, `PersonaSelection.include_agent` exists in the composition schema but `write_agents` never reads it — an agent file is written for every persona unconditionally. `include_agent: false` silently does nothing.

## Evidence

- `foundry_app/templates/agent.md.j2:1` — file starts `# {{ role_name }}`; no frontmatter block anywhere in the template.
- `foundry_app/services/agent_writer.py:279-287` — the render context contains only `role_name`, `role_description`, `expertise_names`, `persona_id`, `mission`, `key_rules`, `expertise_sections`; no `name`/`description`/`tools`/`model` keys exist to emit.
- `foundry_app/services/agent_writer.py:227-231` — the persona loop checks only `persona_info is None`; `persona_sel.include_agent` is never consulted.
- `generated-projects/small-python-team/.claude/agents/developer.md:1` — confirmed output starts `# Python Developer`; grep for `^name:|^description:|^tools:|^model:` across the agents dir returns nothing.
- `README.md` "Component Roles" — promises the agents load as sub-agent definitions.

## Proposed change

1. Add a frontmatter block to `agent.md.j2`, rendered before the H1:
   ```
   ---
   name: {{ agent_name }}
   description: {{ agent_description }}
   {% if agent_tools %}tools: {{ agent_tools }}{% endif %}
   {% if agent_model %}model: {{ agent_model }}{% endif %}
   ---
   ```
2. In `agent_writer.write_agents`, populate:
   - `agent_name` = `_persona_dirname(persona_sel.id)` (flat, tier-stripped — matches the emitted filename so `claude --agent <name>` resolves).
   - `agent_description` = a one-to-two-sentence routing description synthesized from the persona's `## Activated When` triggers (first 2-3 bullets) plus the role name, e.g. "Use for implementation tasks: writing code, refactoring, bug fixes. Python Developer for <project>." Fall back to `_extract_role_description` when `## Activated When` is absent. Add an extractor `_extract_activation_triggers(persona_text)` alongside the existing `_extract_mission`/`_extract_key_rules`.
   - `agent_tools` / `agent_model`: emit only when available. This spec ships sensible per-persona defaults in a small module-level map (e.g. tech-qa and code-quality-reviewer get read-only + Bash for test runs; ba gets no Bash); SPEC-011 later replaces the map with composition-schema knobs. Defaults may also be empty (omit the key) — omission is valid and inherits full access.
3. Honor `include_agent`: at the top of the persona loop, `if not persona_sel.include_agent: continue` (after the `persona_info` lookup so missing-persona warnings still fire).
4. Validate name uniqueness: two personas flattening to the same dirname must raise a generation warning (collision would produce ambiguous `--agent` resolution).
5. Regenerate both sample projects under `generated-projects/` so the checked-in examples show valid subagents.
6. Update the README "Component Roles" row only if wording needs to change (it becomes true rather than aspirational).

## Out of scope

- Composition-schema fields for per-persona `model`/`tools` (SPEC-011).
- Frontmatter for kit/library commands and skills (SPEC-002).
- Fixing the `persona_id` path bugs inside the template body (SPEC-006) — but coordinate: both touch `agent.md.j2`.

## Acceptance criteria

- [ ] `file-contains: generated-projects/small-python-team/.claude/agents/developer.md` — first line is `---` and frontmatter includes `name: developer` and a non-empty `description:`.
- [ ] `test: tests/test_agent_writer.py` — new tests assert (a) frontmatter renders with name/description for core and extended personas; (b) `include_agent: false` produces no agent file; (c) duplicate flattened names produce a warning.
- [ ] `test: uv run pytest` — full suite passes.
- [ ] `lint: uv run ruff check foundry_app/` — clean.
- [ ] `manual:` `claude --agent developer` (or the Agent tool with `subagent_type: developer`) resolves inside a freshly generated project.

## Files to touch

- `foundry_app/templates/agent.md.j2`
- `foundry_app/services/agent_writer.py`
- `tests/test_agent_writer.py` (or the existing agent-writer test module)
- `generated-projects/small-python-team/`, `generated-projects/drill-deck-base/` (regenerated)
- `README.md` (Component Roles wording, if needed)
