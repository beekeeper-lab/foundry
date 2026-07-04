#!/usr/bin/env python3
"""PostToolUse Format Hook (SPEC-015).

Runs `ruff format` + `ruff check --fix` on Python files after Edit/Write,
so formatting never depends on the model remembering to lint. Implements
the intent of the (previously unwired) pre-commit-lint hook doc.

Skips silently when ruff is unavailable or the file isn't Python.
Always exits 0 — formatting must never block the edit that triggered it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if input_data.get("tool_name") not in ("Write", "Edit"):
        sys.exit(0)
    file_path = input_data.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py"):
        sys.exit(0)
    path = Path(file_path)
    if not path.is_file():
        sys.exit(0)

    ruff = shutil.which("ruff")
    runner = [ruff] if ruff else (
        ["uv", "run", "ruff"] if shutil.which("uv") else None
    )
    if runner is None:
        sys.exit(0)

    try:
        subprocess.run(
            [*runner, "format", "--quiet", str(path)],
            capture_output=True, timeout=30,
        )
        result = subprocess.run(
            [*runner, "check", "--fix", "--quiet", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0 and result.stdout.strip():
            # Unfixable findings: surface them without blocking.
            print(
                f"ruff: unfixed issues in {path.name}:\n"
                f"{result.stdout.strip()}"
            )
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
