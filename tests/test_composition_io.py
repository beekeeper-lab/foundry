"""Tests for foundry_app.io.composition_io: YAML round-trip for CompositionSpec."""

from __future__ import annotations

from pathlib import Path

import pytest

from foundry_app.core.models import (
    CompositionSpec,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.io.composition_io import (
    CompositionIOError,
    load_composition,
    load_manifest,
    save_composition,
)


def _make_spec() -> CompositionSpec:
    """Build a representative CompositionSpec for IO tests."""
    return CompositionSpec(
        project=ProjectIdentity(name="IO Test", slug="io-test"),
        stacks=[StackSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="team-lead")]),
        hooks=HooksConfig(),
    )


def test_save_and_load_roundtrip(tmp_path: Path):
    """Saving a spec to YAML and loading it back preserves key fields."""
    spec = _make_spec()
    yaml_file = tmp_path / "composition.yml"

    save_composition(spec, yaml_file)
    loaded = load_composition(yaml_file)

    assert loaded.project.name == spec.project.name
    assert loaded.project.slug == spec.project.slug
    assert loaded.stacks[0].id == spec.stacks[0].id
    assert loaded.team.personas[0].id == spec.team.personas[0].id


def test_save_creates_parent_dirs(tmp_path: Path):
    """save_composition should create intermediate directories as needed."""
    nested_path = tmp_path / "a" / "b" / "c" / "composition.yml"
    spec = _make_spec()

    save_composition(spec, nested_path)

    assert nested_path.is_file()
    loaded = load_composition(nested_path)
    assert loaded.project.slug == "io-test"


def test_load_nonexistent_raises(tmp_path: Path):
    """Loading from a path that does not exist should raise an exception."""
    missing = tmp_path / "does_not_exist.yml"
    with pytest.raises(Exception):
        load_composition(missing)


def test_roundtrip_preserves_all_fields(tmp_path: Path):
    """A full round-trip should preserve every field, not just the key ones."""
    spec = CompositionSpec(
        project=ProjectIdentity(
            name="Full Round Trip",
            slug="full-roundtrip",
            output_root="/custom/root",
            output_folder="my-folder",
        ),
        stacks=[
            StackSelection(id="python", order=10),
            StackSelection(id="react", order=20),
        ],
        team=TeamConfig(
            personas=[
                PersonaSelection(id="team-lead", strictness="strict"),
                PersonaSelection(id="developer", include_agent=False),
            ]
        ),
        hooks=HooksConfig(posture="hardened"),
    )
    yaml_file = tmp_path / "full.yml"

    save_composition(spec, yaml_file)
    loaded = load_composition(yaml_file)

    assert loaded.project.output_root == "/custom/root"
    assert loaded.project.output_folder == "my-folder"
    assert len(loaded.stacks) == 2
    assert loaded.stacks[1].id == "react"
    assert loaded.stacks[1].order == 20
    assert len(loaded.team.personas) == 2
    assert loaded.team.personas[0].strictness == "strict"
    assert loaded.team.personas[1].include_agent is False
    assert loaded.hooks.posture == "hardened"


# -- CompositionIOError: load_composition error paths --------------------------


def test_load_composition_malformed_yaml(tmp_path: Path):
    """Malformed YAML should raise CompositionIOError mentioning 'Malformed YAML'."""
    bad_file = tmp_path / "bad.yml"
    bad_file.write_text(":\n  - :\n  bad:\nyaml: [unbalanced", encoding="utf-8")

    with pytest.raises(CompositionIOError, match="Malformed YAML"):
        load_composition(bad_file)


def test_load_composition_invalid_data(tmp_path: Path):
    """Valid YAML that doesn't match the CompositionSpec schema should raise CompositionIOError."""
    invalid_file = tmp_path / "invalid.yml"
    invalid_file.write_text('project: "not a dict"', encoding="utf-8")

    with pytest.raises(CompositionIOError):
        load_composition(invalid_file)


def test_load_composition_not_a_mapping(tmp_path: Path):
    """A YAML file whose top-level value is a string (not a mapping) should raise CompositionIOError."""
    string_file = tmp_path / "string.yml"
    string_file.write_text('"just a string"', encoding="utf-8")

    with pytest.raises(CompositionIOError, match="mapping"):
        load_composition(string_file)


def test_load_composition_file_not_found(tmp_path: Path):
    """Loading a nonexistent file should raise CompositionIOError with 'not found'."""
    missing = tmp_path / "nonexistent.yml"

    with pytest.raises(CompositionIOError, match="not found"):
        load_composition(missing)


# -- CompositionIOError: load_manifest error paths -----------------------------


def test_load_manifest_malformed_json(tmp_path: Path):
    """Malformed JSON should raise CompositionIOError mentioning 'Malformed JSON'."""
    bad_file = tmp_path / "manifest.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(CompositionIOError, match="Malformed JSON"):
        load_manifest(bad_file)


def test_load_manifest_invalid_data(tmp_path: Path):
    """Valid JSON that doesn't match the GenerationManifest schema should raise CompositionIOError."""
    invalid_file = tmp_path / "manifest.json"
    # stages expects a dict of StageResult, not a plain string
    invalid_file.write_text('{"stages": "not a dict"}', encoding="utf-8")

    with pytest.raises(CompositionIOError):
        load_manifest(invalid_file)


def test_load_manifest_file_not_found(tmp_path: Path):
    """Loading a nonexistent manifest should raise CompositionIOError with 'not found'."""
    missing = tmp_path / "nonexistent.json"

    with pytest.raises(CompositionIOError, match="not found"):
        load_manifest(missing)
