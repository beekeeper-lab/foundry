"""Export screen: copy or move a generated project to a destination directory."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from foundry_app.services.export import (
    check_no_symlinks,
    check_self_contained,
    export_project,
)
from foundry_app.services.validator import validate_generated_project


class ExportScreen(QWidget):
    """Export a generated project: copy/move to destination, optionally init git."""

    def __init__(
        self,
        inspector_stack: QStackedWidget,
        main_window: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._inspector_stack = inspector_stack
        self._main_window = main_window
        self._build_ui()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        outer.addWidget(QLabel("<b>Export &mdash; Deploy Generated Project</b>"))

        # -- Main content splitter: left=settings, right=checklist -------------
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left column: source, destination, options
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Source directory
        src_group = QGroupBox("Source")
        src_layout = QVBoxLayout(src_group)
        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("Directory:"))
        self._src_edit = QLineEdit()
        self._src_edit.setPlaceholderText("Select the generated project to export...")
        self._src_edit.setReadOnly(True)
        src_row.addWidget(self._src_edit, stretch=1)
        self._btn_browse_src = QPushButton("Browse...")
        self._btn_browse_src.clicked.connect(self._on_browse_source)
        src_row.addWidget(self._btn_browse_src)
        src_layout.addLayout(src_row)
        left_layout.addWidget(src_group)

        # Destination directory
        dst_group = QGroupBox("Destination")
        dst_layout = QVBoxLayout(dst_group)
        dst_row = QHBoxLayout()
        dst_row.addWidget(QLabel("Directory:"))
        self._dst_edit = QLineEdit()
        self._dst_edit.setPlaceholderText("Select the destination directory...")
        self._dst_edit.setReadOnly(True)
        dst_row.addWidget(self._dst_edit, stretch=1)
        self._btn_browse_dst = QPushButton("Browse...")
        self._btn_browse_dst.clicked.connect(self._on_browse_destination)
        dst_row.addWidget(self._btn_browse_dst)
        dst_layout.addLayout(dst_row)
        left_layout.addWidget(dst_group)

        # Options
        opts_group = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts_group)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Copy", "Move"])
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()
        opts_layout.addLayout(mode_row)

        self._chk_git_init = QCheckBox("Initialize git repo (git init)")
        # Default from user settings
        from foundry_app.core.settings import load_settings
        _settings = load_settings()
        self._chk_git_init.setChecked(_settings.git_auto_init)
        opts_layout.addWidget(self._chk_git_init)

        left_layout.addWidget(opts_group)

        # Export button
        btn_row = QHBoxLayout()
        self._btn_run_checks = QPushButton("Run Checks")
        self._btn_run_checks.setEnabled(False)
        self._btn_run_checks.clicked.connect(self._on_run_checks)
        btn_row.addWidget(self._btn_run_checks)

        self._btn_export = QPushButton("Export")
        self._btn_export.setEnabled(False)
        self._btn_export.clicked.connect(self._on_export)
        btn_row.addWidget(self._btn_export)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        # Progress bar (hidden until export starts)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # indeterminate
        self._progress.setVisible(False)
        left_layout.addWidget(self._progress)

        left_layout.addStretch()
        splitter.addWidget(left)

        # Right column: pre-export checklist
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        checklist_group = QGroupBox("Pre-Export Checklist")
        checklist_layout = QVBoxLayout(checklist_group)

        self._checklist = QListWidget()
        self._checklist.setSelectionMode(
            QListWidget.SelectionMode.NoSelection
        )

        self._check_items: dict[str, QListWidgetItem] = {}
        checks = [
            ("self_contained", "Project is self-contained"),
            ("no_symlinks", "No symlinks to library"),
            ("claude_md", "CLAUDE.md exists"),
            ("agents_populated", ".claude/agents/ populated"),
            ("composition_present", "composition.yml present"),
        ]
        for key, label in checks:
            item = QListWidgetItem(label)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self._checklist.addItem(item)
            self._check_items[key] = item
            self._set_check_status(key, "pending")

        checklist_layout.addWidget(self._checklist)

        self._checklist_summary = QLabel("Run checks to verify project readiness.")
        self._checklist_summary.setWordWrap(True)
        checklist_layout.addWidget(self._checklist_summary)

        right_layout.addWidget(checklist_group, stretch=1)
        splitter.addWidget(right)

        splitter.setSizes([500, 300])
        outer.addWidget(splitter, stretch=1)

    # -- Public API -----------------------------------------------------------

    def set_source_path(self, path: Path) -> None:
        """Pre-populate the source directory (e.g. from wizard generation)."""
        self._src_edit.setText(str(path))
        self._btn_run_checks.setEnabled(True)
        self._update_export_enabled()
        self._reset_all_checks()

    # -- Check status helpers --------------------------------------------------

    _STATUS_ICONS = {
        "pending": "[ ]",
        "pass": "[x]",
        "fail": "[!]",
    }

    def _set_check_status(self, key: str, status: str) -> None:
        item = self._check_items.get(key)
        if item is None:
            return
        icon = self._STATUS_ICONS.get(status, "[ ]")
        # Preserve the label text after the icon prefix
        base_label = item.text()
        # Strip any existing prefix
        for prefix in self._STATUS_ICONS.values():
            if base_label.startswith(prefix + " "):
                base_label = base_label[len(prefix) + 1:]
                break
        item.setText(f"{icon} {base_label}")

        if status == "pass":
            item.setForeground(QColor("#228B22"))
        elif status == "fail":
            item.setForeground(QColor("#CC0000"))
        else:
            item.setForeground(QColor("#666666"))

    def _reset_all_checks(self) -> None:
        for key in self._check_items:
            self._set_check_status(key, "pending")
        self._checklist_summary.setText("Run checks to verify project readiness.")

    # -- Slots -----------------------------------------------------------------

    def _on_browse_source(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Select Generated Project", str(Path.home())
        )
        if not path:
            return
        self._src_edit.setText(path)
        self._btn_run_checks.setEnabled(True)
        self._update_export_enabled()
        self._reset_all_checks()

    def _on_browse_destination(self) -> None:
        from foundry_app.core.settings import load_settings
        _ws_root = load_settings().workspace_root
        start_dir = _ws_root if _ws_root and Path(_ws_root).is_dir() else str(Path.home())
        path = QFileDialog.getExistingDirectory(
            self, "Select Destination Directory", start_dir
        )
        if not path:
            return
        self._dst_edit.setText(path)
        self._update_export_enabled()

    def _update_export_enabled(self) -> None:
        has_src = bool(self._src_edit.text().strip())
        has_dst = bool(self._dst_edit.text().strip())
        self._btn_export.setEnabled(has_src and has_dst)

    def _on_run_checks(self) -> None:
        src_text = self._src_edit.text().strip()
        if not src_text:
            return
        project_dir = Path(src_text)

        self._reset_all_checks()

        # Run the standard validation
        result = validate_generated_project(project_dir)

        # Map validation results to checklist items
        error_set = set(result.errors)

        # CLAUDE.md exists
        if any("CLAUDE.md" in e for e in error_set):
            self._set_check_status("claude_md", "fail")
        else:
            self._set_check_status("claude_md", "pass")

        # .claude/agents/ populated
        if any(".claude/agents/" in e for e in error_set):
            self._set_check_status("agents_populated", "fail")
        else:
            self._set_check_status("agents_populated", "pass")

        # composition.yml present
        if any("composition.yml" in e for e in error_set):
            self._set_check_status("composition_present", "fail")
        else:
            self._set_check_status("composition_present", "pass")

        # Self-contained check: verify no files reference paths outside the project
        self._set_check_status(
            "self_contained",
            "pass" if self._check_self_contained(project_dir) else "fail",
        )

        # No symlinks check
        self._set_check_status(
            "no_symlinks",
            "pass" if self._check_no_symlinks(project_dir) else "fail",
        )

        # Summary
        fail_count = sum(
            1
            for key in self._check_items
            if self._check_items[key].text().startswith("[!]")
        )
        if fail_count == 0:
            self._checklist_summary.setText("All checks passed. Ready to export.")
            self._checklist_summary.setStyleSheet("color: #228B22; font-weight: bold;")
        else:
            self._checklist_summary.setText(
                f"{fail_count} check(s) failed. Review issues before exporting."
            )
            self._checklist_summary.setStyleSheet("color: #CC0000; font-weight: bold;")

    @staticmethod
    def _check_self_contained(project_dir: Path) -> bool:
        """Check that the project has no references outside its own tree."""
        return len(check_self_contained(project_dir)) == 0

    @staticmethod
    def _check_no_symlinks(project_dir: Path) -> bool:
        """Check that there are no symlinks pointing outside the project."""
        return len(check_no_symlinks(project_dir)) == 0

    def _on_export(self) -> None:
        src_text = self._src_edit.text().strip()
        dst_text = self._dst_edit.text().strip()

        if not src_text or not dst_text:
            QMessageBox.warning(
                self,
                "Missing Paths",
                "Both source and destination directories must be specified.",
            )
            return

        src_dir = Path(src_text)
        dst_dir = Path(dst_text)

        if not src_dir.is_dir():
            QMessageBox.warning(
                self,
                "Invalid Source",
                f"Source directory does not exist:\n{src_dir}",
            )
            return

        if not dst_dir.is_dir():
            QMessageBox.warning(
                self,
                "Invalid Destination",
                f"Destination directory does not exist:\n{dst_dir}",
            )
            return

        # The final destination is dst_dir / <project folder name>
        project_name = src_dir.name
        final_dest = dst_dir / project_name

        if final_dest.exists():
            confirm = QMessageBox.question(
                self,
                "Destination Exists",
                f"The directory already exists:\n{final_dest}\n\n"
                "Overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        mode = self._mode_combo.currentText().lower()
        git_init = self._chk_git_init.isChecked()

        self._progress.setVisible(True)
        self._btn_export.setEnabled(False)

        try:
            result = export_project(
                src=src_dir,
                dest=final_dest,
                mode=mode,
                git_init=git_init,
            )

            self._progress.setVisible(False)
            self._btn_export.setEnabled(True)

            # Check for git init warnings (failure is non-fatal)
            git_warning = ""
            for w in result.warnings:
                if "git init failed" in w:
                    git_warning = w
                    break

            if git_warning:
                QMessageBox.critical(
                    self,
                    "Git Init Failed",
                    f"Project was exported but git init failed:\n{git_warning}",
                )
            else:
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Project exported successfully to:\n{final_dest}"
                    + (
                        "\n\nGit repository initialized."
                        if result.git_initialized
                        else ""
                    ),
                )

        except (OSError, ValueError, FileNotFoundError) as exc:
            self._progress.setVisible(False)
            self._btn_export.setEnabled(True)
            QMessageBox.critical(
                self,
                "Export Failed",
                f"An error occurred during export:\n{exc}",
            )
