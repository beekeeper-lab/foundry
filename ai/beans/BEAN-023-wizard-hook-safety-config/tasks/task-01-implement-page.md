# Task 1: Design and Implement Hook & Safety Config Page

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Status** | Pending |
| **Depends On** | — |

## Description

Create `foundry_app/ui/screens/builder/wizard_pages/hook_safety_page.py` following the established wizard page pattern (see persona_page.py, stack_page.py).

## Requirements

### Hook Pack Section
- Posture selector (QComboBox): baseline, hardened, regulated
- HookPackCard widgets for each pack from LibraryIndex.hook_packs
  - Checkbox to enable/disable
  - Mode selector (QComboBox): enforcing, permissive, disabled
  - Pack ID display and file count badge

### Safety Policy Section
- Preset buttons: Permissive, Baseline, Hardened (calls SafetyConfig factories)
- Six policy sub-sections with toggle controls:
  - Git: allow_push, allow_force_push, allow_branch_delete
  - Shell: allow_shell
  - Filesystem: allow_write, allow_delete
  - Network: allow_network
  - Secrets: scan_for_secrets, block_on_secret
  - Destructive Ops: allow_destructive, require_confirmation

### Public API
- `load_hook_packs(library_index: LibraryIndex)` — populate cards
- `get_hooks_config() -> HooksConfig` — return current config
- `set_hooks_config(config: HooksConfig)` — restore state
- `get_safety_config() -> SafetyConfig` — return current safety config
- `set_safety_config(config: SafetyConfig)` — restore state
- `is_valid() -> bool` — always True (hooks/safety have defaults)
- `selection_changed` signal

## Acceptance Criteria
- Follows Catppuccin Mocha theme
- All model types round-trip correctly
- No dependencies on unbuilt services
