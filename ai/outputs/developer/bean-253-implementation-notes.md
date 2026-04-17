# BEAN-253 — Developer Implementation Notes

| Field | Value |
|-------|-------|
| **Bean** | BEAN-253 |
| **Date** | 2026-04-17 |

## Changes

1. **`foundry_app/services/compiler.py`** — added a `## Scope` section to the lean CLAUDE.md builder, emitted right after the project header and before Tech Stack. Two paragraphs: (a) planning-only scope + `Edit(ai/**)` permission pairing (BEAN-251), (b) "Foundry does not scaffold app code — see `docs/starter-stacks.md`" (BEAN-253). Section is emitted even when no personas are selected (policy, not roster).
2. **`foundry_app/services/scaffold.py`** — extended `_render_readme` to add the Getting Started pointer to `docs/starter-stacks.md` in the Foundry repo. The link is a hard-coded absolute URL because the cheat sheet lives *only* in the Foundry repo, not in generated projects.
3. **`docs/starter-stacks.md`** — new cheat sheet in the Foundry repo with one init command per expertise shipped in the library. Three tables: language/framework stacks, infra/tooling stacks, non-code expertise (no-op). Closing section justifies why the file lives in Foundry and not in generated projects (upstream rename → one edit here, not N regens downstream).
4. **Tests** — 4 new tests covering: Scope section presence, Scope-before-Orchestration ordering, Scope emission with no personas selected, README Getting Started pointer.

## Coordination Notes

- The Scope section is deliberately placed above Team Orchestration Model. A reader should answer "what does this framework produce?" before "how do the agents coordinate?". Test `test_claude_md_scope_precedes_orchestration` locks the ordering.
- BEAN-251 should pick up the Scope section verbatim — the Scope text is now the single source of truth for the paired policy. When BEAN-251 runs, it can add assertions cross-referencing the Scope section's `ai/` mention against the `Edit(ai/**)` rule in `settings.local.json`.
- The starter-stacks cheat sheet avoids over-specification: one command per stack, link to the authoritative upstream doc. This way upstream changes (e.g., Vite 6 → 7 flag renames) do not force a Foundry update — users follow the linked doc.
