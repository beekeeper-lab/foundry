"""Tests for foundry_app.services.bean_approval — approval gate validator."""

from pathlib import Path

from foundry_app.services.bean_approval import check_bean_approvable


def _bean_header(status: str = "Unapproved", category: str = "Process") -> str:
    return (
        "# BEAN-999: Example Bean\n"
        "\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        "| **Bean ID** | BEAN-999 |\n"
        f"| **Status** | {status} |\n"
        "| **Priority** | Medium |\n"
        "| **Created** | 2026-04-17 |\n"
        "| **Owner** | (unassigned) |\n"
        f"| **Category** | {category} |\n"
        "\n"
    )


def _well_formed_bean() -> str:
    return (
        _bean_header()
        + "## Problem Statement\n\n"
        "Beans lack a concrete approval mechanism.\n\n"
        "## Goal\n\n"
        "Every bean passes an explicit approval check.\n\n"
        "## Scope\n\n"
        "### In Scope\n"
        "- Add approve-bean command\n"
        "- Add validator\n\n"
        "### Out of Scope\n"
        "- Multi-step approvals\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Validator implemented\n"
        "- [ ] All tests pass (`uv run pytest`)\n"
        "- [ ] Lint clean (`uv run ruff check foundry_app/`)\n"
    )


def test_well_formed_bean_passes_approval_check(tmp_path: Path) -> None:
    bean = tmp_path / "bean.md"
    bean.write_text(_well_formed_bean(), encoding="utf-8")

    result = check_bean_approvable(bean)

    assert result.ok is True
    assert result.missing == []
    assert result.bean_id == "BEAN-999"


def test_missing_acceptance_criteria_rejected(tmp_path: Path) -> None:
    body = (
        _bean_header()
        + "## Problem Statement\n\nReal problem.\n\n"
        "## Goal\n\nReal outcome.\n\n"
        "## Scope\n\n"
        "### In Scope\n- Add feature\n\n"
        "### Out of Scope\n- Unrelated changes\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Criterion 1\n"
        "- [ ] Criterion 2\n"
        "- [ ] All tests pass (`uv run pytest`)\n"
        "- [ ] Lint clean (`uv run ruff check foundry_app/`)\n"
    )
    bean = tmp_path / "bean.md"
    bean.write_text(body, encoding="utf-8")

    result = check_bean_approvable(bean)

    assert result.ok is False
    assert "Acceptance Criteria" in result.missing


def test_missing_scope_rejected(tmp_path: Path) -> None:
    body = (
        _bean_header()
        + "## Problem Statement\n\nA real problem.\n\n"
        "## Goal\n\nA real goal.\n\n"
        "## Scope\n\n"
        "### In Scope\n- Item 1\n- Item 2\n\n"
        "### Out of Scope\n- Item 1\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Deliver the thing\n"
    )
    bean = tmp_path / "bean.md"
    bean.write_text(body, encoding="utf-8")

    result = check_bean_approvable(bean)

    assert result.ok is False
    assert "Scope" in result.missing


def test_missing_problem_statement_rejected(tmp_path: Path) -> None:
    body = (
        _bean_header()
        + "## Problem Statement\n\n"
        "What problem does this bean solve? Why does it matter?\n\n"
        "## Goal\n\nA real outcome.\n\n"
        "## Scope\n\n"
        "### In Scope\n- A concrete deliverable\n\n"
        "### Out of Scope\n- Something excluded\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Deliver the thing\n"
    )
    bean = tmp_path / "bean.md"
    bean.write_text(body, encoding="utf-8")

    result = check_bean_approvable(bean)

    assert result.ok is False
    assert "Problem Statement" in result.missing


def test_missing_category_rejected(tmp_path: Path) -> None:
    body = (
        _bean_header(category="(App | Process | Infra)")
        + "## Problem Statement\n\nA real problem.\n\n"
        "## Goal\n\nA real goal.\n\n"
        "## Scope\n\n"
        "### In Scope\n- A concrete deliverable\n\n"
        "### Out of Scope\n- An exclusion\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Deliver the thing\n"
    )
    bean = tmp_path / "bean.md"
    bean.write_text(body, encoding="utf-8")

    result = check_bean_approvable(bean)

    assert result.ok is False
    assert "Category" in result.missing


def test_template_rejected(tmp_path: Path) -> None:
    """The project's own bean template must be rejected by the approval gate."""
    repo_root = Path(__file__).resolve().parent.parent
    template = repo_root / "ai" / "beans" / "_bean-template.md"

    result = check_bean_approvable(template)

    assert result.ok is False
    # Template has BEAN-NNN / placeholder body → bean_id should be None.
    assert result.bean_id is None
    # At minimum, these body sections are placeholder in the template.
    for required in ["Problem Statement", "Goal", "Scope", "Acceptance Criteria"]:
        assert required in result.missing
