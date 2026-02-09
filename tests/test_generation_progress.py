"""Tests for foundry_app.ui.screens.generation_progress — progress screen."""

from PySide6.QtWidgets import QApplication

from foundry_app.ui.screens.generation_progress import (
    PIPELINE_STAGES,
    GenerationProgressScreen,
    StageStatusWidget,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# StageStatusWidget
# ---------------------------------------------------------------------------


class TestStageStatusWidget:

    def test_initial_status_is_pending(self):
        w = StageStatusWidget("scaffold", "Scaffold directories")
        assert w.status == "pending"

    def test_set_running(self):
        w = StageStatusWidget("scaffold", "Scaffold directories")
        w.set_running()
        assert w.status == "running"

    def test_set_done(self):
        w = StageStatusWidget("scaffold", "Scaffold directories")
        w.set_done(file_count=5)
        assert w.status == "done"

    def test_set_error(self):
        w = StageStatusWidget("scaffold", "Scaffold directories")
        w.set_error("Disk full")
        assert w.status == "error"

    def test_set_skipped(self):
        w = StageStatusWidget("scaffold", "Scaffold directories")
        w.set_skipped()
        assert w.status == "skipped"

    def test_stage_key_stored(self):
        w = StageStatusWidget("compile", "Compile prompts")
        assert w.stage_key == "compile"


# ---------------------------------------------------------------------------
# GenerationProgressScreen construction
# ---------------------------------------------------------------------------


class TestScreenConstruction:

    def test_creates_screen(self):
        screen = GenerationProgressScreen()
        assert screen is not None

    def test_has_progress_bar(self):
        screen = GenerationProgressScreen()
        assert screen.progress_bar is not None
        assert screen.progress_bar.maximum() == len(PIPELINE_STAGES)

    def test_has_log_widget(self):
        screen = GenerationProgressScreen()
        assert screen.log_widget is not None

    def test_has_summary_label(self):
        screen = GenerationProgressScreen()
        assert screen.summary_label is not None
        assert not screen.summary_label.isVisible()

    def test_has_open_button(self):
        screen = GenerationProgressScreen()
        assert screen.open_button is not None
        assert not screen.open_button.isVisible()

    def test_all_stages_present(self):
        screen = GenerationProgressScreen()
        for key, _ in PIPELINE_STAGES:
            assert screen.stage_widget(key) is not None

    def test_unknown_stage_returns_none(self):
        screen = GenerationProgressScreen()
        assert screen.stage_widget("nonexistent") is None


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


class TestLifecycle:

    def test_start_resets_progress(self):
        screen = GenerationProgressScreen()
        screen.start()
        assert screen.progress_bar.value() == 0

    def test_start_clears_log(self):
        screen = GenerationProgressScreen()
        screen.append_log("old entry")
        screen.start()
        assert screen.log_widget.toPlainText() == "Generation started..."

    def test_start_hides_summary(self):
        screen = GenerationProgressScreen()
        screen.summary_label.setVisible(True)
        screen.start()
        assert not screen.summary_label.isVisible()

    def test_mark_stage_running(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_running("scaffold")
        w = screen.stage_widget("scaffold")
        assert w.status == "running"

    def test_mark_stage_done_updates_progress(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_done("scaffold", file_count=3)
        assert screen.progress_bar.value() == 1
        w = screen.stage_widget("scaffold")
        assert w.status == "done"

    def test_mark_stage_error(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_error("compile", "Template not found")
        w = screen.stage_widget("compile")
        assert w.status == "error"

    def test_mark_stage_skipped_updates_progress(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_skipped("diff_report")
        assert screen.progress_bar.value() == 1

    def test_finish_shows_summary(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=10, warnings=2)
        assert not screen.summary_label.isHidden()
        assert "10 files" in screen.summary_label.text()
        assert "2 warnings" in screen.summary_label.text()

    def test_finish_shows_open_button(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=5)
        assert not screen.open_button.isHidden()

    def test_finish_sets_progress_to_max(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish()
        assert screen.progress_bar.value() == screen.progress_bar.maximum()

    def test_finish_with_error(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish_with_error("Disk full")
        assert not screen.summary_label.isHidden()
        assert "failed" in screen.summary_label.text().lower()
        assert "Disk full" in screen.summary_label.text()

    def test_finish_with_error_no_open_button(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish_with_error("Error")
        assert screen.open_button.isHidden()

    def test_append_log(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.append_log("custom message")
        assert "custom message" in screen.log_widget.toPlainText()

    def test_multiple_stages_done(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_done("scaffold", 3)
        screen.mark_stage_done("compile", 5)
        screen.mark_stage_done("copy_assets", 2)
        assert screen.progress_bar.value() == 3


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


class TestSignals:

    def test_generation_complete_signal(self):
        screen = GenerationProgressScreen()
        received = []
        screen.generation_complete.connect(lambda: received.append(True))
        screen.start()
        screen.finish()
        assert received == [True]

    def test_generation_failed_signal(self):
        screen = GenerationProgressScreen()
        received = []
        screen.generation_failed.connect(lambda msg: received.append(msg))
        screen.start()
        screen.finish_with_error("boom")
        assert received == ["boom"]
