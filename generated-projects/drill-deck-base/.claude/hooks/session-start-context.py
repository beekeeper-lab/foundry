#!/usr/bin/env python3
"""SessionStart Context Hook (SPEC-015).

Injects lightweight project state at session start so agents don't have
to remember to look it up: current branch (with a protected-branch
warning) and bean backlog counts from ai/beans/_index.md.

Stdout from a SessionStart hook is added to the session context.
Always exits 0 — context injection must never block a session.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

PROTECTED = ("main", "master", "test", "prod")


def _branch() -> str:
    try:
        return subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        return ""


def _backlog_counts() -> Counter[str] | None:
    index = Path("ai/beans/_index.md")
    if not index.is_file():
        return None
    counts: Counter[str] = Counter()
    try:
        for line in index.read_text(encoding="utf-8").splitlines():
            # Backlog rows: | BEAN-NNN | ... | <Status> | ...
            if not re.match(r"\|\s*\[?BEAN-\d+", line):
                continue
            for status in (
                "Unapproved", "Approved", "In Progress", "Blocked", "Done",
            ):
                if f"| {status} " in line or f"| {status}|" in line:
                    counts[status] += 1
                    break
    except OSError:
        return None
    return counts


def main() -> None:
    lines: list[str] = []
    branch = _branch()
    if branch:
        lines.append(f"Current git branch: {branch}")
        if branch in PROTECTED:
            lines.append(
                f"WARNING: you are on protected branch '{branch}' — create "
                f"a feature branch before editing (edits here are blocked "
                f"by the branch-protection hook)."
            )
    counts = _backlog_counts()
    if counts:
        active = {k: v for k, v in counts.items() if k != "Done"}
        summary = ", ".join(f"{v} {k}" for k, v in sorted(active.items()))
        lines.append(
            f"Bean backlog: {summary or 'no active beans'} "
            f"({counts.get('Done', 0)} done). Index: ai/beans/_index.md"
        )
    if lines:
        print("\n".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()
