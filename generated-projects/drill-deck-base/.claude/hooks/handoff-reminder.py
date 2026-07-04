#!/usr/bin/env python3
"""Handoff Reminder Hook (SPEC-008 follow-through).

When a bean transitions to Done with no typed handoff packet recorded
under ai/handoffs/, print a non-blocking reminder. Across ~294 historical
beans exactly ONE packet was ever emitted; this makes the gap visible at
the moment it happens without blocking (multi-persona waves need packets;
single-persona beans legitimately may not).

Always exits 0 — advisory only. The blocking gate for bean closure is
vdd-gate.py.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STATUS_DONE_RE = re.compile(r"\*\*Status\*\*\s*\|\s*Done\b", re.IGNORECASE)
BEAN_ID_RE = re.compile(r"BEAN-(\d+)")


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    path = Path(tool_input.get("file_path", ""))
    if path.name != "bean.md" or "beans" not in path.parts:
        sys.exit(0)

    new_text = (
        tool_input.get("content", "") if tool_name == "Write"
        else tool_input.get("new_string", "")
    )
    if not STATUS_DONE_RE.search(new_text):
        sys.exit(0)
    old_text = tool_input.get("old_string", "") if tool_name == "Edit" else ""
    if STATUS_DONE_RE.search(old_text):
        sys.exit(0)  # not a transition

    m = BEAN_ID_RE.search(str(path))
    if not m:
        sys.exit(0)
    bean_num = m.group(1)

    project_root = path.parent
    while project_root != project_root.parent:
        if (project_root / "ai" / "beans").is_dir():
            break
        project_root = project_root.parent

    handoffs_dir = project_root / "ai" / "handoffs"
    has_packet = handoffs_dir.is_dir() and any(
        bean_num in p.name for p in handoffs_dir.glob("*.md")
        if p.name != "_index.md"
    )
    if not has_packet:
        print(
            f"REMINDER: BEAN-{bean_num} is being closed with no typed "
            f"handoff packet under ai/handoffs/. If this bean's wave "
            f"crossed personas (e.g. developer -> tech-qa), emit one with "
            f"/handoff before closing. Single-persona beans may ignore this.",
            file=sys.stderr,
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
