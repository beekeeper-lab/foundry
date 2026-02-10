"""Pure-logic tests for BEAN-086 Stack Create — no Qt/GPU dependencies.

Mocks PySide6 at sys.modules level so the library_manager module can be imported
in environments without libGL.so.1.
"""

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 modules before importing library_manager
# ---------------------------------------------------------------------------

_QT_MODS = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]

_saved = {}
for _mod_name in _QT_MODS:
    if _mod_name in sys.modules:
        _saved[_mod_name] = sys.modules[_mod_name]
    mock = MagicMock(spec=ModuleType)
    sys.modules[_mod_name] = mock

# Provide minimal Qt constants needed by the module at import time
sys.modules["PySide6.QtCore"].Qt = MagicMock()
sys.modules["PySide6.QtGui"].QColor = MagicMock()
sys.modules["PySide6.QtGui"].QFont = MagicMock()
sys.modules["PySide6.QtWidgets"].QWidget = MagicMock
sys.modules["PySide6.QtWidgets"].QTreeWidget = MagicMock
sys.modules["PySide6.QtWidgets"].QTreeWidgetItem = MagicMock
sys.modules["PySide6.QtWidgets"].QLabel = MagicMock
sys.modules["PySide6.QtWidgets"].QPushButton = MagicMock
sys.modules["PySide6.QtWidgets"].QSplitter = MagicMock
sys.modules["PySide6.QtWidgets"].QHBoxLayout = MagicMock
sys.modules["PySide6.QtWidgets"].QVBoxLayout = MagicMock
sys.modules["PySide6.QtWidgets"].QInputDialog = MagicMock
sys.modules["PySide6.QtWidgets"].QMessageBox = MagicMock

# Also mock the MarkdownEditor widget
sys.modules["foundry_app.ui.widgets.markdown_editor"] = MagicMock()
sys.modules["foundry_app.ui.theme"] = MagicMock()

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    STARTER_STACK_CONVENTIONS,
    STARTER_STACK_FILE,
    _build_file_tree,
    starter_content,
    validate_asset_name,
)

# ---------------------------------------------------------------------------
# Starter content for stacks
# ---------------------------------------------------------------------------


class TestStackStarterContent:

    def test_stack_conventions_content(self):
        content = starter_content("Stacks", "go-fiber")
        assert "Go Fiber Stack Conventions" in content
        assert "## Defaults" in content
        assert "## Do / Don't" in content
        assert "## Common Pitfalls" in content
        assert "## Checklist" in content

    def test_stack_file_content(self):
        content = starter_content("Stacks:file", "security")
        assert "# Security" in content
        assert "## Overview" in content
        assert "## Guidelines" in content

    def test_stack_conventions_template_has_placeholders(self):
        assert "{name}" in STARTER_STACK_CONVENTIONS

    def test_stack_file_template_has_placeholders(self):
        assert "{name}" in STARTER_STACK_FILE

    def test_stack_name_formatting(self):
        content = starter_content("Stacks", "python-fastapi")
        assert "Python Fastapi Stack Conventions" in content


# ---------------------------------------------------------------------------
# Validation rules applicable to stack names
# ---------------------------------------------------------------------------


class TestStackNameValidation:

    def test_valid_stack_names(self):
        assert validate_asset_name("python-fastapi") is None
        assert validate_asset_name("go-fiber") is None
        assert validate_asset_name("rust-actix") is None
        assert validate_asset_name("node") is None
        assert validate_asset_name("dotnet-8") is None

    def test_reject_uppercase(self):
        assert validate_asset_name("Python") is not None

    def test_reject_spaces(self):
        assert validate_asset_name("go fiber") is not None

    def test_reject_underscores(self):
        assert validate_asset_name("go_fiber") is not None

    def test_reject_empty(self):
        assert validate_asset_name("") is not None

    def test_reject_leading_hyphen(self):
        assert validate_asset_name("-bad") is not None

    def test_reject_too_long(self):
        assert validate_asset_name("a" * 61) is not None
        assert validate_asset_name("a" * 60) is None


# ---------------------------------------------------------------------------
# Disk operations (pure filesystem, no Qt)
# ---------------------------------------------------------------------------


class TestStackCreateOnDisk:

    def test_create_stack_directory_with_conventions(self, tmp_path: Path):
        """Simulate the disk operations that _on_new_asset performs for stacks."""
        stacks_dir = tmp_path / "stacks"
        stacks_dir.mkdir()
        name = "go-fiber"
        stack_dir = stacks_dir / name
        stack_dir.mkdir()
        dest = stack_dir / "conventions.md"
        content = starter_content("Stacks", name)
        dest.write_text(content, encoding="utf-8")

        assert stack_dir.is_dir()
        assert dest.is_file()
        text = dest.read_text(encoding="utf-8")
        assert "Go Fiber Stack Conventions" in text

    def test_duplicate_stack_detection(self, tmp_path: Path):
        stacks_dir = tmp_path / "stacks"
        stacks_dir.mkdir()
        existing = stacks_dir / "python-fastapi"
        existing.mkdir()
        assert existing.exists()  # duplicate detection checks .exists()

    def test_new_stack_appears_in_tree_scan(self, tmp_path: Path):
        """After creating a stack on disk, _build_file_tree includes it."""
        lib = tmp_path / "lib"
        stacks_dir = lib / "stacks"
        stacks_dir.mkdir(parents=True)
        name = "go-fiber"
        stack_dir = stacks_dir / name
        stack_dir.mkdir()
        (stack_dir / "conventions.md").write_text(
            starter_content("Stacks", name), encoding="utf-8"
        )
        tree = _build_file_tree(lib)
        stacks_cat = next(c for c in tree if c["name"] == "Stacks")
        stack_names = [child["name"] for child in stacks_cat["children"]]
        assert "go-fiber" in stack_names

    def test_new_stack_conventions_has_file_path(self, tmp_path: Path):
        lib = tmp_path / "lib"
        stacks_dir = lib / "stacks"
        stacks_dir.mkdir(parents=True)
        name = "go-fiber"
        stack_dir = stacks_dir / name
        stack_dir.mkdir()
        (stack_dir / "conventions.md").write_text(
            starter_content("Stacks", name), encoding="utf-8"
        )
        tree = _build_file_tree(lib)
        stacks_cat = next(c for c in tree if c["name"] == "Stacks")
        go_fiber = next(c for c in stacks_cat["children"] if c["name"] == "go-fiber")
        conv = next(c for c in go_fiber["children"] if c["name"] == "conventions.md")
        assert conv["path"] is not None
        assert conv["path"].endswith("conventions.md")

    def test_multiple_stacks_sorted(self, tmp_path: Path):
        lib = tmp_path / "lib"
        stacks_dir = lib / "stacks"
        stacks_dir.mkdir(parents=True)
        for name in ["zebra", "alpha", "middle"]:
            d = stacks_dir / name
            d.mkdir()
            (d / "conventions.md").write_text("# " + name, encoding="utf-8")
        tree = _build_file_tree(lib)
        stacks_cat = next(c for c in tree if c["name"] == "Stacks")
        names = [c["name"] for c in stacks_cat["children"]]
        assert names == ["alpha", "middle", "zebra"]
