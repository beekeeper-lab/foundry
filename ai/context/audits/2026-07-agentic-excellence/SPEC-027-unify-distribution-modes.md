# SPEC-027: Unify subtree and library-copy distribution modes

- **Priority:** P2
- **Effort:** M
- **Area:** pipeline
- **Depends on:** SPEC-004 (hook single-source); coordinate with SPEC-026 (distribution decision)
- **Status:** Proposed

## Problem

A generated project's `.claude/` tree differs materially depending on which of the two distribution modes produced it. Library-copy mode is selection-aware (persona-gated governance skills, stack-picked dev-loop commands, only-enabled hook packs, kit-skill overlay); subtree mode pulls the kit wholesale and skips all of that — including the global `.claude` asset copy, so `settings.local.json` (the permissions file) never lands. Which skills, commands, hooks, and permissions a team gets should be a function of the composition, not of the distribution transport. On top of that, "what hooks exist" has three independent representations that already disagree.

## Evidence

- `foundry_app/services/asset_copier.py:148` — `subtree_mode = bool(spec.generation.claude_kit_url)`.
- `asset_copier.py:156-162` — subtree mode skips `_copy_commands` (dev-loop stack selection) and `_copy_skills` (governance persona-gating + kit overlay) entirely.
- `asset_copier.py:165-175` — subtree mode skips every `_GLOBAL_ASSET_DIRS` entry destined for `.claude/`, i.e. `claude/settings → .claude/` (`:17-21`) — so `settings.local.json` permissions are absent in subtree-generated projects.
- `asset_copier.py:178-181` — subtree mode skips `_copy_selected_hooks`, so hook-pack selection (`hooks.packs` in the composition) has no effect on the shipped hook files.
- `asset_copier.py:81-86` — `_KIT_DISTRIBUTED_SKILLS` is a hardcoded 4-tuple that must stay manually in lockstep with the kit's `skills/` directory and the library's `claude/skills/`; a new kit skill (e.g. `generate-video`) is silently missed, a skill moved into the library is double-sourced. A missing kit path is only a warning (`copy_assets` docstring `:134-137`).
- Three disagreeing hook representations: `safety_writer._HOOK_PACK_REGISTRY` (blocks `main/master/test/prod`), the kit/library `settings.json` inline guard (blocks `main/master` only — `.claude/shared/settings.json:9`), and `ai-team-library/claude/hooks/*.md` prose packs (not executable). Which guard a project gets depends on mode + generation stage ordering (see SPEC-004).

## Proposed change

1. **Define the canonical post-generation `.claude` contract** — a written invariant (docstring + doc section) listing what must hold for ANY generated project: selected-only governance skills, stack-matched dev-loop commands, composition-selected hooks wired in settings, `settings.local.json` permissions present, kit-distributed skills present, no non-selected persona commands.
2. **Make subtree mode selection-aware:** after `git subtree add`, run a **prune/overlay pass** — remove governance skills whose unlocking personas are absent, remove non-selected dev-loop stacks, apply hook-pack selection to settings, and copy `_GLOBAL_ASSET_DIRS` `.claude` entries (settings.local.json) exactly as library-copy mode does. Subtree remains the transport; the composition remains the filter.
3. **Replace `_KIT_DISTRIBUTED_SKILLS` with a kit manifest:** the kit ships `skills/kit-manifest.yaml` (or reuse plugin metadata from SPEC-026) listing distributable skills + helper packages; `asset_copier` reads it at generation time. Unknown/missing entries become validator errors, not silent warnings.
4. **Single source of truth for hooks:** consume the outcome of SPEC-004 — one hook-definition registry that both modes render from, so the branch-guard scope and pack contents cannot diverge by mode.
5. **Add a mode-equivalence test:** generate the same composition through both modes into temp dirs and assert the effective `.claude` inventory (skill names, command names, hook wiring, presence of settings.local.json) is identical modulo transport artifacts (`.claude/shared/` dir itself).

## Out of scope

- Choosing submodule vs plugin distribution (SPEC-026).
- Hook content and settings-overwrite bugs (SPEC-004).
- claude-sync.sh internals (SPEC-025).

## Acceptance criteria

- [ ] `test:` mode-equivalence test passes: identical composition → identical effective `.claude` inventory in both modes.
- [ ] `test:` subtree-mode generation produces `settings.local.json` at `.claude/`.
- [ ] `test:` subtree-mode generation with no `extended/security-engineer` on the team does not ship the `threat-model` skill.
- [ ] `file:` `.claude/shared/skills/kit-manifest.yaml` exists (kit repo) and `file-contains:` `foundry_app/services/asset_copier.py` no longer defines `_KIT_DISTRIBUTED_SKILLS` as a literal tuple.
- [ ] `test:` a manifest entry pointing at a missing kit skill fails validation (error, not warning).
- [ ] `file-contains:` docs describe the canonical post-generation `.claude` contract.

## Files to touch

- `foundry_app/services/asset_copier.py`, `foundry_app/services/subtree_setup.py`
- `foundry_app/services/validator.py` (manifest validation)
- `.claude/shared/skills/kit-manifest.yaml` (kit repo — via kit PR flow)
- `tests/` (mode-equivalence + manifest tests)
- `README.md` / `docs/claude-kit.md` (contract documentation)
