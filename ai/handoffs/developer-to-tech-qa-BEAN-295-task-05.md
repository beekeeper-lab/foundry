# Handoff Packet: developer → tech-qa (BEAN-295, tasks 01-05)

| Field | Value |
|-------|-------|
| **From** | developer |
| **To** | tech-qa |
| **Bean** | BEAN-295 |
| **Task** | 01-04 (pack authoring) + 05 (integration) |
| **Date** | 2026-07-03 |

## Artifacts

| Artifact type | Path | Required fields present? |
|---------------|------|--------------------------|
| code-change | ai-team-library/expertise/{fastapi,nextjs,vue,spring-boot}/ (15 files) | yes — summary below, what-changed per pack, how-to-test below, files-touched listed |
| code-change | tests/test_library_indexer.py, foundry_app/services/asset_copier.py | yes |

## Edge Extras

- **test-targets:** tests/test_reference_integrity.py, tests/test_library_indexer.py, full suite
- **rerun-command:** `QT_QPA_PLATFORM=offscreen uv run pytest -q`

## Summary

Four new framework packs (fastapi 4 files, nextjs 4, vue 3, spring-boot 4)
authored to the SPEC-019 contract (frontmatter, canonical schema, Defaults
tables); category normalized to the existing `Frameworks` taxonomy value;
packs registered in the indexer lock-in tests and dev-loop stack map
(fastapi→python, nextjs→node, vue→node, spring-boot→jvm).

## Receiver Can Start When

- This packet exists and the full suite is green (verified at handoff:
  2,567 passing).
