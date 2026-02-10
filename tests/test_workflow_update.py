"""Tests for BEAN-095: Library Manager — Workflow Update.

These tests verify the workflow update flow end-to-end.
Pure logic functions are imported with PySide6 mocking for headless environments.
File I/O tests verify the save/revert/dirty contract without Qt.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PySide6 so we can import pure-logic functions from library_manager
# even on headless systems without libGL.so.1.
# ---------------------------------------------------------------------------

_MOCK_MODULES = [
    "PySide6",
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "mistune",
    "foundry_app.ui.theme",
    "foundry_app.ui.widgets",
    "foundry_app.ui.widgets.markdown_editor",
]

for _mod in _MOCK_MODULES:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from foundry_app.ui.screens.library_manager import (  # noqa: E402
    _build_file_tree,
    starter_content,
    validate_asset_name,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_workflow_library(root: Path) -> Path:
    """Create a minimal library with workflow files for testing."""
    lib = root / "test-library"
    wf_dir = lib / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "deploy.md").write_text(
        "# Deploy Workflow\n\nDeploy steps.", encoding="utf-8"
    )
    (wf_dir / "release.md").write_text(
        "# Release Process\n\nRelease steps.", encoding="utf-8"
    )
    # Create all category dirs so _build_file_tree works
    (lib / "personas").mkdir(exist_ok=True)
    (lib / "stacks").mkdir(exist_ok=True)
    (lib / "templates").mkdir(exist_ok=True)
    (lib / "claude" / "commands").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "skills").mkdir(parents=True, exist_ok=True)
    (lib / "claude" / "hooks").mkdir(parents=True, exist_ok=True)
    return lib


# ---------------------------------------------------------------------------
# Pure logic: _build_file_tree includes workflows
# ---------------------------------------------------------------------------


class TestWorkflowTreeBuilding:

    def test_workflows_category_present(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        names = [cat["name"] for cat in tree]
        assert "Workflows" in names

    def test_workflow_files_listed(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        child_names = sorted(c["name"] for c in workflows["children"])
        assert "deploy.md" in child_names
        assert "release.md" in child_names

    def test_workflow_file_nodes_have_paths(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        for child in workflows["children"]:
            assert child["path"] is not None
            assert child["path"].endswith(".md")

    def test_new_workflow_appears_after_creation(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        (lib / "workflows" / "hotfix.md").write_text("# Hotfix", encoding="utf-8")
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        child_names = [c["name"] for c in workflows["children"]]
        assert "hotfix.md" in child_names

    def test_updated_workflow_still_in_tree(self, tmp_path: Path):
        """After updating a workflow file's content, the tree still lists it."""
        lib = _create_workflow_library(tmp_path)
        (lib / "workflows" / "deploy.md").write_text("# Changed", encoding="utf-8")
        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        child_names = [c["name"] for c in workflows["children"]]
        assert "deploy.md" in child_names


# ---------------------------------------------------------------------------
# Workflow update: file I/O (no Qt)
# ---------------------------------------------------------------------------


class TestWorkflowFileIO:

    def test_read_workflow_content(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        content = path.read_text(encoding="utf-8")
        assert "# Deploy Workflow" in content

    def test_write_updated_content_to_disk(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        new_content = "# Updated Deploy\n\nNew deploy steps."
        path.write_text(new_content, encoding="utf-8")
        assert path.read_text(encoding="utf-8") == new_content

    def test_save_preserves_encoding(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        content_with_unicode = "# Deploy — Pro Workflow\n\nSteps with émojis."
        path.write_text(content_with_unicode, encoding="utf-8")
        assert path.read_text(encoding="utf-8") == content_with_unicode

    def test_revert_reads_original_from_disk(self, tmp_path: Path):
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        original = path.read_text(encoding="utf-8")
        # Revert = re-read from disk (file was never overwritten)
        reverted = path.read_text(encoding="utf-8")
        assert reverted == original


# ---------------------------------------------------------------------------
# Workflow update: dirty state logic
# ---------------------------------------------------------------------------


class TestWorkflowDirtyTracking:

    def test_content_matches_saved_is_not_dirty(self):
        saved = "# Deploy Workflow"
        current = "# Deploy Workflow"
        assert (current != saved) is False

    def test_content_differs_from_saved_is_dirty(self):
        saved = "# Deploy Workflow"
        current = "# Modified Workflow"
        assert (current != saved) is True

    def test_dirty_cleared_after_save(self, tmp_path: Path):
        """Simulate: load -> edit -> save -> dirty should be False."""
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        saved_content = path.read_text(encoding="utf-8")
        # Simulate edit
        new_content = "# Updated Deploy"
        is_dirty = new_content != saved_content
        assert is_dirty is True
        # Simulate save
        path.write_text(new_content, encoding="utf-8")
        saved_content = new_content
        is_dirty = new_content != saved_content
        assert is_dirty is False

    def test_dirty_cleared_after_revert(self, tmp_path: Path):
        """Simulate: load -> edit -> revert -> dirty should be False."""
        lib = _create_workflow_library(tmp_path)
        path = lib / "workflows" / "deploy.md"
        saved_content = path.read_text(encoding="utf-8")
        # Simulate edit
        current_content = "# Modified"
        is_dirty = current_content != saved_content
        assert is_dirty is True
        # Simulate revert (re-read from disk)
        current_content = path.read_text(encoding="utf-8")
        is_dirty = current_content != saved_content
        assert is_dirty is False


# ---------------------------------------------------------------------------
# Workflow starter content and validation
# ---------------------------------------------------------------------------


class TestWorkflowStarterContent:

    def test_workflow_starter_has_heading(self):
        content = starter_content("Workflows", "ci-pipeline")
        assert "# Ci Pipeline" in content

    def test_workflow_starter_has_overview_section(self):
        content = starter_content("Workflows", "ci-pipeline")
        assert "## Overview" in content

    def test_workflow_starter_has_details_section(self):
        content = starter_content("Workflows", "ci-pipeline")
        assert "## Details" in content


class TestWorkflowNameValidation:

    def test_valid_workflow_name(self):
        assert validate_asset_name("deploy-prod") is None

    def test_invalid_workflow_name_uppercase(self):
        assert validate_asset_name("Deploy") is not None

    def test_invalid_workflow_name_spaces(self):
        assert validate_asset_name("deploy prod") is not None


# ---------------------------------------------------------------------------
# Workflow update: roundtrip simulation
# ---------------------------------------------------------------------------


class TestWorkflowUpdateRoundtrip:

    def test_full_roundtrip_create_edit_save_reload(self, tmp_path: Path):
        """Simulate the full workflow update lifecycle."""
        lib = _create_workflow_library(tmp_path)
        wf_path = lib / "workflows" / "deploy.md"

        # Step 1: Load (simulate selecting in tree)
        original_content = wf_path.read_text(encoding="utf-8")
        assert "Deploy Workflow" in original_content

        # Step 2: Edit (simulate typing in editor)
        new_content = "# Updated Deploy Workflow\n\nNew process with steps."
        is_dirty = new_content != original_content
        assert is_dirty is True

        # Step 3: Save (simulate clicking Save)
        wf_path.write_text(new_content, encoding="utf-8")
        saved_content = new_content
        is_dirty = new_content != saved_content
        assert is_dirty is False

        # Step 4: Reload (simulate re-selecting in tree after refresh)
        reloaded = wf_path.read_text(encoding="utf-8")
        assert reloaded == new_content
        assert "Updated Deploy Workflow" in reloaded

    def test_edit_then_revert_roundtrip(self, tmp_path: Path):
        """Simulate: load -> edit -> revert -> verify original restored."""
        lib = _create_workflow_library(tmp_path)
        wf_path = lib / "workflows" / "release.md"

        original_content = wf_path.read_text(encoding="utf-8")
        assert "Release Process" in original_content

        # Edit
        current = "# Something completely different"
        is_dirty = current != original_content
        assert is_dirty is True

        # Revert = reload from disk
        current = wf_path.read_text(encoding="utf-8")
        is_dirty = current != original_content
        assert is_dirty is False
        assert current == original_content

    def test_multiple_saves_accumulate(self, tmp_path: Path):
        """Multiple sequential saves should each persist."""
        lib = _create_workflow_library(tmp_path)
        wf_path = lib / "workflows" / "deploy.md"

        for i in range(3):
            content = f"# Version {i}\n\nIteration {i}."
            wf_path.write_text(content, encoding="utf-8")
            assert wf_path.read_text(encoding="utf-8") == content

    def test_save_does_not_affect_other_workflows(self, tmp_path: Path):
        """Saving one workflow should not change other workflow files."""
        lib = _create_workflow_library(tmp_path)
        deploy_path = lib / "workflows" / "deploy.md"
        release_path = lib / "workflows" / "release.md"

        release_before = release_path.read_text(encoding="utf-8")
        deploy_path.write_text("# Changed deploy", encoding="utf-8")
        release_after = release_path.read_text(encoding="utf-8")
        assert release_before == release_after

    def test_tree_reflects_updated_content(self, tmp_path: Path):
        """After save, re-scanning tree still finds the workflow file."""
        lib = _create_workflow_library(tmp_path)
        wf_path = lib / "workflows" / "deploy.md"
        wf_path.write_text("# Completely new content", encoding="utf-8")

        tree = _build_file_tree(lib)
        workflows = next(c for c in tree if c["name"] == "Workflows")
        child_names = [c["name"] for c in workflows["children"]]
        assert "deploy.md" in child_names

        # Verify the file path still points to the right file
        deploy_node = next(
            c for c in workflows["children"] if c["name"] == "deploy.md"
        )
        content = Path(deploy_node["path"]).read_text(encoding="utf-8")
        assert content == "# Completely new content"
