# Task 04: Entry Points

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | 03 |
| **Status** | Pending |

## Goal

Create `foundry_app/main.py` and `foundry_app/__main__.py` entry points.

## Inputs

- pyproject.toml already has `foundry = "foundry_app.main:main"`
- MainWindow from task 03

## Definition of Done

- [ ] `foundry_app/main.py` — QApplication setup, logging init, MainWindow launch
- [ ] `foundry_app/__main__.py` — `python -m foundry_app` support
- [ ] `uv run foundry` launches the app
