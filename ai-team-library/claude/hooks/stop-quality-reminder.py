#!/usr/bin/env python3
"""Stop Quality Reminder Hook (SPEC-015).

At session stop, if Python source files are modified in the working tree,
prints a reminder to run the test suite and lint before marking work done —
the practical, non-blocking form of the post-task-qa hook doc's intent.

Never blocks (exit 0): a Stop hook that runs a full test suite would add
minutes of latency to every stop, including mid-work interruptions.
The hard gates live elsewhere (vdd-gate.py, branch protection).
"""

from __future__ import annotations

import subprocess
import sys


def main() -> None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        sys.exit(0)

    py_changes = [
        line for line in result.stdout.splitlines()
        if line.strip().endswith(".py") and not line.startswith("??")
    ]
    if py_changes:
        print(
            f"Quality reminder: {len(py_changes)} modified Python file(s) "
            f"in the working tree. Before marking work done: run the test "
            f"suite and lint (e.g. `uv run pytest` and `uv run ruff check`)."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
