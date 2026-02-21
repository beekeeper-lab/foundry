"""Subtree setup service — initializes a git subtree for .claude/ in a generated project."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from foundry_app.core.models import StageResult

logger = logging.getLogger(__name__)

_GIT_TIMEOUT = 30


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command in the given directory."""
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=_GIT_TIMEOUT,
    )


def setup_subtree(
    claude_kit_url: str,
    output_dir: str | Path,
) -> StageResult:
    """Set up a git subtree for .claude/ in the output directory.

    Steps:
    1. Initialize a git repo if the output directory isn't one already.
    2. Make an initial commit if the repo has no commits (subtree add requires one).
    3. Add the claude-kit remote.
    4. Fetch and add the subtree.

    Args:
        claude_kit_url: Git URL for the claude-kit repository.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    out = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    try:
        # Step 1: Ensure git repo exists
        if not (out / ".git").is_dir():
            result = _run_git(["init"], out)
            if result.returncode != 0:
                warnings.append(f"git init failed: {result.stderr.strip()}")
                return StageResult(wrote=wrote, warnings=warnings)
            logger.info("Initialized git repo in %s", out)

        # Step 2: Ensure at least one commit exists (git subtree add requires it)
        result = _run_git(["rev-parse", "HEAD"], out)
        if result.returncode != 0:
            _run_git(["add", "-A"], out)
            result = _run_git(["commit", "-m", "Initial project generation"], out)
            if result.returncode != 0:
                warnings.append(f"Initial commit failed: {result.stderr.strip()}")
                return StageResult(wrote=wrote, warnings=warnings)
            logger.info("Created initial commit for subtree setup")

        # Step 3: Add remote (skip if already exists)
        result = _run_git(["remote", "get-url", "claude-kit"], out)
        if result.returncode != 0:
            result = _run_git(["remote", "add", "claude-kit", claude_kit_url], out)
            if result.returncode != 0:
                warnings.append(f"git remote add failed: {result.stderr.strip()}")
                return StageResult(wrote=wrote, warnings=warnings)
            logger.info("Added claude-kit remote: %s", claude_kit_url)

        # Step 4: Add subtree
        result = _run_git(
            ["subtree", "add", "--prefix=.claude", "claude-kit", "main", "--squash"],
            out,
        )
        if result.returncode != 0:
            warnings.append(f"git subtree add failed: {result.stderr.strip()}")
            return StageResult(wrote=wrote, warnings=warnings)

        # Count files added
        claude_dir = out / ".claude"
        if claude_dir.is_dir():
            for f in claude_dir.rglob("*"):
                if f.is_file():
                    wrote.append(str(f.relative_to(out)))

        logger.info(
            "Subtree setup complete: %d files from claude-kit", len(wrote),
        )

    except subprocess.TimeoutExpired:
        warnings.append("Git command timed out during subtree setup")
    except (subprocess.SubprocessError, OSError) as exc:
        warnings.append(f"Subtree setup error: {exc}")

    return StageResult(wrote=wrote, warnings=warnings)
