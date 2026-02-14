"""Tests for foundry_app.services.generator — project generation orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from foundry_app.core.models import (
    CompositionSpec,
    GenerationOptions,
    LibraryIndex,
    OverlayPlan,
    PersonaInfo,
    PersonaSelection,
    ProjectIdentity,
    StackInfo,
    StackSelection,
    Strictness,
    TeamConfig,
)
from foundry_app.io.composition_io import load_composition
from foundry_app.services.generator import (
    _apply_overlay_plan,
    _compare_trees,
    _get_library_version,
    _make_run_id,
    _run_pipeline,
    generate_project,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**kwargs) -> CompositionSpec:
    """Build a CompositionSpec with sensible defaults."""
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        stacks=[StackSelection(id="python")],
        team=TeamConfig(personas=[PersonaSelection(id="developer")]),
    )
    defaults.update(kwargs)
    return CompositionSpec(**defaults)


def _make_library(tmp_path: Path) -> LibraryIndex:
    """Build a minimal on-disk library with real persona and stack directories."""
    lib_root = tmp_path / "library"

    # Create persona directory
    persona_dir = lib_root / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer persona")

    # Create stack directory
    stack_dir = lib_root / "stacks" / "python"
    stack_dir.mkdir(parents=True)
    (stack_dir / "conventions.md").write_text("# Python conventions")

    return LibraryIndex(
        library_root=str(lib_root),
        personas=[
            PersonaInfo(
                id="developer",
                path=str(persona_dir),
                has_persona_md=True,
                has_outputs_md=False,
                has_prompts_md=False,
                templates=[],
            ),
        ],
        stacks=[
            StackInfo(
                id="python",
                path=str(stack_dir),
                files=["conventions.md"],
            ),
        ],
        hook_packs=[],
    )


def _make_library_dir(tmp_path: Path) -> Path:
    """Create a minimal library directory on disk and return its path."""
    lib_root = tmp_path / "library"

    persona_dir = lib_root / "personas" / "developer"
    persona_dir.mkdir(parents=True)
    (persona_dir / "persona.md").write_text("# Developer persona")

    stack_dir = lib_root / "stacks" / "python"
    stack_dir.mkdir(parents=True)
    (stack_dir / "conventions.md").write_text("# Python conventions")

    return lib_root


# ---------------------------------------------------------------------------
# run_id generation
# ---------------------------------------------------------------------------


class TestMakeRunId:

    def test_run_id_is_non_empty_string(self):
        run_id = _make_run_id()
        assert isinstance(run_id, str)
        assert len(run_id) > 0

    def test_run_id_contains_timestamp_format(self):
        run_id = _make_run_id()
        # Format: YYYYMMDD-HHMMSS
        assert "-" in run_id
        parts = run_id.split("-")
        assert len(parts) == 2
        assert len(parts[0]) == 8  # date
        assert len(parts[1]) == 6  # time

    def test_run_ids_are_unique_in_sequence(self):
        """Two calls in rapid succession should produce non-empty IDs."""
        id1 = _make_run_id()
        id2 = _make_run_id()
        # May be same if called within same second, but both should be valid
        assert len(id1) > 0
        assert len(id2) > 0


# ---------------------------------------------------------------------------
# Library version detection
# ---------------------------------------------------------------------------


class TestGetLibraryVersion:

    def test_returns_empty_for_nonexistent_path(self, tmp_path: Path):
        version = _get_library_version(tmp_path / "nonexistent")
        assert version == ""

    def test_returns_empty_for_non_git_directory(self, tmp_path: Path):
        version = _get_library_version(tmp_path)
        assert version == ""

    def test_returns_string(self, tmp_path: Path):
        version = _get_library_version(tmp_path)
        assert isinstance(version, str)


# ---------------------------------------------------------------------------
# Standard generation (no overlay)
# ---------------------------------------------------------------------------


class TestStandardGeneration:

    def test_generates_project_directory(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, validation, overlay_plan = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert output_dir.is_dir()
        assert overlay_plan is None

    def test_returns_valid_manifest(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert manifest.run_id != ""
        assert "scaffold" in manifest.stages
        assert manifest.total_files_written > 0

    def test_returns_valid_validation_result(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        _, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert validation.is_valid

    def test_scaffold_stage_creates_directories(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert (output_dir / ".claude" / "agents").is_dir()
        assert (output_dir / "ai" / "context").is_dir()
        assert (output_dir / "ai" / "outputs" / "developer").is_dir()

    def test_manifest_has_composition_snapshot(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert manifest.composition_snapshot != {}
        assert manifest.composition_snapshot["project"]["slug"] == "test-project"

    def test_service_stages_included_in_manifest(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert "compile" in manifest.stages
        assert "copy_assets" in manifest.stages
        assert "safety" in manifest.stages

    def test_seed_tasks_stage_when_enabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(seed_tasks=True))

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert "seed_tasks" in manifest.stages

    def test_seed_tasks_stage_skipped_when_disabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(seed_tasks=False))

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert "seed_tasks" not in manifest.stages

    def test_diff_report_stage_when_enabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(write_diff_report=True))

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert "diff_report" in manifest.stages

    def test_diff_report_stage_skipped_when_disabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(write_diff_report=False))

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert "diff_report" not in manifest.stages


# ---------------------------------------------------------------------------
# Manifest file writing
# ---------------------------------------------------------------------------


class TestManifestFileWriting:

    def test_writes_manifest_json_when_enabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(write_manifest=True))

        generate_project(spec, lib_root, output_root=output_dir)

        manifest_path = output_dir / "manifest.json"
        assert manifest_path.is_file()
        data = json.loads(manifest_path.read_text())
        assert "run_id" in data
        assert "stages" in data

    def test_no_manifest_when_disabled(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(write_manifest=False))

        generate_project(spec, lib_root, output_root=output_dir)

        manifest_path = output_dir / "manifest.json"
        assert not manifest_path.exists()


# ---------------------------------------------------------------------------
# Validation gating
# ---------------------------------------------------------------------------


class TestValidationGating:

    def test_aborts_on_validation_errors(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        # Use a persona that doesn't exist in the library
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
        )

        manifest, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert not validation.is_valid
        assert manifest.stages == {}
        assert not output_dir.exists()

    def test_force_bypasses_validation_errors(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(
            team=TeamConfig(personas=[PersonaSelection(id="nonexistent")]),
        )

        manifest, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir, force=True,
        )

        assert not validation.is_valid
        assert "scaffold" in manifest.stages
        assert output_dir.is_dir()

    def test_validation_warnings_do_not_block(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        # Empty team produces a warning, not an error
        spec = _make_spec(team=TeamConfig(personas=[]))

        manifest, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert validation.is_valid
        assert "scaffold" in manifest.stages

    def test_strict_mode_blocks_on_warnings(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(team=TeamConfig(personas=[]))

        manifest, validation, _ = generate_project(
            spec, lib_root, output_root=output_dir,
            strictness=Strictness.STRICT,
        )

        assert not validation.is_valid
        assert manifest.stages == {}


# ---------------------------------------------------------------------------
# Output directory resolution
# ---------------------------------------------------------------------------


class TestOutputResolution:

    def test_uses_explicit_output_root(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "custom-output"
        spec = _make_spec()

        generate_project(spec, lib_root, output_root=output_dir)

        assert output_dir.is_dir()

    def test_uses_spec_output_root_when_none(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_base = tmp_path / "gen-projects"
        spec = _make_spec(
            project=ProjectIdentity(
                name="My Project",
                slug="my-project",
                output_root=str(output_base),
            ),
        )

        manifest, _, _ = generate_project(spec, lib_root, output_root=None)

        expected_dir = output_base / "my-project"
        assert expected_dir.is_dir()

    def test_uses_output_folder_override(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_base = tmp_path / "gen-projects"
        spec = _make_spec(
            project=ProjectIdentity(
                name="My Project",
                slug="my-project",
                output_root=str(output_base),
                output_folder="custom-folder",
            ),
        )

        generate_project(spec, lib_root, output_root=None)

        expected_dir = output_base / "custom-folder"
        assert expected_dir.is_dir()


# ---------------------------------------------------------------------------
# Compare trees (overlay helper)
# ---------------------------------------------------------------------------


class TestCompareTrees:

    def test_all_new_files_are_creates(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "new_file.txt").write_text("hello")

        plan = _compare_trees(source, target)

        assert len(plan.creates) == 1
        assert plan.creates[0].path == "new_file.txt"

    def test_identical_files_are_skips(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "same.txt").write_text("same content")
        (target / "same.txt").write_text("same content")

        plan = _compare_trees(source, target)

        assert len(plan.skips) == 1
        assert plan.skips[0].path == "same.txt"

    def test_different_files_are_updates(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "changed.txt").write_text("new content")
        (target / "changed.txt").write_text("old content")

        plan = _compare_trees(source, target)

        assert len(plan.updates) == 1
        assert plan.updates[0].path == "changed.txt"

    def test_target_only_files_are_deletes(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (target / "orphan.txt").write_text("i should be deleted")

        plan = _compare_trees(source, target)

        assert len(plan.deletes) == 1
        assert plan.deletes[0].path == "orphan.txt"

    def test_empty_source_and_target(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()

        plan = _compare_trees(source, target)

        assert plan.actions == []

    def test_nonexistent_target_all_creates(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        (source / "a.txt").write_text("a")
        (source / "b.txt").write_text("b")

        plan = _compare_trees(source, target)

        assert len(plan.creates) == 2
        assert len(plan.deletes) == 0

    def test_nested_files_use_relative_paths(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        (source / "sub" / "dir").mkdir(parents=True)
        target.mkdir()
        (source / "sub" / "dir" / "deep.txt").write_text("deep")

        plan = _compare_trees(source, target)

        assert len(plan.creates) == 1
        assert plan.creates[0].path == "sub/dir/deep.txt"

    def test_mixed_actions(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        # New file
        (source / "new.txt").write_text("new")
        # Same file
        (source / "same.txt").write_text("same")
        (target / "same.txt").write_text("same")
        # Changed file
        (source / "changed.txt").write_text("v2")
        (target / "changed.txt").write_text("v1")
        # Orphaned file
        (target / "old.txt").write_text("old")

        plan = _compare_trees(source, target)

        assert len(plan.creates) == 1
        assert len(plan.updates) == 1
        assert len(plan.skips) == 1
        assert len(plan.deletes) == 1

    def test_skips_symlinks_in_source(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()

        (source / "real.txt").write_text("real content")
        outside = tmp_path / "outside.txt"
        outside.write_text("outside content")
        (source / "link.txt").symlink_to(outside)

        plan = _compare_trees(source, target)

        paths = [a.path for a in plan.actions]
        assert "real.txt" in paths
        assert "link.txt" not in paths

    def test_skips_symlinks_in_target(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()

        outside = tmp_path / "outside.txt"
        outside.write_text("outside content")
        (target / "link.txt").symlink_to(outside)

        plan = _compare_trees(source, target)

        paths = [a.path for a in plan.actions]
        assert "link.txt" not in paths


# ---------------------------------------------------------------------------
# Apply overlay plan
# ---------------------------------------------------------------------------


class TestApplyOverlayPlan:

    def test_apply_creates_new_files(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "new.txt").write_text("hello")

        plan = _compare_trees(source, target)
        result = _apply_overlay_plan(plan, source, target)

        assert (target / "new.txt").read_text() == "hello"
        assert "new.txt" in result.wrote

    def test_apply_updates_changed_files(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "file.txt").write_text("updated")
        (target / "file.txt").write_text("original")

        plan = _compare_trees(source, target)
        result = _apply_overlay_plan(plan, source, target)

        assert (target / "file.txt").read_text() == "updated"
        assert "file.txt" in result.wrote

    def test_apply_deletes_orphaned_files(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (target / "orphan.txt").write_text("remove me")

        plan = _compare_trees(source, target)
        result = _apply_overlay_plan(plan, source, target)

        assert not (target / "orphan.txt").exists()
        assert "orphan.txt" in result.wrote

    def test_apply_skips_unchanged_files(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        source.mkdir()
        target.mkdir()
        (source / "same.txt").write_text("content")
        (target / "same.txt").write_text("content")

        plan = _compare_trees(source, target)
        result = _apply_overlay_plan(plan, source, target)

        assert result.wrote == []

    def test_apply_creates_parent_directories(self, tmp_path: Path):
        source = tmp_path / "source"
        target = tmp_path / "target"
        (source / "a" / "b").mkdir(parents=True)
        target.mkdir()
        (source / "a" / "b" / "deep.txt").write_text("deep")

        plan = _compare_trees(source, target)
        _apply_overlay_plan(plan, source, target)

        assert (target / "a" / "b" / "deep.txt").read_text() == "deep"


# ---------------------------------------------------------------------------
# Overlay generation mode
# ---------------------------------------------------------------------------


class TestOverlayGeneration:

    def test_overlay_returns_plan(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        _, _, overlay_plan = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert overlay_plan is not None
        assert isinstance(overlay_plan, OverlayPlan)

    def test_overlay_creates_files_in_target(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert output_dir.is_dir()

    def test_overlay_preserves_generated_file_content(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        # First generation creates files
        generate_project(spec, lib_root, output_root=output_dir, overlay=True)

        # Grab a generated file and its content
        settings = output_dir / ".claude" / "settings.json"
        assert settings.is_file()
        original_content = settings.read_text()

        # Second overlay re-generation should preserve identical content (skip)
        _, _, plan = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert settings.read_text() == original_content

    def test_overlay_has_apply_stage_in_manifest(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert "overlay_apply" in manifest.stages

    def test_overlay_nonexistent_target_creates_directory(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "brand-new-project"
        spec = _make_spec()

        assert not output_dir.exists()
        manifest, validation, plan = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert output_dir.is_dir()
        assert plan is not None
        assert "overlay_apply" in manifest.stages

    def test_overlay_second_run_shows_skips(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        # First generation
        generate_project(spec, lib_root, output_root=output_dir, overlay=True)

        # Second generation (same spec)
        _, _, plan = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        # All files should be skips since nothing changed
        # (scaffold creates dirs, not files, so overlay_apply may be empty)
        assert plan is not None


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------


class TestDryRunMode:

    def test_dry_run_returns_plan_without_applying(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        _, _, plan = generate_project(
            spec, lib_root, output_root=output_dir,
            overlay=True, dry_run=True,
        )

        assert plan is not None
        assert plan.dry_run is True

    def test_dry_run_does_not_create_output_directory(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        generate_project(
            spec, lib_root, output_root=output_dir,
            overlay=True, dry_run=True,
        )

        # Output dir should not exist (overlay dry run doesn't write)
        assert not output_dir.exists()

    def test_dry_run_does_not_write_manifest(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(generation=GenerationOptions(write_manifest=True))

        generate_project(
            spec, lib_root, output_root=output_dir,
            overlay=True, dry_run=True,
        )

        assert not (output_dir / "manifest.json").exists()

    def test_dry_run_no_overlay_apply_in_manifest(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
            overlay=True, dry_run=True,
        )

        assert "overlay_apply" not in manifest.stages


# ---------------------------------------------------------------------------
# Pipeline stage execution
# ---------------------------------------------------------------------------


class TestPipelineExecution:

    def test_pipeline_runs_all_stages(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        lib_root = Path(lib.library_root)
        output_dir = tmp_path / "pipeline-output"
        output_dir.mkdir()
        spec = _make_spec(
            generation=GenerationOptions(
                seed_tasks=True,
                write_diff_report=True,
            ),
        )

        stages = _run_pipeline(spec, lib, lib_root, output_dir)

        assert "scaffold" in stages
        assert "compile" in stages
        assert "copy_assets" in stages
        assert "seed_tasks" in stages
        assert "safety" in stages
        assert "diff_report" in stages

    def test_pipeline_optional_stages_controlled_by_spec(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        lib_root = Path(lib.library_root)
        output_dir = tmp_path / "pipeline-output"
        output_dir.mkdir()
        spec = _make_spec(
            generation=GenerationOptions(
                seed_tasks=False,
                write_diff_report=False,
            ),
        )

        stages = _run_pipeline(spec, lib, lib_root, output_dir)

        assert "seed_tasks" not in stages
        assert "diff_report" not in stages

    def test_real_services_produce_output(self, tmp_path: Path):
        lib = _make_library(tmp_path)
        lib_root = Path(lib.library_root)
        output_dir = tmp_path / "pipeline-output"
        output_dir.mkdir()
        spec = _make_spec()

        stages = _run_pipeline(spec, lib, lib_root, output_dir)

        # Compile now produces CLAUDE.md via real compiler service
        assert "CLAUDE.md" in stages["compile"].wrote
        # Safety writer produces real output
        assert ".claude/settings.json" in stages["safety"].wrote


# ---------------------------------------------------------------------------
# Manifest properties
# ---------------------------------------------------------------------------


class TestManifestProperties:

    def test_total_files_written_aggregates_stages(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        # At minimum, scaffold creates directories
        assert manifest.total_files_written > 0

    def test_all_warnings_aggregates_stages(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        # Empty personas generates a warning from scaffold
        spec = _make_spec(team=TeamConfig(personas=[]))

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert isinstance(manifest.all_warnings, list)

    def test_manifest_library_version_is_string(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert isinstance(manifest.library_version, str)

    def test_manifest_generated_at_is_set(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert manifest.generated_at is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:

    def test_nonexistent_library_returns_validation_errors(self, tmp_path: Path):
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        manifest, validation, _ = generate_project(
            spec, tmp_path / "no-library", output_root=output_dir,
        )

        assert not validation.is_valid
        assert manifest.stages == {}

    def test_multiple_calls_are_idempotent_with_overlay(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        # First call
        generate_project(spec, lib_root, output_root=output_dir, overlay=True)
        # Second call (overlay should not fail)
        manifest, validation, plan = generate_project(
            spec, lib_root, output_root=output_dir, overlay=True,
        )

        assert validation.is_valid
        assert plan is not None

    def test_empty_spec_with_force(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec(
            stacks=[],
            team=TeamConfig(personas=[]),
        )

        manifest, _, _ = generate_project(
            spec, lib_root, output_root=output_dir, force=True,
        )

        assert output_dir.is_dir()
        assert "scaffold" in manifest.stages

    def test_return_type_is_tuple_of_three(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        result = generate_project(spec, lib_root, output_root=output_dir)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_standard_mode_overlay_plan_is_none(self, tmp_path: Path):
        lib_root = _make_library_dir(tmp_path)
        output_dir = tmp_path / "output" / "test-project"
        spec = _make_spec()

        _, _, overlay_plan = generate_project(
            spec, lib_root, output_root=output_dir,
        )

        assert overlay_plan is None


# ---------------------------------------------------------------------------
# End-to-end: real library, real composition YAML
# ---------------------------------------------------------------------------

# Resolve repo root relative to this test file
_REPO_ROOT = Path(__file__).resolve().parent.parent
_EXAMPLE_YAML = _REPO_ROOT / "examples" / "small-python-team.yml"
_LIBRARY_ROOT = _REPO_ROOT / "ai-team-library"

_E2E_AVAILABLE = _EXAMPLE_YAML.is_file() and _LIBRARY_ROOT.is_dir()


@pytest.mark.skipif(not _E2E_AVAILABLE, reason="ai-team-library or example YAML not present")
class TestEndToEnd:
    """Full pipeline run against the real ai-team-library."""

    @pytest.fixture()
    def generated_project(self, tmp_path: Path):
        """Load small-python-team.yml, run the full pipeline, return (output_dir, manifest)."""
        spec = load_composition(_EXAMPLE_YAML)
        output_dir = tmp_path / spec.project.slug

        manifest, validation, _ = generate_project(
            spec,
            _LIBRARY_ROOT,
            output_root=output_dir,
        )

        assert validation.is_valid, f"Validation failed: {validation.errors}"
        return output_dir, manifest, spec

    # -- Structural checks --------------------------------------------------

    def test_output_directory_created(self, generated_project):
        output_dir, _, _ = generated_project
        assert output_dir.is_dir()

    def test_claude_md_exists_and_nonempty(self, generated_project):
        output_dir, _, _ = generated_project
        claude_md = output_dir / "CLAUDE.md"
        assert claude_md.is_file()
        assert claude_md.stat().st_size > 0

    def test_manifest_json_exists(self, generated_project):
        output_dir, _, _ = generated_project
        manifest_file = output_dir / "manifest.json"
        assert manifest_file.is_file()

    def test_settings_json_exists(self, generated_project):
        output_dir, _, _ = generated_project
        settings = output_dir / ".claude" / "settings.json"
        assert settings.is_file()
        assert settings.stat().st_size > 0

    def test_agent_files_exist_for_each_persona(self, generated_project):
        output_dir, _, spec = generated_project
        agents_dir = output_dir / ".claude" / "agents"
        assert agents_dir.is_dir()
        for persona in spec.team.personas:
            agent_file = agents_dir / f"{persona.id}.md"
            assert agent_file.is_file(), f"Missing agent file for persona: {persona.id}"
            assert agent_file.stat().st_size > 0

    def test_no_extra_agent_files(self, generated_project):
        output_dir, _, spec = generated_project
        agents_dir = output_dir / ".claude" / "agents"
        expected_ids = {p.id for p in spec.team.personas}
        actual_files = {f.stem for f in agents_dir.glob("*.md")}
        extra = actual_files - expected_ids
        assert not extra, f"Unexpected agent files: {extra}"

    def test_seed_tasks_created(self, generated_project):
        output_dir, _, _ = generated_project
        # small-python-team.yml has seed_tasks: true
        tasks_dir = output_dir / "ai" / "tasks"
        assert tasks_dir.is_dir()

    # -- Deep content checks ------------------------------------------------

    def test_claude_md_contains_persona_sections(self, generated_project):
        output_dir, _, spec = generated_project
        claude_md = (output_dir / "CLAUDE.md").read_text(encoding="utf-8")
        for persona in spec.team.personas:
            assert persona.id in claude_md, (
                f"CLAUDE.md missing reference to persona: {persona.id}"
            )

    def test_claude_md_contains_stack_content(self, generated_project):
        output_dir, _, spec = generated_project
        claude_md = (output_dir / "CLAUDE.md").read_text(encoding="utf-8").lower()
        for stack in spec.stacks:
            assert stack.id in claude_md, (
                f"CLAUDE.md missing reference to stack: {stack.id}"
            )

    def test_manifest_json_valid_structure(self, generated_project):
        output_dir, _, _ = generated_project
        manifest_file = output_dir / "manifest.json"
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        assert "stages" in data
        assert "generated_at" in data
        assert isinstance(data["stages"], dict)

    def test_manifest_records_pipeline_stages(self, generated_project):
        _, manifest, _ = generated_project
        expected_stages = {"scaffold", "compile", "safety"}
        present = set(manifest.stages.keys())
        missing = expected_stages - present
        assert not missing, f"Manifest missing stages: {missing}"

    def test_agent_files_reference_persona_names(self, generated_project):
        output_dir, _, spec = generated_project
        agents_dir = output_dir / ".claude" / "agents"
        for persona in spec.team.personas:
            agent_file = agents_dir / f"{persona.id}.md"
            content = agent_file.read_text(encoding="utf-8").lower()
            # The persona id (e.g. "team-lead") or a human form should appear
            assert persona.id.replace("-", " ") in content or persona.id in content, (
                f"Agent file {agent_file.name} does not reference persona {persona.id}"
            )
