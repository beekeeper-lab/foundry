"""Command-line interface for Foundry project generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from foundry_app.core.models import Strictness

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_GENERATION_ERROR = 2


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="foundry-cli",
        description="Generate Claude Code project folders from reusable building blocks.",
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a project from a composition YAML file")
    gen.add_argument(
        "composition",
        type=str,
        help="Path to the composition YAML file",
    )
    gen.add_argument(
        "--library",
        type=str,
        default="ai-team-library",
        help="Path to the library directory (default: ai-team-library)",
    )
    gen.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: derived from composition spec)",
    )
    gen.add_argument(
        "--overlay",
        action="store_true",
        default=False,
        help="Use overlay mode for re-generation",
    )
    gen.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Compute overlay plan without applying (requires --overlay)",
    )
    gen.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Proceed even when validation produces errors",
    )
    gen.add_argument(
        "--strictness",
        type=str,
        choices=["light", "standard", "strict"],
        default="standard",
        help="Validation strictness level (default: standard)",
    )

    return parser


def _run_generate(args: argparse.Namespace) -> int:
    """Execute the generate command."""
    from pydantic import ValidationError

    from foundry_app.io.composition_io import load_composition
    from foundry_app.services.generator import generate_project

    if args.dry_run and not args.overlay:
        print("Error: --dry-run requires --overlay", file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    comp_path = Path(args.composition)
    if not comp_path.is_file():
        print(f"Error: composition file not found: {comp_path}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    library_path = Path(args.library)
    if not library_path.is_dir():
        print(f"Error: library directory not found: {library_path}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    # Load composition
    try:
        composition = load_composition(comp_path)
    except ValidationError as exc:
        print(f"Validation error in composition: {exc}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR
    except Exception as exc:
        print(f"Error loading composition: {exc}", file=sys.stderr)
        return EXIT_VALIDATION_ERROR

    strictness = Strictness(args.strictness)

    print(f"Generating project: {composition.project.name}")
    print(f"  Library: {library_path}")
    print(f"  Strictness: {strictness.value}")
    if args.overlay:
        print(f"  Mode: overlay{' (dry-run)' if args.dry_run else ''}")
    if args.force:
        print("  Force: yes")

    # Generate
    try:
        manifest, validation, overlay_plan = generate_project(
            composition=composition,
            library_root=library_path,
            output_root=args.output,
            strictness=strictness,
            overlay=args.overlay,
            dry_run=args.dry_run,
            force=args.force,
        )
    except Exception as exc:
        print(f"Generation error: {exc}", file=sys.stderr)
        return EXIT_GENERATION_ERROR

    # Report validation results
    if validation.errors:
        print(f"\nValidation errors ({len(validation.errors)}):")
        for msg in validation.errors:
            print(f"  [{msg.code}] {msg.message}")
        if not args.force:
            print("\nGeneration aborted due to validation errors.")
            print("Use --force to proceed anyway.")
            return EXIT_VALIDATION_ERROR

    if validation.warnings:
        print(f"\nValidation warnings ({len(validation.warnings)}):")
        for msg in validation.warnings:
            print(f"  [{msg.code}] {msg.message}")

    # Report results
    print(f"\nGeneration complete: run_id={manifest.run_id}")
    print(f"  Files written: {manifest.total_files_written}")

    if manifest.all_warnings:
        print(f"  Warnings: {len(manifest.all_warnings)}")
        for w in manifest.all_warnings:
            print(f"    - {w}")

    if overlay_plan is not None:
        print("\nOverlay plan:")
        print(f"  Creates: {len(overlay_plan.creates)}")
        print(f"  Updates: {len(overlay_plan.updates)}")
        print(f"  Deletes: {len(overlay_plan.deletes)}")
        print(f"  Skipped: {len(overlay_plan.skips)}")
        if overlay_plan.dry_run:
            print("  (dry-run — no changes applied)")

    return EXIT_SUCCESS


def main(argv: list[str] | None = None) -> int:
    """Entry point for the foundry-cli command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return EXIT_SUCCESS

    if args.command == "generate":
        return _run_generate(args)

    parser.print_help()
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
