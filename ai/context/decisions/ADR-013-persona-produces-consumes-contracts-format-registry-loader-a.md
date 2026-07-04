# ADR-013: Persona Produces/Consumes Contracts — Format, Registry, Loader, and Compiler Emission

| Field | Value |
|-------|-------|
| **Date** | 2026-04-30 |
| **Status** | Accepted |
| **Bean** | BEAN-273 |
| **Deciders** | Architect |

> **Practice note (2026-07 audit, SPEC-029):** contracts cover the core five personas only (extended personas have no contracts.yml — SPEC-017), and /handoff fired once across ~294 beans, so the runtime value of the contract graph is unproven. Compose-time validation (BEAN-274) is the part that demonstrably works.

## Context

BEAN-273 introduces machine-readable produces/consumes contracts to every core persona, plus a registry of artifact types they reference. This ADR locks four structural choices the rest of BEAN-273 (Developer task 03) and downstream beans (BEAN-274 contract-graph validator, BEAN-276 per-edge handoff schemas) will depend on. BA's task 01 deliverable (`ai/outputs/ba/BEAN-273-artifact-types.md`) supplies the registry content and the per-persona contract payloads; this ADR commits to the on-disk shape, the loader integration, and the compiler emission shape so Developer can implement without further design questions.

The bean Notes recommended YAML frontmatter on `persona.md`. ADR-012 rejected YAML frontmatter for a similar metadata case ("The library has never used YAML front-matter; … adding a third precedent for the same kind of metadata would fragment the parser"). That precedent forces a re-evaluation here.

## Decision

**1. Contract location on personas — sibling `contracts.yml` next to `persona.md`.** Each core persona directory grows one new file, `ai-team-library/personas/<id>/contracts.yml`, holding `produces:` and `consumes:` arrays of artifact-type names. **Rationale:** YAML frontmatter would create a third metadata format on `persona.md` (alongside the existing `## Category` markdown section and the per-expertise `## Applies To` markdown section in ADR-012), fragmenting the parser ADR-012 explicitly preserved. A sibling YAML file keeps `persona.md` pure markdown for human readers, parses with the existing PyYAML dependency in three lines, and follows the ADR-005 / ADR-012 "metadata lives next to its thing" principle. The trade-off — one extra file per persona — is small and consistent with the existing per-persona directory layout (`persona.md`, `outputs.md`, `prompts.md`, `templates/`).

**2. Registry location — `ai-team-library/contracts/artifact-types.yml`.** Confirmed as the canonical path; a new top-level `contracts/` directory is added to the library. **Rationale:** `personas/` describes *who*, `templates/` (per-persona) describes *what to write*, and `workflows/` describes *how the team flows*. Artifact types are a cross-cutting glossary owned by no single persona — they belong in their own top-level slot. Nesting under `personas/` would imply persona ownership; nesting under `templates/` would imply per-template scope; nesting under `workflows/` would imply per-workflow scope. None of those frames fit. A top-level `contracts/` directory makes future siblings (e.g. `handoff-schemas.yml` for BEAN-276) a natural addition without re-rooting paths.

**3. Loader integration — extend `foundry_app/services/library_indexer.py`.** A new `contracts_loader.py` module is rejected. **Rationale:** the indexer already walks every persona directory once (`_scan_personas`) and every category/applies-to file once. Adding the contracts read inline costs one additional `path.read_text` call per persona inside the existing loop and one new top-level `_load_artifact_type_registry(library_root / "contracts" / "artifact-types.yml")` call inside `build_library_index`. The blast radius is two new helpers and two new fields on existing models (`PersonaInfo.produces`, `PersonaInfo.consumes`, plus a new `LibraryIndex.artifact_types` list of `ArtifactTypeInfo`). A separate `contracts_loader.py` would duplicate the directory walk, duplicate caller wiring (`generator.py` would need to call two loaders and reconcile two return shapes), and introduce a parallel error-reporting code path. Rejected.

**4. Compiler emission shape — flat `contracts:` block at the bottom of generated `ai/team/composition.yml`.** The shape is frozen as:

```yaml
contracts:
  personas:
    - id: ba
      produces: [user-story, acceptance-criteria, scope-definition, risk-register, handoff-packet]
      consumes: [bean-spec, scope-definition]
    - id: developer
      produces: [code-change, dev-decision, handoff-packet]
      consumes: [task-spec, user-story, acceptance-criteria, design-spec, adr]
    # … one entry per persona on the team
  artifact-types:
    - name: user-story
      format: markdown
      template-path: personas/ba/templates/user-story.md
    - name: code-change
      format: markdown
      template-path: personas/developer/templates/pr-description.md
    # … one entry per artifact type referenced by any persona on the team
```

**Rationale:** this is a flat, addressable, read-once view of the team's contract graph. `personas:` is a list (ordered) so consumers can iterate. `artifact-types:` is a flat reference list — only types actually referenced by a persona on the team appear, so the block stays small (~10-15 entries) and self-contained for BEAN-274's validator. Each artifact-type entry carries `format` and `template-path` (the two registry fields the validator needs). `description` and `required-fields` from the source registry are intentionally omitted at emit time — they live in the library's `artifact-types.yml` for authoring and can be reloaded by tooling that needs them, but they would bloat every generated `composition.yml` without value to the validator.

The block is appended **after** the existing `orchestration:` policy block emitted by `scaffold.py` (`_ORCHESTRATION_YAML_BLOCK`), and emission is gated on `spec.team.personas` being non-empty — same condition the orchestration block already implicitly relies on.

## Ambiguity Resolutions (from BA's task 01 writeup)

- **`acceptance-criteria` dual producer (BA + Team-Lead).** Both personas keep the type in their `produces:`. The contract-graph view treats the registry-side declaration as legal; the per-bean *active-producer* selection rule is "BA wins when on the wave, Team-Lead is fallback." The loader and compiler do **not** special-case this type — they emit both producers in `contracts.personas[].produces`. BEAN-274's validator codifies the active-producer pick; BEAN-275 codifies the prose policy. This ADR records the structural rule only.
- **`dev-decision` has no declared consumer.** The loader treats dangling produced types as **legal but warned**: `library_indexer` logs `"Artifact type '<name>' produced by '<persona>' has no declared consumer"` at INFO level (not WARNING — it is a real signal but not an error, and Team-Lead reviews `dev-decision` content via `merge-summary` synthesis at bean-close). Handoffs for dangling types are not required.
- **`risk-register` shared by BA + Architect.** Keep one registry entry with two producers, mirroring the `acceptance-criteria` pattern. Defer split into `requirements-risks` / `design-risks` to a later bean if the validator can't disambiguate. Confirmed.
- **`handoff-packet` produced by every persona.** Keep flat repetition — every persona's `produces:` lists `handoff-packet`. Confirmed. A "produced-by-everyone" tag would add a second emission code path for one type; the cost (five extra string entries across five personas) is below the threshold where a special case earns its keep.

## Consequences

**Positive:**
- The persona markdown stays clean and human-readable; no new parser is needed for the contract data (PyYAML already in deps).
- Loader extension is two helpers and two fields — small blast radius, single point of failure, single point of test.
- The frozen `composition.yml` shape gives BEAN-274 a stable target. Validator authors can write tests against canned `composition.yml` fixtures without coordinating with this bean.
- The flat reference list of artifact-types in the emitted block keeps generated projects self-describing without re-reading the library at runtime.
- Adding a new persona to a team is one new `contracts.yml` plus one entry in `composition.yml.contracts.personas` — the artifact-types list rebuilds automatically at compile time.

**Negative:**
- One extra file per persona (`contracts.yml`) — visible cost in the persona directory listing. Mitigated by the file being short (≈10 lines per persona) and self-explanatory.
- The dual-producer `acceptance-criteria` model means BEAN-274 must implement an "active producer" rule rather than a simpler "exactly one producer" check. Acceptable; the rule is short and well-scoped.
- The `contracts.yml` files are an additional surface kit-distribution must keep in sync if the library is mirrored across projects. Existing kit-sync paths already copy whole persona directories, so this is mechanical.

## Alternatives Rejected

1. **YAML frontmatter at the top of `persona.md`** (the bean Notes' recommendation). Rejected for the same reason ADR-012 rejected frontmatter on expertise files: the library's existing convention is markdown-section metadata (`## Category`, `## Conflicts With`, `## Applies To`), and adding a third metadata format fragments the parser. The bean Notes invited a concrete reason; ADR-012 supplies one.
2. **A new `## Contracts` markdown section inside `persona.md`.** Rejected because YAML inside a fenced markdown block requires a custom parser (find the heading, find the fence, slice the body, hand off to PyYAML). The sibling-file approach is parseable in three lines (`yaml.safe_load(path.read_text())`).
3. **A new `foundry_app/services/contracts_loader.py` module.** Rejected — see Decision 3. The indexer already walks the persona tree once; piggy-backing is cheaper than a parallel walker.
4. **Single registry-side definition with `produces-by:` / `consumes-by:` pointers** (instead of duplicating onto each persona). Rejected — the locality argument from ADR-012 holds: a new persona's contract belongs in that persona's directory, not in a centralized registry. Maintainers adding a persona edit the persona's own files.
5. **Embedding the full registry (`description`, `required-fields`, etc.) in every emitted `composition.yml`.** Rejected — bloats the generated file with duplicated data the validator does not consume. The library's `artifact-types.yml` is the source of truth; BEAN-274's validator can reload it from `library_root` (or from the library copy bundled into the generated project) when it needs the deeper schema.

## Reversibility

Fully reversible. Rollback path: delete `ai-team-library/contracts/`, delete each persona's `contracts.yml`, drop the `produces`/`consumes` fields and `ArtifactTypeInfo` model, drop the loader helpers, and remove the `contracts:` block emission in `scaffold.py`. Generated projects with the old shape continue to work — the validator (BEAN-274) is the first consumer of this contract data, and it will not exist until after this bean lands.
