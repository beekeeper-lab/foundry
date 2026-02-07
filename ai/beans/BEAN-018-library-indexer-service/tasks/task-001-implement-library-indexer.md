# Task 001: Implement library_indexer.py

| Field | Value |
|-------|-------|
| **Task ID** | BEAN-018-T001 |
| **Owner** | developer |
| **Status** | Done |
| **Depends On** | — |

## Description

Create `foundry_app/services/library_indexer.py` with the `build_library_index(library_root)` function that:

1. Scans `personas/` directory — for each subdirectory, creates a `PersonaInfo` with:
   - `id`: directory name
   - `path`: absolute path to persona directory
   - `has_persona_md`: whether `persona.md` exists
   - `has_outputs_md`: whether `outputs.md` exists
   - `has_prompts_md`: whether `prompts.md` exists
   - `templates`: list of filenames in `templates/` subdirectory

2. Scans `stacks/` directory — for each subdirectory, creates a `StackInfo` with:
   - `id`: directory name
   - `path`: absolute path to stack directory
   - `files`: list of `.md` filenames in the directory

3. Scans `claude/hooks/` directory — for each `.md` file, creates a `HookPackInfo` with:
   - `id`: filename stem (e.g., `pre-commit-lint`)
   - `path`: absolute path to the file
   - `files`: list containing the filename

4. Returns a `LibraryIndex` with all discovered items, sorted by ID.

5. Handles missing directories gracefully — logs warnings, returns empty lists.

## Acceptance Criteria

- [ ] Function returns LibraryIndex with all 13 personas
- [ ] All 11 stacks indexed with their convention files
- [ ] All 5 hook packs indexed
- [ ] Templates indexed per-persona
- [ ] Missing directories produce warnings, not exceptions
- [ ] Uses standard logging module
