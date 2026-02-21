"""Pure-logic tests for BEAN-086 Expertise Create — no Qt/GPU dependencies.

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
    STARTER_EXPERTISE_CONVENTIONS,
    STARTER_EXPERTISE_FILE,
    _build_file_tree,
    starter_content,
    validate_asset_name,
)

# ---------------------------------------------------------------------------
# Starter content for expertise
# ---------------------------------------------------------------------------


class TestExpertiseStarterContent:

    def test_expertise_conventions_content(self):
        content = starter_content("Expertise", "go-fiber")
        assert "Go Fiber Expertise Conventions" in content
        assert "## Defaults" in content
        assert "## Do / Don't" in content
        assert "## Common Pitfalls" in content
        assert "## Checklist" in content

    def test_expertise_file_content(self):
        content = starter_content("Expertise:file", "security")
        assert "# Security" in content
        assert "## Overview" in content
        assert "## Guidelines" in content

    def test_expertise_conventions_template_has_placeholders(self):
        assert "{name}" in STARTER_EXPERTISE_CONVENTIONS

    def test_expertise_file_template_has_placeholders(self):
        assert "{name}" in STARTER_EXPERTISE_FILE

    def test_expertise_name_formatting(self):
        content = starter_content("Expertise", "python-fastapi")
        assert "Python Fastapi Expertise Conventions" in content


# ---------------------------------------------------------------------------
# Validation rules applicable to expertise names
# ---------------------------------------------------------------------------


class TestExpertiseNameValidation:

    def test_valid_expertise_names(self):
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


class TestExpertiseCreateOnDisk:

    def test_create_expertise_directory_with_conventions(self, tmp_path: Path):
        """Simulate the disk operations that _on_new_asset performs for expertise."""
        expertise_dir = tmp_path / "stacks"
        expertise_dir.mkdir()
        name = "go-fiber"
        expertise_item_dir = expertise_dir / name
        expertise_item_dir.mkdir()
        dest = expertise_item_dir / "conventions.md"
        content = starter_content("Expertise", name)
        dest.write_text(content, encoding="utf-8")

        assert expertise_item_dir.is_dir()
        assert dest.is_file()
        text = dest.read_text(encoding="utf-8")
        assert "Go Fiber Expertise Conventions" in text

    def test_duplicate_expertise_detection(self, tmp_path: Path):
        expertise_dir = tmp_path / "stacks"
        expertise_dir.mkdir()
        existing = expertise_dir / "python-fastapi"
        existing.mkdir()
        assert existing.exists()  # duplicate detection checks .exists()

    def test_new_expertise_appears_in_tree_scan(self, tmp_path: Path):
        """After creating an expertise on disk, _build_file_tree includes it."""
        lib = tmp_path / "lib"
        expertise_dir = lib / "stacks"
        expertise_dir.mkdir(parents=True)
        name = "go-fiber"
        expertise_item_dir = expertise_dir / name
        expertise_item_dir.mkdir()
        (expertise_item_dir / "conventions.md").write_text(
            starter_content("Expertise", name), encoding="utf-8"
        )
        tree = _build_file_tree(lib)
        expertise_cat = next(c for c in tree if c["name"] == "Expertise")
        expertise_names = [child["name"] for child in expertise_cat["children"]]
        assert "go-fiber" in expertise_names

    def test_new_expertise_conventions_has_file_path(self, tmp_path: Path):
        lib = tmp_path / "lib"
        expertise_dir = lib / "stacks"
        expertise_dir.mkdir(parents=True)
        name = "go-fiber"
        expertise_item_dir = expertise_dir / name
        expertise_item_dir.mkdir()
        (expertise_item_dir / "conventions.md").write_text(
            starter_content("Expertise", name), encoding="utf-8"
        )
        tree = _build_file_tree(lib)
        expertise_cat = next(c for c in tree if c["name"] == "Expertise")
        go_fiber = next(c for c in expertise_cat["children"] if c["name"] == "go-fiber")
        conv = next(c for c in go_fiber["children"] if c["name"] == "conventions.md")
        assert conv["path"] is not None
        assert conv["path"].endswith("conventions.md")

    def test_multiple_expertise_sorted(self, tmp_path: Path):
        lib = tmp_path / "lib"
        expertise_dir = lib / "stacks"
        expertise_dir.mkdir(parents=True)
        for name in ["zebra", "alpha", "middle"]:
            d = expertise_dir / name
            d.mkdir()
            (d / "conventions.md").write_text("# " + name, encoding="utf-8")
        tree = _build_file_tree(lib)
        expertise_cat = next(c for c in tree if c["name"] == "Expertise")
        names = [c["name"] for c in expertise_cat["children"]]
        assert names == ["alpha", "middle", "zebra"]
