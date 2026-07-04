#!/usr/bin/env python3
"""One-shot backfill of corrupted bean Duration fields (SPEC-005).

The telemetry-stamp hook used to stamp Duration with git branch AGE
(first commit → now) instead of Started→Completed, corrupting 60+ beans
with values like `1578h 19m` for 14-minute beans. This script recomputes
Duration from the recorded Started/Completed timestamps and rewrites the
field with a `(corrected 2026-07)` marker.

Dry-run by default; pass --apply to write changes.

Usage:
    python3 scripts/backfill-bean-durations.py [--apply] [--beans-dir ai/beans]
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

TIMESTAMP_FMT = "%Y-%m-%d %H:%M"
MARKER = "(corrected 2026-07)"


def parse_field(content: str, field: str) -> str | None:
    m = re.search(
        r"^\|\s*\*\*" + re.escape(field) + r"\*\*\s*\|\s*(.*?)\s*\|",
        content,
        re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def replace_field(content: str, field: str, value: str) -> str:
    pattern = re.compile(
        r"(^\|\s*\*\*" + re.escape(field) + r"\*\*\s*\|\s*)(.*?)(\s*\|)",
        re.MULTILINE,
    )
    return pattern.sub(rf"\g<1>{value}\3", content, count=1)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), TIMESTAMP_FMT)
    except ValueError:
        return None


def format_seconds(seconds: float) -> str:
    total_minutes = int(seconds // 60)
    if total_minutes < 60:
        return f"{total_minutes}m"
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes}m" if minutes else f"{hours}h"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--beans-dir", default="ai/beans", type=Path)
    args = parser.parse_args()

    changed = skipped = 0
    for bean_md in sorted(args.beans_dir.glob("BEAN-*/bean.md")):
        content = bean_md.read_text(encoding="utf-8")
        started = parse_ts(parse_field(content, "Started"))
        completed = parse_ts(parse_field(content, "Completed"))
        current = parse_field(content, "Duration")
        if not started or not completed or not current or MARKER in current:
            skipped += 1
            continue

        correct = format_seconds(max(0, (completed - started).total_seconds()))
        if current == correct:
            skipped += 1
            continue

        new_value = f"{correct} {MARKER}"
        print(f"{bean_md.parent.name}: {current!r} -> {new_value!r}")
        if args.apply:
            bean_md.write_text(
                replace_field(content, "Duration", new_value), encoding="utf-8",
            )
        changed += 1

    mode = "corrected" if args.apply else "would correct (dry-run; use --apply)"
    print(f"\n{mode}: {changed} bean(s); unchanged/skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
