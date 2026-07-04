"""Real-library generation invariants (SPEC-028 CI regeneration check).

The generator e2e tests use fixture libraries; this suite generates the
flagship example against the REAL ai-team-library and asserts the
invariants the 2026-07 audit established. It catches library/codegen
drift that fixture-based tests cannot (e.g. a pack losing its entry
file, hook scripts disappearing, agents losing frontmatter).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from foundry_app.io.composition_io import load_composition
from foundry_app.services.generator import generate_project

REPO = Path(__file__).resolve().parent.parent
LIBRARY = REPO / "ai-team-library"
EXAMPLE = REPO / "examples" / "small-python-team.yml"

pytestmark = pytest.mark.skipif(
    not (LIBRARY.is_dir() and EXAMPLE.is_file()),
    reason="real library or example composition not present",
)


@pytest.fixture(scope="module")
def generated(tmp_path_factory) -> Path:
    # generate_project treats output_root as the project directory itself.
    target = tmp_path_factory.mktemp("invariants") / "project"
    spec = load_composition(EXAMPLE)
    generate_project(spec, LIBRARY, output_root=target)
    assert (target / "CLAUDE.md").is_file()
    return target


class TestAgentInvariants:
    def test_every_agent_has_frontmatter(self, generated: Path):
        agents = list((generated / ".claude" / "agents").glob("*.md"))
        assert agents, "no agents generated"
        for agent in agents:
            text = agent.read_text(encoding="utf-8")
            assert text.startswith("---\n"), f"{agent.name}: no frontmatter"
            fm = text.split("---\n")[1]
            assert f"name: {agent.stem}" in fm
            assert "description:" in fm

    def test_model_tiering_applied(self, generated: Path):
        """Library defaults: team-lead/architect on the strongest tier."""
        tl = (generated / ".claude" / "agents" / "team-lead.md").read_text(
            encoding="utf-8",
        )
        assert "model: opus" in tl


class TestSettingsInvariants:
    def test_hook_events_and_scripts(self, generated: Path):
        settings = json.loads(
            (generated / ".claude" / "settings.json").read_text(encoding="utf-8")
        )
        events = settings["hooks"]
        for event in ("PreToolUse", "PostToolUse", "SessionStart", "Stop"):
            assert event in events, f"missing hook event {event}"
        commands = [
            h["command"] for entries in events.values()
            for e in entries for h in e["hooks"]
        ]
        joined = "\n".join(commands)
        for script in (
            "validate-task-inputs.py", "telemetry-stamp.py", "vdd-gate.py",
            "handoff-reminder.py", "format-on-save.py",
            "session-start-context.py", "stop-quality-reminder.py",
        ):
            assert script in joined, f"{script} not wired"
            assert (generated / ".claude" / "hooks" / script).is_file(), (
                f"{script} wired but not shipped"
            )

    def test_branch_guard_exactly_once(self, generated: Path):
        settings = (generated / ".claude" / "settings.json").read_text(
            encoding="utf-8",
        )
        assert settings.count("Cannot edit files on a protected branch") == 1

    def test_permissions_are_posture_derived(self, generated: Path):
        perms = json.loads(
            (generated / ".claude" / "settings.local.json").read_text(
                encoding="utf-8",
            )
        )["permissions"]
        assert "Bash(git push origin main:*)" in perms["deny"]


class TestContentInvariants:
    def test_expertise_compiled_without_frontmatter(self, generated: Path):
        files = list((generated / "ai" / "generated" / "expertise").glob("*.md"))
        assert files, "no expertise compiled"
        for f in files:
            assert not f.read_text(encoding="utf-8").startswith("---\n"), (
                f"{f.name}: frontmatter leaked into compiled output"
            )

    def test_member_prompts_carry_expertise(self, generated: Path):
        dev = (
            generated / "ai" / "generated" / "members" / "developer.md"
        ).read_text(encoding="utf-8")
        assert "## Expertise Conventions" in dev

    def test_root_artifacts(self, generated: Path):
        assert (generated / ".mcp.json").is_file()
        assert (generated / "MEMORY.md").is_file()
        assert (generated / "manifest.json").is_file()

    def test_seed_bean_is_vdd_checkable(self, generated: Path):
        bean = (
            generated / "ai" / "beans" / "BEAN-001-bootstrap" / "bean.md"
        ).read_text(encoding="utf-8")
        assert "(file:" in bean or "(file-contains:" in bean

    def test_claude_md_links_resolve(self, generated: Path):
        import re

        claude_md = (generated / "CLAUDE.md").read_text(encoding="utf-8")
        for rel in re.findall(r"`(\.claude/agents/[\w/-]+\.md)`", claude_md):
            assert (generated / rel).is_file(), f"dangling link {rel}"
        for rel in re.findall(
            r"`(ai/generated/[\w/-]+\.md)`", claude_md,
        ):
            assert (generated / rel).is_file(), f"dangling link {rel}"
