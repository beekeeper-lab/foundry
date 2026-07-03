#!/usr/bin/env python3
"""VDD Gate Hook for Claude Code (SPEC-008).

Blocks marking a bean's Status as Done unless a passing VDD report exists
for that bean under ai/outputs/tech-qa/. This turns the honor-system
"/merge-bean refuses without VDD" prose into machinery: across ~294
completed beans, only 3 VDD reports were ever produced.

Accepted report locations (either naming convention):
    ai/outputs/tech-qa/vdd-<NNN>.md          (canonical, foundry_app vdd)
    ai/outputs/tech-qa/BEAN-<NNN>-vdd.md     (historical)

The report must contain a PASS verdict line, e.g.:
    **Aggregate verdict:** PASS
    **Verdict:** PASS (with notes)

Escape hatch — for beans with genuinely nothing to verify programmatically,
the bean.md may carry a marker with a >=10 char justification:
    <!-- vdd-gate: skip (justified: docs-only bean, no runtime surface) -->
Skip usage is visible in the diff and counts in orchestration telemetry.

Exit codes: 0 = allow, 2 = block.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

STATUS_DONE_RE = re.compile(r"\*\*Status\*\*\s*\|\s*Done\b", re.IGNORECASE)
SKIP_RE = re.compile(
    r"<!--\s*vdd-gate:\s*skip\s*\(justified:\s*(.{10,}?)\s*\)\s*-->",
    re.IGNORECASE | re.DOTALL,
)
VERDICT_PASS_RE = re.compile(
    r"\*\*(?:Aggregate\s+)?verdict:\*\*\s*PASS\b", re.IGNORECASE
)
BEAN_ID_RE = re.compile(r"BEAN-(\d+)")


def _new_text(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Write":
        return tool_input.get("content", "")
    return tool_input.get("new_string", "")


def _old_text(tool_name: str, tool_input: dict, path: Path) -> str:
    if tool_name == "Edit":
        return tool_input.get("old_string", "")
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _find_vdd_report(project_root: Path, bean_num: str) -> Path | None:
    qa_dir = project_root / "ai" / "outputs" / "tech-qa"
    if not qa_dir.is_dir():
        return None
    for report in sorted(qa_dir.glob("*.md")):
        name = report.name.lower()
        if "vdd" in name and bean_num in name:
            return report
    return None


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    path = Path(file_path)
    if path.name != "bean.md" or "beans" not in path.parts:
        sys.exit(0)

    new_text = _new_text(tool_name, tool_input)
    if not STATUS_DONE_RE.search(new_text):
        sys.exit(0)
    # Only gate the TRANSITION to Done — re-saving an already-Done bean
    # (telemetry stamps, index rollups) must not be blocked.
    if STATUS_DONE_RE.search(_old_text(tool_name, tool_input, path)):
        sys.exit(0)

    m = BEAN_ID_RE.search(str(path))
    if not m:
        sys.exit(0)
    bean_num = m.group(1)

    # Escape hatch: justified skip marker in the bean itself.
    try:
        bean_content = path.read_text(encoding="utf-8")
    except OSError:
        bean_content = ""
    if SKIP_RE.search(new_text) or SKIP_RE.search(bean_content):
        sys.exit(0)

    # Locate the project root (directory containing ai/) from the bean path.
    project_root = path.parent
    while project_root != project_root.parent:
        if (project_root / "ai" / "beans").is_dir():
            break
        project_root = project_root.parent

    report = _find_vdd_report(project_root, bean_num)
    if report is None:
        print(
            f"BLOCKED: BEAN-{bean_num} cannot be marked Done without a VDD "
            f"report. Run /vdd BEAN-{bean_num} first (report goes to "
            f"ai/outputs/tech-qa/). For beans with nothing programmatically "
            f"verifiable, add to bean.md: "
            f"<!-- vdd-gate: skip (justified: <reason, 10+ chars>) -->",
            file=sys.stderr,
        )
        sys.exit(2)

    report_text = report.read_text(encoding="utf-8")
    if not VERDICT_PASS_RE.search(report_text):
        print(
            f"BLOCKED: BEAN-{bean_num} has a VDD report "
            f"({report.name}) but its verdict is not PASS. Fix the failing "
            f"criteria and re-run /vdd BEAN-{bean_num}.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
