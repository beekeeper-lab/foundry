"""Reference-integrity guards (SPEC-007).

These tests pin the classes of reference rot found in the 2026-07 audit:
stale submodule paths, dangling template paths, renamed library dirs, and
slash-commands referenced by kit agents that don't exist anywhere.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / ".claude" / "shared"
LIBRARY = REPO / "ai-team-library"

pytestmark = pytest.mark.skipif(
    not KIT.is_dir(), reason="claude-kit submodule not initialized"
)


def test_no_stale_kit_submodule_path():
    """The submodule moved from .claude/kit to .claude/shared."""
    offenders = [
        str(f.relative_to(REPO))
        for f in KIT.rglob("*.md")
        if ".claude/kit" in f.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_no_stacks_references_in_library():
    """The library renamed stacks/ to expertise/."""
    offenders = [
        str(f.relative_to(REPO))
        for f in LIBRARY.rglob("*.md")
        if "stacks/" in f.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_artifact_type_template_paths_resolve():
    registry = LIBRARY / "contracts" / "artifact-types.yml"
    content = registry.read_text(encoding="utf-8")
    paths = re.findall(r"template-path:\s*(\S+)", content)
    missing = [
        p for p in paths
        if p not in ("null", "~") and not (LIBRARY / p).is_file()
    ]
    assert missing == [], f"dangling template-path entries: {missing}"


def test_kit_agent_command_references_exist():
    """Every /command a kit agent tells the model to run must exist as a
    command or skill in the kit or the project-local layer."""
    known: set[str] = set()
    for base in (KIT, REPO / ".claude" / "local"):
        for cmd in base.glob("commands/**/*.md"):
            known.add(cmd.stem)
        for skill in base.glob("skills/**/SKILL.md"):
            known.add(skill.parent.name)

    # Words that look like /commands but aren't (shell paths, flags, docs).
    ignore = {
        "tmp", "dev", "etc", "usr", "bin", "home", "opt", "var",
        # documentation placeholders and path fragments, not commands
        "command-name", "tasks", "internal",
    }

    missing: dict[str, set[str]] = {}
    for agent in KIT.glob("agents/*.md"):
        text = agent.read_text(encoding="utf-8")
        for ref in re.findall(r"(?<![\w/.])/([a-z][a-z0-9-]{2,})\b", text):
            if ref in known or ref in ignore:
                continue
            missing.setdefault(agent.name, set()).add(ref)

    assert missing == {}, f"agents reference nonexistent commands: {missing}"


def test_expertise_entry_files_have_frontmatter():
    """SPEC-019: every pack's entry file carries valid frontmatter whose id
    matches the pack directory."""
    import yaml

    problems = []
    for pack in sorted((LIBRARY / "expertise").iterdir()):
        if not pack.is_dir():
            continue
        entry = pack / "conventions.md"
        if not entry.is_file():
            mds = sorted(pack.glob("*.md"))
            if not mds:
                continue
            entry = mds[0]
        text = entry.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            problems.append(f"{pack.name}: no frontmatter on {entry.name}")
            continue
        end = text.find("\n---\n", 4)
        try:
            data = yaml.safe_load(text[4:end])
        except yaml.YAMLError as exc:
            problems.append(f"{pack.name}: malformed frontmatter ({exc})")
            continue
        if not isinstance(data, dict) or data.get("id") != pack.name:
            problems.append(f"{pack.name}: frontmatter id != directory name")
        elif not data.get("entry"):
            problems.append(f"{pack.name}: entry file missing 'entry: true'")
    assert problems == []
