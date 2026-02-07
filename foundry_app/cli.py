"""Foundry CLI: batch/scripting entry point for headless project generation.

Usage examples:
    foundry-cli generate composition.yml --library ./ai-team-library
    foundry-cli generate composition.yml --library ./ai-team-library --output ./my-project
    foundry-cli validate composition.yml --library ./ai-team-library
    foundry-cli export ./generated-projects/my-proj ./releases/my-proj --mode copy --git-init
    foundry-cli info ./generated-projects/my-proj
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="foundry-cli",
        description="Foundry CLI — generate Claude Code projects from compositions.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # -- generate ----------------------------------------------------------
    gen = sub.add_parser("generate", help="Run the generation pipeline")
    gen.add_argument(
        "composition",
        type=Path,
        help="Path to a composition.yml file",
    )
    gen.add_argument(
        "--library", "-l",
        type=Path,
        required=True,
        help="Path to the ai-team-library root",
    )
    gen.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Override the output directory (default: from composition spec)",
    )
    gen.add_argument(
        "--strictness", "-s",
        choices=["light", "standard", "strict"],
        default=None,
        help="Validation strictness (default: from settings or 'standard')",
    )

    # -- validate ----------------------------------------------------------
    val = sub.add_parser("validate", help="Validate a composition without generating")
    val.add_argument(
        "composition",
        type=Path,
        help="Path to a composition.yml file",
    )
    val.add_argument(
        "--library", "-l",
        type=Path,
        required=True,
        help="Path to the ai-team-library root",
    )
    val.add_argument(
        "--strictness", "-s",
        choices=["light", "standard", "strict"],
        default=None,
        help="Validation strictness (default: from settings or 'standard')",
    )

    # -- export ------------------------------------------------------------
    exp = sub.add_parser("export", help="Export a generated project to a destination")
    exp.add_argument(
        "project_dir",
        type=Path,
        help="Path to the generated project directory",
    )
    exp.add_argument(
        "destination",
        type=Path,
        help="Destination path for the exported project",
    )
    exp.add_argument(
        "--mode", "-m",
        choices=["copy", "move"],
        default="copy",
        help="Export mode: copy (default) or move",
    )
    exp.add_argument(
        "--git-init",
        action="store_true",
        default=False,
        help="Run 'git init' in the destination after export",
    )
    exp.add_argument(
        "--validate",
        action="store_true",
        default=False,
        help="Run pre-export validation on the project before exporting",
    )

    # -- info --------------------------------------------------------------
    inf = sub.add_parser("info", help="Show generation manifest info for a project")
    inf.add_argument(
        "project_dir",
        type=Path,
        help="Path to a generated project directory",
    )

    # -- diff --------------------------------------------------------------
    diff = sub.add_parser("diff", help="Display the diff report for a generated project")
    diff.add_argument(
        "project_dir",
        type=Path,
        help="Path to a generated project directory",
    )

    return parser


def _resolve_strictness(args: argparse.Namespace) -> str:
    """Resolve validation strictness: CLI flag > settings > default."""
    if args.strictness is not None:
        return args.strictness
    from foundry_app.core.settings import load_settings
    return load_settings().validation_strictness or "standard"


def _cmd_generate(args: argparse.Namespace) -> int:
    """Run the full generation pipeline."""
    from foundry_app.io.composition_io import load_composition
    from foundry_app.services.generator import generate_project

    comp_path: Path = args.composition
    library_root: Path = args.library
    output_override: Path | None = args.output
    strictness: str = _resolve_strictness(args)

    if not comp_path.is_file():
        print(f"Error: Composition file not found: {comp_path}", file=sys.stderr)
        return 1

    if not library_root.is_dir():
        print(f"Error: Library root is not a directory: {library_root}", file=sys.stderr)
        return 1

    print(f"Loading composition from {comp_path}...")
    composition = load_composition(comp_path)
    print(f"  Project: {composition.project.name} ({composition.project.slug})")
    print(f"  Stacks: {', '.join(s.id for s in composition.stacks) or '(none)'}")
    print(f"  Personas: {', '.join(p.id for p in composition.team.personas) or '(none)'}")

    print(f"Running generation pipeline (library: {library_root}, strictness: {strictness})...")
    manifest, validation = generate_project(
        composition, library_root, output_override, strictness
    )

    if not validation.is_valid:
        print("Validation FAILED:", file=sys.stderr)
        for err in validation.errors:
            print(f"  ERROR: {err}", file=sys.stderr)
        for warn in validation.warnings:
            print(f"  WARNING: {warn}", file=sys.stderr)
        return 1

    # Report results
    total_files = 0
    total_warnings = 0
    for stage_name, stage_result in manifest.stages.items():
        n_files = len(stage_result.wrote)
        n_warns = len(stage_result.warnings)
        total_files += n_files
        total_warnings += n_warns
        status = f"{n_files} file(s)"
        if n_warns:
            status += f", {n_warns} warning(s)"
        print(f"  {stage_name}: {status}")

    # Determine output path for display
    if output_override:
        output_path = output_override
    else:
        folder = composition.project.output_folder or composition.project.slug
        output_path = Path(composition.project.output_root) / folder

    print("\nGeneration complete!")
    print(f"  Output: {output_path}")
    print(f"  Total files: {total_files}")
    if total_warnings:
        print(f"  Total warnings: {total_warnings}")

    if validation.warnings:
        for warn in validation.warnings:
            print(f"  WARNING: {warn}")

    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Validate a composition without generating."""
    from foundry_app.io.composition_io import load_composition
    from foundry_app.services.validator import run_pre_generation_validation

    comp_path: Path = args.composition
    library_root: Path = args.library
    strictness: str = _resolve_strictness(args)

    if not comp_path.is_file():
        print(f"Error: Composition file not found: {comp_path}", file=sys.stderr)
        return 1

    if not library_root.is_dir():
        print(f"Error: Library root is not a directory: {library_root}", file=sys.stderr)
        return 1

    print(f"Loading composition from {comp_path}...")
    composition = load_composition(comp_path)
    print(f"  Project: {composition.project.name} ({composition.project.slug})")

    print(f"Validating against library: {library_root} (strictness: {strictness})...")
    result = run_pre_generation_validation(composition, library_root, strictness)

    if result.errors:
        for err in result.errors:
            print(f"  ERROR: {err}", file=sys.stderr)

    if result.warnings:
        for warn in result.warnings:
            print(f"  WARNING: {warn}")

    if result.is_valid:
        print("Validation PASSED.")
        return 0
    else:
        print("Validation FAILED.", file=sys.stderr)
        return 1


def _cmd_export(args: argparse.Namespace) -> int:
    """Export a generated project to a destination directory."""
    from foundry_app.services.export import export_project, validate_generated_project

    project_dir: Path = args.project_dir
    destination: Path = args.destination
    mode: str = args.mode
    git_init: bool = args.git_init
    validate: bool = args.validate

    if not project_dir.is_dir():
        print(f"Error: Source directory does not exist: {project_dir}", file=sys.stderr)
        return 1

    # Optional pre-export validation
    if validate:
        print(f"Validating project at {project_dir}...")
        errors = validate_generated_project(project_dir)
        if errors:
            print("Validation FAILED:", file=sys.stderr)
            for err in errors:
                print(f"  ERROR: {err}", file=sys.stderr)
            return 1
        print("Validation passed.")

    print(f"Exporting project ({mode}) to {destination}...")
    result = export_project(project_dir, destination, mode=mode, git_init=git_init)

    for warn in result.warnings:
        print(f"  WARNING: {warn}")

    print(f"Export complete: {result.destination}")
    if result.git_initialized:
        print("  git repository initialized.")
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    """Display generation manifest info for a project."""
    from foundry_app.core.models import GenerationManifest

    project_dir: Path = args.project_dir
    manifest_path = project_dir / "ai" / "generated" / "manifest.json"

    if not manifest_path.is_file():
        print(
            f"Error: Manifest not found: {manifest_path}",
            file=sys.stderr,
        )
        return 1

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = GenerationManifest.model_validate(data)

    # Project identity
    if manifest.composition_snapshot:
        proj = manifest.composition_snapshot.project
        print(f"Project: {proj.name} ({proj.slug})")
    else:
        print("Project: (no composition snapshot)")

    # Timestamp
    print(f"Generated: {manifest.run_id}")

    # Stages
    total_files = 0
    if manifest.stages:
        print("Stages:")
        for stage_name, stage_result in manifest.stages.items():
            n_files = len(stage_result.wrote)
            total_files += n_files
            print(f"  {stage_name}: {n_files} file(s)")
    else:
        print("Stages: (none)")

    print(f"Total files written: {total_files}")
    return 0


def _cmd_diff(args: argparse.Namespace) -> int:
    """Display the diff report for a generated project."""
    project_dir: Path = args.project_dir
    report_path = project_dir / "ai" / "generated" / "diff-report.md"

    if not report_path.is_file():
        print(
            f"Error: Diff report not found: {report_path}",
            file=sys.stderr,
        )
        return 1

    print(report_path.read_text(encoding="utf-8"))
    return 0


def cli_main() -> None:
    """CLI entry point."""
    from foundry_app.core.logging import setup_logging

    setup_logging(console=False)

    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "generate":
        sys.exit(_cmd_generate(args))
    elif args.command == "validate":
        sys.exit(_cmd_validate(args))
    elif args.command == "export":
        sys.exit(_cmd_export(args))
    elif args.command == "info":
        sys.exit(_cmd_info(args))
    elif args.command == "diff":
        sys.exit(_cmd_diff(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
