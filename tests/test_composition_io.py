"""Tests for foundry_app.io.composition_io — YAML/JSON serialization."""

import json

import pytest
import yaml
from pydantic import ValidationError

from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
    GenerationOptions,
    HookPackSelection,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    StageResult,
    TeamConfig,
)
from foundry_app.io.composition_io import (
    load_composition,
    load_manifest,
    save_composition,
    save_manifest,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec() -> CompositionSpec:
    """Create a minimal but complete CompositionSpec for testing."""
    return CompositionSpec(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        stacks=[
            StackSelection(id="python", order=10),
            StackSelection(id="clean-code", order=20),
        ],
        team=TeamConfig(personas=[
            PersonaSelection(id="team-lead"),
            PersonaSelection(id="developer", strictness="strict"),
        ]),
        hooks=HooksConfig(posture="hardened", packs=[
            HookPackSelection(id="pre-commit-lint"),
        ]),
        generation=GenerationOptions(
            seed_tasks=True, write_manifest=True, write_diff_report=True,
        ),
    )


def _make_manifest() -> GenerationManifest:
    """Create a GenerationManifest for testing."""
    return GenerationManifest(
        run_id="2026-02-07T10-00-00Z",
        library_version="abc1234",
        composition_snapshot={"project": {"name": "Test", "slug": "test"}},
        stages={
            "scaffold": StageResult(wrote=["CLAUDE.md", ".claude/agents/dev.md"], warnings=[]),
            "compile": StageResult(wrote=["ai/generated/members/dev.md"], warnings=["warn1"]),
            "seed": StageResult(wrote=["ai/tasks/seeded-tasks.md"], warnings=[]),
        },
    )


# ---------------------------------------------------------------------------
# load_composition / save_composition
# ---------------------------------------------------------------------------

class TestLoadComposition:
    def test_load_from_yaml(self, tmp_path):
        yml = tmp_path / "comp.yml"
        yml.write_text(yaml.dump({
            "project": {"name": "Hello", "slug": "hello"},
            "stacks": [{"id": "python", "order": 10}],
            "team": {"personas": [{"id": "developer"}]},
        }), encoding="utf-8")
        spec = load_composition(yml)
        assert spec.project.name == "Hello"
        assert spec.stacks[0].id == "python"
        assert spec.team.personas[0].id == "developer"

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_composition(tmp_path / "nope.yml")

    def test_load_invalid_yaml(self, tmp_path):
        bad = tmp_path / "bad.yml"
        bad.write_text("project:\n  name: [invalid", encoding="utf-8")
        with pytest.raises(yaml.YAMLError):
            load_composition(bad)

    def test_load_invalid_schema(self, tmp_path):
        yml = tmp_path / "comp.yml"
        yml.write_text(yaml.dump({"project": {"name": "", "slug": "ok"}}), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_composition(yml)

    def test_load_empty_file(self, tmp_path):
        empty = tmp_path / "empty.yml"
        empty.write_text("", encoding="utf-8")
        with pytest.raises(ValidationError):
            load_composition(empty)

    def test_load_accepts_string_path(self, tmp_path):
        yml = tmp_path / "comp.yml"
        yml.write_text(yaml.dump({
            "project": {"name": "Test", "slug": "test"},
        }), encoding="utf-8")
        spec = load_composition(str(yml))
        assert spec.project.slug == "test"


class TestSaveComposition:
    def test_save_creates_file(self, tmp_path):
        spec = _make_spec()
        out = tmp_path / "out.yml"
        save_composition(spec, out)
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "test-project" in content

    def test_save_creates_parent_dirs(self, tmp_path):
        spec = _make_spec()
        out = tmp_path / "deep" / "nested" / "comp.yml"
        save_composition(spec, out)
        assert out.exists()

    def test_save_accepts_string_path(self, tmp_path):
        spec = _make_spec()
        out = tmp_path / "out.yml"
        save_composition(spec, str(out))
        assert out.exists()

    def test_save_excludes_none_fields_from_yaml(self, tmp_path):
        """save_composition with safety=None must not write a 'safety' key."""
        spec = CompositionSpec(
            project=ProjectIdentity(name="NoSafety", slug="no-safety"),
            safety=None,
        )
        out = tmp_path / "none-check.yml"
        save_composition(spec, out)
        raw = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert "safety" not in raw

    def test_save_produces_valid_yaml(self, tmp_path):
        spec = _make_spec()
        out = tmp_path / "comp.yml"
        save_composition(spec, out)
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert data["project"]["name"] == "Test Project"
        assert len(data["stacks"]) == 2


class TestCompositionRoundTrip:
    def test_yaml_roundtrip(self, tmp_path):
        """CompositionSpec → save YAML → load YAML → identical spec."""
        spec = _make_spec()
        yml = tmp_path / "roundtrip.yml"
        save_composition(spec, yml)
        restored = load_composition(yml)
        assert restored.model_dump(mode="json") == spec.model_dump(mode="json")

    def test_roundtrip_preserves_enums(self, tmp_path):
        spec = _make_spec()
        yml = tmp_path / "enums.yml"
        save_composition(spec, yml)
        restored = load_composition(yml)
        assert restored.team.personas[1].strictness.value == "strict"
        assert restored.hooks.posture.value == "hardened"

    def test_roundtrip_with_safety(self, tmp_path):
        from foundry_app.core.models import SafetyConfig
        spec = CompositionSpec(
            project=ProjectIdentity(name="Safe", slug="safe"),
            safety=SafetyConfig.hardened_safety(),
        )
        yml = tmp_path / "safety.yml"
        save_composition(spec, yml)
        restored = load_composition(yml)
        assert restored.safety is not None
        assert restored.safety.git.allow_force_push is False
        assert len(restored.safety.secrets.secret_patterns) > 0

    def test_roundtrip_minimal_spec(self, tmp_path):
        spec = CompositionSpec(
            project=ProjectIdentity(name="Min", slug="min"),
        )
        yml = tmp_path / "min.yml"
        save_composition(spec, yml)
        restored = load_composition(yml)
        assert restored.project.name == "Min"
        assert restored.stacks == []

    def test_multiple_roundtrips_stable(self, tmp_path):
        """Three consecutive round-trips produce identical results."""
        spec = _make_spec()
        for i in range(3):
            yml = tmp_path / f"rt{i}.yml"
            save_composition(spec, yml)
            spec = load_composition(yml)
        assert spec.model_dump(mode="json") == _make_spec().model_dump(mode="json")


# ---------------------------------------------------------------------------
# load_manifest / save_manifest
# ---------------------------------------------------------------------------

class TestLoadManifest:
    def test_load_from_json(self, tmp_path):
        manifest = _make_manifest()
        out = tmp_path / "manifest.json"
        out.write_text(
            json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8"
        )
        loaded = load_manifest(out)
        assert loaded.run_id == "2026-02-07T10-00-00Z"
        assert loaded.total_files_written == 4

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_path / "nope.json")

    def test_load_invalid_json(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_manifest(bad)

    def test_load_invalid_schema(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps({"not_a": "manifest"}), encoding="utf-8")
        with pytest.raises(ValidationError):
            load_manifest(bad)


class TestSaveManifest:
    def test_save_creates_file(self, tmp_path):
        manifest = _make_manifest()
        out = tmp_path / "manifest.json"
        save_manifest(manifest, out)
        assert out.exists()

    def test_save_creates_parent_dirs(self, tmp_path):
        manifest = _make_manifest()
        out = tmp_path / "deep" / "manifest.json"
        save_manifest(manifest, out)
        assert out.exists()

    def test_save_produces_valid_json(self, tmp_path):
        manifest = _make_manifest()
        out = tmp_path / "manifest.json"
        save_manifest(manifest, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["run_id"] == "2026-02-07T10-00-00Z"
        assert "scaffold" in data["stages"]


class TestManifestRoundTrip:
    def test_json_roundtrip(self, tmp_path):
        """GenerationManifest → save JSON → load JSON → equivalent manifest."""
        manifest = _make_manifest()
        out = tmp_path / "rt.json"
        save_manifest(manifest, out)
        restored = load_manifest(out)
        assert restored.run_id == manifest.run_id
        assert restored.total_files_written == manifest.total_files_written
        assert restored.all_warnings == manifest.all_warnings
        assert restored.library_version == manifest.library_version

    def test_roundtrip_preserves_stages(self, tmp_path):
        manifest = _make_manifest()
        out = tmp_path / "stages.json"
        save_manifest(manifest, out)
        restored = load_manifest(out)
        assert set(restored.stages.keys()) == {"scaffold", "compile", "seed"}
        assert restored.stages["scaffold"].wrote == ["CLAUDE.md", ".claude/agents/dev.md"]
        assert restored.stages["compile"].warnings == ["warn1"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_composition_with_example_yaml(self, tmp_path):
        """Validate that example-style YAML parses correctly."""
        yml_content = """\
project:
  name: "Small Python Team"
  slug: small-python-team
  output_root: "./generated-projects"

stacks:
  - id: python
    order: 10
  - id: clean-code
    order: 20

team:
  personas:
    - id: team-lead
      include_agent: true
      include_templates: true
      strictness: standard
    - id: developer
      include_agent: true
      include_templates: true
      strictness: standard

hooks:
  posture: baseline
  packs:
    - id: hook-policy
      enabled: true
      mode: enforcing

generation:
  seed_tasks: true
  write_manifest: true
  write_diff_report: false
"""
        yml = tmp_path / "example.yml"
        yml.write_text(yml_content, encoding="utf-8")
        spec = load_composition(yml)
        assert spec.project.name == "Small Python Team"
        assert len(spec.stacks) == 2
        assert len(spec.team.personas) == 2
        assert spec.hooks.posture.value == "baseline"

    def test_load_actual_example_files(self):
        """Load the real example YAML files from the repo."""
        import pathlib
        examples_dir = pathlib.Path(__file__).parent.parent / "examples"
        if not examples_dir.exists():
            pytest.skip("Examples directory not found")
        for yml_path in examples_dir.glob("*.yml"):
            spec = load_composition(yml_path)
            assert spec.project.name
            assert spec.project.slug
