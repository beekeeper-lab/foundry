"""History screen: browse recent projects, generation logs, and manifest details."""

from __future__ import annotations

import html
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
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
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from foundry_app.core.models import GenerationManifest
from foundry_app.core.settings import load_settings


class HistoryScreen(QWidget):
    """History screen with three tabs: Recent Projects, Generation Logs, Manifest Viewer."""

    def __init__(
        self,
        inspector_stack: QStackedWidget,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._inspector_stack = inspector_stack
        self._manifest: GenerationManifest | None = None
        self._manifest_project_path: Path | None = None
        self._inspector_browser: QTextBrowser | None = None
        self._build_ui()
        self._load_recent_projects()

    # -- UI construction -------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        outer.addWidget(QLabel("<b>History</b>"))

        self._tabs = QTabWidget()
        self._build_recent_projects_tab()
        self._build_generation_logs_tab()
        self._build_manifest_viewer_tab()
        outer.addWidget(self._tabs, stretch=1)

    # -- Tab 1: Recent Projects ------------------------------------------------

    def _build_recent_projects_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header row with refresh button
        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("Recently generated projects:"))
        header_row.addStretch()
        self._btn_refresh_recent = QPushButton("Refresh")
        self._btn_refresh_recent.clicked.connect(self._load_recent_projects)
        header_row.addWidget(self._btn_refresh_recent)
        layout.addLayout(header_row)

        # Project list
        self._recent_list = QListWidget()
        self._recent_list.setAlternatingRowColors(True)
        layout.addWidget(self._recent_list, stretch=1)

        # Action row
        action_row = QHBoxLayout()
        self._btn_load_recent = QPushButton("Load Manifest")
        self._btn_load_recent.setEnabled(False)
        self._btn_load_recent.clicked.connect(self._on_load_recent_manifest)
        action_row.addWidget(self._btn_load_recent)
        action_row.addStretch()
        layout.addLayout(action_row)

        # Enable/disable load button based on selection
        self._recent_list.currentItemChanged.connect(self._on_recent_selection_changed)

        self._tabs.addTab(tab, "Recent Projects")

    # -- Tab 2: Generation Logs ------------------------------------------------

    def _build_generation_logs_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        # Directory selector
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Project directory:"))
        self._logs_dir_edit = QLineEdit()
        self._logs_dir_edit.setPlaceholderText("Select a project directory...")
        self._logs_dir_edit.setReadOnly(True)
        dir_row.addWidget(self._logs_dir_edit, stretch=1)
        self._btn_browse_logs = QPushButton("Browse...")
        self._btn_browse_logs.clicked.connect(self._on_browse_logs_dir)
        dir_row.addWidget(self._btn_browse_logs)
        layout.addLayout(dir_row)

        # Load button
        btn_row = QHBoxLayout()
        self._btn_load_logs = QPushButton("Load Manifest")
        self._btn_load_logs.setEnabled(False)
        self._btn_load_logs.clicked.connect(self._on_load_logs_manifest)
        btn_row.addWidget(self._btn_load_logs)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Splitter: left = run info, right = stage table
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: run metadata
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("<b>Run Metadata</b>"))

        self._lbl_run_id = QLabel("Run ID: --")
        self._lbl_run_id.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        left_layout.addWidget(self._lbl_run_id)

        self._lbl_timestamp = QLabel("Timestamp: --")
        self._lbl_timestamp.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        left_layout.addWidget(self._lbl_timestamp)

        self._lbl_lib_version = QLabel("Library version: --")
        self._lbl_lib_version.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        left_layout.addWidget(self._lbl_lib_version)

        left_layout.addStretch()
        splitter.addWidget(left)

        # Right: stage summary table
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("<b>Stage Summary</b>"))

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
        right_layout.addWidget(self._stage_table, stretch=1)

        splitter.addWidget(right)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter, stretch=1)

        self._tabs.addTab(tab, "Generation Logs")

    # -- Tab 3: Manifest Viewer ------------------------------------------------

    def _build_manifest_viewer_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(
            QLabel("Full manifest details (load a manifest from another tab):")
        )

        self._manifest_browser = QTextBrowser()
        self._manifest_browser.setOpenExternalLinks(False)
        self._manifest_browser.setPlaceholderText(
            "No manifest loaded. Use the Recent Projects or Generation Logs tab "
            "to load a manifest."
        )
        layout.addWidget(self._manifest_browser, stretch=1)

        self._tabs.addTab(tab, "Manifest Viewer")

    # -- Data loading ----------------------------------------------------------

    def _load_recent_projects(self) -> None:
        """Load (or reload) recent projects from settings into the list widget.

        Scans each path for ai/generated/manifest.json to show project name,
        timestamp, and status indicators.
        """
        self._recent_list.clear()
        settings = load_settings()

        for project_path_str in settings.recent_projects:
            project_path = Path(project_path_str)
            manifest_path = project_path / "ai" / "generated" / "manifest.json"

            # Try to read manifest for richer display
            project_name = project_path.name
            timestamp = ""
            has_manifest = False

            if manifest_path.is_file():
                try:
                    data = json.loads(manifest_path.read_text(encoding="utf-8"))
                    manifest = GenerationManifest.model_validate(data)
                    has_manifest = True
                    if manifest.composition_snapshot and manifest.composition_snapshot.project.name:
                        project_name = manifest.composition_snapshot.project.name
                    run_id = manifest.run_id
                    timestamp = run_id.replace("T", " ").replace("-", ":", 2).rstrip("Z")
                except (json.JSONDecodeError, ValueError, OSError):
                    pass

            # Build display text
            if has_manifest and timestamp:
                display = f"{project_name}  ({timestamp})"
            elif project_path.is_dir():
                display = f"{project_name}  (no manifest)"
            else:
                display = f"{project_name}  (missing)"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, project_path_str)
            item.setToolTip(project_path_str)

            if not project_path.is_dir():
                item.setForeground(QColor("#999999"))
            elif not has_manifest:
                item.setForeground(QColor("#888800"))

            self._recent_list.addItem(item)

        if self._recent_list.count() == 0:
            placeholder = QListWidgetItem("(no recent projects)")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            placeholder.setForeground(QColor("#888888"))
            self._recent_list.addItem(placeholder)

    def _load_manifest_from_path(self, project_path: Path) -> bool:
        """Load a manifest from a project path. Returns True on success."""
        manifest_path = project_path / "ai" / "generated" / "manifest.json"
        if not manifest_path.is_file():
            QMessageBox.warning(
                self,
                "Manifest Not Found",
                f"Could not find manifest at:\n{manifest_path}\n\n"
                "Make sure the project has been generated.",
            )
            return False

        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            self._manifest = GenerationManifest.model_validate(data)
            self._manifest_project_path = project_path
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            QMessageBox.critical(
                self,
                "Error Loading Manifest",
                f"Failed to parse manifest:\n{exc}",
            )
            return False

        self._populate_logs_tab()
        self._populate_manifest_viewer()
        self._update_inspector()
        return True

    # -- Populate tabs after loading -------------------------------------------

    def _populate_logs_tab(self) -> None:
        """Fill the Generation Logs tab with data from the loaded manifest."""
        if self._manifest is None:
            return

        run_id = html.escape(self._manifest.run_id)
        self._lbl_run_id.setText(f"Run ID: {run_id}")

        # Format the run_id as a human-readable timestamp
        timestamp_display = (
            self._manifest.run_id.replace("T", " ").replace("-", ":", 2)
        )
        self._lbl_timestamp.setText(
            f"Timestamp: {html.escape(timestamp_display)}"
        )

        lib_version = self._manifest.library_version or "(not recorded)"
        self._lbl_lib_version.setText(
            f"Library version: {html.escape(lib_version)}"
        )

        # Stage summary table
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

    def _populate_manifest_viewer(self) -> None:
        """Fill the Manifest Viewer tab with full manifest details as HTML."""
        if self._manifest is None:
            self._manifest_browser.setHtml("")
            return

        self._manifest_browser.setHtml(self._build_manifest_html())

    def _update_inspector(self) -> None:
        """Push a summary of the loaded manifest into the inspector panel."""
        if self._manifest is None:
            return

        # Create or reuse the inspector browser widget
        if self._inspector_browser is None:
            self._inspector_browser = QTextBrowser()
            self._inspector_browser.setOpenExternalLinks(False)
            self._inspector_stack.addWidget(self._inspector_browser)

        self._inspector_browser.setHtml(self._build_inspector_html())
        self._inspector_stack.setCurrentWidget(self._inspector_browser)

    # -- HTML builders ---------------------------------------------------------

    def _build_manifest_html(self) -> str:
        """Build full HTML for the Manifest Viewer tab."""
        if self._manifest is None:
            return ""

        m = self._manifest
        run_id = html.escape(m.run_id)
        lib_version = html.escape(m.library_version or "(not recorded)")
        timestamp = html.escape(
            m.run_id.replace("T", " ").replace("-", ":", 2)
        )

        parts: list[str] = []
        parts.append("<h2>Generation Manifest</h2>")

        if self._manifest_project_path is not None:
            parts.append(
                f"<p><b>Project:</b> {html.escape(str(self._manifest_project_path))}</p>"
            )

        parts.append("<h3>Run Metadata</h3>")
        parts.append("<table border='0' cellpadding='4'>")
        parts.append(f"<tr><td><b>Run ID:</b></td><td>{run_id}</td></tr>")
        parts.append(f"<tr><td><b>Timestamp:</b></td><td>{timestamp}</td></tr>")
        parts.append(
            f"<tr><td><b>Library Version:</b></td><td>{lib_version}</td></tr>"
        )
        parts.append("</table>")

        # Composition snapshot
        if m.composition_snapshot is not None:
            snap = m.composition_snapshot
            parts.append("<h3>Composition Snapshot</h3>")
            parts.append("<table border='0' cellpadding='4'>")
            parts.append(
                f"<tr><td><b>Project Name:</b></td>"
                f"<td>{html.escape(snap.project.name)}</td></tr>"
            )
            parts.append(
                f"<tr><td><b>Slug:</b></td>"
                f"<td>{html.escape(snap.project.slug)}</td></tr>"
            )

            stack_ids = ", ".join(
                html.escape(s.id) for s in snap.stacks
            ) or "(none)"
            parts.append(
                f"<tr><td><b>Stacks:</b></td><td>{stack_ids}</td></tr>"
            )

            persona_ids = ", ".join(
                html.escape(p.id) for p in snap.team.personas
            ) or "(none)"
            parts.append(
                f"<tr><td><b>Personas:</b></td><td>{persona_ids}</td></tr>"
            )

            hooks_posture = html.escape(snap.hooks.posture)
            hook_packs = ", ".join(
                html.escape(h.id) for h in snap.hooks.packs
            ) or "(none)"
            parts.append(
                f"<tr><td><b>Hooks Posture:</b></td><td>{hooks_posture}</td></tr>"
            )
            parts.append(
                f"<tr><td><b>Hook Packs:</b></td><td>{hook_packs}</td></tr>"
            )
            parts.append("</table>")

        # Per-stage details
        parts.append("<h3>Stages</h3>")

        if not m.stages:
            parts.append("<p><i>No stages recorded.</i></p>")
        else:
            for stage_name, stage_result in m.stages.items():
                safe_name = html.escape(stage_name)
                warn_count = len(stage_result.warnings)
                file_count = len(stage_result.wrote)

                parts.append(f"<h4>{safe_name}</h4>")

                # Files written
                parts.append(
                    f"<p><b>Files written ({file_count}):</b></p>"
                )
                if stage_result.wrote:
                    parts.append("<ul>")
                    for filepath in stage_result.wrote:
                        parts.append(f"<li>{html.escape(filepath)}</li>")
                    parts.append("</ul>")
                else:
                    parts.append("<p><i>No files written.</i></p>")

                # Warnings
                if warn_count > 0:
                    parts.append(
                        f"<p><b>Warnings ({warn_count}):</b></p>"
                    )
                    parts.append("<ul>")
                    for warning in stage_result.warnings:
                        parts.append(
                            f"<li style='background-color: #FFFFCC;'>"
                            f"{html.escape(warning)}</li>"
                        )
                    parts.append("</ul>")

        return "\n".join(parts)

    def _build_inspector_html(self) -> str:
        """Build concise HTML summary for the inspector panel."""
        if self._manifest is None:
            return ""

        m = self._manifest
        run_id = html.escape(m.run_id)
        lib_version = html.escape(m.library_version or "(not recorded)")
        timestamp = html.escape(
            m.run_id.replace("T", " ").replace("-", ":", 2)
        )

        total_files = sum(len(s.wrote) for s in m.stages.values())
        total_warnings = sum(len(s.warnings) for s in m.stages.values())

        parts: list[str] = []
        parts.append("<h3>Manifest Summary</h3>")
        parts.append("<table border='0' cellpadding='3'>")
        parts.append(f"<tr><td><b>Run ID:</b></td><td>{run_id}</td></tr>")
        parts.append(f"<tr><td><b>Timestamp:</b></td><td>{timestamp}</td></tr>")
        parts.append(
            f"<tr><td><b>Library Version:</b></td><td>{lib_version}</td></tr>"
        )
        parts.append(
            f"<tr><td><b>Total Files:</b></td><td>{total_files}</td></tr>"
        )
        parts.append(
            f"<tr><td><b>Total Warnings:</b></td><td>{total_warnings}</td></tr>"
        )
        parts.append("</table>")

        # Composition snapshot summary
        if m.composition_snapshot is not None:
            snap = m.composition_snapshot
            parts.append("<h4>Composition</h4>")
            parts.append(
                f"<p><b>Project:</b> {html.escape(snap.project.name)}</p>"
            )

            stack_ids = ", ".join(
                html.escape(s.id) for s in snap.stacks
            ) or "(none)"
            parts.append(f"<p><b>Stacks:</b> {stack_ids}</p>")

            persona_ids = ", ".join(
                html.escape(p.id) for p in snap.team.personas
            ) or "(none)"
            parts.append(f"<p><b>Personas:</b> {persona_ids}</p>")

        # Warnings summary
        if total_warnings > 0:
            parts.append("<h4>Warnings</h4>")
            for stage_name, stage_result in m.stages.items():
                for warning in stage_result.warnings:
                    parts.append(
                        f"<p style='background-color: #FFFFCC; padding: 4px;'>"
                        f"<b>[{html.escape(stage_name)}]</b> "
                        f"{html.escape(warning)}</p>"
                    )

        return "\n".join(parts)

    def _build_stage_inspector_html(
        self, stage_name: str
    ) -> str:
        """Build HTML for inspector when a specific stage row is clicked."""
        if self._manifest is None:
            return ""

        stage_result = self._manifest.stages.get(stage_name)
        if stage_result is None:
            return ""

        safe_name = html.escape(stage_name)
        parts: list[str] = []
        parts.append(f"<h3>Stage: {safe_name}</h3>")

        # Files written
        file_count = len(stage_result.wrote)
        parts.append(f"<p><b>Files written ({file_count}):</b></p>")
        if stage_result.wrote:
            parts.append("<ul>")
            for filepath in stage_result.wrote:
                parts.append(f"<li>{html.escape(filepath)}</li>")
            parts.append("</ul>")
        else:
            parts.append("<p><i>No files written.</i></p>")

        # Warnings
        warn_count = len(stage_result.warnings)
        if warn_count > 0:
            parts.append(f"<p><b>Warnings ({warn_count}):</b></p>")
            for warning in stage_result.warnings:
                parts.append(
                    f"<p style='background-color: #FFFFCC; padding: 4px;'>"
                    f"{html.escape(warning)}</p>"
                )
        else:
            parts.append("<p><i>No warnings.</i></p>")

        return "\n".join(parts)

    # -- Slots: Recent Projects tab --------------------------------------------

    def _on_recent_selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        """Enable or disable the Load Manifest button based on selection."""
        has_selection = (
            current is not None
            and current.data(Qt.ItemDataRole.UserRole) is not None
        )
        self._btn_load_recent.setEnabled(has_selection)

    def _on_load_recent_manifest(self) -> None:
        """Load the manifest from the selected recent project."""
        current = self._recent_list.currentItem()
        if current is None:
            return

        path_str = current.data(Qt.ItemDataRole.UserRole)
        if path_str is None:
            return

        project_path = Path(path_str)
        if not project_path.is_dir():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"The project directory no longer exists:\n{project_path}",
            )
            return

        if self._load_manifest_from_path(project_path):
            # Switch to Generation Logs tab to show the loaded data
            self._tabs.setCurrentIndex(1)

    # -- Slots: Generation Logs tab --------------------------------------------

    def _on_browse_logs_dir(self) -> None:
        """Open a file dialog to select a project directory."""
        start_dir = str(Path.home())
        if self._manifest_project_path is not None:
            start_dir = str(self._manifest_project_path)

        path = QFileDialog.getExistingDirectory(
            self, "Select Project Directory", start_dir
        )
        if not path:
            return

        self._logs_dir_edit.setText(path)
        self._btn_load_logs.setEnabled(True)

    def _on_load_logs_manifest(self) -> None:
        """Load the manifest from the browsed project directory."""
        dir_text = self._logs_dir_edit.text().strip()
        if not dir_text:
            return

        project_path = Path(dir_text)
        if not project_path.is_dir():
            QMessageBox.warning(
                self,
                "Directory Not Found",
                f"The directory does not exist:\n{project_path}",
            )
            return

        self._load_manifest_from_path(project_path)

    # -- Slots: Stage table ----------------------------------------------------

    def _on_stage_row_changed(
        self, current_row: int, _col: int, _prev_row: int, _prev_col: int
    ) -> None:
        """When a stage row is selected, show that stage's details in the inspector."""
        if self._manifest is None or current_row < 0:
            return

        stage_names = list(self._manifest.stages.keys())
        if current_row >= len(stage_names):
            return

        stage_name = stage_names[current_row]

        # Update inspector with stage-specific details
        if self._inspector_browser is None:
            self._inspector_browser = QTextBrowser()
            self._inspector_browser.setOpenExternalLinks(False)
            self._inspector_stack.addWidget(self._inspector_browser)

        self._inspector_browser.setHtml(
            self._build_stage_inspector_html(stage_name)
        )
        self._inspector_stack.setCurrentWidget(self._inspector_browser)
