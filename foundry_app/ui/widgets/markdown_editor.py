"""Reusable split-pane markdown editor widget.

Left pane: plain-text editor (QPlainTextEdit).
Right pane: live-rendered HTML preview (QTextBrowser).
Toolbar: Save, Revert, and dirty-state indicator.
"""

from __future__ import annotations

import logging
from pathlib import Path

import mistune
from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

# Catppuccin Mocha palette
_BG = "#1e1e2e"
_SURFACE = "#313244"
_TEXT = "#cdd6f4"
_SUBTEXT = "#a6adc8"
_ACCENT = "#cba6f7"
_RED = "#f38ba8"

_PREVIEW_CSS = f"""
body {{
    background-color: {_SURFACE};
    color: {_TEXT};
    font-family: sans-serif;
    font-size: 13px;
    padding: 12px;
    line-height: 1.5;
}}
h1, h2, h3, h4, h5, h6 {{
    color: {_ACCENT};
    margin-top: 16px;
    margin-bottom: 8px;
}}
code {{
    background-color: {_BG};
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 12px;
}}
pre {{
    background-color: {_BG};
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
}}
pre code {{
    padding: 0;
}}
a {{
    color: {_ACCENT};
}}
blockquote {{
    border-left: 3px solid {_ACCENT};
    margin-left: 0;
    padding-left: 12px;
    color: {_SUBTEXT};
}}
"""

_EDITOR_STYLE = f"""
QPlainTextEdit {{
    background-color: {_SURFACE};
    color: {_TEXT};
    border: 1px solid {_SURFACE};
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    padding: 8px;
}}
"""

_PREVIEW_WIDGET_STYLE = f"""
QTextBrowser {{
    background-color: {_SURFACE};
    color: {_TEXT};
    border: 1px solid {_SURFACE};
    border-radius: 4px;
    padding: 0px;
}}
"""

# Debounce delay for preview updates (ms)
_PREVIEW_DELAY_MS = 300


class MarkdownEditor(QWidget):
    """Split-pane markdown editor with live preview.

    Signals:
        dirty_changed(bool): Emitted when the dirty state changes.
        file_saved(str): Emitted after a successful save, with the file path.
    """

    dirty_changed = Signal(bool)
    file_saved = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._file_path: Path | None = None
        self._saved_content: str = ""
        self._dirty: bool = False
        self._md = mistune.create_markdown()

        self._build_ui()
        self._connect_signals()

    # -- UI construction ---------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._dirty_label = QLabel("")
        self._dirty_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        toolbar.addWidget(self._dirty_label)

        toolbar.addStretch()

        self._revert_btn = QPushButton("Revert")
        self._revert_btn.setEnabled(False)
        self._revert_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_SURFACE};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {_BG};
            }}
            QPushButton:disabled {{
                color: {_SUBTEXT};
            }}
        """)
        toolbar.addWidget(self._revert_btn)

        self._save_btn = QPushButton("Save")
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: {_BG};
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #b4befe;
            }}
            QPushButton:disabled {{
                background-color: {_SURFACE};
                color: {_SUBTEXT};
            }}
        """)
        toolbar.addWidget(self._save_btn)

        layout.addLayout(toolbar)

        # Splitter: editor (left) + preview (right)
        self._splitter = QSplitter()
        self._splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {_SURFACE};
                width: 2px;
            }}
        """)

        self._editor = QPlainTextEdit()
        self._editor.setStyleSheet(_EDITOR_STYLE)
        self._splitter.addWidget(self._editor)

        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        self._preview.setStyleSheet(_PREVIEW_WIDGET_STYLE)
        self._splitter.addWidget(self._preview)

        # Equal split
        self._splitter.setStretchFactor(0, 1)
        self._splitter.setStretchFactor(1, 1)

        layout.addWidget(self._splitter, stretch=1)

        # Debounce timer for preview updates
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(_PREVIEW_DELAY_MS)
        self._preview_timer.timeout.connect(self._update_preview)

    def _connect_signals(self) -> None:
        self._editor.textChanged.connect(self._on_text_changed)
        self._save_btn.clicked.connect(self.save)
        self._revert_btn.clicked.connect(self.revert)

    # -- Public API --------------------------------------------------------

    @property
    def dirty(self) -> bool:
        """Whether the editor content differs from the last saved/loaded state."""
        return self._dirty

    @property
    def file_path(self) -> Path | None:
        """The currently loaded file path, or None."""
        return self._file_path

    @property
    def editor(self) -> QPlainTextEdit:
        """Access the text editor pane."""
        return self._editor

    @property
    def preview_pane(self) -> QTextBrowser:
        """Access the preview pane."""
        return self._preview

    @property
    def save_button(self) -> QPushButton:
        return self._save_btn

    @property
    def revert_button(self) -> QPushButton:
        return self._revert_btn

    @property
    def dirty_label(self) -> QLabel:
        return self._dirty_label

    def load_file(self, path: str | Path) -> None:
        """Load a file into the editor."""
        path = Path(path)
        if not path.is_file():
            logger.warning("Cannot load %s — not a file", path)
            return

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.error("Failed to read %s: %s", path, exc)
            return

        self._file_path = path
        self._saved_content = content
        self._editor.setPlainText(content)
        self._set_dirty(False)
        self._update_preview()

    def load_content(self, content: str, file_path: Path | None = None) -> None:
        """Load raw content into the editor (optionally with a file path for save)."""
        self._file_path = file_path
        self._saved_content = content
        self._editor.setPlainText(content)
        self._set_dirty(False)
        self._update_preview()

    def save(self) -> bool:
        """Write the current editor content to disk. Returns True on success."""
        if self._file_path is None:
            logger.warning("No file path set — cannot save")
            return False

        try:
            self._file_path.write_text(
                self._editor.toPlainText(), encoding="utf-8"
            )
        except OSError as exc:
            logger.error("Failed to save %s: %s", self._file_path, exc)
            return False

        self._saved_content = self._editor.toPlainText()
        self._set_dirty(False)
        self.file_saved.emit(str(self._file_path))
        logger.info("Saved %s", self._file_path)
        return True

    def revert(self) -> None:
        """Reload the file from disk, discarding unsaved changes."""
        if self._file_path is not None and self._file_path.is_file():
            self.load_file(self._file_path)
        else:
            self._editor.setPlainText(self._saved_content)
            self._set_dirty(False)
            self._update_preview()

    def clear(self) -> None:
        """Clear the editor and preview."""
        self._file_path = None
        self._saved_content = ""
        self._editor.clear()
        self._preview.clear()
        self._set_dirty(False)

    # -- Internal ----------------------------------------------------------

    def _on_text_changed(self) -> None:
        """Handle text edits: update dirty state and schedule preview refresh."""
        is_dirty = self._editor.toPlainText() != self._saved_content
        if is_dirty != self._dirty:
            self._set_dirty(is_dirty)
        self._preview_timer.start()

    def _set_dirty(self, dirty: bool) -> None:
        self._dirty = dirty
        self._save_btn.setEnabled(dirty and self._file_path is not None)
        self._revert_btn.setEnabled(dirty)
        if dirty:
            self._dirty_label.setText("Modified")
            self._dirty_label.setStyleSheet(f"color: {_RED}; font-size: 12px;")
        else:
            self._dirty_label.setText("")
            self._dirty_label.setStyleSheet(f"color: {_SUBTEXT}; font-size: 12px;")
        self.dirty_changed.emit(dirty)

    def _update_preview(self) -> None:
        """Render the current editor text as HTML and display in the preview."""
        md_text = self._editor.toPlainText()
        html_body = self._md(md_text)
        full_html = (
            f"<html><head><style>{_PREVIEW_CSS}</style></head>"
            f"<body>{html_body}</body></html>"
        )
        self._preview.setHtml(full_html)
