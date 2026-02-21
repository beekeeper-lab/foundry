# Task 01: Implement Subtree Generation Pipeline

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends On** | — |
| **Status** | Done |
| **Started** | — |
| **Completed** | — |
| **Duration** | — |

## Goal

Add a `claude_kit_url` option to the generation pipeline. When set, skip `.claude/` asset copying and instead set up a git subtree in the output directory.

## Inputs

- `foundry_app/core/models.py` — `GenerationOptions` model
- `foundry_app/services/asset_copier.py` — `_GLOBAL_ASSET_DIRS` and `_copy_selected_hooks`
- `foundry_app/services/generator.py` — pipeline stages
- `foundry_app/cli.py` — CLI options
- `tests/test_asset_copier.py`, `tests/test_generator.py` — existing tests

## Changes Required

### 1. Model: Add claude_kit_url field

In `GenerationOptions`, add:
```python
claude_kit_url: str | None = Field(default=None, description="Git URL for claude-kit subtree repo")
```

### 2. Asset copier: Skip .claude/ when subtree mode active

In `copy_assets()`, when `spec.generation.claude_kit_url` is set:
- Skip `_GLOBAL_ASSET_DIRS` entries targeting `.claude/` (commands, skills, settings)
- Skip `_copy_selected_hooks()`
- Still copy non-`.claude/` dirs (process/beans, process/context)
- Still copy persona templates

### 3. Generator: Add subtree setup stage

Create `foundry_app/services/subtree_setup.py` with a `setup_subtree()` function:
- Initialize git repo if needed (`git init`)
- Add remote (`git remote add claude-kit <url>`)
- Fetch and add subtree (`git subtree add --prefix=.claude claude-kit main --squash`)
- Return `StageResult` with files written

In `_run_pipeline()`, add stage after `copy_assets` when `claude_kit_url` is set.

### 4. CLI: Add --claude-kit-url option

Add `--claude-kit-url` option to the CLI generate command.

### 5. Tests

- Test asset copier skips `.claude/` dirs when `claude_kit_url` is set
- Test subtree_setup service in isolation (mock subprocess calls)
- Test generator runs subtree stage when configured

## Acceptance Criteria

- [ ] `claude_kit_url` field exists on `GenerationOptions`
- [ ] Asset copier skips `.claude/` when subtree mode active
- [ ] Subtree setup service creates working subtree
- [ ] Generator pipeline includes subtree stage
- [ ] CLI supports `--claude-kit-url`
- [ ] Fallback to copy when no URL configured
- [ ] All tests pass
- [ ] Lint clean

## Definition of Done

Pipeline modified to support optional subtree setup for `.claude/` directory.
