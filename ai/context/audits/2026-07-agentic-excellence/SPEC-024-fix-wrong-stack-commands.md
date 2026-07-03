# SPEC-024: Replace wrong-stack bug/feature/chore/test-gen commands

- **Priority:** P2
- **Effort:** S
- **Area:** kit
- **Depends on:** SPEC-002
- **Status:** Proposed

## Problem

The four TDD workflow commands (`/bug`, `/feature`, `/chore`, `/test-gen`) are unmodified boilerplate from a JavaScript/React starter: they instruct Vitest, Playwright MCP, `npm run` scripts, and `src/`/`server/`/`e2e/` directory layouts. The kit ships them to every beekeeper-lab project — which are Python/`uv`/`pytest`/`ruff` repos — so the commands give actively wrong instructions everywhere they are installed. The TDD structure itself (plan format, red-green-refactor phases) is good and worth keeping.

## Evidence

- `.claude/shared/commands/bug.md:25-27` — test-type table names Vitest, Vitest + Testing Library, Playwright MCP.
- `.claude/shared/commands/bug.md:29-45` — "Using Playwright MCP to Reproduce Bugs" section.
- `.claude/shared/commands/bug.md:50-57` — relevant files: `src/**` ("React frontend application"), `server/**`, `e2e/**`, `src/__tests__/**`.
- `.claude/shared/commands/bug.md:185-189` — validation commands: `npm run test:unit`, `npm run test:components`, `npm run test:e2e`, `npm run build`.
- `.claude/shared/commands/feature.md:143-165` — red/green phases keyed to `npm run test:unit` / `test:components` / `test:e2e`.
- Contrast: `.claude/shared/agents/developer.md:125-130` and the kit's own `CLAUDE.md` specify `uv run pytest` / `uv run ruff` — the same kit contradicts itself.

## Proposed change

1. **Rewrite all four commands stack-neutral with a mandatory detection step.** Each command's first phase becomes: read `CLAUDE.md` "Key Commands" (authoritative if present), else detect from manifests — `pyproject.toml` → `uv run pytest` / `uv run ruff check`; `package.json` → its `scripts` entries; `go.mod` → `go test ./...`; `Cargo.toml` → `cargo test`. All later references to "run the tests" use the detected commands, never hardcoded ones.
2. **Generalize the test-type table** to unit / integration / end-to-end with a "use the project's configured tool" column, mentioning concrete tools only as examples. Replace the Playwright-MCP section with a conditional: "if the project has a browser UI and a Playwright/browser MCP is configured, use it to reproduce UI bugs; otherwise reproduce via the project's test harness."
3. **Replace the hardcoded `Relevant Files` globs** with an instruction to derive source/test layout from the repo (CLAUDE.md repository-structure section, `testpaths` in pyproject, etc.).
4. **Keep intact:** the plan-format skeleton (Bug Description / Problem Statement / Steps to Reproduce / Expected Behavior…), the TDD red-green-refactor sequencing, and the `$ARGUMENTS` entry contract.
5. **Add frontmatter** per SPEC-002 (`description`, `argument-hint: <description of the bug|feature|chore>`).
6. Decision taken here (vs. the alternative of a sync-time stack variable): runtime detection is preferred — it needs no claude-sync/generation machinery, works in every consuming repo immediately, and CLAUDE.md already carries the ground truth in well-formed projects.

## Out of scope

- Command-vs-skill placement (SPEC-023 — these four stay commands).
- Foundry generation-time templating of commands per composition stack (possible later optimization; not needed for correctness).
- `implement.md` and `tools.md` (already stack-neutral).

## Acceptance criteria

- [ ] `manual:` `grep -ril "vitest\|playwright\|npm run" .claude/shared/commands/{bug,feature,chore,test-gen}.md` returns no unconditional stack-specific instructions (examples clearly marked as examples are acceptable).
- [ ] `file-contains:` `.claude/shared/commands/bug.md` contains a detection step referencing `CLAUDE.md` and `pyproject.toml`/`package.json`.
- [ ] `manual:` running `/bug <sample>` in the Foundry repo produces a plan whose validation commands are `uv run pytest` / `uv run ruff check foundry_app/`.
- [ ] `manual:` plan-format sections and red-green-refactor phases are preserved in all four commands.

## Files to touch

- `.claude/shared/commands/bug.md`, `feature.md`, `chore.md`, `test-gen.md` (kit repo — via kit PR flow)
- Mirror copies under `ai-team-library/claude/commands/` if present, so generated projects get the fixed versions in library-copy mode
