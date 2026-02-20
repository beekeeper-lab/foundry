# Task 02: Test Open Project Folder Fix

| Field | Value |
|-------|-------|
| **Owner** | Tech-QA |
| **Depends on** | Task 01 |
| **Status** | Done |
| **Started** | 2026-02-20 20:13 |
| **Completed** | 2026-02-20 20:13 |
| **Duration** | < 1m |

## Goal

Add unit tests for the `_open_output_folder` method covering all three platform branches (Linux, macOS, Windows) and the error handling fallback. Verify all acceptance criteria are met.

## Inputs

- `foundry_app/ui/screens/generation_progress.py` (the modified `_open_output_folder` method)
- `tests/test_generation_progress.py` (existing test file for this module)

## Example Output

```python
def test_open_output_folder_linux(monkeypatch, widget):
    """xdg-open is called on Linux."""
    monkeypatch.setattr("sys.platform", "linux")
    mock_popen = MagicMock()
    monkeypatch.setattr("subprocess.Popen", mock_popen)
    widget.set_output_path("/tmp/test")
    widget._open_output_folder()
    mock_popen.assert_called_once_with(["xdg-open", "/tmp/test"])
```

## Definition of Done

- [ ] Tests cover Linux (`xdg-open`), macOS (`open`), and Windows (`explorer`) paths
- [ ] Tests cover error handling / fallback path
- [ ] Tests cover empty `_output_path` (no-op) case
- [ ] All tests pass (`uv run pytest`)
- [ ] Lint clean (`uv run ruff check foundry_app/`)
