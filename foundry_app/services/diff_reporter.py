"""Diff reporter: compare successive generation runs.

Produces a human-readable diff-report.md showing what changed between
the previous manifest and the current one (new files, removed files,
stage changes, warning counts).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from foundry_app.core.models import GenerationManifest, StageResult

_GENERATED_DIR = Path("ai") / "generated"
_MANIFEST_NAME = "manifest.json"
_PREVIOUS_MANIFEST_NAME = "previous-manifest.json"
_DIFF_REPORT_NAME = "diff-report.md"


def backup_previous_manifest(project_dir: Path) -> None:
    """Copy the current manifest to previous-manifest.json before generation.

    Call this BEFORE any generation stages overwrite the manifest.
    If no manifest exists yet (first run), this is a no-op.

    Args:
        project_dir: Root directory of the generated project.
    """
    manifest_path = project_dir / _GENERATED_DIR / _MANIFEST_NAME
    if manifest_path.is_file():
        backup_path = project_dir / _GENERATED_DIR / _PREVIOUS_MANIFEST_NAME
        shutil.copy2(manifest_path, backup_path)


def generate_diff_report(
    project_dir: Path,
    current_manifest: GenerationManifest,
) -> StageResult:
    """Generate a diff report comparing the current manifest to the previous one.

    Writes ``diff-report.md`` into the project's ``ai/generated/`` directory.

    Args:
        project_dir: Root directory of the generated project.
        current_manifest: The manifest produced by the current generation run.

    Returns:
        A StageResult listing ``diff-report.md`` in *wrote*.
    """
    result = StageResult()
    generated_dir = project_dir / _GENERATED_DIR
    generated_dir.mkdir(parents=True, exist_ok=True)

    previous_path = generated_dir / _PREVIOUS_MANIFEST_NAME

    if not previous_path.is_file():
        report = _first_run_report(current_manifest)
    else:
        previous_manifest = _load_previous_manifest(previous_path)
        if previous_manifest is None:
            result.warnings.append(
                "Could not parse previous-manifest.json; treating as first run."
            )
            report = _first_run_report(current_manifest)
        else:
            report = _build_diff_report(previous_manifest, current_manifest)

    report_path = generated_dir / _DIFF_REPORT_NAME
    report_path.write_text(report)
    result.wrote.append(_DIFF_REPORT_NAME)

    return result


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_previous_manifest(path: Path) -> GenerationManifest | None:
    """Attempt to load and validate a previous manifest file."""
    try:
        data = json.loads(path.read_text())
        return GenerationManifest.model_validate(data)
    except Exception:  # noqa: BLE001
        return None


def _first_run_report(manifest: GenerationManifest) -> str:
    """Return a simple report when there is no previous run to compare."""
    lines = [
        "# Diff Report",
        "",
        f"**Run:** `{manifest.run_id}`",
        "",
        "First generation — no previous run to compare.",
        "",
    ]
    return "\n".join(lines)


def _collect_all_files(manifest: GenerationManifest) -> set[str]:
    """Return the set of all file paths recorded across every stage."""
    files: set[str] = set()
    for stage_result in manifest.stages.values():
        files.update(stage_result.wrote)
    return files


def _build_diff_report(
    previous: GenerationManifest,
    current: GenerationManifest,
) -> str:
    """Build the full diff-report markdown comparing two manifests."""
    lines: list[str] = [
        "# Diff Report",
        "",
        "## Run Comparison",
        "",
        "| | Previous | Current |",
        "|---|---|---|",
        f"| **run_id** | `{previous.run_id}` | `{current.run_id}` |",
        "",
    ]

    # --- File diff -----------------------------------------------------------
    prev_files = _collect_all_files(previous)
    curr_files = _collect_all_files(current)

    new_files = sorted(curr_files - prev_files)
    removed_files = sorted(prev_files - curr_files)

    lines.append("## New Files")
    lines.append("")
    if new_files:
        for f in new_files:
            lines.append(f"- `{f}`")
    else:
        lines.append("No new files.")
    lines.append("")

    lines.append("## Removed Files")
    lines.append("")
    if removed_files:
        for f in removed_files:
            lines.append(f"- `{f}`")
    else:
        lines.append("No removed files.")
    lines.append("")

    # --- Stage changes -------------------------------------------------------
    prev_stages = set(previous.stages.keys())
    curr_stages = set(current.stages.keys())

    added_stages = sorted(curr_stages - prev_stages)
    removed_stages = sorted(prev_stages - curr_stages)
    common_stages = sorted(curr_stages & prev_stages)

    lines.append("## Stage Changes")
    lines.append("")

    if added_stages:
        lines.append("**Added stages:**")
        for s in added_stages:
            lines.append(f"- `{s}`")
        lines.append("")

    if removed_stages:
        lines.append("**Removed stages:**")
        for s in removed_stages:
            lines.append(f"- `{s}`")
        lines.append("")

    if common_stages:
        lines.append("**Common stages:**")
        for s in common_stages:
            prev_count = len(previous.stages[s].wrote)
            curr_count = len(current.stages[s].wrote)
            delta = curr_count - prev_count
            delta_str = f" ({'+' if delta > 0 else ''}{delta})" if delta != 0 else ""
            lines.append(f"- `{s}`: {curr_count} files{delta_str}")
        lines.append("")

    if not added_stages and not removed_stages and not common_stages:
        lines.append("No stage changes.")
        lines.append("")

    # --- Warning summary -----------------------------------------------------
    prev_warnings = sum(
        len(sr.warnings) for sr in previous.stages.values()
    )
    curr_warnings = sum(
        len(sr.warnings) for sr in current.stages.values()
    )

    lines.append("## Warning Summary")
    lines.append("")
    lines.append("| | Previous | Current |")
    lines.append("|---|---|---|")
    lines.append(f"| **Total warnings** | {prev_warnings} | {curr_warnings} |")
    lines.append("")

    if curr_warnings > 0:
        lines.append("**Current warnings:**")
        lines.append("")
        for stage_name, stage_result in sorted(current.stages.items()):
            for w in stage_result.warnings:
                lines.append(f"- `{stage_name}`: {w}")
        lines.append("")

    return "\n".join(lines)
