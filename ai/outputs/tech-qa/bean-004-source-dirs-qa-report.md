# BEAN-004: Source Directory Configuration — QA Report

**Author:** Tech-QA | **Date:** 2026-02-07 | **Bean:** BEAN-004

## Verdict: GO

## Test Results

- **Total tests:** 313 (300 existing + 13 new)
- **Pass:** 313
- **Fail:** 0
- **Lint:** 21 pre-existing E501 warnings, 0 new issues

## Traceability Matrix

| Bean AC | Test(s) | Status |
|---------|---------|--------|
| Composition spec supports `editable_dirs` field | `test_filesystem_policy_default_editable_dirs`, `test_custom_editable_dirs_single` | PASS |
| Generated settings.local.json uses configured dirs | `test_custom_editable_dirs_single`, `test_custom_editable_dirs_multiple`, `test_write_safety_files_custom_dirs_in_json` | PASS |
| Default behavior unchanged when field omitted | `test_default_editable_dirs_produces_standard_rules`, `test_old_config_without_editable_dirs_gets_default` | PASS |
| Wizard Safety page includes editable dirs input | Code review verified (safety_page.py:104-111) | PASS |
| Tests cover custom dirs, default, multiple dirs | 13 new tests across all scenarios | PASS |
| All tests pass | 313 passed | PASS |
| Lint clean | 0 new issues | PASS |

## Edge Cases Verified

| ID | Case | Test | Status |
|----|------|------|--------|
| EC-1 | Empty list `[]` | `test_empty_editable_dirs_no_edit_rules` | PASS |
| EC-2 | Field omitted | `test_old_config_without_editable_dirs_gets_default` | PASS |
| EC-3 | Single dir | `test_custom_editable_dirs_single` | PASS |
| EC-4 | Duplicate entries | Manual verification — duplicates pass through (by design per Architect spec) | NOTED |
| EC-5 | Whitespace | `test_editable_dirs_strips_whitespace` | PASS |
| EC-6 | No glob pattern | `test_editable_dirs_without_glob_accepted` | PASS |
| EC-7 | Old YAML without field | `test_old_config_without_editable_dirs_gets_default` | PASS |
| EC-8 | Wizard field cleared | `test_empty_editable_dirs_no_edit_rules` (service layer) | PASS |

## Code Review Summary

### `foundry_app/core/models.py`
- `editable_dirs` field uses `default_factory=lambda` — correct, avoids shared mutable default
- Default `["src/**", "tests/**", "ai/**"]` matches previous hardcoded behavior — backward compatible

### `foundry_app/services/safety.py`
- Loop with `.strip()` and empty-string filter is clean and defensive
- `Read(**)` always emitted regardless of `editable_dirs` — correct

### `foundry_app/ui/screens/builder/wizard_pages/safety_page.py`
- `QLineEdit` with placeholder and tooltip provides good UX guidance
- `_parse_editable_dirs()` correctly handles comma separation, stripping, empty filtering
- Wired into both `build_safety_config()` and `_apply_config()` — round-trip works

### YAML Round-Trip
- `test_editable_dirs_yaml_round_trip` confirms PyYAML serialization works correctly

## Findings

| # | Severity | Finding | Disposition |
|---|----------|---------|------------|
| F-1 | Info | Duplicate entries in `editable_dirs` produce duplicate `Edit()` rules | By design (Architect ADR-002). Claude Code handles duplicates gracefully. |
| F-2 | Info | No validation that dir patterns are syntactically valid | Acceptable — Claude Code treats them as opaque strings. Invalid patterns simply won't match. |

## Recommendation

**GO** — All acceptance criteria met. 13 new tests with full edge case coverage. No regressions. Clean implementation following the design spec.
