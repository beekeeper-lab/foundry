"""Library Manager screen — tree-based browser with CRUD for library assets."""

from __future__ import annotations

import logging
import re
import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from foundry_app.ui.theme import (
    ACCENT_PRIMARY,
    BG_BASE,
    BG_SURFACE,
    BORDER_DEFAULT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from foundry_app.ui.widgets.markdown_editor import MarkdownEditor

logger = logging.getLogger(__name__)

# Top-level categories mapped to their directory paths relative to library root.
# Order matters — this is the display order in the tree.
LIBRARY_CATEGORIES: list[tuple[str, str]] = [
    ("Personas", "personas"),
    ("Stacks", "stacks"),
    ("Shared Templates", "templates"),
    ("Workflows", "workflows"),
    ("Claude Commands", "claude/commands"),
    ("Claude Skills", "claude/skills"),
    ("Claude Hooks", "claude/hooks"),
]

# Categories that support create/delete operations, mapped to their rel_path.
_EDITABLE_CATEGORIES: dict[str, str] = {
    "Personas": "personas",
    "Stacks": "stacks",
    "Shared Templates": "templates",
    "Workflows": "workflows",
    "Claude Commands": "claude/commands",
    "Claude Skills": "claude/skills",
    "Claude Hooks": "claude/hooks",
}

# ---------------------------------------------------------------------------
# Starter templates for new assets
# ---------------------------------------------------------------------------

STARTER_COMMAND = """\
# /{name} Command

## Purpose

Describe what this command does.

## Usage

```
/{name} [arguments]
```

## Inputs

| Input | Source | Required |
|-------|--------|----------|
| | | |

## Process

1. Step one
2. Step two

## Output

Describe the expected output.
"""

STARTER_SKILL = """\
# Skill: {name}

## Description

Describe the skill purpose.

## Trigger

- Invoked by the `/{slug}` slash command.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| | | | |

## Process

1. Step one
2. Step two

## Outputs

Describe the outputs.

## Error Conditions

- Describe error scenarios.
"""

STARTER_HOOK = """\
# Hook Pack: {name}

## Purpose

Describe what this hook pack enforces.

## Hooks

| Hook Name | Trigger | Check | Pass Criteria | Fail Action |
|-----------|---------|-------|---------------|-------------|
| | | | | |

## Configuration

- **Default mode:** enforcing
- **Timeout:** 60 seconds per hook

## Posture Compatibility

| Posture | Included | Default Mode |
|---------|----------|--------------|
| strict | Yes | enforcing |
| standard | Yes | enforcing |
| relaxed | No | — |
"""

STARTER_WORKFLOW = """\
# {name}

## Overview

Describe the workflow or reference document.

## Details

Add content here.
"""

STARTER_STACK_CONVENTIONS = """\
# {name} Stack Conventions

Conventions for {name} projects. Deviations require an ADR with justification.

---

## Defaults

| Concern | Default Tool / Approach |
|---------|------------------------|
| | |

---

## Do / Don't

| Do | Don't |
|----|-------|
| | |

---

## Common Pitfalls

- Describe common pitfalls here.

## Checklist

- [ ] Item one
- [ ] Item two
"""

STARTER_STACK_FILE = """\
# {name}

## Overview

Describe the topic covered by this file.

## Guidelines

- Guideline one
- Guideline two
"""

STARTER_TEMPLATE = """\
# {name}

| Field | Value |
|-------|-------|
| **Category** | |
| **Version** | 1.0 |

## Purpose

Describe what this template is used for.

## Content

[Add template content here]

## Checklist

- [ ] Item one
- [ ] Item two
- [ ] Item three

## Definition of Done

- [ ] Template reviewed
- [ ] Fields populated
- [ ] Checklist completed
"""

STARTER_PERSONA = """\
# Persona: {name}

## Mission

Define the core mission and purpose for this persona. What is this team member
responsible for delivering? What is their primary area of expertise?

## Scope

**Does:**
- List the responsibilities this persona owns
- Define the tasks they are expected to perform
- Clarify the boundaries of their authority

**Does not:**
- List responsibilities that belong to other personas
- Define what this persona should defer or escalate

## Operating Principles

- **Principle one.** Describe a key operating principle for this persona.
- **Principle two.** Describe another guiding behavior.

## Inputs I Expect

- Task assignments with clear objectives and acceptance criteria
- Relevant context documents and specifications

## Outputs I Produce

- Primary deliverables this persona creates
- Supporting artifacts and documentation

## Definition of Done

- All acceptance criteria are met
- Outputs conform to the project's quality standards
- Work has been reviewed and handed off to the next consumer

## Quality Bar

- Outputs are clear, complete, and actionable
- Work follows established conventions and patterns
"""

STARTER_OUTPUTS = """\
# {name} -- Outputs

This document enumerates every artifact this persona is responsible for
producing, including quality standards and who consumes each deliverable.

---

## 1. Primary Deliverable

| Field              | Value                                              |
|--------------------|----------------------------------------------------|
| **Deliverable**    | Describe the main output                           |
| **Cadence**        | How often is this produced                         |
| **Template**       | Reference template if applicable                   |
| **Format**         | Output format (Markdown, code, etc.)               |

**Description.** Describe what this deliverable is and why it matters.

**Quality Bar:**
- Define quality criteria for this deliverable
- List specific standards that must be met

**Downstream Consumers:** List who uses this output.

---

## Output Format Guidelines

- Define formatting standards for all outputs from this persona.
- Specify any templates or conventions to follow.
"""

STARTER_PROMPTS = """\
# {name} -- Prompts

Curated prompt fragments for instructing or activating this persona.
Each prompt is a self-contained instruction block that can be injected into a
conversation to set context, assign a task, or trigger a specific workflow.

---

## Activation Prompt

> You are the {name} for **{{{{ project_name }}}}**. Your mission is to
> [describe the persona's core mission]. You deliver [key outputs] following
> the project's conventions and quality standards.

---

## Task Prompts

### Produce Primary Deliverable

> Describe the instructions for producing the persona's main output.
> Include quality criteria, conventions to follow, and expected format.

---

## Handoff Prompts

### Hand off to Next Consumer

> Package the deliverable for the next team member. Include: what was
> produced, quality checks performed, and any context the consumer needs.

---

## Quality Check Prompts

### Self-Review

> Before handing off, verify: (1) all acceptance criteria are met;
> (2) outputs follow project conventions; (3) work has been self-reviewed.
"""

_FILENAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def validate_asset_name(name: str) -> str | None:
    """Validate an asset filename (without extension).

    Returns None if valid, or an error message string.
    """
    if not name:
        return "Name cannot be empty."
    if not _FILENAME_RE.match(name):
        return (
            "Use lowercase letters, digits, and hyphens only"
            " (must start with a letter or digit)."
        )
    if len(name) > 60:
        return "Name is too long (max 60 characters)."
    return None


def starter_content(category: str, name: str) -> str:
    """Return starter markdown content for a new asset in the given category."""
    title = name.replace("-", " ").title()
    if category == "Claude Commands":
        return STARTER_COMMAND.format(name=name)
    if category == "Claude Skills":
        return STARTER_SKILL.format(name=title, slug=name)
    if category == "Claude Hooks":
        return STARTER_HOOK.format(name=title)
    if category == "Stacks":
        return STARTER_STACK_CONVENTIONS.format(name=title)
    if category == "Stacks:file":
        return STARTER_STACK_FILE.format(name=title)
    if category in ("Shared Templates", "_persona_template"):
        return STARTER_TEMPLATE.format(name=title)
    return STARTER_WORKFLOW.format(name=title)


def persona_starter_files(name: str) -> dict[str, str]:
    """Return a mapping of filename to starter content for a new persona.

    Creates persona.md, outputs.md, and prompts.md with meaningful placeholder
    content based on the persona name.
    """
    title = name.replace("-", " ").title()
    return {
        "persona.md": STARTER_PERSONA.format(name=title),
        "outputs.md": STARTER_OUTPUTS.format(name=title),
        "prompts.md": STARTER_PROMPTS.format(name=title),
    }


# ---------------------------------------------------------------------------
# Pure tree-building logic (testable without Qt)
# ---------------------------------------------------------------------------

def _build_file_tree(library_root: Path) -> list[dict]:
    """Scan a library directory and return a nested structure for the tree.

    Returns a list of category dicts, each with:
        {"name": str, "children": [{"name": str, "path": str|None, "children": [...]}]}

    Leaf nodes with a file path have ``"path"`` set; directories have ``"path": None``.
    """
    if not library_root.is_dir():
        return []

    categories: list[dict] = []
    for display_name, rel_path in LIBRARY_CATEGORIES:
        cat_dir = library_root / rel_path
        if not cat_dir.is_dir():
            categories.append({"name": display_name, "children": []})
            continue

        children = _scan_dir(cat_dir)
        categories.append({"name": display_name, "children": children})

    return categories


def _scan_dir(directory: Path) -> list[dict]:
    """Recursively scan a directory, returning sorted children."""
    children: list[dict] = []
    for entry in sorted(directory.iterdir()):
        if entry.name.startswith("."):
            continue
        if entry.is_dir():
            sub_children = _scan_dir(entry)
            children.append({
                "name": entry.name,
                "path": None,
                "children": sub_children,
            })
        elif entry.is_file():
            children.append({
                "name": entry.name,
                "path": str(entry),
                "children": [],
            })
    return children


# ---------------------------------------------------------------------------
# LibraryManagerScreen
# ---------------------------------------------------------------------------

class LibraryManagerScreen(QWidget):
    """Screen for browsing the library structure with a tree and markdown editor pane."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG_BASE};")
        self._library_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("Library Manager")
        title.setFont(QFont("", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        subtitle = QLabel("Browse the library hierarchy and edit file contents.")
        subtitle.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(subtitle)

        # Splitter: tree (left) + editor (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {BG_SURFACE};
                width: 2px;
            }}
        """)

        # Left pane: toolbar + tree
        left_pane = QWidget()
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(4)

        # Action toolbar for create/delete
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        _btn_style = f"""
            QPushButton {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {BG_BASE};
            }}
            QPushButton:disabled {{
                color: {TEXT_SECONDARY};
            }}
        """

        self._new_btn = QPushButton("New...")
        self._new_btn.setToolTip("Create a new library asset")
        self._new_btn.setStyleSheet(_btn_style)
        self._new_btn.setEnabled(False)
        self._new_btn.clicked.connect(self._on_new_asset)
        toolbar.addWidget(self._new_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setToolTip("Delete the selected library asset")
        self._delete_btn.setStyleSheet(_btn_style)
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._on_delete_asset)
        toolbar.addWidget(self._delete_btn)

        toolbar.addStretch()
        left_layout.addLayout(toolbar)

        # Tree view
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: 4px;
                font-size: 13px;
                padding: 4px;
            }}
            QTreeWidget::item {{
                padding: 4px 8px;
            }}
            QTreeWidget::item:selected {{
                background-color: {BG_BASE};
                color: {ACCENT_PRIMARY};
            }}
            QTreeWidget::branch {{
                background-color: {BG_SURFACE};
            }}
        """)
        self._tree.currentItemChanged.connect(self._on_item_selected)
        left_layout.addWidget(self._tree, stretch=1)

        splitter.addWidget(left_pane)

        # Editor pane (replaces the old read-only preview)
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(4)

        self._file_label = QLabel("")
        self._file_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        editor_layout.addWidget(self._file_label)

        self._editor = MarkdownEditor()
        editor_layout.addWidget(self._editor, stretch=1)
        splitter.addWidget(editor_container)

        # Default split: 1/3 tree, 2/3 editor
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, stretch=1)

        # Empty state message (shown when no library configured)
        self._empty_label = QLabel(
            "No library path configured.\n\n"
            "Go to Settings to set your library root directory."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 14px;")
        self._empty_label.setWordWrap(True)
        layout.addWidget(self._empty_label)
        self._empty_label.hide()

        self._splitter = splitter

    # -- Public API --------------------------------------------------------

    @property
    def tree(self) -> QTreeWidget:
        return self._tree

    @property
    def editor_widget(self) -> MarkdownEditor:
        """The markdown editor widget."""
        return self._editor

    @property
    def preview(self) -> MarkdownEditor:
        """Backward-compatible alias for the editor widget."""
        return self._editor

    @property
    def file_label(self) -> QLabel:
        return self._file_label

    @property
    def empty_label(self) -> QLabel:
        return self._empty_label

    @property
    def new_button(self) -> QPushButton:
        return self._new_btn

    @property
    def delete_button(self) -> QPushButton:
        return self._delete_btn

    def set_library_root(self, root: str | Path) -> None:
        """Set the library root directory and refresh the tree."""
        self._library_root = Path(root) if root else None
        self.refresh_tree()

    def refresh_tree(self) -> None:
        """Rebuild the tree from the library directory."""
        self._tree.clear()
        self._editor.clear()
        self._file_label.setText("")

        if self._library_root is None or not self._library_root.is_dir():
            self._splitter.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._splitter.show()

        categories = _build_file_tree(self._library_root)
        for cat in categories:
            cat_item = QTreeWidgetItem([cat["name"]])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, None)
            self._tree.addTopLevelItem(cat_item)
            style = "shared" if cat["name"] == "Shared Templates" else None
            self._add_children(
                cat_item, cat.get("children", []), template_style=style
            )

    def showEvent(self, event) -> None:  # noqa: N802
        """Auto-refresh the tree when the screen becomes visible."""
        super().showEvent(event)
        self.refresh_tree()

    # -- Internal ----------------------------------------------------------

    def _add_children(
        self,
        parent: QTreeWidgetItem,
        children: list[dict],
        template_style: str | None = None,
    ) -> None:
        """Recursively add child items to a tree node.

        *template_style* applies visual distinction: "shared" renders
        items in accent colour with italic font.
        """
        for child in children:
            item = QTreeWidgetItem([child["name"]])
            item.setData(0, Qt.ItemDataRole.UserRole, child.get("path"))

            # Visual distinction for shared templates (italic + accent colour)
            if template_style == "shared":
                item.setForeground(0, QColor(ACCENT_PRIMARY))
                font = item.font(0)
                font.setItalic(True)
                item.setFont(0, font)

            parent.addChild(item)

            # Auto-detect persona template subtrees
            child_style = template_style
            if (
                template_style is None
                and child["name"] == "templates"
                and child.get("path") is None
            ):
                child_style = "persona"

            self._add_children(
                item, child.get("children", []), template_style=child_style
            )

    def _on_item_selected(self, current: QTreeWidgetItem | None, _prev) -> None:
        """Load the file into the editor when a file node is selected."""
        self._update_button_state(current)

        if current is None:
            self._editor.clear()
            self._file_label.setText("")
            return

        file_path = current.data(0, Qt.ItemDataRole.UserRole)
        if file_path is None:
            self._editor.clear()
            self._file_label.setText("")
            return

        path = Path(file_path)
        if not path.is_file():
            self._editor.load_content("File not found.")
            self._file_label.setText(str(path))
            return

        self._editor.load_file(path)
        self._file_label.setText(str(path))

    def _get_category_for_item(self, item: QTreeWidgetItem | None) -> str | None:
        """Walk up from *item* to the top-level category and return its name."""
        if item is None:
            return None
        node = item
        while node.parent() is not None:
            node = node.parent()
        return node.text(0)


    def _is_template_context(self, item: QTreeWidgetItem | None) -> bool:
        """Return True if *item* sits inside a template-editable subtree."""
        if item is None:
            return False
        cat = self._get_category_for_item(item)
        if cat == "Shared Templates":
            return True
        if cat == "Personas":
            node = item
            while node is not None:
                if (
                    node.text(0) == "templates"
                    and node.data(0, Qt.ItemDataRole.UserRole) is None
                    and node.parent() is not None
                ):
                    return True
                node = node.parent()
        return False

    def _reconstruct_item_path(self, item: QTreeWidgetItem) -> Path | None:
        """Reconstruct the filesystem path for a directory tree item."""
        if self._library_root is None:
            return None
        parts: list[str] = []
        node = item
        while node.parent() is not None:
            parts.append(node.text(0))
            node = node.parent()
        cat_name = node.text(0)
        if not parts:
            for display_name, rel_path in LIBRARY_CATEGORIES:
                if display_name == cat_name:
                    return self._library_root / rel_path
            return None
        parts.reverse()
        for display_name, rel_path in LIBRARY_CATEGORIES:
            if display_name == cat_name:
                return self._library_root / rel_path / Path(*parts)
        return None

    def _resolve_template_dir(self, item: QTreeWidgetItem | None) -> Path | None:
        """Return the target directory for a template create/delete, or None."""
        if not self._is_template_context(item) or self._library_root is None:
            return None
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            return Path(file_path).parent
        return self._reconstruct_item_path(item)

    def _update_button_state(self, item: QTreeWidgetItem | None) -> None:
        """Enable/disable New and Delete based on the selected item."""
        cat = self._get_category_for_item(item)
        in_template = self._is_template_context(item)
        editable = cat in _EDITABLE_CATEGORIES or in_template
        self._new_btn.setEnabled(editable)

        # Delete is enabled only when a file leaf in an editable category is selected
        has_file = (
            item is not None
            and item.data(0, Qt.ItemDataRole.UserRole) is not None
        )
        # For skills/stacks/personas, also allow deleting the directory node
        is_asset_dir = (
            cat in ("Claude Skills", "Stacks", "Personas")
            and item is not None
            and item.parent() is not None
            and item.data(0, Qt.ItemDataRole.UserRole) is None
            and item.parent().parent() is None  # direct child of top-level
        )
        self._delete_btn.setEnabled(editable and (has_file or is_asset_dir))

    # -- Stack helpers -----------------------------------------------------

    def _is_stack_subitem(self, item: QTreeWidgetItem | None) -> bool:
        """Return True if *item* is inside a specific stack (dir or file).

        A stack subitem is a node under the Stacks category whose parent is
        *not* the top-level category node itself -- i.e. it sits inside one
        of the stack directories.
        """
        if item is None:
            return False
        cat = self._get_category_for_item(item)
        if cat != "Stacks":
            return False
        return item.parent() is not None and item.parent().parent() is not None

    def _get_stack_dir_for_item(self, item: QTreeWidgetItem) -> Path | None:
        """Return the filesystem path of the stack directory for *item*.

        Walks up to the stack-directory node (direct child of the Stacks
        category) and resolves the path.
        """
        if self._library_root is None:
            return None
        cat = self._get_category_for_item(item)
        if cat != "Stacks":
            return None

        node = item
        while node.parent() is not None and node.parent().parent() is not None:
            node = node.parent()

        if node.parent() is None:
            return None  # category node itself

        rel_path = _EDITABLE_CATEGORIES["Stacks"]
        return self._library_root / rel_path / node.text(0)

    # -- Create / Delete operations ----------------------------------------

    def _on_new_asset(self) -> None:
        """Prompt user for a name and create a new asset file or directory."""
        item = self._tree.currentItem()
        cat = self._get_category_for_item(item)
        in_template = self._is_template_context(item)

        if self._library_root is None:
            return
        if cat not in _EDITABLE_CATEGORIES and not in_template:
            return

        # Route to template creation when in a template subtree
        if in_template:
            tpl_dir = self._resolve_template_dir(item)
            if tpl_dir is not None:
                self._create_template(tpl_dir)
            return

        # Determine whether we are adding a file *inside* an existing stack
        adding_to_stack = cat == "Stacks" and self._is_stack_subitem(item)

        if adding_to_stack:
            prompt_title = "New Stack File"
            prompt_label = "Enter filename (lowercase, hyphens, no extension):"
        elif cat == "Stacks":
            prompt_title = "New Stack"
            prompt_label = "Enter stack name (lowercase, hyphens):"
        else:
            label = {
                "Personas": "persona",
                "Workflows": "workflow",
                "Claude Commands": "command",
                "Claude Skills": "skill",
                "Claude Hooks": "hook pack",
            }.get(cat, "file")
            prompt_title = f"New {label.title()}"
            prompt_label = f"Enter {label} name (lowercase, hyphens):"

        name, ok = QInputDialog.getText(
            self, prompt_title, prompt_label,
        )
        if not ok or not name:
            return

        name = name.strip()
        error = validate_asset_name(name)
        if error:
            QMessageBox.warning(self, "Invalid Name", error)
            return

        rel_path = _EDITABLE_CATEGORIES[cat]
        target_dir = self._library_root / rel_path

        # Personas: create directory with starter files
        if cat == "Personas":
            persona_dir = target_dir / name
            if persona_dir.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"Persona '{name}' already exists."
                )
                return
            persona_dir.mkdir(parents=True, exist_ok=True)
            (persona_dir / "templates").mkdir(exist_ok=True)
            for filename, content in persona_starter_files(name).items():
                (persona_dir / filename).write_text(content, encoding="utf-8")
            logger.info("Created persona %s", persona_dir)
            self.refresh_tree()
            return

        # --- Stack: add file to existing stack ---
        if adding_to_stack:
            stack_dir = self._get_stack_dir_for_item(item)
            if stack_dir is None:
                return
            dest = stack_dir / f"{name}.md"
            if dest.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"File '{name}.md' already exists."
                )
                return
            content = starter_content("Stacks:file", name)
            dest.write_text(content, encoding="utf-8")
            logger.info("Created %s", dest)
            self.refresh_tree()
            return

        # --- Stack: create new stack directory with conventions.md ---
        if cat == "Stacks":
            stack_dir = target_dir / name
            if stack_dir.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"Stack '{name}' already exists."
                )
                return
            stack_dir.mkdir(parents=True, exist_ok=True)
            dest = stack_dir / "conventions.md"
            content = starter_content("Stacks", name)
            dest.write_text(content, encoding="utf-8")
            logger.info("Created stack %s", stack_dir)
            self.refresh_tree()
            return

        # Skills: create directory with SKILL.md
        if cat == "Claude Skills":
            dest = target_dir / name / "SKILL.md"
            if dest.parent.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"Skill '{name}' already exists."
                )
                return
            dest.parent.mkdir(parents=True, exist_ok=True)
        else:
            dest = target_dir / f"{name}.md"
            if dest.exists():
                QMessageBox.warning(
                    self, "Duplicate", f"File '{name}.md' already exists."
                )
                return
            dest.parent.mkdir(parents=True, exist_ok=True)

        content = starter_content(cat, name)
        dest.write_text(content, encoding="utf-8")
        logger.info("Created %s", dest)
        self.refresh_tree()


    def _create_template(self, target_dir: Path) -> None:
        """Prompt user and create a new template file in *target_dir*."""
        name, ok = QInputDialog.getText(
            self, "New Template", "Enter template name (lowercase, hyphens):"
        )
        if not ok or not name:
            return
        name = name.strip()
        error = validate_asset_name(name)
        if error:
            QMessageBox.warning(self, "Invalid Name", error)
            return
        dest = target_dir / f"{name}.md"
        if dest.exists():
            QMessageBox.warning(
                self, "Duplicate", f"Template '{name}.md' already exists."
            )
            return
        target_dir.mkdir(parents=True, exist_ok=True)
        content = starter_content("_persona_template", name)
        dest.write_text(content, encoding="utf-8")
        logger.info("Created template %s", dest)
        self.refresh_tree()

    def _on_delete_asset(self) -> None:
        """Delete the selected file (or asset directory) after confirmation."""
        item = self._tree.currentItem()
        if item is None:
            return

        cat = self._get_category_for_item(item)
        in_template = self._is_template_context(item)
        if cat not in _EDITABLE_CATEGORIES and not in_template:
            return

        file_path = item.data(0, Qt.ItemDataRole.UserRole)

        # Asset directory node (no path, direct child of category)
        is_asset_dir = (
            cat in ("Claude Skills", "Stacks", "Personas")
            and file_path is None
            and item.parent() is not None
            and item.parent().parent() is None
        )

        if file_path:
            path = Path(file_path)
            display = path.name
        elif is_asset_dir:
            rel_path = _EDITABLE_CATEGORIES[cat]
            path = self._library_root / rel_path / item.text(0)
            display = item.text(0)
        else:
            return

        if cat == "Personas" and is_asset_dir:
            msg = (
                f"Delete persona '{display}' and all its files? "
                "This cannot be undone."
            )
        else:
            msg = f"Delete '{display}'? This cannot be undone."

        answer = QMessageBox.question(
            self,
            "Confirm Delete",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        resolved = path.resolve()
        if not resolved.is_relative_to(self._library_root.resolve()):
            logger.error("Refusing to delete path outside library root: %s", resolved)
            QMessageBox.critical(self, "Error", "Cannot delete: path is outside library root.")
            return

        if path.is_dir():
            shutil.rmtree(path)
            logger.info("Deleted directory %s", path)
        elif path.is_file():
            path.unlink()
            logger.info("Deleted %s", path)

        self.refresh_tree()
