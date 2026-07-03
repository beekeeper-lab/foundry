# SPEC-015: Implement or de-scope the documented quality-gate hooks

- **Priority:** P1
- **Effort:** M
- **Area:** kit
- **Depends on:** SPEC-004 (hook generation reconciliation), coordinates with SPEC-008 (VDD/handoff gates)
- **Status:** Proposed

## Problem

The kit ships three hook documents (`hook-policy.md`, `pre-commit-lint.md`, `post-task-qa.md`) describing an elaborate quality-gate framework — `pre-task-start` / `post-task-complete` / `pre-commit` events, posture levels, a `.foundry/hooks.yml` project override file, audit trails. **None of it executes.** `settings.json` wires only `PreToolUse` and `PostToolUse` hooks; `SessionStart`, `Stop`, `SubagentStop`, and `UserPromptSubmit` are entirely unused. Personas and the bean workflow assume these gates exist (pre-commit lint, post-task acceptance checks), but they are documentation, not machinery. This is a root cause of the audit's core finding: gates that are prose get skipped.

## Evidence

- `.claude/shared/hooks/hook-policy.md:63,111` — describes a `.foundry/hooks.yml` override file that nothing reads.
- `.claude/shared/hooks/pre-commit-lint.md`, `post-task-qa.md` — describe lint/QA gates; no reference to either file exists in `.claude/shared/settings.json` or `.claude/local/`.
- `.claude/shared/settings.json:3,41` — only `PreToolUse` and `PostToolUse` blocks exist; no `SessionStart`, `Stop`, or `SubagentStop`.
- `ai-team-library/claude/hooks/` — the same doc-only hook packs ship to every generated project via the library.
- Process audit: across ~294 completed beans, honor-system gates were skipped ~95–99% of the time; the only gates that held were the two wired as real hooks.

## Proposed change

Implement the three highest-value gates as real hooks; explicitly de-scope the rest.

1. **`SessionStart` context injection** — new `.claude/shared/hooks/session_context.py`. Emits: current branch (with a prominent warning when on `main`/`master`), count of Approved / In Progress beans parsed from `ai/beans/_index.md` (skip silently if absent), and a pointer to the in-progress bean if exactly one. Registered under a new `SessionStart` block in `settings.json`.
2. **`PostToolUse` auto-format** — new `.claude/shared/hooks/format_on_edit.py`, matcher `Edit|Write|NotebookEdit`. When the edited file is `*.py` and `ruff` is available (`uv run ruff --version` succeeds), run `uv run ruff format <file>` and `uv run ruff check --fix <file>` scoped to that file only. Never blocks; on failure prints a one-line advisory. Exits 0 fast for non-Python files.
3. **`Stop` / `SubagentStop` test-and-lint gate** — new `.claude/shared/hooks/stop_gate.py`. If any `*.py` file under the project was modified this session (derive from `git status --porcelain`), run `uv run ruff check` on changed files; on failure, block the stop with a reason listing the failures (Claude Code Stop hooks may return a blocking decision). Running the full test suite at Stop is too slow by default — gate it behind an env flag `FOUNDRY_STOP_RUN_TESTS=1` documented in the hook header. This implements the enforceable core of `post-task-qa.md`.
4. **De-scope the rest honestly.** Rewrite `hook-policy.md`, `pre-commit-lint.md`, `post-task-qa.md` to open with a status banner: `> **Status:** design reference. Enforced hooks are listed in settings.json; everything else in this document is aspirational.` Delete all references to `.foundry/hooks.yml` (or implement it — not recommended; settings.json local overlays already fill that role).
5. **Generation path:** register the three new hooks in `safety_writer._HOOK_PACK_REGISTRY` (per SPEC-004's reconciliation) so generated projects receive them according to posture: `SessionStart` + auto-format at all postures; Stop gate at `hardened`+.
6. Language-awareness: the auto-format and stop-gate scripts read the lint command from an optional `FOUNDRY_LINT_CMD` env (default `uv run ruff`), so non-Python generated projects can retarget without editing the hook.

## Out of scope

- VDD-report and handoff enforcement hooks (SPEC-008).
- Fixing `bash_safety.py` / `write_safety.py` false positives (SPEC-014).
- The generator-side single-source-of-truth for hooks (SPEC-004); this spec adds hook content, SPEC-004 fixes plumbing.

## Acceptance criteria

- [ ] `file:` `.claude/shared/hooks/session_context.py`, `.claude/shared/hooks/format_on_edit.py`, `.claude/shared/hooks/stop_gate.py` exist and are executable.
- [ ] `file-contains:` `.claude/shared/settings.json` contains a `"SessionStart"` key and registers all three new hooks.
- [ ] `file-contains:` `.claude/shared/hooks/hook-policy.md` contains `Status: design reference`.
- [ ] `lint:` `uv run ruff check` passes on the three new hook scripts.
- [ ] `test:` unit tests cover: session_context output on main vs feature branch; format_on_edit no-op on non-Python file; stop_gate blocks on a ruff failure and passes on clean tree.
- [ ] `manual:` in a scratch project, a session started on `main` shows the warning; editing a `.py` file with bad formatting leaves it ruff-clean; ending a session with a lint error is blocked with a reason.
- [ ] `file-contains:` no file under `.claude/shared/hooks/` or `ai-team-library/claude/hooks/` references `.foundry/hooks.yml`.

## Files to touch

- `.claude/shared/hooks/session_context.py` (new), `format_on_edit.py` (new), `stop_gate.py` (new)
- `.claude/shared/settings.json`
- `.claude/shared/hooks/hook-policy.md`, `pre-commit-lint.md`, `post-task-qa.md`
- `ai-team-library/claude/hooks/` (mirrored doc updates + new hook registration — via the kit-publish flow)
- `foundry_app/services/safety_writer.py` (registry entries; with SPEC-004)
- `tests/` (new hook tests)
