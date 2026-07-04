# ADR-012: Per-Expertise Persona Relevance for Compile-Time Filtering

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-259 |
| **Deciders** | Architect |

## Context

External audit (2026-04-17): every persona's compiled member prompt receives every selected expertise verbatim. The DevOps-Release agent's prompt contains `tsconfig.json` strict-mode detail; the UX/UI Designer's prompt contains `ruff` formatter defaults. This inflates context, dilutes role focus, and only gets worse as the expertise library grows. Today the join is unconditional: `compile_project` calls `_compile_persona_section` and `_compile_expertise_section` independently, the agent_writer joins all expertise highlights into every agent file (`expertise_sections` is shared across the per-persona loop), and the library has no metadata describing which expertise belongs with which persona.

Two candidate mechanisms were considered:

- **(A) Per-expertise persona relevance** — each expertise declares the personas it applies to.
- **(B) Per-persona expertise category filter** — each persona declares which expertise categories it wants (`Languages`, `Infrastructure & Platforms`, …).

Categories already exist on expertise (`## Category` heading, parsed by `library_indexer._parse_expertise_category`), so (B) would reuse existing metadata. But categories are coarse: `python` and `typescript` share `Languages`, yet DevOps-Release cares about Python's `pyproject.toml`/lockfile content while wanting nothing to do with TypeScript's `tsconfig.json`. Sub-categorising would re-create the per-pair granularity that (A) provides directly.

## Decision

**Mechanism A — per-expertise persona relevance.** Each expertise's primary markdown file declares the personas it applies to in an `## Applies To` section; the compiler and agent_writer filter expertise per persona at emit time. **Rationale (developer can quote):** *the author of an expertise file already knows its audience, and locality wins — adding a new expertise is one file change in one place, not a sweep across every persona.*

**Metadata schema.** A new `## Applies To` section on each expertise's primary markdown file (`conventions.md`, or the alphabetically-first `*.md` for multi-file packs like `accessibility-compliance/`). Same parser shape as `## Category` and `## Conflicts With` (ADR-005): a markdown heading followed by a bulleted list of persona IDs.

```markdown
## Applies To

- developer
- tech-qa
- architect
```

`ExpertiseInfo` gains `applies_to: list[str]` (default `[]`). The library indexer parses the section into that field. **The default when the section is absent or empty is "applies to every persona"** — this preserves today's behavior for any composition or library file without the new metadata. Unknown persona IDs in the list are dropped with a warning at index time (mirrors the `Persona '<id>' not found` warning shape already in `compiler.py`).

## Filter Contract

The filter operates on the **full expertise content** that gets joined to per-persona prompts. Specifically:

1. **`compiler._compile_persona_section`** — when assembling a persona's member prompt at `ai/generated/members/<persona>.md`, only expertise whose `applies_to` is empty *or* contains this persona ID contributes content. (Today the persona section does not in fact embed expertise content; this clause is a forward-compat hook for if it ever does — a no-op until then.)
2. **`agent_writer.write_agents`** — `expertise_sections` is no longer pre-computed once and shared. It is recomputed inside the per-persona loop, filtered by `applies_to`, before being passed to the Jinja template. This is the load-bearing change: today every agent file embeds every expertise's `Defaults` highlights; after BEAN-259, an agent file only embeds expertise whose `applies_to` matches.
3. **Lean CLAUDE.md (`_build_lean_claude_md`)** — **unfiltered**. The Tech Stack table continues to list every emitted expertise; that table is project-level scope, not persona-level scope, and removing entries would break the cross-reference contract (`ai/generated/expertise/<id>.md`).
4. **`ai/generated/expertise/<id>.md`** — **unfiltered**. The full expertise file is always written so any persona that needs to read it can. The filter only governs *which expertise gets inlined into a persona's prompt*, not which expertise gets emitted as a standalone file.

A new helper `compiler._expertise_applies_to(persona_id, expertise_info) -> bool` encapsulates the rule: returns `True` when `applies_to` is empty or `persona_id in applies_to`. Both call sites use it; tests target it directly.

## Test Cases

The implementation must satisfy at minimum these assertions:

1. **DevOps-Release / React+TS composition**: the generated `.claude/agents/devops-release.md` and `ai/generated/members/devops-release.md` contain no `tsconfig` substring (case-insensitive) and no React-specific content.
2. **UX/UI Designer / same composition**: the corresponding agent and member files contain no `ruff` substring and no Python-specific content.
3. **Developer / same composition**: the corresponding agent and member files contain both `tsconfig` and `ruff` (Developer is in `applies_to` for both).
4. **Backward-compat — empty metadata**: an expertise file with no `## Applies To` section produces the same agent/member output for every persona as before BEAN-259 (byte-equal on a regression fixture, modulo any unrelated changes).
5. **Backward-compat — empty list**: an expertise file with `## Applies To` present but no bullets is treated identically to "section absent" (apply to all).
6. **Unknown persona ID**: `applies_to: [bogus-persona]` raises an indexer warning and is treated as if the ID were not present (i.e., for a real persona, that persona is *not* matched by the bogus entry).
7. **Lean CLAUDE.md unaffected**: the Tech Stack table in `CLAUDE.md` lists every emitted expertise regardless of `applies_to`.
8. **Standalone expertise files unaffected**: `ai/generated/expertise/<id>.md` is written for every emitted expertise regardless of `applies_to`.

## Consequences

**Positive:**
- Per-persona prompts shrink in proportion to how narrow the persona is. DevOps-Release and UX/UI Designer benefit most; Developer is unaffected by design.
- The metadata lives next to the content it scopes — a library author adding a new expertise edits one file.
- Backward-compatible by construction: existing library files (none of which have `## Applies To` today) continue to produce identical output until the metadata is added.
- The filter helper is a pure function over `(persona_id, ExpertiseInfo)`, trivially unit-testable in isolation.

**Negative:**
- Curating `applies_to` lists is ongoing library-author work. Mitigated by the empty-default rule (forgetting to add the section is a no-op, not a regression).
- A persona–expertise pair can drift if the persona's role changes but the expertise's `applies_to` is not revisited. Acceptable; this is the same drift risk as `## Conflicts With` (ADR-005).

## Reversibility

Fully reversible. Rollback path: delete the `## Applies To` parsing in `library_indexer.py`, drop the `ExpertiseInfo.applies_to` field, and remove the `_expertise_applies_to` calls in `agent_writer.py` and `compiler.py`. Library `## Applies To` sections become inert text (the indexer ignores unknown sections today). No on-disk schema migration is needed: composition specs and generated projects are unaffected.

## Alternatives Rejected

1. **Mechanism B — per-persona expertise-category filter:** Rejected. Categories are coarse (`Languages` covers both Python and TypeScript), so DevOps-Release would either get both or neither — neither matches the audit's complaint. Refining the taxonomy with sub-categories adds a second metadata surface to maintain *and* still places the declaration far from the content being filtered.
2. **Front-matter YAML on persona/expertise files:** Rejected. The library has never used YAML front-matter; existing metadata (`## Category`, `## Conflicts With`) lives in markdown sections parsed by the indexer. Adding a third precedent for the same kind of metadata would fragment the parser.
3. **Separate `_index.yml` in `ai-team-library/expertise/`:** Rejected. Centralized metadata invites drift between the index and the file it describes; the ADR-005 precedent (declarations live with the thing being declared) applies here too.
4. **Runtime filtering at agent-load time:** Out of scope per the bean (compile-time filter only). Runtime tailoring is BEAN-240's territory.

