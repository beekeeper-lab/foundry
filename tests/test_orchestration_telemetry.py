"""Tests for BEAN-278 Orchestration Telemetry stamping in
.claude/hooks/telemetry-stamp.py.

Covers the new helpers:
    - has_orchestration_telemetry
    - parse_orchestration_field / replace_orchestration_field
    - telemetry_owners_with_data
    - collect_dispatch_markers / infer_dispatch_mode_from_worktrees
    - compute_dispatch_mode
    - stamp_orchestration_telemetry
    - extract_bean_id

and the integration into handle_bean_file (only fires when status flips
to Done; silent no-op for beans missing the section; idempotent on
re-run; never overwrites persona-recorded values).
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# Import the hook module (filename has a hyphen).
_hook_path = str(Path(__file__).resolve().parent.parent / ".claude" / "hooks")
if _hook_path not in sys.path:
    sys.path.insert(0, _hook_path)
_mod = importlib.import_module("telemetry-stamp")

SENTINEL = _mod.SENTINEL
parse_metadata_field = _mod.parse_metadata_field
handle_bean_file = _mod.handle_bean_file
has_orchestration_telemetry = _mod.has_orchestration_telemetry
parse_orchestration_field = _mod.parse_orchestration_field
replace_orchestration_field = _mod.replace_orchestration_field
telemetry_owners_with_data = _mod.telemetry_owners_with_data
collect_dispatch_markers = _mod.collect_dispatch_markers
infer_dispatch_mode_from_worktrees = _mod.infer_dispatch_mode_from_worktrees
compute_dispatch_mode = _mod.compute_dispatch_mode
stamp_orchestration_telemetry = _mod.stamp_orchestration_telemetry
extract_bean_id = _mod.extract_bean_id


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# A bean.md mirror of the new template (BEAN-278) — full metadata, two
# Done tasks with populated telemetry rows so `telemetry_owners_with_data`
# has actual data, and the Orchestration Telemetry block at the end.
BEAN_WITH_ORCH = """\
# BEAN-099: Test Bean

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-099 |
| **Status** | {status} |
| **Priority** | Medium |
| **Created** | 2026-04-30 |
| **Started** | {started} |
| **Completed** | {completed} |
| **Duration** | {duration} |
| **Owner** | team-lead |
| **Category** | App |

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | First task | developer | — | {task1_status} |
| 2 | Second task | tech-qa | 1 | {task2_status} |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | First task | developer | {t1_dur} | {t1_in} | {t1_out} | {t1_cost} |
| 2 | Second task | tech-qa | {t2_dur} | {t2_in} | {t2_out} | {t2_cost} |

| Metric | Value |
|--------|-------|
| **Total Tasks** | {total_tasks} |
| **Total Duration** | {total_duration} |
| **Total Tokens In** | {total_tok_in} |
| **Total Tokens Out** | {total_tok_out} |
| **Total Cost** | {total_cost} |

## Orchestration Telemetry

| Field | Value |
|-------|-------|
| **Personas activated** | {personas} |
| **Bounces** | {bounces} |
| **Scope changes** | {scope_changes} |
| **Contract violations** | {contract_violations} |
| **Inputs escape-hatch invocations** | {escape_hatch} |
| **Dispatch mode** | {dispatch_mode} |
"""


# Bean WITHOUT the new Orchestration Telemetry block (legacy).
BEAN_LEGACY = """\
# BEAN-098: Legacy Bean

| Field | Value |
|-------|-------|
| **Bean ID** | BEAN-098 |
| **Status** | {status} |
| **Priority** | Medium |
| **Created** | 2026-01-15 |
| **Started** | {started} |
| **Completed** | {completed} |
| **Duration** | {duration} |
| **Owner** | team-lead |
| **Category** | App |

## Tasks

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Only task | developer | — | {task1_status} |

## Telemetry

| # | Task | Owner | Duration | Tokens In | Tokens Out | Cost |
|---|------|-------|----------|-----------|------------|------|
| 1 | Only task | developer | 5m | 1000 | 500 | $0.05 |

| Metric | Value |
|--------|-------|
| **Total Tasks** | {total_tasks} |
| **Total Duration** | {total_duration} |
| **Total Tokens In** | — |
| **Total Tokens Out** | — |
| **Total Cost** | — |
"""


def make_orch_bean(
    status: str = "Done",
    started: str = "2026-04-30 10:00",
    completed: str = "2026-04-30 11:30",
    duration: str = "1h 30m",
    task1_status: str = "Done",
    task2_status: str = "Done",
    t1_dur: str = "45m",
    t1_in: str = "10000",
    t1_out: str = "2000",
    t1_cost: str = "$0.30",
    t2_dur: str = "30m",
    t2_in: str = "5000",
    t2_out: str = "1000",
    t2_cost: str = "$0.15",
    total_tasks: str = "2",
    total_duration: str = "1h 30m",
    total_tok_in: str = "15000",
    total_tok_out: str = "3000",
    total_cost: str = "$0.45",
    personas: str = "— (comma-separated, actual not planned)",
    bounces: str = "— (Tech-QA → Developer kicks)",
    scope_changes: str = "— (in-flight scope edits)",
    contract_violations: str = "— (BEAN-274 catches at compose time)",
    escape_hatch: str = "— (BEAN-272's NONE-justified)",
    dispatch_mode: str = "— (in-process / tmux-worker / mixed)",
) -> str:
    return BEAN_WITH_ORCH.format(
        status=status,
        started=started,
        completed=completed,
        duration=duration,
        task1_status=task1_status,
        task2_status=task2_status,
        t1_dur=t1_dur,
        t1_in=t1_in,
        t1_out=t1_out,
        t1_cost=t1_cost,
        t2_dur=t2_dur,
        t2_in=t2_in,
        t2_out=t2_out,
        t2_cost=t2_cost,
        total_tasks=total_tasks,
        total_duration=total_duration,
        total_tok_in=total_tok_in,
        total_tok_out=total_tok_out,
        total_cost=total_cost,
        personas=personas,
        bounces=bounces,
        scope_changes=scope_changes,
        contract_violations=contract_violations,
        escape_hatch=escape_hatch,
        dispatch_mode=dispatch_mode,
    )


def make_legacy_bean(
    status: str = "Done",
    started: str = "2026-01-15 10:00",
    completed: str = "2026-01-15 10:30",
    duration: str = "30m",
    task1_status: str = "Done",
    total_tasks: str = "1",
    total_duration: str = "30m",
) -> str:
    return BEAN_LEGACY.format(
        status=status,
        started=started,
        completed=completed,
        duration=duration,
        task1_status=task1_status,
        total_tasks=total_tasks,
        total_duration=total_duration,
    )


def write_bean(tmp_path: Path, slug: str, content: str) -> Path:
    """Write a bean file under the canonical layout: tmp/ai/beans/<slug>/bean.md."""
    bean_dir = tmp_path / "ai" / "beans" / slug
    bean_dir.mkdir(parents=True)
    bean_file = bean_dir / "bean.md"
    bean_file.write_text(content)
    return bean_file


# Auto-mock the worktree fallback so host-state never leaks into tests.
@pytest.fixture(autouse=True)
def _isolate_worktree_fallback(monkeypatch):
    """Default: pretend no /tmp/agentic-task-* worktrees exist.

    Tests that exercise the fallback path override this with their own
    monkeypatch.
    """
    monkeypatch.setattr(
        _mod, "infer_dispatch_mode_from_worktrees", lambda bean_id: None,
    )
    # git_branch_duration touches the real repo — neuter it so our fixture
    # bean's Duration field is deterministic.
    monkeypatch.setattr(_mod, "git_branch_duration", lambda: None)


# ---------------------------------------------------------------------------
# extract_bean_id
# ---------------------------------------------------------------------------


class TestExtractBeanId:
    def test_extracts_canonical_id(self, tmp_path):
        d = tmp_path / "BEAN-099-some-slug"
        d.mkdir()
        assert extract_bean_id(d) == "BEAN-099"

    def test_returns_none_when_no_match(self, tmp_path):
        d = tmp_path / "not-a-bean"
        d.mkdir()
        assert extract_bean_id(d) is None

    def test_handles_multi_digit_id(self, tmp_path):
        d = tmp_path / "BEAN-12345-x"
        d.mkdir()
        assert extract_bean_id(d) == "BEAN-12345"


# ---------------------------------------------------------------------------
# has_orchestration_telemetry
# ---------------------------------------------------------------------------


class TestHasOrchestrationTelemetry:
    def test_present(self):
        content = make_orch_bean()
        assert has_orchestration_telemetry(content) is True

    def test_absent(self):
        content = make_legacy_bean()
        assert has_orchestration_telemetry(content) is False

    def test_empty_string(self):
        assert has_orchestration_telemetry("") is False


# ---------------------------------------------------------------------------
# parse_orchestration_field / replace_orchestration_field — scoping
# ---------------------------------------------------------------------------


class TestOrchestrationFieldIO:
    def test_parse_returns_value(self):
        content = make_orch_bean(personas="developer, tech-qa")
        assert parse_orchestration_field(
            content, "Personas activated"
        ) == "developer, tech-qa"

    def test_parse_returns_none_when_section_missing(self):
        content = make_legacy_bean()
        assert parse_orchestration_field(content, "Personas activated") is None

    def test_replace_updates_value(self):
        content = make_orch_bean()
        result = replace_orchestration_field(
            content, "Personas activated", "developer, tech-qa",
        )
        assert parse_orchestration_field(
            result, "Personas activated"
        ) == "developer, tech-qa"

    def test_replace_noop_when_section_missing(self):
        content = make_legacy_bean()
        result = replace_orchestration_field(
            content, "Personas activated", "developer",
        )
        assert result == content

    def test_replace_does_not_touch_top_metadata_table(self):
        """The top metadata table has its own **Started** / **Completed** rows.
        replace_orchestration_field must only edit rows inside the
        Orchestration Telemetry section, never the top table.
        """
        # Use an Orchestration field name that does NOT appear in the
        # top table — but verify by direct substring count that the top
        # table's `Started` field is untouched even when we ask for an
        # Orchestration replacement.
        content = make_orch_bean()
        before_started = parse_metadata_field(content, "Started")
        result = replace_orchestration_field(
            content, "Personas activated", "developer",
        )
        # Top-table Started must not change.
        assert parse_metadata_field(result, "Started") == before_started


# ---------------------------------------------------------------------------
# telemetry_owners_with_data
# ---------------------------------------------------------------------------


class TestTelemetryOwnersWithData:
    def test_collects_owners_with_data(self):
        content = make_orch_bean()  # both rows fully populated
        assert telemetry_owners_with_data(content) == ["developer", "tech-qa"]

    def test_skips_owners_with_no_data(self):
        # Make the second row sentinel-only across all data cols.
        content = make_orch_bean(
            t2_dur=SENTINEL, t2_in=SENTINEL, t2_out=SENTINEL, t2_cost=SENTINEL,
        )
        assert telemetry_owners_with_data(content) == ["developer"]

    def test_dedupes_repeated_owners_in_order(self):
        # Author both rows as `developer` and confirm we only see it once.
        content = make_orch_bean()
        content = content.replace(
            "| 2 | Second task | tech-qa |",
            "| 2 | Second task | developer |",
        )
        assert telemetry_owners_with_data(content) == ["developer"]

    def test_empty_when_all_sentinel(self):
        content = make_orch_bean(
            t1_dur=SENTINEL, t1_in=SENTINEL, t1_out=SENTINEL, t1_cost=SENTINEL,
            t2_dur=SENTINEL, t2_in=SENTINEL, t2_out=SENTINEL, t2_cost=SENTINEL,
        )
        assert telemetry_owners_with_data(content) == []


# ---------------------------------------------------------------------------
# collect_dispatch_markers / compute_dispatch_mode
# ---------------------------------------------------------------------------


class TestDispatchMarkers:
    def test_no_marker_dir_returns_empty(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        assert collect_dispatch_markers(bean_dir) == []

    def test_reads_marker_files(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("in-process\n")
        (marker_dir / "task-2-mode").write_text("tmux-worker\n")
        modes = collect_dispatch_markers(bean_dir)
        assert sorted(modes) == ["in-process", "tmux-worker"]

    def test_skips_files_not_named_task(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "README").write_text("ignore me")
        (marker_dir / "task-1-mode").write_text("in-process")
        modes = collect_dispatch_markers(bean_dir)
        assert modes == ["in-process"]

    def test_skips_empty_marker(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("")
        (marker_dir / "task-2-mode").write_text("tmux-worker")
        modes = collect_dispatch_markers(bean_dir)
        assert modes == ["tmux-worker"]


class TestComputeDispatchMode:
    def test_uniform_in_process(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("in-process")
        (marker_dir / "task-2-mode").write_text("in-process")
        assert compute_dispatch_mode(bean_dir, "BEAN-099") == "in-process"

    def test_uniform_tmux_worker(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("tmux-worker")
        assert compute_dispatch_mode(bean_dir, "BEAN-099") == "tmux-worker"

    def test_mixed(self, tmp_path):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("in-process")
        (marker_dir / "task-2-mode").write_text("tmux-worker")
        assert compute_dispatch_mode(bean_dir, "BEAN-099") == "mixed"

    def test_no_markers_falls_back_to_worktree_heuristic(
        self, tmp_path, monkeypatch
    ):
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        # Override fallback: simulate worktrees present.
        monkeypatch.setattr(
            _mod,
            "infer_dispatch_mode_from_worktrees",
            lambda bean_id: "tmux-worker",
        )
        assert compute_dispatch_mode(bean_dir, "BEAN-099") == "tmux-worker"

    def test_no_markers_no_worktrees_defaults_to_in_process(self, tmp_path):
        # Autouse fixture already mocks infer_dispatch_mode_from_worktrees → None.
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        assert compute_dispatch_mode(bean_dir, "BEAN-099") == "in-process"


# ---------------------------------------------------------------------------
# stamp_orchestration_telemetry — direct unit-level
# ---------------------------------------------------------------------------


class TestStampOrchestrationTelemetry:
    def test_no_section_is_silent_noop(self, tmp_path):
        content = make_legacy_bean()
        bean_dir = tmp_path / "BEAN-098-legacy"
        bean_dir.mkdir()
        result, actions = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-098",
        )
        assert result == content
        assert actions == []

    def test_populates_personas_from_telemetry_owners(self, tmp_path):
        content = make_orch_bean()
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        result, actions = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-099",
        )
        personas = parse_orchestration_field(result, "Personas activated")
        assert personas == "developer, tech-qa"
        assert any(a.startswith("Personas=") for a in actions)

    def test_populates_dispatch_mode_from_markers(self, tmp_path):
        content = make_orch_bean()
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        marker_dir = bean_dir / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("tmux-worker")
        (marker_dir / "task-2-mode").write_text("tmux-worker")
        result, actions = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-099",
        )
        assert parse_orchestration_field(
            result, "Dispatch mode"
        ) == "tmux-worker"
        assert any(a.startswith("Dispatch=") for a in actions)

    def test_zero_fills_persona_recorded_counters(self, tmp_path):
        content = make_orch_bean()
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        result, _ = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-099",
        )
        # All four persona-recorded counters should now read "0 (...)" —
        # the "0" plus the preserved hint.
        for field in (
            "Bounces",
            "Scope changes",
            "Contract violations",
            "Inputs escape-hatch invocations",
        ):
            value = parse_orchestration_field(result, field)
            assert value is not None
            assert value.startswith("0"), f"{field}: {value!r}"
            assert "(" in value, (
                f"{field} should preserve hint suffix: {value!r}"
            )

    def test_preserves_persona_recorded_nonzero_value(self, tmp_path):
        # Tech-QA already recorded Bounces=2; the hook must NOT clobber it.
        content = make_orch_bean(
            bounces="2 (Tech-QA → Developer kicks)",
        )
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        result, actions = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-099",
        )
        assert parse_orchestration_field(
            result, "Bounces"
        ) == "2 (Tech-QA → Developer kicks)"
        # No Bounces=0 action emitted.
        assert not any(a.startswith("Bounces=") for a in actions)

    def test_idempotent_re_run(self, tmp_path):
        content = make_orch_bean()
        bean_dir = tmp_path / "BEAN-099-x"
        bean_dir.mkdir()
        first, first_actions = stamp_orchestration_telemetry(
            content, bean_dir, "BEAN-099",
        )
        # Second invocation on the post-stamp content must not emit any
        # additional actions and must not change content.
        second, second_actions = stamp_orchestration_telemetry(
            first, bean_dir, "BEAN-099",
        )
        assert second == first
        assert second_actions == []


# ---------------------------------------------------------------------------
# handle_bean_file integration — fires only on Done, only when block exists
# ---------------------------------------------------------------------------


class TestHandleBeanFileOrchestrationIntegration:
    """End-to-end: drop a bean.md under tmp_path/ai/beans/BEAN-NNN-slug/
    and call handle_bean_file(). Verify the orchestration block is
    populated when status flips to Done, untouched for legacy beans, and
    idempotent on re-run.
    """

    def test_done_populates_personas_and_dispatch(self, tmp_path):
        # Status already Done so handle_bean_file's Done-branch fires.
        bean_file = write_bean(
            tmp_path,
            "BEAN-099-orch-test",
            make_orch_bean(status="Done"),
        )
        # Drop a marker indicating the in-process path was used.
        marker_dir = bean_file.parent / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("in-process")
        (marker_dir / "task-2-mode").write_text("in-process")

        actions = handle_bean_file(bean_file, "2026-04-30 11:30")
        content = bean_file.read_text()

        # Personas and Dispatch mode populated.
        assert parse_orchestration_field(
            content, "Personas activated"
        ) == "developer, tech-qa"
        assert parse_orchestration_field(
            content, "Dispatch mode"
        ) == "in-process"
        # Counters zero-filled.
        for field in (
            "Bounces",
            "Scope changes",
            "Contract violations",
            "Inputs escape-hatch invocations",
        ):
            val = parse_orchestration_field(content, field)
            assert val is not None and val.startswith("0"), (
                f"{field} not zero-filled: {val!r}"
            )
        # Actions list mentions our orchestration stamps.
        joined = " | ".join(actions)
        assert "Personas=" in joined
        assert "Dispatch=" in joined

    def test_done_legacy_bean_no_silent_injection(self, tmp_path):
        bean_file = write_bean(
            tmp_path,
            "BEAN-098-legacy",
            make_legacy_bean(status="Done"),
        )

        actions = handle_bean_file(bean_file, "2026-01-15 10:30")
        result = bean_file.read_text()

        # The contract under test: no Orchestration Telemetry section is
        # injected for legacy beans (existing pre-BEAN-278 stamping of
        # Total Tokens / Total Cost from per-task rows is allowed and
        # unrelated to this bean).
        assert has_orchestration_telemetry(result) is False
        # No orchestration-related actions emitted.
        joined = " | ".join(actions)
        assert "Personas=" not in joined
        assert "Dispatch=" not in joined
        for field in (
            "Bounces",
            "Scope changes",
            "Contract violations",
            "Inputs escape-hatch invocations",
        ):
            assert f"{field}=" not in joined

    def test_idempotent_on_rerun(self, tmp_path):
        bean_file = write_bean(
            tmp_path,
            "BEAN-099-orch-rerun",
            make_orch_bean(status="Done"),
        )
        marker_dir = bean_file.parent / ".orchestration"
        marker_dir.mkdir()
        (marker_dir / "task-1-mode").write_text("tmux-worker")
        (marker_dir / "task-2-mode").write_text("tmux-worker")

        # First run — stamps orchestration block.
        handle_bean_file(bean_file, "2026-04-30 11:30")
        first = bean_file.read_text()

        # Second run — must not change anything related to orchestration.
        actions = handle_bean_file(bean_file, "2026-04-30 11:30")
        second = bean_file.read_text()

        assert second == first
        joined = " | ".join(actions)
        assert "Personas=" not in joined
        assert "Dispatch=" not in joined
        assert "Bounces=" not in joined

    def test_in_progress_does_not_stamp_orchestration(self, tmp_path):
        """Hook stamps orchestration only on Done. In Progress beans must
        leave the Orchestration Telemetry block untouched."""
        bean_file = write_bean(
            tmp_path,
            "BEAN-099-orch-ip",
            make_orch_bean(
                status="In Progress",
                completed=SENTINEL,
                duration=SENTINEL,
                task1_status="In Progress",
                task2_status="Pending",
            ),
        )
        handle_bean_file(bean_file, "2026-04-30 11:30")
        content = bean_file.read_text()
        # Personas activated still the sentinel — not auto-filled.
        personas = parse_orchestration_field(content, "Personas activated")
        assert personas is not None
        assert personas.startswith(SENTINEL), (
            f"Personas should still be sentinel pre-Done: {personas!r}"
        )
        dispatch = parse_orchestration_field(content, "Dispatch mode")
        assert dispatch is not None
        assert dispatch.startswith(SENTINEL)

    def test_done_preserves_persona_recorded_bounces(self, tmp_path):
        """The /handoff and /spawn-task skills increment Bounces inline.
        When the hook fires on Done, it must not overwrite that value
        with 0."""
        bean_file = write_bean(
            tmp_path,
            "BEAN-099-orch-bounces",
            make_orch_bean(
                status="Done",
                bounces="3 (Tech-QA → Developer kicks)",
            ),
        )
        handle_bean_file(bean_file, "2026-04-30 11:30")
        content = bean_file.read_text()
        assert parse_orchestration_field(
            content, "Bounces"
        ) == "3 (Tech-QA → Developer kicks)"
