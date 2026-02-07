# BEAN-004: Source Directory Configuration — Design Spec

**Author:** Architect | **Date:** 2026-02-07 | **Bean:** BEAN-004

## Overview

Add a configurable `editable_dirs` field to `FileSystemPolicy` so the safety service generates project-specific `Edit()` rules instead of hardcoding `Edit(src/**)`.

## Changes

### 1. Model: `FileSystemPolicy` in `foundry_app/core/models.py`

Add one field:

```python
class FileSystemPolicy(BaseModel):
    allow_outside_project: bool = False
    deny_patterns: list[str] = Field(default_factory=list)
    editable_dirs: list[str] = Field(
        default_factory=lambda: ["src/**", "tests/**", "ai/**"]
    )
```

**Design decisions:**
- Field name: `editable_dirs` (not `source_dirs`) — because it includes non-source dirs like `tests/**` and `ai/**`
- Default value: `["src/**", "tests/**", "ai/**"]` — matches current hardcoded behavior exactly, ensuring backward compatibility
- Type: `list[str]` — each entry becomes one `Edit(<entry>)` rule
- Pydantic `default_factory` with lambda — so the default list is not shared across instances

### 2. Service: `safety_to_settings_json()` in `foundry_app/services/safety.py`

Replace the hardcoded block (lines 56-59):

```python
# Before (hardcoded):
allow.append("Read(**)")
allow.append("Edit(src/**)")
allow.append("Edit(tests/**)")
allow.append("Edit(ai/**)")

# After (configurable):
allow.append("Read(**)")
for d in safety.filesystem.editable_dirs:
    stripped = d.strip()
    if stripped:
        allow.append(f"Edit({stripped})")
```

**Behavior:**
- Iterates `editable_dirs`, strips whitespace, skips empty strings
- No deduplication in the service — Pydantic validators or the caller can handle that
- Empty list → no `Edit()` rules (per BA edge case EC-1). No warning emitted by the service (warnings are a UI concern).

### 3. UI: `SafetyPage` in `foundry_app/ui/screens/builder/wizard_pages/safety_page.py`

Add a `QLineEdit` to the Filesystem group box:

```python
# Inside the fs_group section:
self.txt_editable_dirs = QLineEdit()
self.txt_editable_dirs.setPlaceholderText("src/**, tests/**, ai/**")
self.txt_editable_dirs.setToolTip(
    "Comma-separated glob patterns for directories agents can edit. "
    "Default: src/**, tests/**, ai/**"
)
fs_layout.addWidget(QLabel("Editable directories:"))
fs_layout.addWidget(self.txt_editable_dirs)
```

**Parsing:** Comma-separated, stripped, empty entries filtered out.

**`build_safety_config()`:** Read from the text field:
```python
raw = self.txt_editable_dirs.text()
editable = [d.strip() for d in raw.split(",") if d.strip()] if raw.strip() else []
# If empty, use default (user cleared the field)
```

**`_apply_config()`:** Populate from config:
```python
self.txt_editable_dirs.setText(", ".join(config.filesystem.editable_dirs))
```

**Preset behavior:** When a non-custom preset is selected, the editable dirs field shows the default value and is disabled (along with other config groups). In custom mode, it's editable.

### 4. Preset Functions

No changes needed. The three preset functions (`permissive_safety`, `baseline_safety`, `hardened_safety`) construct `FileSystemPolicy()` without specifying `editable_dirs`, so they automatically get the default `["src/**", "tests/**", "ai/**"]`.

### 5. YAML Round-Trip

No changes needed. Pydantic + PyYAML serialization handles `list[str]` natively. Existing compositions without the field get the default via Pydantic.

### 6. Files Changed

| File | Change |
|------|--------|
| `foundry_app/core/models.py` | Add `editable_dirs` field to `FileSystemPolicy` |
| `foundry_app/services/safety.py` | Replace hardcoded `Edit()` rules with loop over `editable_dirs` |
| `foundry_app/ui/screens/builder/wizard_pages/safety_page.py` | Add `QLineEdit` for editable dirs, wire into `build_safety_config()` and `_apply_config()` |
| `tests/test_safety.py` | New tests for custom dirs, default, empty list, whitespace |
| `tests/test_models.py` | Test `FileSystemPolicy` default and custom `editable_dirs` |

## Backward Compatibility

- Old composition YAMLs missing `editable_dirs` → Pydantic default applies → same behavior as before
- Old `SafetyConfig()` calls without the field → same behavior
- Preset functions → unchanged, get default automatically
- No migration needed
