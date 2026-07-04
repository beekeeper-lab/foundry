"""Tests for the orchestration report aggregator (SPEC-009)."""

from datetime import datetime, timezone
from pathlib import Path

from foundry_app.services.orchestration_report import (
    build_report,
    collect_stats,
    parse_bean,
    write_report,
)

_NOW = datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc)


def _bean(
    tmp_path: Path, num: int, *, status: str = "Done", duration: str = "14m",
    telemetry: str | None = None, body: str = "", tasks: list[str] = (),
) -> Path:
    bean_dir = tmp_path / "ai" / "beans" / f"BEAN-{num:03d}-x"
    (bean_dir / "tasks").mkdir(parents=True)
    content = (
        f"# BEAN-{num:03d}\n\n| Field | Value |\n|---|---|\n"
        f"| **Status** | {status} |\n"
        f"| **Duration** | {duration} |\n"
        f"| **Category** | App |\n"
        + (telemetry or "") + body
    )
    (bean_dir / "bean.md").write_text(content, encoding="utf-8")
    for i, task in enumerate(tasks):
        (bean_dir / "tasks" / f"{i:02d}-t.md").write_text(task, encoding="utf-8")
    return bean_dir


_TEMPLATE_BLOCK = (
    "\n## Orchestration Telemetry\n\n| Field | Value |\n|---|---|\n"
    "| **Bounces** | 0 (Tech-QA kicks) |\n"
    "| **Scope changes** | 0 (in-flight) |\n"
    "| **Contract violations** | 0 |\n"
    "| **Dispatch mode** | in-process |\n"
)
_MEASURED_BLOCK = _TEMPLATE_BLOCK.replace("| **Bounces** | 0 (Tech-QA kicks) |",
                                          "| **Bounces** | 2 |")


class TestParseBean:
    def test_parses_core_fields(self, tmp_path):
        d = _bean(tmp_path, 1, duration="1h 5m (corrected 2026-07)")
        s = parse_bean(d)
        assert s.number == 1
        assert s.status == "Done"
        assert s.duration_minutes == 65

    def test_without_telemetry_block(self, tmp_path):
        s = parse_bean(_bean(tmp_path, 2))
        assert not s.has_telemetry_block

    def test_template_default_block_detected(self, tmp_path):
        s = parse_bean(_bean(tmp_path, 3, telemetry=_TEMPLATE_BLOCK))
        assert s.has_telemetry_block
        assert s.telemetry_is_template_default
        assert s.dispatch_mode == "in-process"

    def test_measured_block_not_template_default(self, tmp_path):
        s = parse_bean(_bean(tmp_path, 4, telemetry=_MEASURED_BLOCK))
        assert not s.telemetry_is_template_default

    def test_waiver_and_inputs_none_counted(self, tmp_path):
        d = _bean(
            tmp_path, 5,
            body="\n<!-- vdd-gate: skip (justified: docs only bean) -->\n",
            tasks=["# T\n\nInputs: NONE (justified: bootstrap task)\n"],
        )
        s = parse_bean(d)
        assert s.vdd_waived
        assert s.inputs_none_count == 1


class TestReport:
    def test_report_aggregates_and_writes(self, tmp_path):
        _bean(tmp_path, 1, duration="10m")
        _bean(tmp_path, 2, duration="20m", telemetry=_TEMPLATE_BLOCK)
        _bean(tmp_path, 3, status="Approved", duration="—",
              telemetry=_MEASURED_BLOCK)

        out = write_report(tmp_path, now=_NOW)
        assert out == (
            tmp_path / "ai" / "outputs" / "team-lead"
            / "orchestration-report-2026-07.md"
        )
        text = out.read_text(encoding="utf-8")
        assert "**Generated-through:** BEAN-003" in text
        assert "Beans total: 3" in text
        assert "Median: 15" in text
        assert "Measured (non-template-default) blocks: 1 / 2" in text
        assert "Recommended process changes" in text

    def test_anomaly_for_absurd_duration(self, tmp_path):
        _bean(tmp_path, 1, duration="1578h 19m")
        stats = collect_stats(tmp_path / "ai" / "beans")
        report = build_report(stats, now=_NOW)
        assert any("exceeds a working day" in a for a in report.anomalies)

    def test_done_without_duration_flagged(self, tmp_path):
        _bean(tmp_path, 1, duration="—")
        stats = collect_stats(tmp_path / "ai" / "beans")
        report = build_report(stats, now=_NOW)
        assert any("no parseable Duration" in a for a in report.anomalies)

    def test_empty_backlog_does_not_crash(self, tmp_path):
        (tmp_path / "ai" / "beans").mkdir(parents=True)
        out = write_report(tmp_path, now=_NOW)
        assert "Beans total: 0" in out.read_text(encoding="utf-8")
