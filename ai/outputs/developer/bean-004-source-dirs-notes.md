# BEAN-004: Source Directory Configuration — Implementation Notes

**Author:** Developer | **Date:** 2026-02-07 | **Bean:** BEAN-004

## What Changed

### 1. `foundry_app/core/models.py`
- Added `editable_dirs: list[str]` field to `FileSystemPolicy` with default `["src/**", "tests/**", "ai/**"]`
- Uses `default_factory=lambda` to avoid shared mutable default

### 2. `foundry_app/services/safety.py`
- Replaced hardcoded `Edit(src/**)`, `Edit(tests/**)`, `Edit(ai/**)` (lines 57-59) with a loop over `safety.filesystem.editable_dirs`
- Loop strips whitespace and skips empty strings

### 3. `foundry_app/ui/screens/builder/wizard_pages/safety_page.py`
- Added `QLineEdit` import
- Added `txt_editable_dirs` text field to Filesystem group with placeholder and tooltip
- Added `_parse_editable_dirs()` helper method (comma-separated parsing, strip, filter empty)
- Wired into `build_safety_config()` and `_apply_config()`

### 4. `tests/test_safety.py`
- Added `FileSystemPolicy` import
- 11 new tests:
  - `test_default_editable_dirs_produces_standard_rules`
  - `test_custom_editable_dirs_single`
  - `test_custom_editable_dirs_multiple`
  - `test_empty_editable_dirs_no_edit_rules`
  - `test_editable_dirs_strips_whitespace`
  - `test_editable_dirs_skips_empty_entries`
  - `test_preset_functions_get_default_editable_dirs`
  - `test_filesystem_policy_default_editable_dirs`
  - `test_editable_dirs_yaml_round_trip`
  - `test_old_config_without_editable_dirs_gets_default`
  - (Plus the existing 23 tests all still pass)

## Deviations from Design

None. Implementation follows the design spec exactly.

## Test Results

- **310 tests pass** (300 existing + 10 new)
- **Lint:** 21 pre-existing E501 warnings, 0 new issues

## How to Verify

```bash
uv run pytest tests/test_safety.py -v         # All 34 tests pass
uv run pytest --tb=short -q                    # All 310 tests pass
uv run ruff check foundry_app/                 # No new lint issues
```

Test a custom config:
```python
from foundry_app.core.models import SafetyConfig, FileSystemPolicy
from foundry_app.services.safety import safety_to_settings_json

config = SafetyConfig(filesystem=FileSystemPolicy(editable_dirs=["foundry_app/**", "tests/**"]))
result = safety_to_settings_json(config)
print(result["permissions"]["allow"])
# ['Bash(git push *)', 'Read(**)', 'Edit(foundry_app/**)', 'Edit(tests/**)']
```
