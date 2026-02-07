"""Reusable markdown editor widget with source editing, preview, and save."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class MarkdownEditor(QWidget):
    """Markdown editor with source/preview tabs and save button."""

    file_saved = Signal(str)  # emits the file path after save

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_path: Path | None = None
        self._dirty = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with filename and save button
        header = QHBoxLayout()
        self._filename_label = QLabel("No file loaded")
        self._filename_label.setStyleSheet("font-weight: bold;")
        header.addWidget(self._filename_label)
        header.addStretch()

        self._save_btn = QPushButton("Save")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)
        header.addWidget(self._save_btn)
        layout.addLayout(header)

        # Tabs: Source / Preview
        self._tabs = QTabWidget()

        self._source_edit = QPlainTextEdit()
        self._source_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        # Apply font settings from user preferences
        from foundry_app.core.settings import load_settings
        _settings = load_settings()
        font = self._source_edit.font()
        font.setFamily("monospace")
        font.setPointSize(_settings.editor_font_size)
        self._source_edit.setFont(font)
        self._source_edit.setTabStopDistance(
            self._source_edit.fontMetrics().horizontalAdvance(" ") * _settings.editor_tab_width
        )
        self._source_edit.textChanged.connect(self._on_text_changed)
        self._tabs.addTab(self._source_edit, "Source")

        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        self._tabs.addTab(self._preview, "Preview")

        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

    def load_file(self, path: Path) -> None:
        """Load a markdown file into the editor."""
        self._current_path = path
        content = path.read_text() if path.is_file() else ""
        self._source_edit.setPlainText(content)
        self._filename_label.setText(path.name)
        self._dirty = False
        self._save_btn.setEnabled(False)

    def _on_text_changed(self) -> None:
        if not self._dirty:
            self._dirty = True
            self._save_btn.setEnabled(True)
            if self._current_path:
                self._filename_label.setText(f"{self._current_path.name} *")

    def _on_tab_changed(self, index: int) -> None:
        if index == 1:  # Preview tab
            self._render_preview()

    def _render_preview(self) -> None:
        """Render markdown source as basic HTML preview."""
        source = self._source_edit.toPlainText()
        # Basic markdown-to-html: headers, bold, italic, code blocks, lists
        html = _simple_md_to_html(source)
        self._preview.setHtml(html)

    def _on_save(self) -> None:
        if self._current_path is None:
            return
        content = self._source_edit.toPlainText()
        self._current_path.write_text(content)
        self._dirty = False
        self._save_btn.setEnabled(False)
        self._filename_label.setText(self._current_path.name)
        self.file_saved.emit(str(self._current_path))

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    @property
    def current_path(self) -> Path | None:
        return self._current_path


def _simple_md_to_html(md: str) -> str:
    """Minimal markdown to HTML conversion for preview."""
    import re

    lines = md.split("\n")
    html_lines: list[str] = []
    in_code_block = False
    in_list = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</pre>")
                in_code_block = False
            else:
                html_lines.append("<pre style='background:#f4f4f4;padding:8px;'>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line)
            continue

        # Headers
        if line.startswith("######"):
            html_lines.append(f"<h6>{line[6:].strip()}</h6>")
            continue
        if line.startswith("#####"):
            html_lines.append(f"<h5>{line[5:].strip()}</h5>")
            continue
        if line.startswith("####"):
            html_lines.append(f"<h4>{line[4:].strip()}</h4>")
            continue
        if line.startswith("###"):
            html_lines.append(f"<h3>{line[3:].strip()}</h3>")
            continue
        if line.startswith("##"):
            html_lines.append(f"<h2>{line[2:].strip()}</h2>")
            continue
        if line.startswith("#"):
            html_lines.append(f"<h1>{line[1:].strip()}</h1>")
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            html_lines.append("<hr>")
            continue

        # Lists
        if re.match(r"^\s*[-*]\s", line):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*[-*]\s", "", line)
            item = _inline_format(item)
            html_lines.append(f"<li>{item}</li>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False

        # Empty line
        if not line.strip():
            html_lines.append("<br>")
            continue

        # Regular paragraph
        html_lines.append(f"<p>{_inline_format(line)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_code_block:
        html_lines.append("</pre>")

    return "\n".join(html_lines)


def _inline_format(text: str) -> str:
    """Apply inline markdown formatting: bold, italic, code."""
    import re

    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    return text
