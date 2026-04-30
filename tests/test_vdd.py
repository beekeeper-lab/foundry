"""Tests for foundry_app.services.vdd — programmatic VDD gate runner.

Covers BEAN-277 Task 02 acceptance:

1.  Parser — recognizes prefixes (one item per evidence type)
2.  Parser — multiple criteria (BEAN-273 oracle)
3.  Parser — empty AC section raises a clear error
4.  Runner — test evidence pass
5.  Runner — test evidence fail
6.  Runner — lint evidence pass
7.  Runner — file-exists evidence (match + no-match)
8.  Runner — file-contains evidence (substring present + absent)
9.  Runner — manual evidence (no prefix → MANUAL)
10. Runner — aggregate verdict (PASS / FAIL / PARTIAL)
11. Runner — report file written with correct shape
12. Merge-bean gate — precondition refuses when VDD report missing / not PASS
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from foundry_app.services import vdd
from foundry_app.services.vdd import (
    EMPTY,
    FAIL,
    PARTIAL,
    PASS,
    RESULT_FAIL,
    RESULT_MANUAL,
    RESULT_PASS,
    Criterion,
    CriterionResult,
    VDDReport,
    aggregate_verdict,
    parse_acceptance_criteria,
    render_report,
    report_path,
    run_criterion,
    run_vdd,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bean(
    repo_root: Path,
    bean_id: str,
    ac_block: str,
    *,
    slug: str = "demo",
) -> Path:
    """Create a minimal bean directory with the given Acceptance Criteria block."""
    bean_dir = repo_root / "ai" / "beans" / f"{bean_id}-{slug}"
    bean_dir.mkdir(parents=True, exist_ok=True)
    body = (
        f"# {bean_id}: synthetic\n\n"
        "## Acceptance Criteria\n\n"
        f"{ac_block}\n\n"
        "## Notes\n"
    )
    (bean_dir / "bean.md").write_text(body, encoding="utf-8")
    return bean_dir


# ---------------------------------------------------------------------------
# 1. Parser — recognizes each evidence-type prefix
# ---------------------------------------------------------------------------


def test_parser_recognizes_each_prefix():
    """One AC item per evidence type parses to the right Criterion record."""
    md = textwrap.dedent(
        """\
        # Header

        ## Acceptance Criteria

        - [ ] (test:tests/test_x.py::test_y) Foo behaves
        - [ ] (lint:foundry_app/) Lint clean
        - [ ] (file:ai/outputs/x.md) File exists
        - [ ] (file-contains:ai/x.md::needle) File contains needle
        - [ ] Manual sign-off required

        ## Notes
        """
    )
    items = parse_acceptance_criteria(md)
    assert len(items) == 5

    assert items[0].kind == "test"
    assert items[0].target == "tests/test_x.py::test_y"
    assert items[0].text == "Foo behaves"

    assert items[1].kind == "lint"
    assert items[1].target == "foundry_app/"

    assert items[2].kind == "file"
    assert items[2].target == "ai/outputs/x.md"

    assert items[3].kind == "file-contains"
    assert items[3].target == "ai/x.md::needle"

    assert items[4].kind is None
    assert items[4].target is None
    assert items[4].text == "Manual sign-off required"


# ---------------------------------------------------------------------------
# 2. Parser — multiple criteria from a real bean (BEAN-273 oracle)
# ---------------------------------------------------------------------------


def test_parser_multiple_criteria_from_real_bean():
    """BEAN-273's bean.md AC section parses to its full visible list."""
    repo_root = Path(__file__).resolve().parents[1]
    bean_md = (
        repo_root / "ai" / "beans" / "BEAN-273-persona-produces-consumes-contracts" / "bean.md"
    ).read_text(encoding="utf-8")
    items = parse_acceptance_criteria(bean_md)
    # BEAN-273 bean.md lists eight AC checklist items in the AC section.
    assert len(items) == 8
    # All eight are unprefixed in BEAN-273 (legacy authoring) → MANUAL.
    assert all(c.kind is None for c in items)
    assert "artifact-types.yml" in items[0].text


# ---------------------------------------------------------------------------
# 3. Parser — empty AC section produces no criteria (runner reports EMPTY)
# ---------------------------------------------------------------------------


def test_parser_empty_ac_section_returns_empty_list(tmp_path: Path):
    """A bean with the AC heading but no checklist items yields [] and run_vdd → EMPTY."""
    md = textwrap.dedent(
        """\
        # Header

        ## Acceptance Criteria

        ## Notes
        """
    )
    items = parse_acceptance_criteria(md)
    assert items == []

    # End-to-end: run_vdd should produce an EMPTY verdict (the user-facing
    # "clear error" is exit code 2 + the EMPTY note in the report).
    bean_dir = _make_bean(tmp_path, "BEAN-901", "")
    # Replace bean.md with a body that has the AC heading but no items.
    (bean_dir / "bean.md").write_text(md, encoding="utf-8")
    report = run_vdd("901", tmp_path)
    assert report.verdict == EMPTY
    assert report.results == []
    assert "no acceptance criteria" in report.note.lower()


# ---------------------------------------------------------------------------
# 4. Runner — test evidence pass
# ---------------------------------------------------------------------------


def test_runner_test_evidence_pass(monkeypatch, tmp_path: Path):
    """test: criterion whose pytest invocation returns 0 → RESULT_PASS."""

    class _Proc:
        returncode = 0
        stdout = "1 passed"
        stderr = ""

    monkeypatch.setattr(vdd.subprocess, "run", lambda *a, **kw: _Proc())
    crit = Criterion(text="pretend test passes", kind="test", target="tests/x.py::y")
    result = run_criterion(crit, tmp_path)
    assert result.result == RESULT_PASS
    assert "ok" in result.details.lower()


# ---------------------------------------------------------------------------
# 5. Runner — test evidence fail
# ---------------------------------------------------------------------------


def test_runner_test_evidence_fail(monkeypatch, tmp_path: Path):
    """test: criterion whose pytest invocation returns nonzero → RESULT_FAIL."""

    class _Proc:
        returncode = 1
        stdout = "FAILED tests/x.py::y - AssertionError"
        stderr = ""

    monkeypatch.setattr(vdd.subprocess, "run", lambda *a, **kw: _Proc())
    crit = Criterion(text="pretend fail", kind="test", target="tests/x.py::y")
    result = run_criterion(crit, tmp_path)
    assert result.result == RESULT_FAIL
    assert "exit=1" in result.details


# ---------------------------------------------------------------------------
# 6. Runner — lint evidence pass on a clean file
# ---------------------------------------------------------------------------


def test_runner_lint_evidence_pass_clean_file(tmp_path: Path):
    """ruff check on a syntactically clean file returns PASS."""
    clean = tmp_path / "clean.py"
    clean.write_text('"""Empty module."""\n', encoding="utf-8")
    crit = Criterion(text="lint clean", kind="lint", target="clean.py")
    result = run_criterion(crit, tmp_path)
    assert result.result == RESULT_PASS
    assert "clean" in result.details.lower()


# ---------------------------------------------------------------------------
# 7. Runner — file-exists evidence
# ---------------------------------------------------------------------------


def test_runner_file_exists_match_and_no_match(tmp_path: Path):
    """file: glob with at least one match → PASS; no match → FAIL."""
    (tmp_path / "present.md").write_text("hi", encoding="utf-8")
    pass_crit = Criterion(text="found", kind="file", target="present.md")
    fail_crit = Criterion(text="missing", kind="file", target="absent-*.md")
    assert run_criterion(pass_crit, tmp_path).result == RESULT_PASS
    assert run_criterion(fail_crit, tmp_path).result == RESULT_FAIL


# ---------------------------------------------------------------------------
# 8. Runner — file-contains evidence (substring present / absent)
# ---------------------------------------------------------------------------


def test_runner_file_contains_present_and_absent(tmp_path: Path):
    """file-contains: substring present → PASS, substring absent → FAIL."""
    target = tmp_path / "doc.md"
    target.write_text("alpha beta gamma\n", encoding="utf-8")

    hit = Criterion(text="has beta", kind="file-contains", target="doc.md::beta")
    miss = Criterion(text="lacks omega", kind="file-contains", target="doc.md::omega")

    hit_result = run_criterion(hit, tmp_path)
    miss_result = run_criterion(miss, tmp_path)
    assert hit_result.result == RESULT_PASS
    assert "beta" in hit_result.details
    assert miss_result.result == RESULT_FAIL


# ---------------------------------------------------------------------------
# 9. Runner — manual evidence (no prefix → MANUAL)
# ---------------------------------------------------------------------------


def test_runner_manual_evidence_emits_pending_line(tmp_path: Path):
    """An unprefixed criterion produces a MANUAL line in the rendered report."""
    crit = Criterion(text="Spot-check the wizard", kind=None, target=None)
    result = run_criterion(crit, tmp_path)
    assert result.result == RESULT_MANUAL

    report = VDDReport(bean_id="BEAN-999", verdict=PARTIAL, results=[result])
    rendered = render_report(report)
    # The MANUAL row appears verbatim in the table.
    assert "MANUAL" in rendered
    assert "Spot-check the wizard" in rendered


# ---------------------------------------------------------------------------
# 10. Runner — aggregate verdict (PASS / FAIL / PARTIAL / EMPTY + manual_pass)
# ---------------------------------------------------------------------------


def test_runner_aggregate_verdict_combinations():
    """Mixed result lists aggregate to the right verdict per the runner spec."""
    p = CriterionResult(criterion=Criterion(text="ok"), result=RESULT_PASS)
    f = CriterionResult(criterion=Criterion(text="bad"), result=RESULT_FAIL)
    m = CriterionResult(criterion=Criterion(text="man"), result=RESULT_MANUAL)

    assert aggregate_verdict([]) == EMPTY
    assert aggregate_verdict([p, p]) == PASS
    assert aggregate_verdict([p, f]) == FAIL
    assert aggregate_verdict([p, m]) == PARTIAL
    # --manual=pass upgrades PARTIAL → PASS
    assert aggregate_verdict([p, m], manual_pass=True) == PASS
    # FAIL still wins even with manual_pass
    assert aggregate_verdict([p, f, m], manual_pass=True) == FAIL


# ---------------------------------------------------------------------------
# 11. Runner — report file written with correct shape
# ---------------------------------------------------------------------------


def test_runner_writes_report_at_canonical_path(tmp_path: Path):
    """run_vdd writes ai/outputs/tech-qa/vdd-<NNN>.md with the documented shape."""
    ac_block = textwrap.dedent(
        """\
        - [ ] (file:bean.md) bean.md exists
        - [ ] Manual sign-off
        """
    ).strip()
    bean_dir = _make_bean(tmp_path, "BEAN-902", ac_block, slug="report-shape")

    # The (file:bean.md) glob is evaluated relative to repo_root; create one
    # at the root so the criterion passes.
    (tmp_path / "bean.md").write_text("placeholder", encoding="utf-8")

    report = run_vdd("902", tmp_path)

    expected_path = report_path("BEAN-902", tmp_path)
    assert expected_path == tmp_path / "ai" / "outputs" / "tech-qa" / "vdd-902.md"
    assert expected_path.is_file(), "VDD report not written to canonical path"

    body = expected_path.read_text(encoding="utf-8")
    assert body.startswith("# VDD Report — BEAN-902")
    assert "**Aggregate verdict:**" in body
    # Markdown table header present.
    assert "| # | Result | Kind | Target | Criterion | Details |" in body
    # One row per criterion (2 ACs → exactly 2 data rows).
    data_rows = [
        ln for ln in body.splitlines() if ln.startswith("| ") and not ln.startswith("| # |")
    ]
    assert len(data_rows) == 2
    # Bean dir was used.
    assert bean_dir.is_dir()
    # Verdict is PARTIAL because the manual row is unprefixed.
    assert report.verdict == PARTIAL


# ---------------------------------------------------------------------------
# 12. Merge-bean gate — precondition refuses when VDD report missing / not PASS
# ---------------------------------------------------------------------------


def _merge_bean_precondition(bean_id: str, repo_root: Path) -> tuple[bool, str]:
    """Mirror the merge-bean SKILL precondition logic for testability.

    Returns ``(ok, reason)``. ``ok=True`` means the gate would allow merge.
    Mirrors the rules in `ai-team-library/claude/skills/merge-bean/SKILL.md`
    Phase 1 step 2a:

    - Missing report           → VDDMissing
    - Aggregate verdict EMPTY  → VDDEmpty
    - Aggregate verdict FAIL   → VDDFail
    - Aggregate verdict PARTIAL→ VDDPartial (no Notes override here)
    - Aggregate verdict PASS   → ok
    """
    rp = report_path(bean_id, repo_root)
    if not rp.is_file():
        return False, f"VDDMissing: no report for {bean_id} at {rp}"
    body = rp.read_text(encoding="utf-8")
    for line in body.splitlines():
        if line.startswith("**Aggregate verdict:**"):
            verdict = line.split("**Aggregate verdict:**", 1)[1].strip()
            if verdict == "PASS":
                return True, "ok"
            return False, f"VDD{verdict.title()}: {bean_id} verdict is {verdict} ({rp})"
    return False, f"VDDMalformed: no verdict line in {rp}"


def test_merge_bean_gate_refuses_without_passing_vdd(tmp_path: Path):
    """The merge-bean precondition refuses when the report is missing or not PASS."""
    # 1. Missing report → refused, error names the bean.
    ok, reason = _merge_bean_precondition("BEAN-903", tmp_path)
    assert ok is False
    assert "BEAN-903" in reason
    assert "VDDMissing" in reason

    # 2. Build a real report via run_vdd whose verdict is PARTIAL.
    bean_dir = _make_bean(
        tmp_path,
        "BEAN-903",
        "- [ ] Manual sign-off only",
        slug="merge-gate",
    )
    assert bean_dir.is_dir()
    report = run_vdd("903", tmp_path)
    assert report.verdict == PARTIAL
    ok, reason = _merge_bean_precondition("BEAN-903", tmp_path)
    assert ok is False
    assert "BEAN-903" in reason
    assert "Partial" in reason or "PARTIAL" in reason

    # 3. Now build a passing report (single file: criterion that matches).
    pass_dir = _make_bean(
        tmp_path,
        "BEAN-904",
        "- [ ] (file:bean.md) bean exists",
        slug="merge-gate-pass",
    )
    assert pass_dir.is_dir()
    # Make the (file:bean.md) glob find something at repo_root.
    (tmp_path / "bean.md").write_text("placeholder", encoding="utf-8")
    pass_report = run_vdd("904", tmp_path)
    assert pass_report.verdict == PASS
    ok, reason = _merge_bean_precondition("BEAN-904", tmp_path)
    assert ok is True, reason


# ---------------------------------------------------------------------------
# Bonus invariant: the merge-bean SKILL.md actually documents the gate.
# (Cheap proof the policy was wired in — a regression catcher.)
# ---------------------------------------------------------------------------


def test_merge_bean_skill_documents_vdd_gate():
    """merge-bean SKILL.md must mention the VDD gate path/verdicts."""
    repo_root = Path(__file__).resolve().parents[1]
    skill = repo_root / "ai-team-library" / "claude" / "skills" / "merge-bean" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert "ai/outputs/tech-qa/vdd-" in text
    assert "VDDMissing" in text
    assert "VDDFail" in text
    assert "PASS" in text


# ---------------------------------------------------------------------------
# Bonus: dogfood — runner against BEAN-277 itself, in a mirror tmp dir so the
# real working tree is not mutated.
# ---------------------------------------------------------------------------


def test_dogfood_run_against_bean_277(tmp_path: Path):
    """Copy BEAN-277's bean.md into a tmp repo and run the gate against it.

    Exercises Phase 1–5 end-to-end without permanently mutating the working
    tree. Confirms the report lands at vdd-277.md.
    """
    src_repo = Path(__file__).resolve().parents[1]
    src_bean = src_repo / "ai" / "beans" / "BEAN-277-programmatic-vdd-gate" / "bean.md"
    dst_bean_dir = tmp_path / "ai" / "beans" / "BEAN-277-programmatic-vdd-gate"
    dst_bean_dir.mkdir(parents=True)
    (dst_bean_dir / "bean.md").write_text(src_bean.read_text(encoding="utf-8"), encoding="utf-8")

    report = run_vdd("277", tmp_path)
    expected = tmp_path / "ai" / "outputs" / "tech-qa" / "vdd-277.md"
    assert expected.is_file()
    # BEAN-277's AC are unprefixed legacy items → at least PARTIAL or FAIL,
    # never EMPTY (the section has items).
    assert report.verdict in {PASS, FAIL, PARTIAL}
    assert report.bean_id == "BEAN-277"


# ---------------------------------------------------------------------------
# CLI-surface check — `foundry-cli vdd` is wired and forwards args through.
# ---------------------------------------------------------------------------


def test_cli_vdd_subcommand_forwards_to_runner(monkeypatch, tmp_path: Path):
    """`foundry-cli vdd 277 --repo-root <tmp>` calls into vdd.main."""
    captured: dict[str, list[str]] = {}

    def fake_main(argv):
        captured["argv"] = list(argv or [])
        return 0

    monkeypatch.setattr("foundry_app.services.vdd.main", fake_main)

    from foundry_app.cli import main as cli_main

    rc = cli_main(["vdd", "277", "--repo-root", str(tmp_path)])
    assert rc == 0
    assert captured["argv"][0] == "277"
    assert "--manual" in captured["argv"]
    assert "--repo-root" in captured["argv"]


# ---------------------------------------------------------------------------
# Exit-code mapping (2 for EMPTY so /merge-bean refuses).
# ---------------------------------------------------------------------------


def test_main_exit_codes(tmp_path: Path):
    """vdd.main: PASS→0, EMPTY→2, FAIL/PARTIAL→1, usage error→3."""
    # PASS path
    _make_bean(tmp_path, "BEAN-905", "- [ ] (file:bean.md) ok", slug="exit-pass")
    (tmp_path / "bean.md").write_text("hi", encoding="utf-8")
    rc_pass = vdd.main(["905", "--repo-root", str(tmp_path)])
    assert rc_pass == 0

    # EMPTY path
    empty_md = "# x\n\n## Acceptance Criteria\n\n## Notes\n"
    bean_dir = tmp_path / "ai" / "beans" / "BEAN-906-empty"
    bean_dir.mkdir(parents=True)
    (bean_dir / "bean.md").write_text(empty_md, encoding="utf-8")
    rc_empty = vdd.main(["906", "--repo-root", str(tmp_path)])
    assert rc_empty == 2

    # PARTIAL path → exit 1
    _make_bean(tmp_path, "BEAN-907", "- [ ] manual only", slug="exit-partial")
    rc_partial = vdd.main(["907", "--repo-root", str(tmp_path)])
    assert rc_partial == 1

    # Usage error: bean ID not found
    rc_missing = vdd.main(["999", "--repo-root", str(tmp_path)])
    assert rc_missing == 3


# ---------------------------------------------------------------------------
# Sanity: normalize_bean_id contract
# ---------------------------------------------------------------------------


def test_normalize_bean_id_accepts_int_and_canonical_form():
    assert vdd.normalize_bean_id("277") == "BEAN-277"
    assert vdd.normalize_bean_id("bean-277") == "BEAN-277"
    assert vdd.normalize_bean_id("BEAN-7") == "BEAN-007"
    with pytest.raises(ValueError):
        vdd.normalize_bean_id("xyz")
