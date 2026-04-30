# BEAN-273 — Design Note: Persona Produces/Consumes Contracts

**Owner:** Architect
**Bean:** BEAN-273 — Persona `produces:` / `consumes:` Contracts
**Task:** 02 — ADR — contract format, location, loader integration
**Status:** Deliverable for Developer (Task 03).
**ADR:** [ADR-013 in `ai/context/decisions.md`](../../context/decisions.md)

This note is the implementation contract for Developer (Task 03). It collapses
ADR-013 into the four concrete questions the bean asked, then lists exact
entry points with signatures and pipeline hooks. A Developer reading this note
end-to-end should be able to write the registry, edit the persona files, stub
the loader, and emit the compiler block without re-reading the bean spec or
BA's task 01 writeup.

---

## The Four Decisions

1. **Contract location on personas:** **sibling `contracts.yml` next to `persona.md`** (not YAML frontmatter, not a markdown `## Contracts` section).
2. **Registry location:** **`ai-team-library/contracts/artifact-types.yml`** — confirmed; new top-level `contracts/` directory in the library.
3. **Loader integration:** **extend `foundry_app/services/library_indexer.py`** with two helpers and two new model fields (no new `contracts_loader.py` module).
4. **Compiler emission shape:** **flat `contracts:` block appended to `ai/team/composition.yml`** with two keys — `personas:` (list of `{id, produces, consumes}`) and `artifact-types:` (list of `{name, format, template-path}` for types referenced by any persona on the team).

Ambiguity resolutions (mirrored from ADR-013, repeated here so Developer doesn't have to flip back):

- `acceptance-criteria` keeps both BA and Team-Lead under `produces:`. Loader does **not** special-case it. Active-producer rule lives in BEAN-274.
- `dev-decision` with no declared consumer is **legal**; loader logs an INFO-level message naming the type and producer. No warning, no error.
- `risk-register` keeps one registry entry, two producers (BA + Architect). No split.
- `handoff-packet` is repeated on every persona's `produces:`. Flat repetition by design.

---

## Worked Example 1 — Persona file with sibling `contracts.yml`

`persona.md` is **unchanged** by this bean. The contract lives in a sibling file. Below is the first 15 lines of `ai-team-library/personas/ba/persona.md` (unchanged) followed by the new sibling.

`ai-team-library/personas/ba/persona.md` (first 15 lines, unchanged):

```markdown
# Persona: Business Analyst (BA)

## Category
Software Development

## Mission

Ensure that every piece of work the **{{ project_name }}** team undertakes is grounded in a clear, validated understanding of the problem. Translate vague business needs into precise, actionable requirements that developers can implement without guessing. Produce requirements that are specific enough to implement, testable enough to verify, and traceable enough to audit. Eliminate ambiguity before it reaches the development pipeline.

## Scope

**Does:**
- Elicit, analyze, and document requirements from stakeholder inputs, briefs, and domain research
- Write user stories with clear acceptance criteria in a testable format (Given/When/Then or equivalent)
- Define scope boundaries -- what is in, what is out, and why
```

New `ai-team-library/personas/ba/contracts.yml`:

```yaml
# Persona contract — produces / consumes artifact types declared by this persona.
# Names must resolve to entries in ai-team-library/contracts/artifact-types.yml.
# Validated at index time by foundry_app/services/library_indexer.py.

produces:
  - user-story
  - acceptance-criteria   # See ADR-013 — dual-producer with team-lead; active-producer pick is BEAN-274.
  - scope-definition
  - risk-register
  - handoff-packet
consumes:
  - bean-spec
  - scope-definition
```

Schema rules the loader enforces:

- File is optional during the rollout but **required** for any persona on a team in a generated project (the compiler refuses to emit `contracts:` for a persona missing the file — emits a warning naming the missing file and skips the entry).
- Top-level keys are exactly `produces` and `consumes`, both required, each a list of strings (empty list is **legal at the schema level** but the bean AC requires non-empty for the five core personas).
- Every name must be present as `name:` in the registry — unknown names log `WARNING` at index time and the entry is dropped from the in-memory model (mirrors the `Persona '<id>' not found` warning shape used elsewhere).
- Duplicates within `produces:` or `consumes:` are deduped silently. Cross-list overlap (a persona produces and consumes the same type) is legal — it represents a self-edit of an artifact across waves.

The same pattern applies to `architect/`, `developer/`, `tech-qa/`, `team-lead/`. Per-persona `produces:` and `consumes:` payloads are in [`ai/outputs/ba/BEAN-273-artifact-types.md` § Persona Contracts](../ba/BEAN-273-artifact-types.md). Developer copies them verbatim into each `contracts.yml`.

---

## Worked Example 2 — `contracts:` block in generated `composition.yml`

After this bean, a generated project's `ai/team/composition.yml` ends with the existing `orchestration:` block followed by the new `contracts:` block. Sample with three personas:

```yaml
# … existing project / team / safety / generation blocks …

orchestration:
  orchestrator_role: team-lead
  team_model: available-bench
  required_roles:
    software-development:
      - developer
      - tech-qa
  optional_roles:
    - architect
    - ux-ui-designer
    - integrator-merge-captain
    - ba

contracts:
  personas:
    - id: ba
      produces:
        - user-story
        - acceptance-criteria
        - scope-definition
        - risk-register
        - handoff-packet
      consumes:
        - bean-spec
        - scope-definition
    - id: developer
      produces:
        - code-change
        - dev-decision
        - handoff-packet
      consumes:
        - task-spec
        - user-story
        - acceptance-criteria
        - design-spec
        - adr
    - id: tech-qa
      produces:
        - test-suite
        - traceability-matrix
        - vdd-report
        - handoff-packet
      consumes:
        - acceptance-criteria
        - design-spec
        - code-change
        - bean-spec
  artifact-types:
    - name: user-story
      format: markdown
      template-path: personas/ba/templates/user-story.md
    - name: acceptance-criteria
      format: markdown
      template-path: personas/ba/templates/acceptance-criteria.md
    - name: scope-definition
      format: markdown
      template-path: null
    - name: risk-register
      format: markdown
      template-path: null
    - name: handoff-packet
      format: markdown
      template-path: null
    - name: bean-spec
      format: markdown
      template-path: ai/beans/_bean-template.md
    - name: code-change
      format: markdown
      template-path: personas/developer/templates/pr-description.md
    - name: dev-decision
      format: markdown
      template-path: personas/developer/templates/dev-design-decision.md
    - name: task-spec
      format: markdown
      template-path: personas/team-lead/templates/task-spec.md
    - name: design-spec
      format: markdown
      template-path: personas/architect/templates/design-spec.md
    - name: adr
      format: markdown
      template-path: personas/architect/templates/adr.md
    - name: test-suite
      format: markdown
      template-path: personas/tech-qa/templates/test-plan.md
    - name: traceability-matrix
      format: markdown
      template-path: personas/tech-qa/templates/traceability-matrix.md
    - name: vdd-report
      format: markdown
      template-path: personas/tech-qa/templates/test-report.md
```

Shape rules the compiler enforces:

- `contracts.personas` is ordered identically to `spec.team.personas` (preserves the wizard's selection order).
- Each persona's `produces:` / `consumes:` is copied verbatim from the persona's `contracts.yml` after registry validation.
- `contracts.artifact-types` is the **union** of every name appearing in any persona's `produces:` or `consumes:` on this team — no team-irrelevant types leak into the emit.
- `artifact-types` is sorted by `name:` (stable ordering for diffing).
- Each artifact-type entry carries `name`, `format`, `template-path` only. `description` and `required-fields` are intentionally omitted from the emit (see ADR-013 Decision 4).
- Block is omitted entirely when `spec.team.personas` is empty (parallels the existing orchestration-block gating).

---

## Implementation Entry Points (signatures Developer adds or extends)

### A. New file — registry source of truth

**Location:** `ai-team-library/contracts/artifact-types.yml`
**Author:** Developer copies the registry content from BA's task 01 deliverable verbatim. Schema is fixed: top-level `types:` list, each entry has `name`, `description`, `format`, `required-fields`, `template-path`. (BA already laid this out — see `ai/outputs/ba/BEAN-273-artifact-types.md` § Registry, lines 23–253.)

### B. New Pydantic model — `ArtifactTypeInfo`

**Location:** `foundry_app/core/models.py` (added near `PersonaInfo`, before `LibraryIndex`)

```python
class ArtifactTypeInfo(BaseModel):
    """Metadata about an artifact type defined in the contracts registry."""

    name: str = Field(..., min_length=1)
    description: str = ""
    format: str = "markdown"  # markdown | yaml | json
    required_fields: list[str] = Field(default_factory=list)
    template_path: str | None = None
```

### C. Extended Pydantic models — `PersonaInfo`, `LibraryIndex`

Add two fields to `PersonaInfo`:

```python
class PersonaInfo(BaseModel):
    # … existing fields …
    produces: list[str] = Field(
        default_factory=list,
        description="Artifact-type names this persona produces. See ADR-013.",
    )
    consumes: list[str] = Field(
        default_factory=list,
        description="Artifact-type names this persona consumes. See ADR-013.",
    )
```

Add one field to `LibraryIndex`:

```python
class LibraryIndex(BaseModel):
    # … existing fields …
    artifact_types: list[ArtifactTypeInfo] = Field(default_factory=list)

    def artifact_type_by_name(self, name: str) -> ArtifactTypeInfo | None:
        return next((a for a in self.artifact_types if a.name == name), None)
```

### D. New helpers — extend `foundry_app/services/library_indexer.py`

Two new functions plus a one-line addition inside the existing `_scan_personas` loop and a small change to `build_library_index`.

**New helper 1 — load the registry:**

```python
def _load_artifact_type_registry(contracts_dir: Path) -> list[ArtifactTypeInfo]:
    """Load and parse ``contracts/artifact-types.yml``.

    Returns an empty list (with a logger.warning) if the file is missing,
    malformed, or has no ``types:`` key. Per ADR-013, every name referenced
    by a persona's contracts.yml must resolve to an entry returned here.
    """
```

**New helper 2 — load a persona's contracts:**

```python
def _load_persona_contracts(
    persona_dir: Path,
    known_artifact_names: set[str],
) -> tuple[list[str], list[str]]:
    """Read ``<persona_dir>/contracts.yml`` and return (produces, consumes).

    Validates each name against ``known_artifact_names`` and drops unknown
    names with a logger.warning ("Artifact type '<name>' not found in
    registry (referenced by persona '<id>' contracts.yml)").

    Returns ([], []) if the file is missing or malformed.
    """
```

**Wire-up inside `_scan_personas`** — after building `templates`, before constructing `PersonaInfo`, add:

```python
produces, consumes = _load_persona_contracts(entry, known_artifact_names)
```

This requires `_scan_personas` to accept `known_artifact_names: set[str]` as a parameter (currently signature is `(personas_dir: Path) -> list[PersonaInfo]`). The new signature is:

```python
def _scan_personas(
    personas_dir: Path,
    known_artifact_names: set[str],
) -> list[PersonaInfo]:
```

Pass `produces` and `consumes` into the `PersonaInfo(...)` constructor.

**Wire-up inside `build_library_index`** — load artifact types **before** scanning personas (the persona scan needs the names to validate against), then pass the names down:

```python
def build_library_index(library_root: str | Path) -> LibraryIndex:
    root = Path(library_root).resolve()
    if not root.is_dir():
        logger.warning("Library root does not exist: %s", root)
        return LibraryIndex(library_root=str(root))

    artifact_types = _load_artifact_type_registry(root / "contracts")
    known_names = {a.name for a in artifact_types}

    personas = _scan_personas(root / "personas", known_names)
    expertise = _scan_expertise(root / "expertise")
    expertise = _validate_expertise_applies_to(
        expertise, {p.id for p in personas},
    )
    hook_packs = _scan_hook_packs(root / "claude" / "hooks")

    # Dangling-producer pass — INFO log per ADR-013 ambiguity resolution.
    _log_dangling_producers(personas)

    logger.info(
        "Indexed library: %d personas, %d expertise, %d hook packs, %d artifact types",
        len(personas), len(expertise), len(hook_packs), len(artifact_types),
    )

    return LibraryIndex(
        library_root=str(root),
        personas=personas,
        expertise=expertise,
        hook_packs=hook_packs,
        artifact_types=artifact_types,
    )
```

**New helper 3 — dangling-producer info log:**

```python
def _log_dangling_producers(personas: list[PersonaInfo]) -> None:
    """Emit INFO log entries for produced artifact types with no consumer.

    Per ADR-013: ``dev-decision`` and similar types are legal but warned —
    we surface them as INFO (not WARNING) so reviewers can see them in CI
    output without failing the build. ``handoff-packet`` is excluded from
    this check because it is universally produced and consumed implicitly
    by team-lead at handoff time.
    """
```

### E. New helpers — extend `foundry_app/services/scaffold.py` (compiler emission)

The `contracts:` block is appended to the same file where `_ORCHESTRATION_YAML_BLOCK` is written. Add a new builder function and call it in `scaffold_project` immediately after the orchestration-block append.

**New helper:**

```python
def _build_contracts_yaml_block(
    spec: CompositionSpec,
    library_index: LibraryIndex,
) -> str:
    """Render the ``contracts:`` block for the generated composition.yml.

    Emits one entry per persona on the team (`spec.team.personas`),
    sourcing produces/consumes from the LibraryIndex's PersonaInfo. Then
    emits a flat artifact-types reference list — the union of every name
    appearing in any persona's produces/consumes, sorted by name.

    Returns an empty string when ``spec.team.personas`` is empty so the
    caller can append unconditionally.
    """
```

**Wire-up inside `scaffold_project`** — locate the existing append-orchestration-block code (around line 324–328 in `scaffold.py`):

```python
composition_path.write_text(
    composition_path.read_text(encoding="utf-8")
    + _ORCHESTRATION_YAML_BLOCK
    + _build_contracts_yaml_block(spec, library_index),
    encoding="utf-8",
)
```

`scaffold_project` already receives `library_index` (it does not today — confirm signature). If it doesn't, **the smaller change is to extend `scaffold_project`'s signature to accept `library_index: LibraryIndex`** and have `generator._run_pipeline` pass it through. Compare `_run_stage("scaffold", scaffold_project, spec, output_dir, library_root)` with how `compile_project` already gets the index — extend scaffold to match (`spec, output_dir, library_root, library_index` is the natural order). Developer should pick whichever ordering matches the existing convention; the substantive change is "scaffold now sees `library_index`."

### F. Generator orchestrator hooks (`foundry_app/services/generator.py`)

No new stage. The existing pipeline order **stays the same**:

1. Validate
2. **Scaffold** ← appends `contracts:` block to `composition.yml`
3. Compile
4. Copy Assets
5. Seed
6. Write Manifest

The library index is built once at the top of `generate_project` (line 291: `library = build_library_index(library_path)`). After this bean, that single call already loads the artifact-type registry and the per-persona contracts; downstream stages see them via `LibraryIndex` and `PersonaInfo` without further wiring.

The only generator-level change is whichever signature tweak Developer makes for `scaffold_project` (passing `library_index` through), which is one parameter added at the `_run_stage("scaffold", ...)` call site in `_run_pipeline`.

---

## Test Hooks (for Tech-QA, Task 04 — non-binding sketch)

The bean AC requires three tests beyond the lint sweep. Tech-QA owns these; this list is just to confirm the design supports them.

1. **Registry loads.** `_load_artifact_type_registry(Path('ai-team-library/contracts'))` returns a non-empty list whose `name`s match the BA-supplied set.
2. **Every persona-referenced type exists in the registry.** For every persona in `LibraryIndex.personas`, every name in `produces` and `consumes` resolves via `LibraryIndex.artifact_type_by_name`.
3. **Round-trip through compiler.** Generate a project from a fixture composition with at least 3 personas, parse the resulting `composition.yml` with PyYAML, and assert: (a) `contracts.personas` length equals team size, (b) `contracts.personas[*].id` ordering matches `spec.team.personas[*].id`, (c) `contracts.artifact-types` is the sorted union of all referenced names, (d) the block is absent when the team is empty.
4. **At least one matching produces → consumes pair.** Trivially satisfied by the BA → Developer (`user-story`) and Developer → Tech-QA (`code-change`) edges in BA's task 01 contract set.
5. **No core persona has empty produces or consumes.** Already satisfied by BA's contract payloads — verify by parse.

---

## Files Developer Touches in Task 03 (summary)

**New files:**
- `ai-team-library/contracts/artifact-types.yml` — registry (content from BA's task 01 deliverable).
- `ai-team-library/personas/ba/contracts.yml`
- `ai-team-library/personas/architect/contracts.yml`
- `ai-team-library/personas/developer/contracts.yml`
- `ai-team-library/personas/tech-qa/contracts.yml`
- `ai-team-library/personas/team-lead/contracts.yml`

**Edited files:**
- `foundry_app/core/models.py` — add `ArtifactTypeInfo`; extend `PersonaInfo` and `LibraryIndex`.
- `foundry_app/services/library_indexer.py` — add `_load_artifact_type_registry`, `_load_persona_contracts`, `_log_dangling_producers`; extend `_scan_personas` signature; rewire `build_library_index`.
- `foundry_app/services/scaffold.py` — add `_build_contracts_yaml_block`; extend `scaffold_project` signature; append the new block after `_ORCHESTRATION_YAML_BLOCK`.
- `foundry_app/services/generator.py` — pass `library` through to `scaffold_project` at the `_run_stage("scaffold", ...)` call site.

**Untouched (intentional):**
- `ai-team-library/personas/*/persona.md` — no edits. The contracts live in the sibling YAML.
- `foundry_app/services/compiler.py` — no edits. Contracts emission is the scaffold stage's job because that is where `composition.yml` is written.
- `foundry_app/io/composition_io.py` — no edits. The contracts block is appended as raw YAML text after `save_composition`, mirroring how `_ORCHESTRATION_YAML_BLOCK` works today.

---

## Out of Scope for Task 03 (and this bean)

- Validating the contract graph at compose-time (which type is the active producer of `acceptance-criteria` for a given team) → **BEAN-274**.
- Per-edge handoff schemas tied to specific producer-consumer pairs → **BEAN-276**.
- Codifying the `acceptance-criteria` ownership policy text → **BEAN-275**.
- Updating extended (non-core) personas → out of scope by bean Scope.
- Schema enforcement on artifact bodies (e.g. "user-story must contain Given/When/Then") → follow-up bean.
