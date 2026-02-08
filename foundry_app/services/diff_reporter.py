"""Diff reporter service — generates a diff-report.md for overlay re-generation."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from foundry_app.core.models import OverlayPlan, StageResult

logger = logging.getLogger(__name__)


def write_diff_report(plan: OverlayPlan, output_dir: str | Path) -> StageResult:
    """Generate a human-readable ``diff-report.md`` summarising overlay changes.

    The report groups file actions by type (creates, updates, deletes, skips)
    with counts and path lists.

    Args:
        plan: The overlay plan computed by the generator.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing the report file and any warnings.
    """
    root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    creates = plan.creates
    updates = plan.updates
    deletes = plan.deletes
    skips = plan.skips

    lines: list[str] = [
        "# Diff Report",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        "| Action | Count |",
        "|--------|-------|",
        f"| Created | {len(creates)} |",
        f"| Updated | {len(updates)} |",
        f"| Deleted | {len(deletes)} |",
        f"| Skipped (unchanged) | {len(skips)} |",
        f"| **Total** | **{len(plan.actions)}** |",
        "",
    ]

    if creates:
        lines.append("## Created Files")
        lines.append("")
        for action in creates:
            lines.append(f"- `{action.path}`")
        lines.append("")

    if updates:
        lines.append("## Updated Files")
        lines.append("")
        for action in updates:
            lines.append(f"- `{action.path}`")
        lines.append("")

    if deletes:
        lines.append("## Deleted Files")
        lines.append("")
        for action in deletes:
            lines.append(f"- `{action.path}`")
        lines.append("")

    if skips:
        lines.append("## Skipped Files (unchanged)")
        lines.append("")
        for action in skips:
            lines.append(f"- `{action.path}`")
        lines.append("")

    if not plan.actions:
        lines.append("No changes detected.")
        lines.append("")

    report_path = root / "diff-report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    rel_path = str(report_path.relative_to(root))
    wrote.append(rel_path)

    logger.info(
        "Diff report written: %d creates, %d updates, %d deletes, %d skips",
        len(creates),
        len(updates),
        len(deletes),
        len(skips),
    )

    return StageResult(wrote=wrote, warnings=warnings)
