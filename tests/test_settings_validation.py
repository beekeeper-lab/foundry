"""Tests for foundry_app.core.settings: validate_library_path and validate_workspace_path."""

from __future__ import annotations

from pathlib import Path

from foundry_app.core.settings import validate_library_path, validate_workspace_path

# -- validate_library_path ----------------------------------------------------


def test_validate_library_path_valid(tmp_path: Path) -> None:
    """A directory with both personas/ and stacks/ subdirs should return no issues."""
    (tmp_path / "personas").mkdir()
    (tmp_path / "stacks").mkdir()

    issues = validate_library_path(str(tmp_path))
    assert issues == []


def test_validate_library_path_missing_dir(tmp_path: Path) -> None:
    """A nonexistent directory should return a list with 'does not exist'."""
    nonexistent = tmp_path / "no-such-dir"

    issues = validate_library_path(str(nonexistent))
    assert len(issues) >= 1
    assert any("does not exist" in msg for msg in issues)


def test_validate_library_path_missing_personas(tmp_path: Path) -> None:
    """A directory without personas/ should return issues mentioning 'personas'."""
    (tmp_path / "stacks").mkdir()

    issues = validate_library_path(str(tmp_path))
    assert len(issues) >= 1
    assert any("personas" in msg for msg in issues)


def test_validate_library_path_missing_stacks(tmp_path: Path) -> None:
    """A directory without stacks/ should return issues mentioning 'stacks'."""
    (tmp_path / "personas").mkdir()

    issues = validate_library_path(str(tmp_path))
    assert len(issues) >= 1
    assert any("stacks" in msg for msg in issues)


def test_validate_library_path_missing_both(tmp_path: Path) -> None:
    """A directory with neither personas/ nor stacks/ should return two issues."""
    issues = validate_library_path(str(tmp_path))
    assert len(issues) == 2
    assert any("personas" in msg for msg in issues)
    assert any("stacks" in msg for msg in issues)


# -- validate_workspace_path --------------------------------------------------


def test_validate_workspace_path_valid(tmp_path: Path) -> None:
    """An existing writable directory should return no issues."""
    issues = validate_workspace_path(str(tmp_path))
    assert issues == []


def test_validate_workspace_path_parent_exists(tmp_path: Path) -> None:
    """A nonexistent dir whose parent is writable should return no issues."""
    future_dir = tmp_path / "new-workspace"

    issues = validate_workspace_path(str(future_dir))
    assert issues == []


def test_validate_workspace_path_nothing_exists(tmp_path: Path) -> None:
    """A nonexistent dir whose parent also does not exist should flag issues."""
    deep = tmp_path / "nonexistent-parent" / "nonexistent-child"

    issues = validate_workspace_path(str(deep))
    assert len(issues) >= 1
    assert any("exist" in msg.lower() for msg in issues)
