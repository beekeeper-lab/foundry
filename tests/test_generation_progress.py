"""Tests for foundry_app.ui.screens.generation_progress — progress screen."""

import pytest

from foundry_app.ui.screens.generation_progress import (
    GenerationProgressScreen,
    StageStatusWidget,
)

pytestmark = pytest.mark.usefixtures("qapp")


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

    def test_finish_appends_warnings_to_log(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(
            total_files=3,
            warnings=2,
            warnings_list=[
                "Expertise 'clean-code' missing conventions.md",
                "Unresolved placeholders in foo.md: strictness",
            ],
        )
        log_text = screen.log_widget.toPlainText()
        assert "Expertise 'clean-code'" in log_text
        assert "Unresolved placeholders" in log_text
        assert log_text.count("\u26a0") == 2

    def test_finish_without_warnings_list_is_backward_compatible(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=3, warnings=0)
        # No warning-prefixed lines appear.
        assert "\u26a0" not in screen.log_widget.toPlainText()

    def test_mark_stage_skipped_logs(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.mark_stage_skipped("diff_report")
        log_text = screen.log_widget.toPlainText()
        assert "diff_report" in log_text
        assert "skipped" in log_text

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

    def test_back_requested_signal(self):
        screen = GenerationProgressScreen()
        received = []
        screen.back_requested.connect(lambda: received.append(True))
        screen.back_button.click()
        assert received == [True]


# ---------------------------------------------------------------------------
# Output path & back button
# ---------------------------------------------------------------------------


class TestOutputPath:

    def test_set_output_path_shows_label(self):
        screen = GenerationProgressScreen()
        screen.set_output_path("/tmp/my-project")
        assert not screen.path_label.isHidden()
        assert "/tmp/my-project" in screen.path_label.text()

    def test_path_label_hidden_initially(self):
        screen = GenerationProgressScreen()
        assert screen.path_label.isHidden()

    def test_start_hides_path_label(self):
        screen = GenerationProgressScreen()
        screen.set_output_path("/tmp/test")
        screen.start()
        assert screen.path_label.isHidden()

    def test_back_button_hidden_initially(self):
        screen = GenerationProgressScreen()
        assert screen.back_button.isHidden()

    def test_back_button_visible_after_finish(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=5)
        assert not screen.back_button.isHidden()

    def test_back_button_visible_after_error(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish_with_error("Error")
        assert not screen.back_button.isHidden()

    def test_start_hides_back_button(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=5)
        assert not screen.back_button.isHidden()
        screen.start()
        assert screen.back_button.isHidden()


# ---------------------------------------------------------------------------
# BEAN-287 — Sticky outcome banner (success + failure recovery affordance)
#
# When generation finishes (success or failure), the summary + recovery
# buttons must appear in a sticky banner above the scroll area so the
# Back to Builder button stays on-screen even on small windows where it
# previously sat below the fold.
# ---------------------------------------------------------------------------


class TestOutcomeBanner:
    """The outcome banner is the recovery affordance — must stay above fold."""

    def test_banner_hidden_after_construction(self):
        screen = GenerationProgressScreen()
        assert screen._outcome_banner.isHidden() is True

    def test_banner_hidden_after_start_clears_prior_outcome(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=5)
        assert screen._outcome_banner.isHidden() is False
        # A fresh run must not display the prior outcome.
        screen.start()
        assert screen._outcome_banner.isHidden() is True

    def test_banner_visible_after_finish_with_buttons(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish(total_files=5)
        assert screen._outcome_banner.isHidden() is False
        # Both recovery affordances are present on success.
        assert screen.back_button.isHidden() is False
        assert screen.open_button.isHidden() is False
        # Summary label has the success text.
        assert "complete" in screen.summary_label.text().lower()

    def test_banner_visible_after_error_back_only(self):
        screen = GenerationProgressScreen()
        screen.start()
        screen.finish_with_error("Hook packs conflict")
        assert screen._outcome_banner.isHidden() is False
        # Back button must be on-screen; Open button hidden on failure.
        assert screen.back_button.isHidden() is False
        assert screen.open_button.isHidden() is True
        # Summary names the failure verbatim.
        assert "failed" in screen.summary_label.text().lower()
        assert "Hook packs conflict" in screen.summary_label.text()

    def test_banner_is_sibling_of_scroll_not_nested(self):
        """Banner must be a sibling of the scroll area in the outer layout,
        not a child of the scrolled container — that's what makes it sticky
        on small windows where the recovery affordance previously sat below
        the fold (BEAN-287)."""
        screen = GenerationProgressScreen()
        # Both must share the same direct parent (the screen) — so neither
        # is the descendant of the other.
        assert screen._outcome_banner.parent() is screen
        assert screen._scroll.parent() is screen
        # Banner is not a descendant of the scroll viewport.
        assert not screen._scroll.isAncestorOf(screen._outcome_banner)

    def test_finish_with_error_resets_scroll_to_top(self):
        """Auto-scroll safety net: failure pops the scroll position back
        to the top so the banner is on-screen even if a custom theme
        somehow inflates the banner past the viewport."""
        screen = GenerationProgressScreen()
        screen.start()
        # Simulate a scroll position somewhere in the middle of the body.
        screen._scroll.verticalScrollBar().setValue(200)
        screen.finish_with_error("Boom")
        assert screen._scroll.verticalScrollBar().value() == 0


