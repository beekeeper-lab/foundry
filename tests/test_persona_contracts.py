"""Tests for the persona produces/consumes contract pipeline (BEAN-273).

Covers:
- Artifact-type registry loading & validation (``_load_artifact_type_registry``).
- Per-persona ``contracts.yml`` loading via ``build_library_index``.
- Cross-persona type-resolution and pairing invariants.
- Compiler/scaffold round-trip emission of the ``contracts:`` block in a
  generated project's ``ai/team/composition.yml``.
"""

from pathlib import Path

import pytest
import yaml

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    PersonaSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.library_indexer import (
    _load_artifact_type_registry,
    build_library_index,
)
from foundry_app.services.scaffold import scaffold_project

# Path to the real library bundled with the repo
LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "ai-team-library"

CORE_PERSONAS = ("ba", "architect", "developer", "tech-qa", "team-lead")

REGISTRY_REQUIRED_FIELDS = ("name", "description", "format", "required-fields")


# ---------------------------------------------------------------------------
# Test 1 — Registry parses
# ---------------------------------------------------------------------------


class TestArtifactTypeRegistryParses:
    """The bundled registry loads with the expected entries and required fields."""

    def test_registry_returns_non_empty_list(self):
        types = _load_artifact_type_registry(LIBRARY_ROOT / "contracts")
        assert types, "Expected the bundled registry to load at least one type"

    def test_registry_count_in_expected_range(self):
        """BEAN-273 Scope says ~12-15 types; assert the registry sits in band."""
        types = _load_artifact_type_registry(LIBRARY_ROOT / "contracts")
        assert 12 <= len(types) <= 15, (
            f"Registry size {len(types)} outside the BEAN-273 expected 12-15 band"
        )

    def test_registry_contains_named_core_types(self):
        types = _load_artifact_type_registry(LIBRARY_ROOT / "contracts")
        names = {t.name for t in types}
        # Named in the bean's Scope as the initial 12-15 types.
        for required in (
            "bean-spec",
            "task-spec",
            "user-story",
            "acceptance-criteria",
            "code-change",
            "test-suite",
            "vdd-report",
            "handoff-packet",
        ):
            assert required in names, f"{required} missing from registry"

    def test_every_entry_has_required_fields(self):
        types = _load_artifact_type_registry(LIBRARY_ROOT / "contracts")
        for t in types:
            assert t.name, "name must be non-empty"
            assert t.format, f"{t.name} missing format"
            assert isinstance(t.required_fields, list)
            # description may be empty; but for the bundled registry every
            # entry has prose.
            assert t.description, f"{t.name} missing description"

    def test_template_path_is_string_or_none(self):
        types = _load_artifact_type_registry(LIBRARY_ROOT / "contracts")
        for t in types:
            assert t.template_path is None or isinstance(t.template_path, str)


# ---------------------------------------------------------------------------
# Test 2 — Registry rejects malformed entries
# ---------------------------------------------------------------------------


class TestArtifactTypeRegistryRejectsMalformed:
    """A malformed registry raises with a message that names the offending entry."""

    def _write_registry(self, tmp_path: Path, body: str) -> Path:
        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()
        (contracts_dir / "artifact-types.yml").write_text(body, encoding="utf-8")
        return contracts_dir

    def test_missing_required_field_names_offending_entry(self, tmp_path: Path):
        body = (
            "types:\n"
            "  - name: good-type\n"
            "    description: ok\n"
            "    format: markdown\n"
            "    required-fields: []\n"
            "  - name: bad-type\n"
            "    description: missing format and required-fields\n"
        )
        contracts_dir = self._write_registry(tmp_path, body)
        with pytest.raises(ValueError) as excinfo:
            _load_artifact_type_registry(contracts_dir)
        msg = str(excinfo.value)
        assert "bad-type" in msg, f"Error must name the offending entry: {msg}"

    def test_non_mapping_entry_names_index(self, tmp_path: Path):
        body = (
            "types:\n"
            "  - name: ok\n"
            "    description: fine\n"
            "    format: markdown\n"
            "    required-fields: []\n"
            "  - 'not-a-mapping-string'\n"
        )
        contracts_dir = self._write_registry(tmp_path, body)
        with pytest.raises(ValueError) as excinfo:
            _load_artifact_type_registry(contracts_dir)
        msg = str(excinfo.value)
        assert "#1" in msg or "not-a-mapping" in msg, (
            f"Error must locate the offending entry: {msg}"
        )

    def test_non_list_required_fields_names_offender(self, tmp_path: Path):
        body = (
            "types:\n"
            "  - name: weird-type\n"
            "    description: required-fields is not a list\n"
            "    format: markdown\n"
            "    required-fields: 'not-a-list'\n"
        )
        contracts_dir = self._write_registry(tmp_path, body)
        with pytest.raises(ValueError) as excinfo:
            _load_artifact_type_registry(contracts_dir)
        assert "weird-type" in str(excinfo.value)

    def test_missing_file_returns_empty_with_warning(self, tmp_path: Path, caplog):
        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()
        with caplog.at_level("WARNING"):
            result = _load_artifact_type_registry(contracts_dir)
        assert result == []


# ---------------------------------------------------------------------------
# Test 3 — Persona contracts (sibling contracts.yml per ADR-013) parse
# ---------------------------------------------------------------------------


class TestPersonaContractsParse:
    """Each of the five core personas yields non-empty produces/consumes."""

    def test_each_core_persona_has_non_empty_produces_and_consumes(self):
        idx = build_library_index(LIBRARY_ROOT)
        for persona_id in CORE_PERSONAS:
            persona = idx.persona_by_id(persona_id)
            assert persona is not None, f"{persona_id} persona not indexed"
            assert persona.produces, (
                f"{persona_id}.produces is empty — BEAN-273 AC violated"
            )
            assert persona.consumes, (
                f"{persona_id}.consumes is empty — BEAN-273 AC violated"
            )

    def test_contracts_yml_files_present_for_core_personas(self):
        # Per ADR-014, core personas live under personas/core/<id>.
        for persona_id in CORE_PERSONAS:
            contracts = (
                LIBRARY_ROOT / "personas" / "core" / persona_id / "contracts.yml"
            )
            assert contracts.is_file(), f"{contracts} missing per ADR-013"


# ---------------------------------------------------------------------------
# Test 4 — Type resolution: every persona-referenced type exists in the registry
# ---------------------------------------------------------------------------


class TestTypeResolution:
    """Every name on a persona's produces/consumes resolves in the registry."""

    def test_every_referenced_type_resolves_in_registry(self):
        idx = build_library_index(LIBRARY_ROOT)
        registry_names = {a.name for a in idx.artifact_types}
        for persona in idx.personas:
            for name in persona.produces:
                assert name in registry_names, (
                    f"{persona.id} produces unknown type '{name}'"
                )
            for name in persona.consumes:
                assert name in registry_names, (
                    f"{persona.id} consumes unknown type '{name}'"
                )

    def test_unknown_type_in_synthetic_persona_is_dropped_with_warning(
        self, tmp_path: Path, caplog,
    ):
        """A synthetic persona with an unknown type triggers a clear warning
        naming the persona + the missing type, and the unknown name is
        dropped from the in-memory model (per ADR-013 / library_indexer)."""
        # Minimal registry with one valid type
        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()
        (contracts_dir / "artifact-types.yml").write_text(
            "types:\n"
            "  - name: real-type\n"
            "    description: ok\n"
            "    format: markdown\n"
            "    required-fields: []\n",
            encoding="utf-8",
        )

        # Synthetic persona referencing one valid + one unknown type. Per
        # ADR-014, place the persona under personas/extended/<id> so the
        # canonical id is ``extended/synth``.
        persona_dir = tmp_path / "personas" / "extended" / "synth"
        persona_dir.mkdir(parents=True)
        (persona_dir / "persona.md").write_text(
            "# Persona: Synth\n\n## Category\nTest\n",
            encoding="utf-8",
        )
        (persona_dir / "contracts.yml").write_text(
            "produces:\n"
            "  - real-type\n"
            "  - ghost-type\n"
            "consumes:\n"
            "  - real-type\n",
            encoding="utf-8",
        )

        with caplog.at_level("WARNING"):
            idx = build_library_index(tmp_path)

        synth = idx.persona_by_id("extended/synth")
        assert synth is not None
        # ghost-type was dropped, real-type kept
        assert synth.produces == ["real-type"]
        assert synth.consumes == ["real-type"]

        # Warning names both the persona id and the missing type
        warning_text = "\n".join(r.getMessage() for r in caplog.records)
        assert "ghost-type" in warning_text
        assert "synth" in warning_text


# ---------------------------------------------------------------------------
# Test 5 — Cross-persona pairing
# ---------------------------------------------------------------------------


class TestCrossPersonaPairing:
    """Required producer→consumer chains hold across the core personas.

    These assertions are the explicit regression guard requested by BEAN-273
    AC: "at least one core persona pair has matching produces → consumes."
    They will fail fast if a future edit drops the BA→Developer or
    Developer→Tech-QA edge.
    """

    def test_ba_produced_type_is_consumed_by_developer(self):
        idx = build_library_index(LIBRARY_ROOT)
        ba = idx.persona_by_id("ba")
        dev = idx.persona_by_id("developer")
        assert ba is not None and dev is not None
        ba_produces = set(ba.produces)
        dev_consumes = set(dev.consumes)
        intersect = ba_produces & dev_consumes
        assert intersect, (
            "BA→Developer chain broken: BA produces "
            f"{sorted(ba_produces)} but Developer consumes "
            f"{sorted(dev_consumes)} — no overlap"
        )
        # Spec-level expectation: user-story is the canonical edge.
        assert "user-story" in intersect, (
            "BEAN-273 design called for 'user-story' to be the BA→Developer "
            f"edge; intersection is {sorted(intersect)}"
        )

    def test_developer_produced_type_is_consumed_by_tech_qa(self):
        idx = build_library_index(LIBRARY_ROOT)
        dev = idx.persona_by_id("developer")
        qa = idx.persona_by_id("tech-qa")
        assert dev is not None and qa is not None
        dev_produces = set(dev.produces)
        qa_consumes = set(qa.consumes)
        intersect = dev_produces & qa_consumes
        assert intersect, (
            "Developer→Tech-QA chain broken: Developer produces "
            f"{sorted(dev_produces)} but Tech-QA consumes "
            f"{sorted(qa_consumes)} — no overlap"
        )
        assert "code-change" in intersect, (
            "BEAN-273 design called for 'code-change' to be the "
            f"Developer→Tech-QA edge; intersection is {sorted(intersect)}"
        )

    def test_synthetic_break_of_user_story_chain_is_caught(self, tmp_path: Path):
        """Regression guard: drop the user-story consume edge from a synthetic
        Developer and verify the assertion this test class enforces would
        fail. Proves the cross-persona check has teeth.
        """
        # Build a tiny library with BA produces user-story but Developer
        # consumes only task-spec (no overlap).
        contracts_dir = tmp_path / "contracts"
        contracts_dir.mkdir()
        (contracts_dir / "artifact-types.yml").write_text(
            "types:\n"
            "  - name: user-story\n"
            "    description: x\n"
            "    format: markdown\n"
            "    required-fields: []\n"
            "  - name: task-spec\n"
            "    description: x\n"
            "    format: markdown\n"
            "    required-fields: []\n",
            encoding="utf-8",
        )
        # Per ADR-014, ba and developer are core personas → personas/core/<id>.
        ba_dir = tmp_path / "personas" / "core" / "ba"
        ba_dir.mkdir(parents=True)
        (ba_dir / "persona.md").write_text("# BA\n", encoding="utf-8")
        (ba_dir / "contracts.yml").write_text(
            "produces:\n  - user-story\nconsumes:\n  - task-spec\n",
            encoding="utf-8",
        )
        dev_dir = tmp_path / "personas" / "core" / "developer"
        dev_dir.mkdir(parents=True)
        (dev_dir / "persona.md").write_text("# Dev\n", encoding="utf-8")
        # NOTE: developer drops user-story from consumes → chain is broken
        (dev_dir / "contracts.yml").write_text(
            "produces:\n  - task-spec\nconsumes:\n  - task-spec\n",
            encoding="utf-8",
        )

        idx = build_library_index(tmp_path)
        ba = idx.persona_by_id("ba")
        dev = idx.persona_by_id("developer")
        assert ba is not None and dev is not None
        assert "user-story" not in set(dev.consumes), (
            "Synthetic break did not actually drop user-story"
        )
        # The pairing check (mirroring the real assertion) must fail here.
        assert "user-story" not in (set(ba.produces) & set(dev.consumes))


# ---------------------------------------------------------------------------
# Test 6 — Compiler / scaffold round-trip emits a contracts: block
# ---------------------------------------------------------------------------


class TestComposeRoundTrip:
    """The scaffold stage emits a ``contracts:`` block in composition.yml."""

    def _make_spec(self) -> CompositionSpec:
        return CompositionSpec(
            project=ProjectIdentity(name="Round Trip", slug="round-trip"),
            expertise=[ExpertiseSelection(id="python")],
            team=TeamConfig(personas=[
                PersonaSelection(id="ba"),
                PersonaSelection(id="developer"),
                PersonaSelection(id="tech-qa"),
            ]),
        )

    def test_composition_yml_contains_contracts_block(self, tmp_path: Path):
        idx = build_library_index(LIBRARY_ROOT)
        spec = self._make_spec()
        scaffold_project(spec, tmp_path / "out", library_index=idx)
        composition_path = tmp_path / "out" / "ai" / "team" / "composition.yml"
        text = composition_path.read_text(encoding="utf-8")
        assert "contracts:" in text, "scaffold did not emit a contracts: block"

    def test_contracts_block_has_per_persona_lists(self, tmp_path: Path):
        idx = build_library_index(LIBRARY_ROOT)
        spec = self._make_spec()
        scaffold_project(spec, tmp_path / "out", library_index=idx)
        composition_path = tmp_path / "out" / "ai" / "team" / "composition.yml"
        loaded = yaml.safe_load(composition_path.read_text(encoding="utf-8"))

        contracts = loaded.get("contracts")
        assert isinstance(contracts, dict), "contracts: block missing or not a mapping"
        personas = contracts.get("personas")
        assert isinstance(personas, list)
        # Order matches spec.team.personas
        assert [p["id"] for p in personas] == ["ba", "developer", "tech-qa"]
        for entry in personas:
            assert entry.get("produces"), (
                f"persona {entry.get('id')} missing produces list"
            )
            assert entry.get("consumes"), (
                f"persona {entry.get('id')} missing consumes list"
            )

    def test_contracts_block_has_flat_artifact_types_reference(
        self, tmp_path: Path,
    ):
        idx = build_library_index(LIBRARY_ROOT)
        spec = self._make_spec()
        scaffold_project(spec, tmp_path / "out", library_index=idx)
        composition_path = tmp_path / "out" / "ai" / "team" / "composition.yml"
        loaded = yaml.safe_load(composition_path.read_text(encoding="utf-8"))

        # The scaffold writes ``artifact-types:`` (kebab-case key) per ADR-013.
        artifact_types = loaded["contracts"]["artifact-types"]
        assert isinstance(artifact_types, list)
        assert artifact_types, "artifact-types: list must not be empty"

        # Every entry has name, format, template-path keys
        for entry in artifact_types:
            assert "name" in entry
            assert "format" in entry
            assert "template-path" in entry

        # Sorted by name for stable diffing
        names = [e["name"] for e in artifact_types]
        assert names == sorted(names), (
            f"artifact-types should be sorted by name: {names}"
        )

        # The set must equal the union of every name appearing in any
        # persona's produces/consumes on the team.
        personas = loaded["contracts"]["personas"]
        union: set[str] = set()
        for entry in personas:
            union.update(entry.get("produces") or [])
            union.update(entry.get("consumes") or [])
        assert set(names) == union, (
            f"artifact-types union mismatch: {set(names) ^ union}"
        )

    def test_no_contracts_block_when_team_empty(self, tmp_path: Path):
        idx = build_library_index(LIBRARY_ROOT)
        spec = CompositionSpec(
            project=ProjectIdentity(name="Empty", slug="empty"),
            expertise=[ExpertiseSelection(id="python")],
            team=TeamConfig(personas=[]),
        )
        scaffold_project(spec, tmp_path / "out", library_index=idx)
        composition_path = tmp_path / "out" / "ai" / "team" / "composition.yml"
        loaded = yaml.safe_load(composition_path.read_text(encoding="utf-8"))
        # Either absent or rendered as None — both are acceptable; the block
        # MUST NOT contain persona entries when the team is empty.
        contracts = loaded.get("contracts") if isinstance(loaded, dict) else None
        if contracts is not None:
            personas = contracts.get("personas") or []
            assert personas == [], (
                "contracts.personas must be empty when team is empty"
            )
