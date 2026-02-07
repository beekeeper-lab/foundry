"""Tests for foundry_app.services.diff_reporter: diff reports between generation runs."""

from __future__ import annotations

import json
from pathlib import Path

from foundry_app.core.models import GenerationManifest, StageResult
from foundry_app.services.diff_reporter import (
    backup_previous_manifest,
    generate_diff_report,
)


def _make_manifest(**stage_files: list[str]) -> GenerationManifest:
    """Build a GenerationManifest with the given stage -> wrote mappings.

    Example: _make_manifest(scaffold=["CLAUDE.md"], compile=["team-lead.md"])
    """
    stages = {name: StageResult(wrote=files) for name, files in stage_files.items()}
    return GenerationManifest(stages=stages)


# -- First-run report ---------------------------------------------------------


def test_first_run_report(tmp_path: Path):
    """generate_diff_report on a project with no previous manifest should note 'First generation'."""
    manifest = _make_manifest(scaffold=["CLAUDE.md", "README.md"])

    result = generate_diff_report(tmp_path, manifest)

    assert isinstance(result, StageResult)
    assert "diff-report.md" in result.wrote

    report_path = tmp_path / "ai" / "generated" / "diff-report.md"
    assert report_path.is_file()
    content = report_path.read_text()
    assert "First generation" in content


# -- Backup previous manifest --------------------------------------------------


def test_backup_previous_manifest(tmp_path: Path):
    """backup_previous_manifest should copy manifest.json to previous-manifest.json."""
    generated_dir = tmp_path / "ai" / "generated"
    generated_dir.mkdir(parents=True)
    manifest_path = generated_dir / "manifest.json"

    original_data = GenerationManifest(
        stages={"scaffold": StageResult(wrote=["CLAUDE.md"])}
    )
    manifest_path.write_text(original_data.model_dump_json(indent=2))

    backup_previous_manifest(tmp_path)

    previous_path = generated_dir / "previous-manifest.json"
    assert previous_path.is_file()

    backed_up = json.loads(previous_path.read_text())
    assert backed_up["stages"]["scaffold"]["wrote"] == ["CLAUDE.md"]


def test_backup_no_manifest_is_noop(tmp_path: Path):
    """backup_previous_manifest on an empty directory should not raise or create files."""
    # No ai/generated/manifest.json exists
    backup_previous_manifest(tmp_path)

    generated_dir = tmp_path / "ai" / "generated"
    if generated_dir.is_dir():
        assert not (generated_dir / "previous-manifest.json").exists()


# -- Diff report with previous manifest ----------------------------------------


def test_diff_report_with_previous(tmp_path: Path):
    """When a previous-manifest.json exists, the diff report should show file changes."""
    generated_dir = tmp_path / "ai" / "generated"
    generated_dir.mkdir(parents=True)

    # Write a previous manifest with one set of files
    previous = _make_manifest(scaffold=["CLAUDE.md", "old-file.md"])
    previous_path = generated_dir / "previous-manifest.json"
    previous_path.write_text(previous.model_dump_json(indent=2))

    # Generate a current manifest with a different set of files
    current = _make_manifest(
        scaffold=["CLAUDE.md", "README.md"],
        compile=["team-lead.md"],
    )

    result = generate_diff_report(tmp_path, current)

    report_path = generated_dir / "diff-report.md"
    assert report_path.is_file()
    content = report_path.read_text()

    # old-file.md was removed, README.md and team-lead.md are new
    assert "New Files" in content
    assert "Removed Files" in content
    # The report should list the specific changes
    assert "README.md" in content or "team-lead.md" in content
    assert "old-file.md" in content
    assert len(result.warnings) == 0


# -- Corrupt previous manifest -------------------------------------------------


def test_diff_report_corrupt_previous(tmp_path: Path):
    """Corrupt previous-manifest.json should trigger a warning, not a crash."""
    generated_dir = tmp_path / "ai" / "generated"
    generated_dir.mkdir(parents=True)

    # Write invalid JSON as the previous manifest
    previous_path = generated_dir / "previous-manifest.json"
    previous_path.write_text("{this is not valid json!!")

    current = _make_manifest(scaffold=["CLAUDE.md"])

    result = generate_diff_report(tmp_path, current)

    # Should still produce a report (falls back to first-run)
    report_path = generated_dir / "diff-report.md"
    assert report_path.is_file()
    content = report_path.read_text()
    assert "First generation" in content

    # Should warn about the parsing failure
    assert len(result.warnings) > 0
    assert any("parse" in w.lower() or "previous" in w.lower() for w in result.warnings)
