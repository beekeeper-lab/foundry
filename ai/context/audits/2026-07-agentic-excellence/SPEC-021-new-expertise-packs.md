# SPEC-021: New expertise packs: LLM/agent-app development and modern web

- **Priority:** P2
- **Effort:** L
- **Area:** expertise
- **Depends on:** SPEC-003 (compile contract — new packs must be born live), SPEC-019 (author with frontmatter)
- **Status:** Proposed

## Problem

Foundry is a factory for AI-agent teams, yet its library ships **no expertise pack for building LLM/agent applications** — the single most likely domain of its own users. The only LLM content in the repo (`mlops/llm-operations.md`, 339 lines) is a dead sibling file the compiler never reads, and it is model/price-stale. Beyond that: web coverage stops at React (no Vue/Angular/Svelte/Next), there are no backend-framework packs (FastAPI/Django/Spring/Express/Nest), testing and observability exist only as dead sibling files inside other packs — and the dev-loop command mapping covers only the python and node families, so teams generated for go, dotnet, java, kotlin, rust, dart, flutter, swift, or r get **no dev-loop commands at all** despite rich packs existing for all nine.

## Evidence

- `ai-team-library/expertise/` — 42 packs; none named for LLM/agent development; `grep -ril 'tool.use\|agent\|mcp' expertise/` hits only `mlops/llm-operations.md` (dead: no `conventions.md` sibling reachable per SPEC-003 evidence) and incidental uses.
- `ai-team-library/expertise/mlops/llm-operations.md:40,328-330` — stale model IDs/prices (see SPEC-020).
- No `vue/`, `angular/`, `svelte/`, `nextjs/`, `fastapi/`, `django/`, `spring/`, `express/`, `nestjs/` directories exist.
- `foundry_app/services/asset_copier.py:28-37` — `_DEV_LOOP_STACK_BY_EXPERTISE` maps only `python`, `python-qt-pyside6`, `node`, `react`, `typescript`, `react-native`, `frontend-build-tooling`; a composition selecting `go` or `flutter` silently gets no dev-loop commands.

## Proposed change

1. **`llm-agent-development` pack (flagship, spec in full).** Structure per SPEC-019 schema, entry `conventions.md` plus siblings, grounded in mid-2026 practice:
   - `conventions.md` (entry): defaults table — pick the latest-generation frontier model for agentic work and parameterize model IDs in config (never hardcode); structured outputs / tool-schemas over prompt-parsing; context-window budgeting; temperature/effort defaults per task class; cost & latency budgets as first-class NFRs; eval-before-ship rule; do/don't; pitfalls (prompt-drift, unbounded loops, silent truncation, injection via retrieved content); checklist.
   - `agent-architecture.md`: single-agent vs orchestrator/worker vs pipeline; when to fan out; state & memory patterns; checkpointing and resumability; human-in-the-loop gates; sandboxing and permissioning of tool-wielding agents.
   - `tool-design.md`: tool/function schema design; idempotency; error surfaces the model can act on; MCP servers (when to build vs consume); tool-count budgets and progressive disclosure.
   - `evals.md`: golden sets, LLM-as-judge (with its failure modes), regression evals in CI, trace-based debugging, online monitoring; hallucination and injection test cases.
   - `prompt-context-engineering.md`: system-prompt structure, few-shot placement, context-diet patterns, RAG chunking/citation hygiene, caching-aware prompt layout.
   - Absorb the salvageable content of `mlops/llm-operations.md` here and delete it from `mlops/` (coordinate with SPEC-020 item 1).
2. **Backend web pack, one not five:** a single `backend-web-frameworks` pack risks being too generic; instead add the two highest-demand: `fastapi/` (pairs with the python pack) and `nextjs/` (pairs with react/typescript). Defer Spring/Django/Nest until demand shows; record the deferral in the pack README.
3. **Promote dead siblings into live packs:** `testing-strategy/` and `observability/` packs assembled from the existing per-language `testing.md`/observability sibling content (which SPEC-003 makes reachable; this item is about giving the cross-cutting versions a first-class home). Keep language-specific detail in the language packs per SPEC-020's precedence rule.
4. **Dev-loop mapping for all languages:** extend `_DEV_LOOP_STACK_BY_EXPERTISE` and add command stacks under `ai-team-library/claude/commands/dev-loop/` for `go`, `dotnet`, `java` (gradle/maven), `kotlin`, `rust` (cargo), `dart`, `flutter`, `swift`, `r`. Each stack is small: test, lint/format, build/run commands idiomatic to the toolchain. Add a validator INFO when a selected language expertise has no dev-loop mapping so future gaps surface instead of silently no-op'ing.
5. Author everything against the SPEC-019 frontmatter schema and the canonical section shape (`## Defaults` table first — it is what `agent_writer` extracts into agent prompts).

## Out of scope

- Refreshing existing pack content (SPEC-020).
- Vue/Angular/Svelte, Spring/Django/Nest, C++/PHP/Ruby/Scala/Elixir packs — explicitly deferred, not forgotten.
- MCP server *distribution* to generated projects (SPEC-022).

## Acceptance criteria

- [ ] `file:` `ai-team-library/expertise/llm-agent-development/conventions.md` exists with the four sibling files listed above.
- [ ] `file:` `ai-team-library/expertise/fastapi/conventions.md` and `ai-team-library/expertise/nextjs/conventions.md` exist.
- [ ] `file-contains:` `llm-agent-development/conventions.md` contains no hardcoded per-token price and no dated model ID presented as a default.
- [ ] `test:` a composition selecting `llm-agent-development` compiles a non-empty expertise section (extends SPEC-003's no-dead-packs test).
- [ ] `file-contains:` `foundry_app/services/asset_copier.py` maps `go`, `rust`, `flutter`, `dotnet`, `java`, `kotlin`, `dart`, `swift`, `r` in `_DEV_LOOP_STACK_BY_EXPERTISE`.
- [ ] `test:` generating a go-expertise composition copies a go dev-loop command set; validator INFO fires for a hypothetical unmapped language pack.
- [ ] `test:` `uv run pytest` passes.
- [ ] `manual:` review the llm-agent-development pack against current (implementation-time) provider guidance — this domain moves fast; the pack must carry `last_reviewed` and version-agnostic phrasing.

## Files to touch

- `ai-team-library/expertise/llm-agent-development/` (new, 5 files), `fastapi/` (new), `nextjs/` (new), `testing-strategy/` (new), `observability/` (new)
- `ai-team-library/expertise/mlops/llm-operations.md` (content moved; file removed)
- `ai-team-library/claude/commands/dev-loop/{go,dotnet,java,kotlin,rust,dart,flutter,swift,r}/` (new command stacks)
- `foundry_app/services/asset_copier.py`, `validator.py`
- `tests/test_asset_copier.py`, `tests/test_compiler.py`
