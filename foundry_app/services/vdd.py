"""Programmatic VDD (Verification-Driven Development) gate runner.

Parses a bean's ``## Acceptance Criteria`` section, dispatches each
prefixed criterion to the appropriate evidence runner, and emits a
structured pass/fail report at
``ai/outputs/tech-qa/vdd-<NNN>.md``.

Recognized prefixes (immediately after the ``- [ ]`` checkbox, in
parentheses):

- ``test:<pytest-pattern-or-path>`` — runs ``uv run pytest -q <target>``;
  pass when returncode is 0.
- ``lint:<path>`` — runs ``uv run ruff check <path>``; pass when
  returncode is 0 (ruff prints "All checks passed!" on stdout).
- ``file:<glob>`` — pass when at least one path matches the glob,
  evaluated relative to the repo root.
- ``file-contains:<glob>::<substring>`` — pass when at least one matched
  file contains the substring.

Unprefixed criteria become ``MANUAL`` items. The aggregate verdict is:

- ``EMPTY`` — the bean has no Acceptance Criteria section (or it is empty).
- ``FAIL`` — at least one programmatic criterion failed.
- ``PARTIAL`` — all programmatic criteria pass but at least one manual
  item remains. ``--manual=pass`` upgrades this to ``PASS``.
- ``PASS`` — every criterion passed and no manual items remain.

Exit codes:

- ``0`` — verdict ``PASS``.
- ``1`` — verdict ``FAIL`` or ``PARTIAL``.
- ``2`` — verdict ``EMPTY`` (no AC section / empty AC).
- ``3`` — bean directory not found (or other usage error).

The runner uses ``subprocess.run`` with argument lists only — no shell
interpolation — so target strings cannot inject shell metacharacters.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Recognized criterion-evidence prefixes.
_PREFIX_RE = re.compile(r"^- \[[ xX]\] \(([a-z-]+):([^)]+)\)\s*(.+)$")
# Unprefixed checklist item.
_PLAIN_RE = re.compile(r"^- \[[ xX]\]\s*(.+)$")
# Section heading detector: ``## Acceptance Criteria`` (case-insensitive).
_AC_HEADING_RE = re.compile(r"^##\s+acceptance criteria\s*$", re.IGNORECASE)
_NEXT_HEADING_RE = re.compile(r"^##\s+\S")

# Verdict labels.
PASS = "PASS"
FAIL = "FAIL"
PARTIAL = "PARTIAL"
EMPTY = "EMPTY"

# Per-criterion result labels.
RESULT_PASS = "PASS"
RESULT_FAIL = "FAIL"
RESULT_MANUAL = "MANUAL"


@dataclass
class Criterion:
    """A single acceptance-criterion line parsed from a bean."""

    text: str
    """The human-readable criterion text (after the prefix, if any)."""

    kind: str | None = None
    """Evidence kind: ``test``, ``lint``, ``file``, ``file-contains``,
    or ``None`` for an unprefixed (manual) criterion."""

    target: str | None = None
    """The raw target string after the ``:`` in the prefix."""


@dataclass
class CriterionResult:
    """Outcome of running a single criterion."""

    criterion: Criterion
    result: str  # RESULT_PASS / RESULT_FAIL / RESULT_MANUAL
    details: str = ""
    """Short human-readable explanation (e.g., truncated stderr)."""


@dataclass
class VDDReport:
    """Aggregate result of running all criteria for a bean."""

    bean_id: str
    verdict: str  # PASS / FAIL / PARTIAL / EMPTY
    results: list[CriterionResult] = field(default_factory=list)
    note: str = ""


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------


def parse_acceptance_criteria(bean_md: str) -> list[Criterion]:
    """Extract all checklist items from the bean's Acceptance Criteria section.

    Returns an empty list when the section is missing or contains no
    checklist items.
    """
    lines = bean_md.splitlines()
    in_section = False
    criteria: list[Criterion] = []
    for line in lines:
        if not in_section:
            if _AC_HEADING_RE.match(line):
                in_section = True
            continue
        # We are inside the AC section. Stop at the next ``## `` heading.
        if _NEXT_HEADING_RE.match(line):
            break
        prefixed = _PREFIX_RE.match(line)
        if prefixed:
            kind, target, text = prefixed.group(1), prefixed.group(2), prefixed.group(3)
            criteria.append(Criterion(text=text.strip(), kind=kind, target=target.strip()))
            continue
        plain = _PLAIN_RE.match(line)
        if plain:
            criteria.append(Criterion(text=plain.group(1).strip()))
    return criteria


# --------------------------------------------------------------------------
# Per-criterion runners
# --------------------------------------------------------------------------


def _run_test(target: str, repo_root: Path) -> CriterionResult:
    """Run ``uv run pytest -q <target>`` and report pass/fail."""
    cmd = ["uv", "run", "pytest", "-q", target]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return CriterionResult(
            criterion=Criterion(text="", kind="test", target=target),
            result=RESULT_PASS,
            details=f"pytest {target}: ok",
        )
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-3:]
    return CriterionResult(
        criterion=Criterion(text="", kind="test", target=target),
        result=RESULT_FAIL,
        details=f"pytest exit={proc.returncode}: " + " | ".join(tail),
    )


def _run_lint(target: str, repo_root: Path) -> CriterionResult:
    """Run ``uv run ruff check <target>`` and report pass/fail."""
    cmd = ["uv", "run", "ruff", "check", target]
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return CriterionResult(
            criterion=Criterion(text="", kind="lint", target=target),
            result=RESULT_PASS,
            details=f"ruff {target}: clean",
        )
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()[-3:]
    return CriterionResult(
        criterion=Criterion(text="", kind="lint", target=target),
        result=RESULT_FAIL,
        details=f"ruff exit={proc.returncode}: " + " | ".join(tail),
    )


def _run_file(target: str, repo_root: Path) -> CriterionResult:
    """Pass when at least one path matches the glob ``target``."""
    matches = list(repo_root.glob(target))
    if matches:
        return CriterionResult(
            criterion=Criterion(text="", kind="file", target=target),
            result=RESULT_PASS,
            details=f"matched {len(matches)} path(s)",
        )
    return CriterionResult(
        criterion=Criterion(text="", kind="file", target=target),
        result=RESULT_FAIL,
        details=f"no path matches glob: {target}",
    )


def _run_file_contains(target: str, repo_root: Path) -> CriterionResult:
    """Pass when at least one file matching the glob contains the substring.

    The target is split on the first ``::`` separator: the left side is
    the glob, the right side is the substring to search for.
    """
    if "::" not in target:
        return CriterionResult(
            criterion=Criterion(text="", kind="file-contains", target=target),
            result=RESULT_FAIL,
            details="malformed file-contains target (expected '<glob>::<substring>')",
        )
    glob_part, _, needle = target.partition("::")
    glob_part = glob_part.strip()
    needle = needle.strip()
    if not glob_part or not needle:
        return CriterionResult(
            criterion=Criterion(text="", kind="file-contains", target=target),
            result=RESULT_FAIL,
            details="empty glob or substring in file-contains target",
        )
    matches = list(repo_root.glob(glob_part))
    if not matches:
        return CriterionResult(
            criterion=Criterion(text="", kind="file-contains", target=target),
            result=RESULT_FAIL,
            details=f"no path matches glob: {glob_part}",
        )
    for path in matches:
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if needle in content:
            return CriterionResult(
                criterion=Criterion(text="", kind="file-contains", target=target),
                result=RESULT_PASS,
                details=f"found '{needle}' in {path.relative_to(repo_root)}",
            )
    return CriterionResult(
        criterion=Criterion(text="", kind="file-contains", target=target),
        result=RESULT_FAIL,
        details=f"substring '{needle}' not found in {len(matches)} match(es) of {glob_part}",
    )


_DISPATCH = {
    "test": _run_test,
    "lint": _run_lint,
    "file": _run_file,
    "file-contains": _run_file_contains,
}


def run_criterion(criterion: Criterion, repo_root: Path) -> CriterionResult:
    """Dispatch a single criterion to the correct evidence runner."""
    if criterion.kind is None:
        return CriterionResult(criterion=criterion, result=RESULT_MANUAL, details="no prefix")
    runner = _DISPATCH.get(criterion.kind)
    if runner is None:
        return CriterionResult(
            criterion=criterion,
            result=RESULT_FAIL,
            details=f"unknown evidence kind: {criterion.kind}",
        )
    target = criterion.target or ""
    raw = runner(target, repo_root)
    # Replace the placeholder criterion in the runner's result with the
    # original (text-bearing) criterion, so the report shows the AC text.
    return CriterionResult(criterion=criterion, result=raw.result, details=raw.details)


# --------------------------------------------------------------------------
# Bean discovery
# --------------------------------------------------------------------------


def normalize_bean_id(raw: str) -> str:
    """Normalize a bean ID input to the canonical zero-padded ``BEAN-NNN`` form."""
    s = raw.strip()
    if s.lower().startswith("bean-"):
        s = s[len("bean-") :]
    if not s.isdigit():
        raise ValueError(f"bean ID must be a number or BEAN-<number>, got: {raw!r}")
    return f"BEAN-{int(s):03d}"


def find_bean_dir(bean_id: str, repo_root: Path) -> Path:
    """Locate ``ai/beans/<bean_id>-<slug>/`` for the given canonical bean ID."""
    beans_root = repo_root / "ai" / "beans"
    matches = sorted(beans_root.glob(f"{bean_id}-*"))
    if not matches:
        raise FileNotFoundError(f"no bean directory found for {bean_id} under {beans_root}")
    return matches[0]


# --------------------------------------------------------------------------
# Aggregation & reporting
# --------------------------------------------------------------------------


def aggregate_verdict(results: list[CriterionResult], manual_pass: bool = False) -> str:
    """Compute the aggregate verdict from per-criterion results."""
    if not results:
        return EMPTY
    if any(r.result == RESULT_FAIL for r in results):
        return FAIL
    if any(r.result == RESULT_MANUAL for r in results):
        return PASS if manual_pass else PARTIAL
    return PASS


def render_report(report: VDDReport) -> str:
    """Render a VDDReport as a markdown document."""
    lines: list[str] = []
    lines.append(f"# VDD Report — {report.bean_id}")
    lines.append("")
    lines.append(f"**Aggregate verdict:** {report.verdict}")
    lines.append("")
    if report.note:
        lines.append(f"> {report.note}")
        lines.append("")
    lines.append("| # | Result | Kind | Target | Criterion | Details |")
    lines.append("|---|--------|------|--------|-----------|---------|")
    for i, r in enumerate(report.results, 1):
        kind = r.criterion.kind or "—"
        target = (r.criterion.target or "—").replace("|", r"\|")
        text = r.criterion.text.replace("|", r"\|")
        details = r.details.replace("|", r"\|").replace("\n", " ")
        lines.append(f"| {i} | {r.result} | {kind} | {target} | {text} | {details} |")
    lines.append("")
    return "\n".join(lines)


def report_path(bean_id: str, repo_root: Path) -> Path:
    """Canonical report path for a given bean."""
    return repo_root / "ai" / "outputs" / "tech-qa" / f"vdd-{bean_id[len('BEAN-'):]}.md"


# --------------------------------------------------------------------------
# Top-level runner
# --------------------------------------------------------------------------


def run_vdd(
    bean_id_raw: str,
    repo_root: Path,
    *,
    manual_pass: bool = False,
) -> VDDReport:
    """Run VDD for the given bean ID and return the aggregate report.

    Side effect: writes the rendered markdown report to the canonical
    path. Re-running overwrites the previous report (idempotent).
    """
    bean_id = normalize_bean_id(bean_id_raw)
    bean_dir = find_bean_dir(bean_id, repo_root)
    bean_md_path = bean_dir / "bean.md"
    if not bean_md_path.is_file():
        raise FileNotFoundError(f"bean.md missing in {bean_dir}")
    bean_md = bean_md_path.read_text(encoding="utf-8")

    criteria = parse_acceptance_criteria(bean_md)
    if not criteria:
        report = VDDReport(
            bean_id=bean_id,
            verdict=EMPTY,
            results=[],
            note="No acceptance criteria found — bean cannot be merged.",
        )
    else:
        results = [run_criterion(c, repo_root) for c in criteria]
        verdict = aggregate_verdict(results, manual_pass=manual_pass)
        report = VDDReport(bean_id=bean_id, verdict=verdict, results=results)

    out_path = report_path(bean_id, repo_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_report(report), encoding="utf-8")
    return report


# --------------------------------------------------------------------------
# CLI / module entry point
# --------------------------------------------------------------------------


def _exit_code_for(verdict: str) -> int:
    if verdict == PASS:
        return 0
    if verdict == EMPTY:
        return 2
    return 1  # FAIL or PARTIAL


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m foundry_app.services.vdd`` and the CLI."""
    parser = argparse.ArgumentParser(
        prog="foundry-cli vdd",
        description="Run the programmatic VDD gate against a bean's acceptance criteria.",
    )
    parser.add_argument("bean_id", help="Bean ID (e.g., 277 or BEAN-277)")
    parser.add_argument(
        "--manual",
        choices=["pending", "pass"],
        default="pending",
        help=(
            "How to treat unprefixed (manual) criteria: 'pending' makes the "
            "verdict PARTIAL (default); 'pass' upgrades to PASS when all "
            "programmatic criteria pass."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: current working directory).",
    )
    args = parser.parse_args(argv)

    repo_root = (args.repo_root or Path.cwd()).resolve()
    try:
        report = run_vdd(args.bean_id, repo_root, manual_pass=(args.manual == "pass"))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3

    out_path = report_path(report.bean_id, repo_root)
    print(f"VDD report: {out_path}")
    print(f"Aggregate verdict: {report.verdict}")
    return _exit_code_for(report.verdict)


if __name__ == "__main__":
    sys.exit(main())
