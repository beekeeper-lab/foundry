"""Orchestration report — aggregates per-bean telemetry into a roll-up.

The bean lifecycle collects telemetry on every bean (BEAN-278) but until
SPEC-009 nothing ever consumed it. This service parses every
``ai/beans/BEAN-*/bean.md`` and emits
``ai/outputs/team-lead/orchestration-report-<YYYY-MM>.md`` with throughput,
duration distribution, dispatch-mode mix, gate-waiver counts, and a
telemetry-completeness rate — turning write-only data into a feedback loop.

Exposed via ``foundry-cli orchestration-report`` and the
``/orchestration-report`` skill (same pattern as ``/vdd`` → ``vdd.py``).
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_FIELD_RE_TEMPLATE = r"^\|\s*\*\*{field}\*\*\s*\|\s*(.*?)\s*\|"
_DURATION_RE = re.compile(r"(?:(\d+)h)?\s*(?:(\d+)m)?")
_VDD_SKIP_RE = re.compile(r"vdd-gate:\s*skip", re.IGNORECASE)
_INPUTS_NONE_RE = re.compile(r"Inputs:\s*NONE\s*\(justified:", re.IGNORECASE)


def _parse_field(content: str, name: str) -> str | None:
    m = re.search(
        _FIELD_RE_TEMPLATE.format(field=re.escape(name)),
        content, re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def _duration_minutes(raw: str | None) -> int | None:
    """Parse '14m', '1h 5m', '2h' (ignoring backfill markers); None if absent."""
    if not raw or raw in ("—", "-"):
        return None
    raw = raw.split("(")[0].strip()
    m = _DURATION_RE.match(raw)
    if not m or (m.group(1) is None and m.group(2) is None):
        return None
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


@dataclass
class BeanStats:
    """Parsed roll-up inputs for a single bean."""

    bean_id: str
    number: int
    status: str = ""
    category: str = ""
    duration_minutes: int | None = None
    dispatch_mode: str | None = None
    has_telemetry_block: bool = False
    telemetry_is_template_default: bool = False
    vdd_waived: bool = False
    inputs_none_count: int = 0


def parse_bean(bean_dir: Path) -> BeanStats | None:
    """Parse one bean directory into BeanStats; None if bean.md missing."""
    bean_md = bean_dir / "bean.md"
    if not bean_md.is_file():
        return None
    content = bean_md.read_text(encoding="utf-8")

    m = re.match(r"BEAN-(\d+)", bean_dir.name)
    number = int(m.group(1)) if m else 0

    stats = BeanStats(
        bean_id=f"BEAN-{number:03d}" if number else bean_dir.name,
        number=number,
        status=_parse_field(content, "Status") or "",
        category=_parse_field(content, "Category") or "",
        duration_minutes=_duration_minutes(_parse_field(content, "Duration")),
        vdd_waived=bool(_VDD_SKIP_RE.search(content)),
    )

    if "## Orchestration Telemetry" in content:
        stats.has_telemetry_block = True
        bounces = _parse_field(content, "Bounces") or ""
        scope = _parse_field(content, "Scope changes") or ""
        violations = _parse_field(content, "Contract violations") or ""
        dispatch = _parse_field(content, "Dispatch mode") or ""
        stats.dispatch_mode = dispatch.split("(")[0].strip() or None
        # The template ships zeros + in-process; a block still carrying all
        # of them verbatim was copy-pasted, not measured. Count separately
        # so completeness isn't overstated (SPEC-009).
        stats.telemetry_is_template_default = (
            bounces.startswith("0")
            and scope.startswith("0")
            and violations.startswith("0")
            and stats.dispatch_mode == "in-process"
        )

    tasks_dir = bean_dir / "tasks"
    if tasks_dir.is_dir():
        for task in tasks_dir.glob("*.md"):
            try:
                if _INPUTS_NONE_RE.search(task.read_text(encoding="utf-8")):
                    stats.inputs_none_count += 1
            except OSError:
                continue

    return stats


def collect_stats(beans_dir: Path) -> list[BeanStats]:
    """Parse all beans, sorted by bean number."""
    stats = []
    for bean_dir in sorted(beans_dir.glob("BEAN-*")):
        if not bean_dir.is_dir():
            continue
        parsed = parse_bean(bean_dir)
        if parsed is not None:
            stats.append(parsed)
    return sorted(stats, key=lambda s: s.number)


@dataclass
class Report:
    generated_at: str
    generated_through: str
    body: str
    anomalies: list[str] = field(default_factory=list)


def _percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round(pct * (len(ordered) - 1))))
    return ordered[idx]


def build_report(stats: list[BeanStats], now: datetime | None = None) -> Report:
    """Aggregate BeanStats into the markdown roll-up."""
    now = now or datetime.now(timezone.utc)
    done = [s for s in stats if s.status.lower() == "done"]
    durations = [
        s.duration_minutes for s in done if s.duration_minutes is not None
    ]
    with_block = [s for s in stats if s.has_telemetry_block]
    measured = [s for s in with_block if not s.telemetry_is_template_default]
    dispatch_mix: dict[str, int] = {}
    for s in with_block:
        if s.dispatch_mode:
            dispatch_mix[s.dispatch_mode] = dispatch_mix.get(s.dispatch_mode, 0) + 1
    waivers = [s.bean_id for s in stats if s.vdd_waived]
    inputs_none_total = sum(s.inputs_none_count for s in stats)

    anomalies: list[str] = []
    for s in sorted(
        (s for s in done if (s.duration_minutes or 0) > 8 * 60),
        key=lambda s: -(s.duration_minutes or 0),
    )[:5]:
        anomalies.append(
            f"{s.bean_id}: duration {s.duration_minutes} min exceeds a "
            f"working day — verify Started/Completed stamps"
        )
    done_without_duration = [s.bean_id for s in done if s.duration_minutes is None]
    if done_without_duration:
        anomalies.append(
            f"{len(done_without_duration)} Done bean(s) carry no parseable "
            f"Duration (e.g. {', '.join(done_without_duration[:5])})"
        )

    generated_through = f"BEAN-{stats[-1].number:03d}" if stats else "none"
    status_counts: dict[str, int] = {}
    for s in stats:
        status_counts[s.status or "(missing)"] = (
            status_counts.get(s.status or "(missing)", 0) + 1
        )

    lines = [
        f"# Orchestration Report — {now:%Y-%m}",
        "",
        f"**Generated:** {now:%Y-%m-%d %H:%M} UTC",
        f"**Generated-through:** {generated_through}",
        "",
        "## Throughput",
        "",
        f"- Beans total: {len(stats)}",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"  - {status}: {count}")
    lines += [
        "",
        "## Duration (Done beans, minutes)",
        "",
        f"- With parseable duration: {len(durations)} / {len(done)}",
        f"- Median: {int(statistics.median(durations)) if durations else 0}",
        f"- p90: {_percentile(durations, 0.9)}",
        "",
        "## Telemetry completeness",
        "",
        f"- Beans with an Orchestration Telemetry block: "
        f"{len(with_block)} / {len(stats)}",
        f"- Measured (non-template-default) blocks: {len(measured)} / "
        f"{len(with_block) or 1}"
        + (" — every block still carries the template defaults; the data "
           "is copy-pasted, not measured" if with_block and not measured else ""),
        "",
        "## Dispatch mode mix",
        "",
    ]
    if dispatch_mix:
        for mode, count in sorted(dispatch_mix.items()):
            lines.append(f"- {mode}: {count}")
    else:
        lines.append("- (no dispatch data recorded)")
    lines += [
        "",
        "## Gate waivers and escape hatches",
        "",
        f"- VDD-gate skips (`vdd-gate: skip`): {len(waivers)}"
        + (f" — {', '.join(waivers[:10])}" if waivers else ""),
        f"- `Inputs: NONE (justified:)` task invocations: {inputs_none_total}",
        "",
        "## Anomalies",
        "",
    ]
    lines += [f"- {a}" for a in anomalies] or ["- none detected"]
    lines += [
        "",
        "## Recommended process changes",
        "",
        "> Filled by the Team Lead after reviewing the numbers above. Each",
        "> accepted recommendation lands as an ADR amendment in",
        "> `ai/context/decisions.md` or an improvement bean.",
        "",
        "- [ ] (none proposed yet)",
        "",
    ]
    return Report(
        generated_at=f"{now:%Y-%m-%d %H:%M}",
        generated_through=generated_through,
        body="\n".join(lines),
        anomalies=anomalies,
    )


def write_report(
    repo_root: Path, now: datetime | None = None,
) -> Path:
    """Generate and write the report; returns the output path."""
    now = now or datetime.now(timezone.utc)
    stats = collect_stats(repo_root / "ai" / "beans")
    report = build_report(stats, now=now)
    out_dir = repo_root / "ai" / "outputs" / "team-lead"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"orchestration-report-{now:%Y-%m}.md"
    out_path.write_text(report.body + "\n", encoding="utf-8")
    return out_path
