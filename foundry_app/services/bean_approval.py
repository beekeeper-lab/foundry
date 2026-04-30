"""Validate whether a bean is ready for the Unapproved → Approved transition.

The approval gate checks that a bean has real content in every field a
reviewer would want to evaluate: metadata (Priority, Category), and the
body sections (Problem Statement, Goal, Scope, Acceptance Criteria). A
bean that still contains template placeholder text fails the check.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

# Template placeholder cells in the metadata table.
_PLACEHOLDER_META_VALUES = {
    "BEAN-NNN",
    "YYYY-MM-DD",
    "(App | Process | Infra)",
    "(unassigned)",
    "—",
    "-",
    "",
}

# Template lines inside body sections that indicate nothing was filled in.
_PLACEHOLDER_BODY_LINES = {
    "What problem does this bean solve? Why does it matter?",
    "What is the desired outcome when this bean is complete?",
    "- Item 1",
    "- Item 2",
    "- [ ] Criterion 1",
    "- [ ] Criterion 2",
    # BEAN-275 added a static "Authored by" subnote under the AC heading.
    # It is part of the template, not user-supplied content — treat it as
    # placeholder so the approval gate still rejects an unfilled template.
    "> Authored by: BA (when activated) | Team-Lead (default)",
    # BEAN-277 added the criterion-prefix convention guidance under the AC
    # heading. These multi-line blockquotes are template scaffolding, not
    # user content.
    "> Authored by: BA (when activated) | Team-Lead (default).",
    "> Prefix each item with an evidence-type tag so `/vdd` can verify it",
    "> automatically. See `ai/context/vdd-policy.md` for the full convention.",
    "> Recognized prefixes: `(test:<path>)`, `(lint:<path>)`, `(file:<glob>)`,",
    "> `(file-contains:<glob>::<substring>)`. Unprefixed items become manual.",
    # BEAN-277 added two example AC lines that ship with the template; they
    # are illustrative scaffolding, not real bean content.
    "- [ ] (test:tests/test_foo.py::test_bar) Example prefixed criterion — runs pytest",
    "- [ ] Criterion without a prefix becomes a manual sign-off",
}

# Acceptance-criteria lines that are boilerplate (real, but every bean carries
# them). A bean must have at least one criterion beyond these to be approvable.
_BOILERPLATE_CRITERIA = {
    "- [ ] All tests pass (`uv run pytest`)",
    "- [ ] Lint clean (`uv run ruff check foundry_app/`)",
    # BEAN-277 added prefixed equivalents of the same boilerplate criteria.
    "- [ ] (test:tests/) All tests pass (`uv run pytest`)",
    "- [ ] (lint:foundry_app/) Lint clean (`uv run ruff check foundry_app/`)",
}


class ApprovalCheck(BaseModel):
    """Result of an approval-gate check on a bean.md file."""

    ok: bool
    missing: list[str] = Field(default_factory=list)
    bean_id: str | None = None


def check_bean_approvable(bean_path: Path) -> ApprovalCheck:
    """Return an ApprovalCheck for the bean markdown at `bean_path`."""
    text = bean_path.read_text(encoding="utf-8")
    meta = _parse_metadata_table(text)

    bean_id = meta.get("Bean ID", "")
    if bean_id in _PLACEHOLDER_META_VALUES:
        bean_id = None

    missing: list[str] = []

    if meta.get("Priority", "") in _PLACEHOLDER_META_VALUES:
        missing.append("Priority")
    if meta.get("Category", "") in _PLACEHOLDER_META_VALUES:
        missing.append("Category")

    if not _has_real_content(_section_body(text, "Problem Statement")):
        missing.append("Problem Statement")
    if not _has_real_content(_section_body(text, "Goal")):
        missing.append("Goal")

    scope = _section_body(text, "Scope")
    in_scope = _subsection_body(scope, "In Scope")
    if not _has_real_content(in_scope):
        missing.append("Scope")

    ac = _section_body(text, "Acceptance Criteria")
    if not _has_real_content(ac, boilerplate=_BOILERPLATE_CRITERIA):
        missing.append("Acceptance Criteria")

    return ApprovalCheck(ok=not missing, missing=missing, bean_id=bean_id)


_META_ROW = re.compile(r"^\|\s*\*\*([^|]+?)\*\*\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)


def _parse_metadata_table(text: str) -> dict[str, str]:
    """Extract the bean's `| **Field** | Value |` metadata table entries."""
    return {m.group(1).strip(): m.group(2).strip() for m in _META_ROW.finditer(text)}


def _section_body(text: str, heading: str) -> str:
    """Return the body below `## heading`, stopping at the next `##` section."""
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def _subsection_body(section_body: str, heading: str) -> str:
    """Return the body below `### heading`, stopping at the next `###` heading."""
    pattern = re.compile(
        rf"^### {re.escape(heading)}\s*\n(.*?)(?=\n### |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(section_body)
    return m.group(1).strip() if m else ""


def _has_real_content(body: str, boilerplate: set[str] = frozenset()) -> bool:
    """True when at least one line is real content (not blank, placeholder, boilerplate)."""
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("###"):
            continue
        if line in _PLACEHOLDER_BODY_LINES:
            continue
        if line in boilerplate:
            continue
        return True
    return False
