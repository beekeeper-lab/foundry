"""Tests for foundry_app.cli: CLI entry-point, generate, validate, export, and info commands."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from foundry_app.cli import (
    _build_parser,
    _cmd_diff,
    _cmd_export,
    _cmd_generate,
    _cmd_info,
    _cmd_validate,
)
from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
    HooksConfig,
    PersonaSelection,
    ProjectIdentity,
    StackSelection,
    StageResult,
    TeamConfig,
)
from foundry_app.io.composition_io import save_composition

LIBRARY_ROOT = Path(__file__).parent.parent / "ai-team-library"


def _make_spec(
    personas: list[str] | None = None,
    stacks: list[str] | None = None,
    name: str = "CLI Test Project",
    slug: str = "cli-test-project",
    output_root: str = "./generated-projects",
    output_folder: str = "",
) -> CompositionSpec:
    """Helper to build a minimal CompositionSpec for CLI tests."""
    if personas is None:
        personas = ["team-lead", "developer"]
    if stacks is None:
        stacks = ["python"]
    return CompositionSpec(
        project=ProjectIdentity(
            name=name,
            slug=slug,
            output_root=output_root,
            output_folder=output_folder,
        ),
        stacks=[StackSelection(id=sid) for sid in stacks],
        team=TeamConfig(personas=[PersonaSelection(id=pid) for pid in personas]),
        hooks=HooksConfig(),
    )


# -- generate command ----------------------------------------------------------


def test_generate_valid_composition(tmp_path: Path) -> None:
    """A valid composition + real library should generate successfully (exit 0)."""
    comp_file = tmp_path / "composition.yml"
    output_dir = tmp_path / "output"

    spec = _make_spec(
        output_root=str(output_dir),
        output_folder="project",
    )
    save_composition(spec, comp_file)

    args = argparse.Namespace(
        composition=comp_file,
        library=LIBRARY_ROOT,
        output=None,
        strictness=None,
    )
    rc = _cmd_generate(args)
    assert rc == 0
    assert (output_dir / "project").is_dir()


def test_generate_missing_composition(tmp_path: Path) -> None:
    """Pointing at a nonexistent composition file should return exit code 1."""
    missing = tmp_path / "does-not-exist.yml"

    args = argparse.Namespace(
        composition=missing,
        library=LIBRARY_ROOT,
        output=None,
        strictness=None,
    )
    rc = _cmd_generate(args)
    assert rc == 1


def test_generate_missing_library(tmp_path: Path) -> None:
    """A valid composition but nonexistent library dir should return exit code 1."""
    comp_file = tmp_path / "composition.yml"
    spec = _make_spec(output_root=str(tmp_path / "out"))
    save_composition(spec, comp_file)

    args = argparse.Namespace(
        composition=comp_file,
        library=tmp_path / "no-such-library",
        output=None,
        strictness=None,
    )
    rc = _cmd_generate(args)
    assert rc == 1


def test_generate_with_output_override(tmp_path: Path) -> None:
    """Using --output should place generated files at the override location."""
    comp_file = tmp_path / "composition.yml"
    override_dir = tmp_path / "custom-output"

    spec = _make_spec(
        output_root=str(tmp_path / "default-output"),
        output_folder="ignored",
    )
    save_composition(spec, comp_file)

    args = argparse.Namespace(
        composition=comp_file,
        library=LIBRARY_ROOT,
        output=override_dir,
        strictness=None,
    )
    rc = _cmd_generate(args)
    assert rc == 0
    assert override_dir.is_dir()
    # At minimum, CLAUDE.md and composition.yml should be present
    assert (override_dir / "CLAUDE.md").is_file()
    assert (override_dir / "ai" / "team" / "composition.yml").is_file()


# -- validate command ----------------------------------------------------------


def test_validate_valid(tmp_path: Path) -> None:
    """A valid composition + real library should validate successfully (exit 0)."""
    comp_file = tmp_path / "composition.yml"
    spec = _make_spec()
    save_composition(spec, comp_file)

    args = argparse.Namespace(
        composition=comp_file,
        library=LIBRARY_ROOT,
        strictness=None,
    )
    rc = _cmd_validate(args)
    assert rc == 0


def test_validate_bad_persona(tmp_path: Path) -> None:
    """A composition referencing a nonexistent persona should fail validation (exit 1)."""
    comp_file = tmp_path / "composition.yml"
    spec = _make_spec(personas=["nonexistent-persona-xyz"])
    save_composition(spec, comp_file)

    args = argparse.Namespace(
        composition=comp_file,
        library=LIBRARY_ROOT,
        strictness=None,
    )
    rc = _cmd_validate(args)
    assert rc == 1


def test_validate_missing_file(tmp_path: Path) -> None:
    """Pointing at a nonexistent composition file should return exit code 1."""
    missing = tmp_path / "nope.yml"

    args = argparse.Namespace(
        composition=missing,
        library=LIBRARY_ROOT,
        strictness=None,
    )
    rc = _cmd_validate(args)
    assert rc == 1


# -- parser --------------------------------------------------------------------


def test_parser_help() -> None:
    """Calling parse_args with no arguments should leave command as None."""
    parser = _build_parser()
    args = parser.parse_args([])
    assert args.command is None


# -- export command --------------------------------------------------------


def test_export_copy(tmp_path: Path) -> None:
    """Exporting in copy mode should create the destination directory with contents."""
    src = tmp_path / "my-project"
    src.mkdir()
    (src / "CLAUDE.md").write_text("# Project", encoding="utf-8")
    (src / "README.md").write_text("Hello", encoding="utf-8")

    dest = tmp_path / "exported"

    args = argparse.Namespace(
        project_dir=src,
        destination=dest,
        mode="copy",
        git_init=False,
        validate=False,
    )
    rc = _cmd_export(args)
    assert rc == 0
    assert dest.is_dir()
    assert (dest / "CLAUDE.md").is_file()
    assert (dest / "README.md").is_file()
    # Source should still exist (copy, not move)
    assert src.is_dir()


def test_export_missing_source(tmp_path: Path) -> None:
    """Exporting from a nonexistent source directory should return exit code 1."""
    missing_src = tmp_path / "does-not-exist"
    dest = tmp_path / "exported"

    args = argparse.Namespace(
        project_dir=missing_src,
        destination=dest,
        mode="copy",
        git_init=False,
        validate=False,
    )
    rc = _cmd_export(args)
    assert rc == 1


# -- info command ----------------------------------------------------------


def test_info_shows_manifest(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Running info on a project with a manifest should print the project name."""
    project_dir = tmp_path / "my-project"
    manifest_dir = project_dir / "ai" / "generated"
    manifest_dir.mkdir(parents=True)

    spec = _make_spec(name="Info Test Project", slug="info-test")
    manifest = GenerationManifest(
        run_id="2025-01-15T12-00-00Z",
        composition_snapshot=spec,
        stages={
            "claude_md": StageResult(wrote=["CLAUDE.md"], warnings=[]),
            "agents": StageResult(wrote=["agent-a.md", "agent-b.md"], warnings=[]),
        },
    )
    manifest_path = manifest_dir / "manifest.json"
    manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")

    args = argparse.Namespace(project_dir=project_dir)
    rc = _cmd_info(args)
    assert rc == 0

    captured = capsys.readouterr()
    assert "Info Test Project" in captured.out
    assert "info-test" in captured.out
    assert "Total files written: 3" in captured.out


def test_info_missing_manifest(tmp_path: Path) -> None:
    """Running info on a directory without a manifest should return exit code 1."""
    empty_project = tmp_path / "no-manifest"
    empty_project.mkdir()

    args = argparse.Namespace(project_dir=empty_project)
    rc = _cmd_info(args)
    assert rc == 1


# -- diff command ----------------------------------------------------------


def test_diff_shows_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Running diff on a project with a diff-report.md should print the report content."""
    project_dir = tmp_path / "my-project"
    report_dir = project_dir / "ai" / "generated"
    report_dir.mkdir(parents=True)

    report_content = "# Diff Report\n\n- Changed CLAUDE.md\n- Added agent-x.md\n"
    (report_dir / "diff-report.md").write_text(report_content, encoding="utf-8")

    args = argparse.Namespace(project_dir=project_dir)
    rc = _cmd_diff(args)
    assert rc == 0

    captured = capsys.readouterr()
    assert "Diff Report" in captured.out
    assert "Changed CLAUDE.md" in captured.out
    assert "Added agent-x.md" in captured.out


def test_diff_missing_report(tmp_path: Path) -> None:
    """Running diff on a directory without a diff report should return exit code 1."""
    project_dir = tmp_path / "no-report"
    project_dir.mkdir()

    args = argparse.Namespace(project_dir=project_dir)
    rc = _cmd_diff(args)
    assert rc == 1
