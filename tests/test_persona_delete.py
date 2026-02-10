"""Tests for persona delete logic — filesystem-level, no PySide6/Qt required.

BEAN-084: Verifies persona deletion at the filesystem layer, including
tree-building after removal and safety checks. These complement the
full UI tests in test_library_manager.py::TestDeletePersona.
"""

import shutil
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 so we can import the pure functions without libGL.so.1
# ---------------------------------------------------------------------------
_PYSIDE6_MODULES = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

_stashed: dict[str, ModuleType | None] = {}
for _mod_name in _PYSIDE6_MODULES:
    _stashed[_mod_name] = sys.modules.get(_mod_name)
    mock = MagicMock()
    # Provide Qt.ItemDataRole.UserRole as an int so tree-building works
    if _mod_name == "PySide6.QtCore":
        mock.Qt.ItemDataRole.UserRole = 0x0100
        mock.Qt.Orientation.Horizontal = 1
        mock.Qt.AlignmentFlag.AlignCenter = 4
    sys.modules[_mod_name] = mock

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
    persona_starter_files,
)

# Restore original modules (or remove mocks) so other tests are unaffected
for _mod_name in _PYSIDE6_MODULES:
    prev = _stashed[_mod_name]
    if prev is None:
        sys.modules.pop(_mod_name, None)
    else:
        sys.modules[_mod_name] = prev


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_persona(lib: Path, name: str) -> Path:
    """Create a minimal persona directory under *lib*/personas/."""
    persona_dir = lib / "personas" / name
    persona_dir.mkdir(parents=True)
    (persona_dir / "templates").mkdir()
    for filename, content in persona_starter_files(name).items():
        (persona_dir / filename).write_text(content, encoding="utf-8")
    return persona_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPersonaDeleteFilesystem:
    """Verify persona deletion works at the filesystem level."""

    def test_rmtree_removes_persona_directory(self, tmp_path: Path):
        lib = tmp_path / "lib"
        persona_dir = _make_persona(lib, "my-agent")
        assert persona_dir.is_dir()
        assert (persona_dir / "persona.md").is_file()
        shutil.rmtree(persona_dir)
        assert not persona_dir.exists()

    def test_tree_reflects_removal_after_delete(self, tmp_path: Path):
        lib = tmp_path / "lib"
        _make_persona(lib, "agent-a")
        _make_persona(lib, "agent-b")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 2

        shutil.rmtree(lib / "personas" / "agent-a")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 1
        assert personas["children"][0]["name"] == "agent-b"

    def test_delete_persona_leaves_sibling_intact(self, tmp_path: Path):
        lib = tmp_path / "lib"
        _make_persona(lib, "keep-me")
        target = _make_persona(lib, "delete-me")
        shutil.rmtree(target)
        assert not target.exists()
        assert (lib / "personas" / "keep-me" / "persona.md").is_file()

    def test_delete_persona_removes_all_starter_files(self, tmp_path: Path):
        lib = tmp_path / "lib"
        persona_dir = _make_persona(lib, "full-agent")
        assert (persona_dir / "persona.md").is_file()
        assert (persona_dir / "outputs.md").is_file()
        assert (persona_dir / "prompts.md").is_file()
        assert (persona_dir / "templates").is_dir()
        shutil.rmtree(persona_dir)
        assert not persona_dir.exists()
        for name in ("persona.md", "outputs.md", "prompts.md", "templates"):
            assert not (persona_dir / name).exists()

    def test_delete_persona_with_extra_template_files(self, tmp_path: Path):
        lib = tmp_path / "lib"
        persona_dir = _make_persona(lib, "custom-agent")
        (persona_dir / "templates" / "review.md").write_text("# Review", encoding="utf-8")
        (persona_dir / "templates" / "deploy.md").write_text("# Deploy", encoding="utf-8")
        shutil.rmtree(persona_dir)
        assert not persona_dir.exists()

    def test_tree_empty_after_last_persona_deleted(self, tmp_path: Path):
        lib = tmp_path / "lib"
        _make_persona(lib, "only-one")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 1
        shutil.rmtree(lib / "personas" / "only-one")
        tree = _build_file_tree(lib)
        personas = next(c for c in tree if c["name"] == "Personas")
        assert len(personas["children"]) == 0

    def test_path_safety_relative_check(self, tmp_path: Path):
        """Verify that a resolved persona path is relative to library root."""
        lib = tmp_path / "lib"
        persona_dir = _make_persona(lib, "safe-agent")
        resolved = persona_dir.resolve()
        assert resolved.is_relative_to(lib.resolve())

    def test_path_outside_library_fails_relative_check(self, tmp_path: Path):
        """A path outside the library root should fail the safety check."""
        lib = tmp_path / "lib"
        lib.mkdir(parents=True)
        outside = tmp_path / "outside"
        outside.mkdir()
        assert not outside.resolve().is_relative_to(lib.resolve())
