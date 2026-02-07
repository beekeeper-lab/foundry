"""Generate screen: run the pipeline and inspect a generation manifest."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import GenerationManifest
from foundry_app.core.settings import add_recent_project, load_settings, save_settings
from foundry_app.io.composition_io import load_composition
from foundry_app.services.generator import generate_project
from foundry_app.services.validator import validate_generated_project


class GenerateScreen(QWidget):
    """Run the generation pipeline and inspect results."""

    def __init__(
        self,
        inspector_stack: QStackedWidget,
        main_window: QWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._inspector_stack = inspector_stack
        self._main_window = main_window
        self._manifest: GenerationManifest | None = None
        self._project_dir: Path | None = None
        self._build_ui()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        # ==================================================================
        # Pipeline Runner section
        # ==================================================================
        self._build_pipeline_runner(outer)

        # ==================================================================
        # Inspect Results section (existing functionality)
        # ==================================================================
        self._build_inspect_section(outer)

    def _build_pipeline_runner(self, outer: QVBoxLayout) -> None:
        """Build the pipeline runner group box at the top of the screen."""
        runner_group = QGroupBox("Run Pipeline")
        runner_layout = QVBoxLayout(runner_group)

        # -- Composition file selector -------------------------------------
        comp_row = QHBoxLayout()
        comp_row.addWidget(QLabel("Composition File:"))
        self._comp_edit = QLineEdit()
        self._comp_edit.setPlaceholderText("Select a composition.yml file...")
        self._comp_edit.setReadOnly(True)
        comp_row.addWidget(self._comp_edit, stretch=1)

        btn_browse_comp = QPushButton("Browse...")
        btn_browse_comp.clicked.connect(self._on_browse_composition)
        comp_row.addWidget(btn_browse_comp)
        runner_layout.addLayout(comp_row)

        # -- Library root selector -----------------------------------------
        lib_row = QHBoxLayout()
        lib_row.addWidget(QLabel("Library Root:"))
        self._lib_edit = QLineEdit()
        self._lib_edit.setPlaceholderText("Uses library from main window if blank...")
        # Pre-fill from main_window if available, else from settings
        mw_root = getattr(self._main_window, "library_root", None)
        if mw_root is not None:
            self._lib_edit.setText(str(mw_root))
        else:
            _settings = load_settings()
            _fallback = _settings.library_root or (
                _settings.recent_libraries[0] if _settings.recent_libraries else ""
            )
            if _fallback:
                self._lib_edit.setText(_fallback)
        lib_row.addWidget(self._lib_edit, stretch=1)

        btn_browse_lib = QPushButton("Browse...")
        btn_browse_lib.clicked.connect(self._on_browse_library)
        lib_row.addWidget(btn_browse_lib)
        runner_layout.addLayout(lib_row)

        # -- Generate button -----------------------------------------------
        btn_row = QHBoxLayout()
        self._btn_generate = QPushButton("Generate")
        self._btn_generate.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white; "
            "font-weight: bold; padding: 6px 18px; }"
            "QPushButton:hover { background-color: #388e3c; }"
            "QPushButton:disabled { background-color: #aaa; color: #666; }"
        )
        self._btn_generate.clicked.connect(self._on_generate)
        btn_row.addWidget(self._btn_generate)
        btn_row.addStretch()
        runner_layout.addLayout(btn_row)

        # -- Progress list -------------------------------------------------
        runner_layout.addWidget(QLabel("Progress:"))
        self._progress_list = QListWidget()
        self._progress_list.setMaximumHeight(120)
        runner_layout.addWidget(self._progress_list)

        outer.addWidget(runner_group)

    def _build_inspect_section(self, outer: QVBoxLayout) -> None:
        """Build the inspect / manifest viewer section (existing UI)."""
        outer.addWidget(QLabel("<b>Generate &mdash; Inspect Results</b>"))

        # -- Project directory selector ----------------------------------------
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Generated Project:"))
        self._dir_edit = QLineEdit()
        self._dir_edit.setPlaceholderText("Select a generated project directory...")
        self._dir_edit.setReadOnly(True)
        dir_row.addWidget(self._dir_edit, stretch=1)

        self._btn_browse = QPushButton("Browse...")
        self._btn_browse.clicked.connect(self._on_browse)
        dir_row.addWidget(self._btn_browse)
        outer.addLayout(dir_row)

        # -- Action buttons ----------------------------------------------------
        btn_row = QHBoxLayout()
        self._btn_load = QPushButton("Load Manifest")
        self._btn_load.setEnabled(False)
        self._btn_load.clicked.connect(self._on_load_manifest)
        btn_row.addWidget(self._btn_load)

        self._btn_validate = QPushButton("Validate")
        self._btn_validate.setEnabled(False)
        self._btn_validate.clicked.connect(self._on_validate)
        btn_row.addWidget(self._btn_validate)

        self._btn_open_folder = QPushButton("Open Folder")
        self._btn_open_folder.setEnabled(False)
        self._btn_open_folder.clicked.connect(self._on_open_folder)
        btn_row.addWidget(self._btn_open_folder)

        btn_row.addStretch()
        outer.addLayout(btn_row)

        # -- Manifest details area (splitter: left=summary+table, right=lists) -
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left column: run info + stage table
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Run info group
        info_group = QGroupBox("Run Info")
        info_layout = QVBoxLayout(info_group)
        self._lbl_run_id = QLabel("Run ID: --")
        self._lbl_run_id.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        info_layout.addWidget(self._lbl_run_id)
        self._lbl_timestamp = QLabel("Timestamp: --")
        self._lbl_timestamp.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        info_layout.addWidget(self._lbl_timestamp)
        left_layout.addWidget(info_group)

        # Stage table
        left_layout.addWidget(QLabel("Stages"))
        self._stage_table = QTableWidget(0, 3)
        self._stage_table.setHorizontalHeaderLabels(
            ["Stage", "Files Written", "Warnings"]
        )
        self._stage_table.horizontalHeader().setStretchLastSection(True)
        self._stage_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._stage_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self._stage_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._stage_table.currentCellChanged.connect(self._on_stage_row_changed)
        left_layout.addWidget(self._stage_table, stretch=1)

        splitter.addWidget(left)

        # Right column: files list + warnings list
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_layout.addWidget(QLabel("Files Written"))
        self._files_list = QListWidget()
        right_layout.addWidget(self._files_list, stretch=1)

        right_layout.addWidget(QLabel("Warnings"))
        self._warnings_list = QListWidget()
        right_layout.addWidget(self._warnings_list, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([400, 400])

        outer.addWidget(splitter, stretch=1)

        # -- Validation results ------------------------------------------------
        self._validation_group = QGroupBox("Validation Results")
        val_layout = QVBoxLayout(self._validation_group)
        self._validation_list = QListWidget()
        val_layout.addWidget(self._validation_list)
        self._validation_group.setVisible(False)
        outer.addWidget(self._validation_group)

    # -- Public API -----------------------------------------------------------

    def set_wizard_result(self, composition_path: Path, project_dir: Path | None) -> None:
        """Pre-populate from wizard results: composition file and project dir."""
        if composition_path and composition_path.is_file():
            self._comp_edit.setText(str(composition_path))
        if project_dir:
            self._project_dir = project_dir
            self._dir_edit.setText(str(project_dir))
            self._btn_load.setEnabled(True)
            self._btn_validate.setEnabled(True)
            self._btn_open_folder.setEnabled(True)

    # -- Pipeline runner slots -------------------------------------------------

    def _on_browse_composition(self) -> None:
        """Open a file dialog to select a composition.yml file."""
        start_dir = str(Path.home())
        comp_text = self._comp_edit.text().strip()
        if comp_text:
            parent = Path(comp_text).parent
            if parent.is_dir():
                start_dir = str(parent)

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Composition File",
            start_dir,
            "YAML Files (*.yml *.yaml);;All Files (*)",
        )
        if path:
            self._comp_edit.setText(path)

    def _on_browse_library(self) -> None:
        """Open a directory dialog to override the library root."""
        current = self._lib_edit.text().strip()
        start_dir = current if current and Path(current).is_dir() else str(Path.home())

        path = QFileDialog.getExistingDirectory(
            self, "Select Library Root", start_dir
        )
        if path:
            self._lib_edit.setText(path)

    def _add_progress(self, message: str, *, color: str = "") -> None:
        """Append a line to the progress list and force a UI repaint."""
        escaped = html.escape(message)
        item = QListWidgetItem(escaped)
        if color:
            item.setForeground(QColor(color))
        self._progress_list.addItem(item)
        self._progress_list.scrollToBottom()
        QApplication.processEvents()

    def _on_generate(self) -> None:
        """Run the full generation pipeline from the selected composition."""
        # -- Validate inputs ---------------------------------------------------
        comp_path_str = self._comp_edit.text().strip()
        if not comp_path_str:
            QMessageBox.warning(
                self,
                "No Composition Selected",
                "Please select a composition.yml file first.",
            )
            return

        comp_path = Path(comp_path_str)
        if not comp_path.is_file():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Composition file does not exist:\n{html.escape(str(comp_path))}",
            )
            return

        lib_text = self._lib_edit.text().strip()
        if not lib_text:
            mw_root = getattr(self._main_window, "library_root", None)
            if mw_root is not None:
                lib_text = str(mw_root)

        # Fallback to settings if main window has no library
        if not lib_text:
            settings = load_settings()
            if settings.library_root:
                lib_text = settings.library_root
            elif settings.recent_libraries:
                lib_text = settings.recent_libraries[0]

        if not lib_text:
            QMessageBox.warning(
                self,
                "No Library Root",
                "Please specify a library root directory or open one via the toolbar.",
            )
            return

        library_root = Path(lib_text)
        if not library_root.is_dir():
            QMessageBox.warning(
                self,
                "Invalid Library Root",
                f"Library root is not a valid directory:\n"
                f"{html.escape(str(library_root))}",
            )
            return

        # -- Clear previous progress -------------------------------------------
        self._progress_list.clear()
        self._btn_generate.setEnabled(False)
        QApplication.processEvents()

        try:
            # Stage 1: Load composition
            self._add_progress("Loading composition...")
            composition = load_composition(comp_path)
            self._add_progress(
                f"Loaded: {html.escape(composition.project.name or composition.project.slug)}",
                color="#228B22",
            )

            # Stage 2: Run pipeline
            self._add_progress("Running generation pipeline...")
            self._add_progress("  - Validating...")
            QApplication.processEvents()

            settings = load_settings()
            strictness = settings.validation_strictness or "standard"
            manifest, validation = generate_project(
                composition, library_root, strictness=strictness
            )

            if not validation.is_valid:
                for err in validation.errors:
                    self._add_progress(f"  ERROR: {html.escape(err)}", color="#CC0000")
                for warn in validation.warnings:
                    self._add_progress(f"  WARNING: {html.escape(warn)}", color="#CC8800")
                self._add_progress("Generation aborted due to validation errors.", color="#CC0000")
                QMessageBox.warning(
                    self,
                    "Validation Failed",
                    "Pre-generation validation failed.\n\n"
                    + "\n".join(validation.errors[:10]),
                )
                return

            # Report completed stages
            for stage_name, stage_result in manifest.stages.items():
                n_files = len(stage_result.wrote)
                n_warns = len(stage_result.warnings)
                msg = f"  - {html.escape(stage_name)}: {n_files} file(s) written"
                if n_warns:
                    msg += f", {n_warns} warning(s)"
                self._add_progress(msg, color="#228B22")

            # Determine the output directory
            folder = composition.project.output_folder or composition.project.slug
            output_root = Path(composition.project.output_root) / folder

            self._add_progress(
                f"Generation complete: {html.escape(str(output_root))}",
                color="#228B22",
            )

            # Stage 3: Save to recent projects
            self._add_progress("Saving to recent projects...")
            settings = load_settings()
            settings = add_recent_project(settings, str(output_root))
            save_settings(settings)
            self._add_progress("Saved.", color="#228B22")

            # Stage 4: Auto-load the manifest into the inspect section
            self._project_dir = output_root
            self._dir_edit.setText(str(output_root))
            self._btn_load.setEnabled(True)
            self._btn_validate.setEnabled(True)
            self._btn_open_folder.setEnabled(True)

            self._manifest = manifest
            self._populate_manifest_details()
            self._add_progress("Manifest loaded into inspector.", color="#228B22")

        except (OSError, ValueError, KeyError) as exc:
            self._add_progress(f"Error: {html.escape(str(exc))}", color="#CC0000")
            QMessageBox.critical(
                self,
                "Generation Failed",
                f"An error occurred during generation:\n\n{exc}",
            )
        finally:
            self._btn_generate.setEnabled(True)

    # -- Inspect section slots (existing functionality) ------------------------

    def _on_browse(self) -> None:
        start_dir = str(self._project_dir) if self._project_dir else str(Path.home())
        path = QFileDialog.getExistingDirectory(
            self, "Select Generated Project Directory", start_dir
        )
        if not path:
            return
        self._project_dir = Path(path)
        self._dir_edit.setText(str(self._project_dir))
        self._btn_load.setEnabled(True)
        self._btn_validate.setEnabled(True)
        self._btn_open_folder.setEnabled(True)

    def _on_load_manifest(self) -> None:
        if self._project_dir is None:
            return

        manifest_path = self._project_dir / "ai" / "generated" / "manifest.json"
        if not manifest_path.is_file():
            QMessageBox.warning(
                self,
                "Manifest Not Found",
                f"Could not find manifest at:\n{manifest_path}\n\n"
                "Make sure the project has been generated.",
            )
            return

        try:
            data = json.loads(manifest_path.read_text())
            self._manifest = GenerationManifest.model_validate(data)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            QMessageBox.critical(
                self,
                "Error Loading Manifest",
                f"Failed to parse manifest:\n{exc}",
            )
            return

        self._populate_manifest_details()

    def _populate_manifest_details(self) -> None:
        if self._manifest is None:
            return

        # Run info
        run_id = self._manifest.run_id
        self._lbl_run_id.setText(f"Run ID: {html.escape(run_id)}")

        # The run_id is formatted as a timestamp: 2024-01-15T10-30-00Z
        # Display it in a friendlier way as the timestamp
        timestamp_display = run_id.replace("T", " ").replace("-", ":", 2)
        self._lbl_timestamp.setText(
            f"Timestamp: {html.escape(timestamp_display)}"
        )

        # Stage table
        stages = self._manifest.stages
        self._stage_table.setRowCount(len(stages))

        for row, (stage_name, stage_result) in enumerate(stages.items()):
            name_item = QTableWidgetItem(stage_name)
            self._stage_table.setItem(row, 0, name_item)

            files_item = QTableWidgetItem(str(len(stage_result.wrote)))
            files_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._stage_table.setItem(row, 1, files_item)

            warn_count = len(stage_result.warnings)
            warn_item = QTableWidgetItem(str(warn_count))
            warn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if warn_count > 0:
                warn_item.setBackground(QColor("#FFFFCC"))
            self._stage_table.setItem(row, 2, warn_item)

        # Populate full files and warnings lists (all stages combined)
        self._files_list.clear()
        self._warnings_list.clear()

        for stage_name, stage_result in stages.items():
            for filepath in stage_result.wrote:
                item = QListWidgetItem(filepath)
                item.setToolTip(f"Stage: {html.escape(stage_name)}")
                self._files_list.addItem(item)

            for warning in stage_result.warnings:
                item = QListWidgetItem(
                    f"[{html.escape(stage_name)}] {html.escape(warning)}"
                )
                item.setBackground(QColor("#FFFFCC"))
                self._warnings_list.addItem(item)

    def _on_stage_row_changed(
        self, current_row: int, _col: int, _prev_row: int, _prev_col: int
    ) -> None:
        """When a stage row is selected, filter the file/warning lists to that stage."""
        if self._manifest is None or current_row < 0:
            return

        stage_names = list(self._manifest.stages.keys())
        if current_row >= len(stage_names):
            return

        stage_name = stage_names[current_row]
        stage_result = self._manifest.stages[stage_name]

        self._files_list.clear()
        for filepath in stage_result.wrote:
            self._files_list.addItem(QListWidgetItem(filepath))

        self._warnings_list.clear()
        for warning in stage_result.warnings:
            item = QListWidgetItem(warning)
            item.setBackground(QColor("#FFFFCC"))
            self._warnings_list.addItem(item)

    def _on_validate(self) -> None:
        if self._project_dir is None:
            return

        result = validate_generated_project(self._project_dir)

        self._validation_list.clear()
        self._validation_group.setVisible(True)

        if result.is_valid and not result.warnings:
            item = QListWidgetItem("All checks passed.")
            item.setForeground(QColor("#228B22"))
            self._validation_list.addItem(item)
            return

        for error in result.errors:
            item = QListWidgetItem(f"ERROR: {error}")
            item.setForeground(QColor("#CC0000"))
            self._validation_list.addItem(item)

        for warning in result.warnings:
            item = QListWidgetItem(f"WARNING: {warning}")
            item.setBackground(QColor("#FFFFCC"))
            self._validation_list.addItem(item)

        if result.is_valid:
            title = "Validation Passed (with warnings)"
        else:
            title = f"Validation Failed ({len(result.errors)} error(s))"
        self._validation_group.setTitle(title)

    def _on_open_folder(self) -> None:
        if self._project_dir is None:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._project_dir)))
