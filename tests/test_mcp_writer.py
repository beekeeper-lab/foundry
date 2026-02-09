"""Tests for foundry_app.services.mcp_writer — MCP config generation."""

import json
from pathlib import Path

from foundry_app.core.models import (
    CompositionSpec,
    ProjectIdentity,
    StackSelection,
    TeamConfig,
)
from foundry_app.services.mcp_writer import write_mcp_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_spec(**overrides) -> CompositionSpec:
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        team=TeamConfig(personas=[]),
    )
    defaults.update(overrides)
    return CompositionSpec(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWriteMcpConfig:

    def test_creates_mcp_json(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, output)

        mcp_file = output / ".claude" / "mcp.json"
        assert mcp_file.is_file()
        assert ".claude/mcp.json" in result.wrote

    def test_baseline_filesystem_server_always_present(self, tmp_path: Path):
        spec = _make_spec(stacks=[])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        assert "mcpServers" in config
        assert "filesystem" in config["mcpServers"]
        assert config["mcpServers"]["filesystem"]["type"] == "stdio"

    def test_valid_json_structure(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        content = (output / ".claude" / "mcp.json").read_text()
        config = json.loads(content)
        assert isinstance(config, dict)
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)

    def test_python_stack_adds_server(self, tmp_path: Path):
        spec = _make_spec(stacks=[StackSelection(id="python")])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        servers = config["mcpServers"]
        assert "filesystem" in servers
        assert "python-docs" in servers

    def test_node_stack_adds_server(self, tmp_path: Path):
        spec = _make_spec(stacks=[StackSelection(id="node")])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        assert "node-docs" in config["mcpServers"]

    def test_react_stack_adds_server(self, tmp_path: Path):
        spec = _make_spec(stacks=[StackSelection(id="react")])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        assert "react-docs" in config["mcpServers"]

    def test_unknown_stack_no_extra_servers(self, tmp_path: Path):
        spec = _make_spec(stacks=[StackSelection(id="cobol")])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        # Only baseline server
        assert list(config["mcpServers"].keys()) == ["filesystem"]

    def test_multiple_stacks(self, tmp_path: Path):
        spec = _make_spec(stacks=[
            StackSelection(id="python"),
            StackSelection(id="react"),
        ])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        config = json.loads((output / ".claude" / "mcp.json").read_text())
        servers = config["mcpServers"]
        assert "filesystem" in servers
        assert "python-docs" in servers
        assert "react-docs" in servers

    def test_empty_stacks(self, tmp_path: Path):
        spec = _make_spec(stacks=[])
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, output)

        assert len(result.wrote) == 1
        assert result.warnings == []
        config = json.loads((output / ".claude" / "mcp.json").read_text())
        assert len(config["mcpServers"]) == 1

    def test_no_warnings_for_valid_spec(self, tmp_path: Path):
        spec = _make_spec(stacks=[StackSelection(id="python")])
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, output)

        assert result.warnings == []

    def test_json_is_pretty_printed(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, output)

        content = (output / ".claude" / "mcp.json").read_text()
        # Pretty-printed JSON has newlines and indentation
        assert "\n" in content
        assert "  " in content
        # Ends with newline
        assert content.endswith("\n")
