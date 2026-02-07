"""Tests for export service functions and validate_generated_project."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from foundry_app.services.export import (
    check_no_symlinks,
    check_self_contained,
    export_project,
)
from foundry_app.services.export import (
    validate_generated_project as export_validate_generated_project,
)
from foundry_app.services.validator import validate_generated_project
from foundry_app.ui.screens.builder.export_screen import ExportScreen

# -- Service-level: check_self_contained ---------------------------------------


def test_check_self_contained_clean_dir(tmp_path: Path) -> None:
    """A directory with only regular files and subdirs should be self-contained."""
    (tmp_path / "file.txt").write_text("hello")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.md").write_text("world")

    assert check_self_contained(tmp_path) == []
    # Backward compat: ExportScreen delegates to the service
    assert ExportScreen._check_self_contained(tmp_path) is True


@pytest.mark.skipif(os.name == "nt", reason="symlinks may require privileges on Windows")
def test_check_self_contained_with_external_symlink(tmp_path: Path) -> None:
    """A symlink pointing outside the project tree should cause the check to fail."""
    (tmp_path / "real.txt").write_text("content")

    # Create a target outside tmp_path
    external = tmp_path.parent / "external_target"
    external.mkdir(exist_ok=True)
    (external / "data.txt").write_text("external data")

    # Symlink inside project pointing outside
    os.symlink(str(external), str(tmp_path / "escape_link"))

    try:
        warnings = check_self_contained(tmp_path)
        assert len(warnings) > 0
        # Backward compat
        assert ExportScreen._check_self_contained(tmp_path) is False
    finally:
        # Clean up the external directory we created outside tmp_path
        import shutil
        shutil.rmtree(external, ignore_errors=True)


# -- Service-level: check_no_symlinks -----------------------------------------


def test_check_no_symlinks_clean_dir(tmp_path: Path) -> None:
    """A directory with no symlinks should pass."""
    (tmp_path / "a.txt").write_text("aaa")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "b.txt").write_text("bbb")

    assert check_no_symlinks(tmp_path) == []
    assert ExportScreen._check_no_symlinks(tmp_path) is True


@pytest.mark.skipif(os.name == "nt", reason="symlinks may require privileges on Windows")
def test_check_no_symlinks_with_symlink(tmp_path: Path) -> None:
    """Any symlink (even internal) should cause the check to fail."""
    real_file = tmp_path / "real.txt"
    real_file.write_text("content")

    # Even an internal symlink should be rejected
    os.symlink(str(real_file), str(tmp_path / "link.txt"))

    warnings = check_no_symlinks(tmp_path)
    assert len(warnings) > 0
    assert ExportScreen._check_no_symlinks(tmp_path) is False


# -- Service-level: export_project ---------------------------------------------


def test_export_project_copy(tmp_path: Path) -> None:
    """export_project in copy mode should duplicate the source."""
    src = tmp_path / "project"
    src.mkdir()
    (src / "file.txt").write_text("hello")

    dest = tmp_path / "exported" / "project"
    result = export_project(src, dest, mode="copy")

    assert result.destination == dest
    assert dest.is_dir()
    assert (dest / "file.txt").read_text() == "hello"
    # Source should still exist after copy
    assert src.is_dir()


def test_export_project_move(tmp_path: Path) -> None:
    """export_project in move mode should relocate the source."""
    src = tmp_path / "project"
    src.mkdir()
    (src / "file.txt").write_text("hello")

    dest = tmp_path / "exported" / "project"
    result = export_project(src, dest, mode="move")

    assert result.destination == dest
    assert dest.is_dir()
    assert (dest / "file.txt").read_text() == "hello"
    # Source should no longer exist after move
    assert not src.exists()


def test_export_project_overwrites_existing(tmp_path: Path) -> None:
    """export_project should remove an existing destination first."""
    src = tmp_path / "project"
    src.mkdir()
    (src / "new.txt").write_text("new")

    dest = tmp_path / "exported"
    dest.mkdir()
    (dest / "old.txt").write_text("old")

    result = export_project(src, dest, mode="copy")

    assert (dest / "new.txt").is_file()
    assert not (dest / "old.txt").exists()
    assert any("removed" in w.lower() for w in result.warnings)


def test_export_project_invalid_source(tmp_path: Path) -> None:
    """export_project should raise FileNotFoundError for missing source."""
    with pytest.raises(FileNotFoundError):
        export_project(tmp_path / "nonexistent", tmp_path / "dest")


def test_export_project_invalid_mode(tmp_path: Path) -> None:
    """export_project should raise ValueError for an unknown mode."""
    src = tmp_path / "project"
    src.mkdir()
    with pytest.raises(ValueError):
        export_project(src, tmp_path / "dest", mode="link")


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available on system")
def test_export_project_git_init(tmp_path: Path) -> None:
    """export_project with git_init=True should initialise a git repo in the destination."""
    src = tmp_path / "project"
    src.mkdir()
    (src / "README.md").write_text("# My Project\n", encoding="utf-8")
    (src / "CLAUDE.md").write_text("# CLAUDE\n", encoding="utf-8")

    dest = tmp_path / "exported"
    result = export_project(src, dest, mode="copy", git_init=True)

    assert result.git_initialized is True
    assert (dest / ".git").is_dir()


# -- Service-level: validate_generated_project (export module) -----------------


def test_export_validate_generated_project_valid(tmp_path: Path) -> None:
    """A fully valid project should return an empty error list."""
    _create_valid_project(tmp_path)
    errors = export_validate_generated_project(tmp_path)
    assert errors == []


def test_export_validate_generated_project_missing_claude_md(tmp_path: Path) -> None:
    """Missing CLAUDE.md should appear in the error list."""
    _create_valid_project(tmp_path)
    (tmp_path / "CLAUDE.md").unlink()
    errors = export_validate_generated_project(tmp_path)
    assert any("CLAUDE.md" in e for e in errors)


# -- validate_generated_project ------------------------------------------------


def _create_valid_project(root: Path) -> None:
    """Populate *root* with the minimum structure that passes validation."""
    (root / "CLAUDE.md").write_text("# CLAUDE\n")

    team_dir = root / "ai" / "team"
    team_dir.mkdir(parents=True)
    (team_dir / "composition.yml").write_text("project:\n  name: test\n")

    agents_dir = root / ".claude" / "agents"
    agents_dir.mkdir(parents=True)
    (agents_dir / "lead.md").write_text("# Lead agent\n")

    members_dir = root / "ai" / "generated" / "members"
    members_dir.mkdir(parents=True)
    (members_dir / "lead.md").write_text("# Lead member prompt\n")


def test_validate_generated_project_valid(tmp_path: Path) -> None:
    """A complete project structure should pass validation with no errors or warnings."""
    _create_valid_project(tmp_path)

    result = validate_generated_project(tmp_path)

    assert result.is_valid, f"Unexpected errors: {result.errors}"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_validate_generated_project_missing_claude_md(tmp_path: Path) -> None:
    """Missing CLAUDE.md should produce an error mentioning that file."""
    _create_valid_project(tmp_path)
    (tmp_path / "CLAUDE.md").unlink()

    result = validate_generated_project(tmp_path)

    assert not result.is_valid
    assert any("CLAUDE.md" in e for e in result.errors)


def test_validate_generated_project_missing_agents(tmp_path: Path) -> None:
    """Missing .claude/agents/ directory should produce an error about agents."""
    _create_valid_project(tmp_path)
    import shutil
    shutil.rmtree(tmp_path / ".claude" / "agents")

    result = validate_generated_project(tmp_path)

    assert not result.is_valid
    assert any("agents" in e.lower() for e in result.errors)


def test_validate_generated_project_missing_members(tmp_path: Path) -> None:
    """Missing ai/generated/members/ should produce a warning about members."""
    _create_valid_project(tmp_path)
    import shutil
    shutil.rmtree(tmp_path / "ai" / "generated" / "members")

    result = validate_generated_project(tmp_path)

    # Members missing is a warning, not an error
    assert result.is_valid, "Missing members should be a warning, not an error"
    assert any("members" in w.lower() for w in result.warnings)
