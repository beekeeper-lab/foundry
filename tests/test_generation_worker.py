"""Tests for foundry_app.ui.generation_worker — background generation thread."""

from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    CompositionSpec,
    GenerationManifest,
    GenerationOptions,
    ProjectIdentity,
    Severity,
    StageResult,
    TeamConfig,
    ValidationMessage,
    ValidationResult,
)
from foundry_app.ui.generation_worker import GenerationWorker

_app = QApplication.instance() or QApplication([])


def _make_spec(tmp_path):
    """Create a minimal CompositionSpec for testing."""
    return CompositionSpec(
        project=ProjectIdentity(
            name="Test Project",
            slug="test-project",
            output_root=str(tmp_path),
        ),
        team=TeamConfig(),
        generation=GenerationOptions(
            seed_tasks=False,
            write_manifest=False,
            write_diff_report=False,
        ),
    )


class TestWorkerConstruction:

    def test_creates_worker(self, tmp_path):
        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")
        assert worker is not None

    def test_worker_is_qthread(self, tmp_path):
        from PySide6.QtCore import QThread

        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")
        assert isinstance(worker, QThread)


class TestWorkerSignals:

    def test_finished_ok_emits_on_success(self, tmp_path):
        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")

        results = []
        worker.finished_ok.connect(lambda f, w, p: results.append((f, w, p)))

        manifest = GenerationManifest(
            run_id="test",
            stages={"scaffold": StageResult(wrote=["a.md"], warnings=[])},
        )
        validation = ValidationResult()

        with patch(
            "foundry_app.services.generator.generate_project",
            return_value=(manifest, validation, None),
        ):
            worker.run()

        assert len(results) == 1
        assert results[0][0] == 1  # total_files
        assert results[0][1] == 0  # warnings

    def test_finished_err_emits_on_validation_failure(self, tmp_path):
        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")

        errors = []
        worker.finished_err.connect(lambda msg: errors.append(msg))

        manifest = GenerationManifest(run_id="test")
        validation = ValidationResult(messages=[
            ValidationMessage(
                severity=Severity.ERROR, code="bad-persona", message="bad persona",
            ),
        ])

        with patch(
            "foundry_app.services.generator.generate_project",
            return_value=(manifest, validation, None),
        ):
            worker.run()

        assert len(errors) == 1
        assert "Validation failed" in errors[0]

    def test_finished_err_emits_on_exception(self, tmp_path):
        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")

        errors = []
        worker.finished_err.connect(lambda msg: errors.append(msg))

        with patch(
            "foundry_app.services.generator.generate_project",
            side_effect=RuntimeError("disk full"),
        ):
            worker.run()

        assert len(errors) == 1
        assert "disk full" in errors[0]

    def test_stage_progress_emitted(self, tmp_path):
        spec = _make_spec(tmp_path)
        worker = GenerationWorker(spec, "/fake/lib")

        stages = []
        worker.stage_progress.connect(lambda k, s, c: stages.append((k, s, c)))

        manifest = GenerationManifest(
            run_id="test",
            stages={"scaffold": StageResult(wrote=["a.md"], warnings=[])},
        )
        validation = ValidationResult()

        def fake_generate(**kwargs):
            cb = kwargs.get("stage_callback")
            if cb:
                cb("scaffold", "running", 0)
                cb("scaffold", "done", 1)
            return manifest, validation, None

        with patch(
            "foundry_app.services.generator.generate_project",
            side_effect=fake_generate,
        ):
            worker.run()

        assert ("scaffold", "running", 0) in stages
        assert ("scaffold", "done", 1) in stages
