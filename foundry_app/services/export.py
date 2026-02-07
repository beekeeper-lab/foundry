"""Export service: copy or move a generated project to a destination directory.

Pure business logic — no Qt/PySide6 dependencies. Usable from both the GUI
and the CLI.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExportResult:
    """Outcome of an export_project() call."""

    destination: Path = field(default_factory=lambda: Path())
    warnings: list[str] = field(default_factory=list)
    git_initialized: bool = False


def export_project(
    src: Path,
    dest: Path,
    mode: str = "copy",
    git_init: bool = False,
) -> ExportResult:
    """Copy or move a project directory to *dest*.

    Args:
        src: Source project directory (must exist).
        dest: Final destination path. If it already exists it will be
              removed first.
        mode: ``"copy"`` (default) uses :func:`shutil.copytree`;
              ``"move"`` uses :func:`shutil.move`.
        git_init: If True, run ``git init`` inside the destination after
                  the copy/move.

    Returns:
        An :class:`ExportResult` with the destination path and any warnings.

    Raises:
        FileNotFoundError: If *src* does not exist.
        ValueError: If *mode* is not ``"copy"`` or ``"move"``.
    """
    if not src.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {src}")

    mode = mode.lower()
    if mode not in ("copy", "move"):
        raise ValueError(f"Invalid mode {mode!r}; expected 'copy' or 'move'.")

    result = ExportResult(destination=dest)

    # Remove existing destination so copytree/move don't clash
    if dest.exists():
        shutil.rmtree(dest)
        result.warnings.append(f"Existing destination removed: {dest}")

    logger.info("Exporting project: %s -> %s (mode=%s)", src, dest, mode)
    if mode == "copy":
        shutil.copytree(src, dest)
    else:
        shutil.move(str(src), str(dest))

    # Optionally initialise a git repo
    if git_init:
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(dest),
                check=True,
                capture_output=True,
                text=True,
            )
            result.git_initialized = True
        except subprocess.CalledProcessError as exc:
            result.warnings.append(
                f"git init failed: {exc.stderr or exc}"
            )

    return result


def check_self_contained(project_dir: Path) -> list[str]:
    """Check that *project_dir* has no symlinks pointing outside its tree.

    Returns:
        A list of warning strings describing each external symlink found.
        An empty list means the project is self-contained.
    """
    warnings: list[str] = []
    try:
        resolved = project_dir.resolve()
        for item in resolved.rglob("*"):
            if item.is_symlink():
                target = item.resolve()
                if not str(target).startswith(str(resolved)):
                    warnings.append(
                        f"External symlink: {item} -> {target}"
                    )
    except OSError as exc:
        warnings.append(f"OS error while scanning: {exc}")
    return warnings


def check_no_symlinks(project_dir: Path) -> list[str]:
    """Check for *any* symlinks inside *project_dir*.

    Returns:
        A list of warning strings, one per symlink found.
        An empty list means there are no symlinks.
    """
    warnings: list[str] = []
    try:
        for item in project_dir.rglob("*"):
            if item.is_symlink():
                warnings.append(f"Symlink found: {item}")
    except OSError as exc:
        warnings.append(f"OS error while scanning: {exc}")
    return warnings


def validate_generated_project(project_dir: Path) -> list[str]:
    """Validate that a generated project has the expected directory structure.

    Checks for:
    - ``CLAUDE.md`` at the project root
    - ``.claude/agents/`` directory with at least one ``.md`` file
    - ``ai/generated/members/`` directory with at least one ``.md`` file

    Returns:
        A list of error strings. An empty list means the project is valid.
    """
    errors: list[str] = []

    if not (project_dir / "CLAUDE.md").is_file():
        errors.append("Missing CLAUDE.md at project root.")

    agents_dir = project_dir / ".claude" / "agents"
    if not agents_dir.is_dir() or not any(agents_dir.glob("*.md")):
        errors.append("No agent definitions found in .claude/agents/")

    members_dir = project_dir / "ai" / "generated" / "members"
    if not members_dir.is_dir() or not any(members_dir.glob("*.md")):
        errors.append("No compiled member prompts in ai/generated/members/")

    return errors
