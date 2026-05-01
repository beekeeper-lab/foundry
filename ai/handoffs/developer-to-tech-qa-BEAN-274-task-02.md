# Handoff: developer → tech-qa — BEAN-274 task 02

| Field | Value |
|-------|-------|
| **From** | developer |
| **To** | tech-qa |
| **Bean** | BEAN-274 |
| **Task** | tasks/02-tech-qa-contract-validator-tests.md |
| **Date** | 2026-05-01 |
| **Packet schema** | `code-change` (intersection of developer.produces ∩ tech-qa.consumes) + edge extras (developer → tech-qa) |

## Contract intersection — how this packet was shaped

- `developer.produces` = `[code-change, dev-decision, handoff-packet]`
- `tech-qa.consumes` = `[acceptance-criteria, design-spec, code-change, bean-spec]`
- `intersection` = `[code-change]`
  - `dev-decision` and `handoff-packet` are produced by Developer but not
    consumed by Tech-QA, so they are not part of this packet's schema.
  - `acceptance-criteria`, `design-spec`, and `bean-spec` are consumed by
    Tech-QA but produced upstream (BA/Architect/Team-Lead), not by
    Developer — they are out of scope for this edge.

## Produced artifacts

### code-change

Required fields per `contracts/artifact-types.yml :: code-change`:
`summary`, `what-changed`, `how-to-test`, `files-touched`.

- **summary:** Compose-time `validate_contract_graph(personas, registry)`
  that hard-fails standard generations on unsatisfied `consumes` and warns
  (via `GenerationManifest`) on overlay re-generations. Wizard's persona
  page now renders a green/yellow/red coherence indicator that reacts to
  selection changes.
- **what-changed:**
  - Added `validate_contract_graph(...)` and the
    `_CONTRACT_GRAPH_IGNORED_TYPES` set in
    `foundry_app/services/validator.py` (extends the existing module
    rather than introducing a parallel one — see comment block at line
    290).
  - Wired the new check into `generate_project` in
    `foundry_app/services/generator.py` between `_apply_default_team` and
    `run_pre_generation_validation`. Standard mode raises; overlay mode
    records warnings on `GenerationManifest.all_warnings`.
  - Wizard indicator added to
    `foundry_app/ui/screens/builder/wizard_pages/persona_page.py`.
    Single signal/slot connection on persona-selection change recomputes
    the indicator state (🟢 / 🟡 / 🔴) — no per-checkbox flicker.
- **how-to-test:** See `rerun-command` and `test-targets` under Edge
  Extras below. End-to-end: assemble a team that omits a producer for a
  consumed type (e.g., a team with Tech-QA but no Developer), call
  `validate_contract_graph` directly for a unit assertion, then call
  `generate_project` with `overlay=False` and verify it raises with the
  exact missing-producer message format from the bean.
- **files-touched:**
  - `foundry_app/services/validator.py` — new `validate_contract_graph`
    function (lines 290-360+).
  - `foundry_app/services/generator.py` — new call site between
    `_apply_default_team` and `run_pre_generation_validation`.
  - `foundry_app/ui/screens/builder/wizard_pages/persona_page.py` —
    indicator widget + selection-change handler.
  - Comprehension and dev-decision notes are NOT part of `code-change`
    but are referenced under "Start here" as starting context.

## Edge extras (developer → tech-qa)

Per `contracts/artifact-types.yml :: pair-fields`, this edge adds
`test-targets` and `rerun-command` to the packet schema:

- **test-targets:** Tech-QA should focus on
  `tests/test_validator.py` (extend the existing module — see lines
  590+ where the existing `validate_contract_graph` smoke tests
  already live; the comprehensive sweep belongs alongside them) and
  `tests/test_persona_page.py` (wizard indicator transitions, mirrors
  the BEAN-271 tier-group test idiom). End-to-end pipeline integration
  belongs in `tests/test_generator.py`.
- **rerun-command:** `uv run pytest tests/test_validator.py
  tests/test_generator.py tests/test_persona_page.py -q` (developer's
  last green run); full-suite final verification is `uv run pytest`.

## Start here

The 3 files Tech-QA should read first, in order:

1. `foundry_app/services/validator.py` (lines 290-360) — the
   `validate_contract_graph` API surface. Read this first to know the
   exact message format and result shape to assert against.
2. `tests/test_validator.py` (lines 590+) — existing smoke tests show
   the construction pattern (`_registry(...)` helper, `team` fixtures);
   extend rather than start fresh.
3. `ai/beans/BEAN-274-contract-graph-validator/tasks/02-tech-qa-contract-validator-tests.md`
   — the task spec with the full AC list.

## Notes

- `validate_contract_graph` excludes `handoff-packet` from the orphan
  check (it is universally produced and implicitly consumed by Team
  Lead); tests should assert that an orphan `handoff-packet` does NOT
  trigger a warning.
- Overlay mode warning channel is `GenerationManifest.all_warnings` —
  do not invent a new field.
- The wizard indicator is hard to test through Qt without a running
  event loop; the task explicitly allows a unit test on the
  computation function as a fallback.
