"""Tests for foundry_app.cli — command-line interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from foundry_app.cli import (
    EXIT_GENERATION_ERROR,
    EXIT_SUCCESS,
    EXIT_VALIDATION_ERROR,
    _build_parser,
    main,
)
from foundry_app.core.models import (
    GenerationManifest,
    OverlayPlan,
    Severity,
    ValidationMessage,
    ValidationResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_composition(path: Path, **overrides) -> Path:
    """Write a minimal composition YAML file."""
    data = {
        "project": {"name": "Test", "slug": "test"},
        "stacks": [{"id": "python"}],
        "team": {"personas": [{"id": "developer"}]},
    }
    data.update(overrides)
    comp_path = path / "composition.yml"
    comp_path.write_text(yaml.dump(data), encoding="utf-8")
    return comp_path


def _make_library(path: Path) -> Path:
    """Create a minimal library directory."""
    lib = path / "library"
    lib.mkdir()
    return lib


def _mock_generate_result(
    files: int = 5,
    warnings: list[str] | None = None,
    validation_errors: list[ValidationMessage] | None = None,
    validation_warnings: list[ValidationMessage] | None = None,
):
    """Create a mock return value for generate_project."""
    from foundry_app.core.models import StageResult

    manifest = GenerationManifest(
        run_id="20260207-120000",
        stages={"scaffold": StageResult(
            wrote=[f"file{i}.txt" for i in range(files)],
            warnings=warnings or [],
        )},
    )
    messages = list(validation_errors or []) + list(validation_warnings or [])
    validation = ValidationResult(messages=messages)
    return manifest, validation, None


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------


class TestParser:

    def test_generate_subcommand(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml"])
        assert args.command == "generate"
        assert args.composition == "comp.yml"

    def test_default_library(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml"])
        assert args.library == "ai-team-library"

    def test_custom_library(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml", "--library", "/my/lib"])
        assert args.library == "/my/lib"

    def test_overlay_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml", "--overlay"])
        assert args.overlay is True

    def test_dry_run_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml", "--dry-run"])
        assert args.dry_run is True

    def test_force_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml", "--force"])
        assert args.force is True

    def test_strictness_choices(self):
        parser = _build_parser()
        for level in ["light", "standard", "strict"]:
            args = parser.parse_args(["generate", "comp.yml", "--strictness", level])
            assert args.strictness == level

    def test_default_strictness(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml"])
        assert args.strictness == "standard"

    def test_output_flag(self):
        parser = _build_parser()
        args = parser.parse_args(["generate", "comp.yml", "--output", "/out"])
        assert args.output == "/out"


# ---------------------------------------------------------------------------
# main() entry point
# ---------------------------------------------------------------------------


class TestMain:

    def test_no_command_shows_help(self, capsys):
        result = main([])
        assert result == EXIT_SUCCESS

    def test_missing_composition_file(self, tmp_path: Path, capsys):
        lib = _make_library(tmp_path)
        result = main([
            "generate", str(tmp_path / "nonexistent.yml"),
            "--library", str(lib),
        ])
        assert result == EXIT_VALIDATION_ERROR
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_missing_library_dir(self, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        result = main([
            "generate", str(comp),
            "--library", str(tmp_path / "no-such-lib"),
        ])
        assert result == EXIT_VALIDATION_ERROR
        captured = capsys.readouterr()
        assert "not found" in captured.err


# ---------------------------------------------------------------------------
# Generate command
# ---------------------------------------------------------------------------


class TestGenerate:

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_successful_generation(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"
        mock_gen.return_value = _mock_generate_result()

        result = main([
            "generate", str(comp),
            "--library", str(lib),
        ])
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "Generation complete" in captured.out

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_validation_errors_abort(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"
        mock_gen.return_value = _mock_generate_result(
            validation_errors=[
                ValidationMessage(
                    severity=Severity.ERROR,
                    code="missing-persona",
                    message="Persona 'ba' not found",
                ),
            ],
        )

        result = main([
            "generate", str(comp),
            "--library", str(lib),
        ])
        assert result == EXIT_VALIDATION_ERROR
        captured = capsys.readouterr()
        assert "Validation errors" in captured.out
        assert "missing-persona" in captured.out

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_force_bypasses_errors(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"
        mock_gen.return_value = _mock_generate_result(
            validation_errors=[
                ValidationMessage(
                    severity=Severity.ERROR,
                    code="missing-persona",
                    message="Persona 'ba' not found",
                ),
            ],
        )

        result = main([
            "generate", str(comp),
            "--library", str(lib),
            "--force",
        ])
        # With force, generation proceeds even with validation errors
        # The manifest still reports success
        assert result == EXIT_SUCCESS

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_generation_exception(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"
        mock_gen.side_effect = RuntimeError("Disk full")

        result = main([
            "generate", str(comp),
            "--library", str(lib),
        ])
        assert result == EXIT_GENERATION_ERROR
        captured = capsys.readouterr()
        assert "Generation error" in captured.err

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_overlay_plan_reported(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"

        from foundry_app.core.models import FileAction, FileActionType, StageResult

        manifest = GenerationManifest(
            run_id="test",
            stages={"scaffold": StageResult(wrote=["a.txt"])},
        )
        validation = ValidationResult()
        plan = OverlayPlan(actions=[
            FileAction(path="new.py", action=FileActionType.CREATE),
            FileAction(path="old.py", action=FileActionType.DELETE),
        ])
        mock_gen.return_value = (manifest, validation, plan)

        result = main([
            "generate", str(comp),
            "--library", str(lib),
            "--overlay",
        ])
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "Overlay plan" in captured.out
        assert "Creates: 1" in captured.out
        assert "Deletes: 1" in captured.out

    @patch("foundry_app.services.generator.generate_project")
    @patch("foundry_app.io.composition_io.load_composition")
    def test_warnings_displayed(self, mock_load, mock_gen, tmp_path: Path, capsys):
        comp = _write_composition(tmp_path)
        lib = _make_library(tmp_path)

        mock_load.return_value = MagicMock()
        mock_load.return_value.project.name = "Test"
        mock_gen.return_value = _mock_generate_result(
            warnings=["No templates for persona 'ba'"],
            validation_warnings=[
                ValidationMessage(
                    severity=Severity.WARNING,
                    code="no-templates",
                    message="No templates for persona 'ba'",
                ),
            ],
        )

        result = main([
            "generate", str(comp),
            "--library", str(lib),
        ])
        assert result == EXIT_SUCCESS
        captured = capsys.readouterr()
        assert "Validation warnings" in captured.out

    def test_invalid_yaml_composition(self, tmp_path: Path, capsys):
        lib = _make_library(tmp_path)
        comp = tmp_path / "bad.yml"
        comp.write_text(": : invalid: yaml: {{", encoding="utf-8")

        result = main([
            "generate", str(comp),
            "--library", str(lib),
        ])
        assert result == EXIT_VALIDATION_ERROR
        captured = capsys.readouterr()
        assert "Error loading composition" in captured.err
