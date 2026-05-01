"""Background worker for running project generation off the main thread."""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from foundry_app.core.models import CompositionSpec

logger = logging.getLogger(__name__)


class GenerationWorker(QThread):
    """Runs generate_project() on a background thread with progress signals."""

    # (stage_key, status, file_count) — status is "running", "done", or "skipped"
    stage_progress = Signal(str, str, int)
    # (total_files, warnings_list, output_path) — warnings_list carries full
    # messages so the UI can surface content, not just a count.
    finished_ok = Signal(int, list, str)
    # error message
    finished_err = Signal(str)

    def __init__(
        self,
        spec: CompositionSpec,
        library_root: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._spec = spec
        self._library_root = library_root

    def run(self) -> None:
        """Execute generation (runs on the worker thread)."""
        from foundry_app.services.generator import generate_project

        try:
            manifest, validation, _overlay = generate_project(
                composition=self._spec,
                library_root=self._library_root,
                stage_callback=self._on_stage,
            )

            if not validation.is_valid:
                error_messages = [e.message for e in validation.errors[:5]]
                if len(error_messages) == 1:
                    body = error_messages[0]
                else:
                    body = error_messages[0] + "\n• " + "\n• ".join(
                        error_messages[1:]
                    )
                self.finished_err.emit(body)
                return

            output_dir = (
                Path(self._spec.project.output_root)
                / self._spec.project.resolved_output_folder
            )
            self.finished_ok.emit(
                manifest.total_files_written,
                list(manifest.all_warnings),
                str(output_dir),
            )
        except Exception:
            logger.exception("Generation failed")
            self.finished_err.emit(
                "Generation failed. Check the log file for details."
            )

    def _on_stage(self, stage_key: str, status: str, file_count: int) -> None:
        """Forward stage callbacks as Qt signals (thread-safe via queued connection)."""
        self.stage_progress.emit(stage_key, status, file_count)
