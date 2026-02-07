"""Tests for foundry_app.services.generator: full Foundry generation pipeline."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
    GenerationOptions,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.generator import generate_project

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def _make_spec(
    personas: list[str] | None = None,
    stacks: list[str] | None = None,
    name: str = "Test",
    slug: str = "test",
    seed_tasks: bool = False,
    write_manifest: bool = True,
    write_diff_report: bool = False,
) -> CompositionSpec:
    """Build a minimal CompositionSpec for generator tests."""
    if personas is None:
        personas = ["team-lead", "developer"]
    if stacks is None:
        stacks = ["python"]
    return CompositionSpec(
        project=ProjectIdentity(name=name, slug=slug),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=[PersonaSelection(id=pid) for pid in personas]),
        hooks=HooksConfig(),
        generation=GenerationOptions(
            seed_tasks=seed_tasks,
            write_manifest=write_manifest,
            write_diff_report=write_diff_report,
        ),
    )


# -- Successful generation -----------------------------------------------------


def test_generate_project_succeeds(tmp_path: Path):
    """Full pipeline with valid spec should produce scaffold and compile stages, plus CLAUDE.md."""
    spec = _make_spec()
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert validation.is_valid, f"Unexpected errors: {validation.errors}"
    assert isinstance(manifest, GenerationManifest)
    assert "scaffold" in manifest.stages
    assert "compile" in manifest.stages
    assert (output / "CLAUDE.md").is_file()


# -- Validation failure --------------------------------------------------------


def test_generate_validation_failure_returns_empty(tmp_path: Path):
    """Spec with a nonexistent persona should fail validation and return an empty manifest."""
    spec = _make_spec(personas=["nonexistent-ghost"])
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert not validation.is_valid
    assert len(manifest.stages) == 0


# -- Output override -----------------------------------------------------------


def test_generate_output_override(tmp_path: Path):
    """Passing output_root should place generated files in that directory."""
    custom_output = tmp_path / "custom-out"
    spec = _make_spec()

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=custom_output)

    assert validation.is_valid
    assert custom_output.is_dir()
    assert (custom_output / "CLAUDE.md").is_file()
    assert (custom_output / "ai" / "generated" / "members" / "team-lead.md").is_file()


# -- Strictness ----------------------------------------------------------------


def test_generate_strictness_passed(tmp_path: Path):
    """Strict mode with no stacks should fail validation (promoted to error)."""
    spec = _make_spec(stacks=[])
    output = tmp_path / "project"

    manifest, validation = generate_project(
        spec, LIBRARY_ROOT, output_root=output, strictness="strict"
    )

    assert not validation.is_valid
    assert any("stack" in e.lower() for e in validation.errors)
    assert len(manifest.stages) == 0


# -- Seed tasks ----------------------------------------------------------------


def test_generate_seed_tasks_creates_tasks_dir(tmp_path: Path):
    """When seed_tasks=True the pipeline should create ai/tasks/ with content."""
    spec = _make_spec(
        personas=["team-lead", "developer"],
        seed_tasks=True,
    )
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert validation.is_valid
    tasks_dir = output / "ai" / "tasks"
    assert tasks_dir.is_dir()
    task_files = list(tasks_dir.iterdir())
    assert len(task_files) > 0, "Expected at least one seeded task file"
    assert "seed" in manifest.stages


# -- GenerationOptions flags ---------------------------------------------------


def test_write_manifest_false_skips_manifest(tmp_path: Path):
    """When write_manifest=False the manifest.json file should NOT be written to disk."""
    spec = _make_spec(write_manifest=False)
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert validation.is_valid, f"Unexpected errors: {validation.errors}"
    assert isinstance(manifest, GenerationManifest)
    # The function still returns a manifest object, but the file must not exist on disk
    manifest_file = output / "ai" / "generated" / "manifest.json"
    assert not manifest_file.exists(), (
        "manifest.json should not be written when write_manifest=False"
    )


def test_seed_tasks_false_skips_seeder(tmp_path: Path):
    """When seed_tasks=False the pipeline should skip the seed stage entirely."""
    spec = _make_spec(seed_tasks=False)
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert validation.is_valid, f"Unexpected errors: {validation.errors}"
    # The seed stage should not appear in the manifest
    assert "seed" not in manifest.stages, (
        "seed stage should not be present when seed_tasks=False"
    )
    # The scaffold creates ai/tasks/ as an empty directory, but the seeder
    # should NOT have written seeded-tasks.md into it.
    seeded_file = output / "ai" / "tasks" / "seeded-tasks.md"
    assert not seeded_file.exists(), (
        "seeded-tasks.md should not exist when seed_tasks=False"
    )


def test_write_diff_report_true_creates_report(tmp_path: Path):
    """When write_diff_report=True the pipeline should produce a diff-report.md."""
    spec = _make_spec(write_diff_report=True)
    output = tmp_path / "project"

    manifest, validation = generate_project(spec, LIBRARY_ROOT, output_root=output)

    assert validation.is_valid, f"Unexpected errors: {validation.errors}"
    # The diff stage should be recorded in the manifest
    assert "diff" in manifest.stages, (
        "diff stage should be present when write_diff_report=True"
    )
    # The diff report file should exist on disk
    diff_report = output / "ai" / "generated" / "diff-report.md"
    assert diff_report.is_file(), (
        "diff-report.md should be written when write_diff_report=True"
    )
    # On first run (no previous manifest), it should note this is the first generation
    content = diff_report.read_text()
    assert "Diff Report" in content
