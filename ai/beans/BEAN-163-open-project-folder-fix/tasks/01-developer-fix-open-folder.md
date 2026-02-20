# Task 01: Fix Open Project Folder Button

| Field | Value |
|-------|-------|
| **Owner** | Developer |
| **Depends on** | — |
| **Status** | Done |
| **Started** | 2026-02-20 20:13 |
| **Completed** | 2026-02-20 20:13 |
| **Duration** | < 1m |

## Goal

Replace the unreliable `QDesktopServices.openUrl()` call in `_open_output_folder()` with a cross-platform subprocess-based implementation that uses `xdg-open` on Linux, `open` on macOS, and `explorer` on Windows. Add graceful error handling if the file manager fails to open.

## Inputs

- `foundry_app/ui/screens/generation_progress.py` (lines 482-488 — the `_open_output_folder` method)

## Example Output

```python
def _open_output_folder(self) -> None:
    """Open the output folder in the system file manager."""
    if not self._output_path:
        return
    import subprocess
    import sys

    path = self._output_path
    try:
        if sys.platform == "win32":
            subprocess.Popen(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except OSError:
        # Fallback to Qt method if subprocess fails
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
```

## Definition of Done

- [ ] `_open_output_folder` uses subprocess calls (`xdg-open`, `open`, `explorer`) instead of `QDesktopServices.openUrl()`
- [ ] Handles Linux, macOS, and Windows platforms
- [ ] Has graceful error handling (fallback or user-facing message)
- [ ] `uv run ruff check foundry_app/` passes
- [ ] `uv run pytest` passes
