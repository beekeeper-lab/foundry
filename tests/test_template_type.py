"""Tests for template type inference in the template browser."""

from __future__ import annotations

import pytest

from foundry_app.ui.screens.library.template_browser import _infer_template_type

# -- Specific filename → expected type --

@pytest.mark.parametrize(
    "filename, expected",
    [
        # checklist
        ("regression-checklist.md", "checklist"),
        ("ship-no-ship-checklist.md", "checklist"),
        ("architecture-review-checklist.md", "checklist"),
        ("security-test-checklist.md", "checklist"),
        ("code-review-checklist.md", "checklist"),
        ("style-consistency-checklist.md", "checklist"),
        ("merge-checklist.md", "checklist"),
        ("accessibility-checklist.md", "checklist"),
        # adr
        ("adr.md", "adr"),
        ("adr-index.md", "adr"),
        ("decision-log.md", "adr"),
        ("decision-matrix.md", "adr"),
        # runbook
        ("release-runbook.md", "runbook"),
        ("rollback-runbook.md", "runbook"),
        ("secrets-rotation-plan.md", "runbook"),
        ("cutover-plan.md", "runbook"),
        ("runbook.md", "runbook"),
        # test (should match BEFORE plan/report)
        ("test-plan.md", "test"),
        ("test-charter.md", "test"),
        ("test-report.md", "test"),
        ("manual-test-case.md", "test"),
        ("traceability-matrix.md", "test"),
        # report (includes bug)
        ("bug-report.md", "report"),
        ("bug-report-wrapper.md", "report"),
        ("status-report.md", "report"),
        ("audit-notes.md", "report"),
        ("conflict-resolution-notes.md", "report"),
        ("research-memo.md", "report"),
        ("debugging-notes.md", "report"),
        ("stakeholder-notes.md", "report"),
        ("synthesis-memo.md", "report"),
        # review
        ("review-comments.md", "review"),
        ("suggested-diffs.md", "review"),
        ("pipeline-yaml-review.md", "review"),
        ("secure-design-review.md", "review"),
        # spec
        ("design-spec.md", "spec"),
        ("task-spec.md", "spec"),
        ("component-spec.md", "spec"),
        ("epic-brief.md", "spec"),
        ("acceptance-criteria.md", "spec"),
        ("ux-acceptance-criteria.md", "spec"),
        ("api-contract.md", "spec"),
        # plan
        ("implementation-plan.md", "plan"),
        ("task-seeding-plan.md", "plan"),
        ("evidence-plan.md", "plan"),
        ("experiment-plan.md", "plan"),
        ("integration-plan.md", "plan"),
        ("mitigations-plan.md", "plan"),
        ("control-mapping.md", "plan"),
        ("environment-matrix.md", "plan"),
        # docs
        ("readme.md", "docs"),
        ("onboarding-guide.md", "docs"),
        ("api-docs.md", "docs"),
        ("content-style-guide.md", "docs"),
        ("annotated-bibliography.md", "docs"),
        # design
        ("user-story.md", "design"),
        ("user-flows.md", "design"),
        ("wireframes-text.md", "design"),
        # other (things that don't match)
        ("pr-description.md", "other"),
        ("system-context.md", "other"),
        ("threat-model-stride.md", "other"),
        ("release-notes.md", "report"),
        ("risk-register.md", "other"),
        ("policy-procedure.md", "other"),
        ("dev-design-decision.md", "adr"),
    ],
)
def test_infer_template_type(filename: str, expected: str) -> None:
    """Each library template should be categorized correctly."""
    assert _infer_template_type(filename) == expected, (
        f"_infer_template_type({filename!r}) returned {_infer_template_type(filename)!r}, "
        f"expected {expected!r}"
    )


def test_infer_unknown_returns_other() -> None:
    """A filename with no matching keywords should return 'other'."""
    assert _infer_template_type("random-thing.md") == "other"


def test_infer_case_insensitive() -> None:
    """Inference should be case-insensitive."""
    assert _infer_template_type("Test-Plan.MD") == "test"
    assert _infer_template_type("ADR.md") == "adr"
