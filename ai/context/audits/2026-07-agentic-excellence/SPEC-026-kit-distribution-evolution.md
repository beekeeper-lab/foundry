# SPEC-026: Kit distribution evolution: plugin path and contribution loop

- **Priority:** P2
- **Effort:** L
- **Area:** kit
- **Depends on:** SPEC-002 (frontmatter is a prerequisite for plugin packaging); informs SPEC-027
- **Status:** Proposed — decision spec; deliverable is an ADR plus an implementation plan

## Problem

ClaudeKit's distribution model (git submodule + symlink sync + `claude-publish.sh`) is one-directional and lossy. Improvements flow *out* of Foundry slowly (each consumer must bump the submodule pointer and re-sync) and flow *back in* essentially never: downstream projects have no scripted contribution path, and the only local-adaptation mechanism is whole-file override — which permanently forks the file and stops it receiving upstream improvements. This is the explicitly stated pain: the kit lets other apps adapt the agentic process, but pushing the good parts back upstream while keeping the local parts is manual and error-prone. Meanwhile, Claude Code's plugin/marketplace system now natively does what the submodule apparatus reimplements: versioned install and update of commands + skills + agents + hooks + MCP config as a unit.

## Evidence

- `.claude/shared/README.md:82-93` — "Publishing changes (foundry only): Only the foundry project pushes changes to this repo." The contribution model is exclusionary by design.
- `.claude/shared/CLAUDE.md` ("Kit Management") — "Only the **foundry** project pushes changes to this repo."
- `scripts/claude-publish.sh:11-14` — submodules sit on detached HEAD by default; `git rev-parse @{u}` then fails, the `|| echo ''` makes the inequality true, and the script runs `git push` from a detached HEAD, which fails. The script also contradicts the README's own instruction to branch first (`README.md:87-88`), and has no lock: between the submodule push and the parent push, kit `main` can advance (TOCTOU) so the parent records an unreviewed pointer.
- `.claude/shared/scripts/claude-sync.sh:109-111,188-190` — override is whole-file by basename: a project wanting to change one line of a shared command must copy the entire file into `.claude/local/`, permanently forking it (warned at `:123` but with no reconciliation tooling).
- SPEC-025's findings — the symlink layer itself is fragile (non-atomic, GNU-only), i.e. ongoing maintenance cost of the bespoke mechanism.

## Proposed change

1. **Write an ADR** ("Kit distribution: plugin vs submodule") in `ai/context/decisions.md` evaluating three options:
   - **A. Claude Code plugin + marketplace (recommended direction):** package claude-kit as a plugin (`plugin.json` manifest bundling commands, skills, agents, hooks, MCP). Consumers `plugin install`/`update`; versioning is explicit; `claude-sync.sh`'s symlink generation, settings merge, and git-hook installer are deleted. Local assets remain plain `.claude/` files, which naturally layer over plugin content. Requires SPEC-002 (frontmatter) first.
   - **B. Keep submodule, fix the loop:** retain current mechanics, apply SPEC-025 hardening, and add the contribution tooling from (2)–(3). Lowest migration cost, keeps all known fragilities.
   - **C. Hybrid:** plugin for the stable, rarely-forked layer (safety hooks, media skills, generic commands); submodule or plain files for the fast-moving orchestration layer that projects adapt.
   The ADR must cover: version pinning per consumer, offline/air-gapped installs, how Foundry's generator emits the chosen form into generated projects (both distribution paths in SPEC-027), and migration sequencing for existing beekeeper-lab repos.
2. **Regardless of the decision, ship a contribution flow** replacing raw `claude-publish.sh`, e.g. `scripts/kit-contribute.sh`:
   - detects dirty/committed changes under `.claude/shared/` (or the local override being promoted),
   - creates a branch from kit `origin/main` (handling detached HEAD correctly),
   - cherry-picks/copies the change, pushes, and opens a PR via `gh pr create` against `beekeeper-lab/claude-kit`,
   - works from any consuming repo with fork fallback when the user lacks push rights.
3. **Fix `claude-publish.sh` now** (independent of the ADR): refuse to run on detached HEAD with a clear message, verify the recorded submodule SHA is an ancestor of the pushed branch before pushing the parent, and document it as Foundry-maintainer-only.
4. **Document an override policy** in the kit README distinguishing: *patch upstream* (default for fixes/improvements — use the contribution flow) vs *fork locally* (project-specific behavior — accept divergence, record the fork in a `LOCAL-OVERRIDES.md` ledger so drift is visible and auditable).

## Out of scope

- Implementing the plugin migration itself (follow-on beans once the ADR is accepted).
- The sync-script hardening (SPEC-025) and mode unification (SPEC-027) — they proceed independently and remain valuable under options B/C.

## Acceptance criteria

- [ ] `file-contains:` `ai/context/decisions.md` gains an accepted ADR covering options A/B/C with a decision and migration plan.
- [ ] `file:` `scripts/kit-contribute.sh` exists and is executable.
- [ ] `manual:` from a non-Foundry consuming repo, `kit-contribute.sh` produces an open PR against `beekeeper-lab/claude-kit` containing a sample change.
- [ ] `file-contains:` `scripts/claude-publish.sh` handles detached HEAD explicitly (guard + message) rather than pushing blind.
- [ ] `file-contains:` `.claude/shared/README.md` documents the patch-upstream vs fork-locally policy and the `LOCAL-OVERRIDES.md` ledger.

## Files to touch

- `ai/context/decisions.md` (new ADR)
- `scripts/claude-publish.sh`, new `scripts/kit-contribute.sh` (and kit-side copy under `.claude/shared/scripts/`)
- `.claude/shared/README.md`, `.claude/shared/CLAUDE.md` (contribution policy)
- If option A/C accepted: new `plugin.json` + packaging scripts in the kit repo (follow-on)
