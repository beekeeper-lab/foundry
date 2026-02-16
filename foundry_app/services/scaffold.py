"""Scaffold service — creates the directory skeleton for a generated project."""

from __future__ import annotations

import logging
from pathlib import Path

from foundry_app.core.models import CompositionSpec, StageResult

logger = logging.getLogger(__name__)

# Standard directory structure for a Claude Code project
_CLAUDE_DIRS = [
    ".claude/agents",
    ".claude/commands",
    ".claude/hooks",
    ".claude/skills",
]

_AI_DIRS = [
    "ai/context",
    "ai/outputs",
    "ai/beans",
    "ai/tasks",
]


def scaffold_project(
    spec: CompositionSpec,
    output_dir: str | Path,
) -> StageResult:
    """Create the directory skeleton for a generated Claude Code project.

    Creates the standard directory tree based on the composition spec:
    - ``.claude/`` subdirectories (agents, commands, hooks, skills)
    - ``ai/`` subdirectories (context, outputs, beans, tasks)
    - Per-persona output directories under ``ai/outputs/``

    Existing directories are silently skipped (overlay-safe).

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory for the generated project.

    Returns:
        A StageResult listing all directories that were created.
    """
    root = Path(output_dir)
    created: list[str] = []
    warnings: list[str] = []

    # Collect all directories to create
    dirs_to_create: list[Path] = []

    # Project root
    dirs_to_create.append(root)

    # .claude/ directories
    for d in _CLAUDE_DIRS:
        dirs_to_create.append(root / d)

    # ai/ directories
    for d in _AI_DIRS:
        dirs_to_create.append(root / d)

    # Per-persona output directories
    for persona in spec.team.personas:
        dirs_to_create.append(root / "ai" / "outputs" / persona.id)

    # Track which directories already exist so we know what we actually created
    existing = {d for d in dirs_to_create if d.exists()}

    # Create all directories
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        if dir_path not in existing:
            rel = str(dir_path.relative_to(root))
            if dir_path == root:
                rel = "."
            created.append(rel)
            logger.info("Created directory: %s", dir_path)

    if not spec.team.personas:
        warnings.append("No personas selected — no per-persona output directories created")

    logger.info(
        "Scaffold complete: %d directories created, %d warnings",
        len(created),
        len(warnings),
    )

    return StageResult(wrote=created, warnings=warnings)
