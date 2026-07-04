"""Tests for foundry_app.services.mcp_writer — MCP config generation."""

import json
from pathlib import Path

import pytest
import yaml

from foundry_app.core.models import (
    CompositionSpec,
    ExpertiseSelection,
    ProjectIdentity,
    TeamConfig,
)
from foundry_app.services.mcp_writer import REGISTRY_RELPATH, write_mcp_config

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LIBRARY_ROOT = Path(__file__).resolve().parents[1] / "ai-team-library"


def _make_spec(**overrides) -> CompositionSpec:
    defaults = dict(
        project=ProjectIdentity(name="Test Project", slug="test-project"),
        team=TeamConfig(personas=[]),
    )
    defaults.update(overrides)
    return CompositionSpec(**defaults)


def _load_registry() -> dict:
    return yaml.safe_load((LIBRARY_ROOT / REGISTRY_RELPATH).read_text())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWriteMcpConfig:

    def test_creates_mcp_json(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, LIBRARY_ROOT, output)

        mcp_file = output / ".mcp.json"
        assert mcp_file.is_file()
        assert ".mcp.json" in result.wrote

    def test_baseline_filesystem_server_always_present(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        assert "mcpServers" in config
        assert "filesystem" in config["mcpServers"]
        assert config["mcpServers"]["filesystem"]["type"] == "stdio"

    def test_valid_json_structure(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        content = (output / ".mcp.json").read_text()
        config = json.loads(content)
        assert isinstance(config, dict)
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)

    def test_unknown_expertise_no_extra_servers(self, tmp_path: Path):
        spec = _make_spec(expertise=[ExpertiseSelection(id="cobol")])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        assert list(config["mcpServers"].keys()) == ["filesystem"]

    def test_empty_expertise(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, LIBRARY_ROOT, output)

        assert len(result.wrote) == 1
        assert result.warnings == []
        config = json.loads((output / ".mcp.json").read_text())
        assert len(config["mcpServers"]) == 1  # filesystem only (SPEC-022)

    def test_baseline_filesystem_uses_real_package(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        filesystem = config["mcpServers"]["filesystem"]
        assert filesystem["command"] == "npx"
        assert "@modelcontextprotocol/server-filesystem" in filesystem["args"]

    def test_workflow_servers_are_opt_in(self, tmp_path: Path):
        """SPEC-022: obsidian/trello are no longer force-installed."""
        spec = _make_spec(expertise=[])
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        assert "obsidian" not in config["mcpServers"]
        assert "trello" not in config["mcpServers"]

    def test_mcp_add_from_registry_by_id(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        spec.mcp.add = {"trello": None}
        spec.mcp.env = {"trello": {"TRELLO_API_KEY": "${TRELLO_API_KEY}"}}
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        trello = config["mcpServers"]["trello"]
        assert trello["command"] == "npx"
        assert trello["env"] == {"TRELLO_API_KEY": "${TRELLO_API_KEY}"}

    def test_mcp_add_inline_definition(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        spec.mcp.add = {"github": {
            "type": "stdio", "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_TOKEN": "${GITHUB_TOKEN}"},
        }}
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        assert config["mcpServers"]["github"]["env"] == {
            "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        }

    def test_mcp_remove_baseline_server(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        spec.mcp.remove = ["filesystem"]
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        assert config["mcpServers"] == {}

    def test_mcp_add_unknown_registry_id_warns(self, tmp_path: Path):
        spec = _make_spec(expertise=[])
        spec.mcp.add = {"nonexistent": None}
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, LIBRARY_ROOT, output)

        assert any("nonexistent" in w for w in result.warnings)

    def test_no_warnings_for_valid_spec(self, tmp_path: Path):
        spec = _make_spec(expertise=[ExpertiseSelection(id="python")])
        output = tmp_path / "output"
        output.mkdir()

        result = write_mcp_config(spec, LIBRARY_ROOT, output)

        assert result.warnings == []

    def test_json_is_pretty_printed(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        content = (output / ".mcp.json").read_text()
        assert "\n" in content
        assert "  " in content
        assert content.endswith("\n")


class TestRegistryInvariant:
    """Regression guards: generated mcp.json never drifts off the registry."""

    @pytest.mark.parametrize(
        "expertise_ids",
        [
            [],
            ["python"],
            ["node"],
            ["react"],
            ["typescript"],
            ["python", "react"],
            ["cobol"],  # unknown expertise → no extra servers, still valid
        ],
    )
    def test_every_emitted_server_matches_registry(
        self, tmp_path: Path, expertise_ids: list[str]
    ):
        spec = _make_spec(
            expertise=[ExpertiseSelection(id=eid) for eid in expertise_ids]
        )
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        registry = _load_registry()

        for server_id, entry in config["mcpServers"].items():
            assert server_id in registry["servers"], (
                f"server '{server_id}' is not in the vetted registry"
            )
            reg_entry = registry["servers"][server_id]
            for field in ("type", "command", "args"):
                assert entry[field] == reg_entry[field], (
                    f"server '{server_id}' field '{field}' drifted from registry"
                )

    def test_no_anthropic_scoped_packages(self, tmp_path: Path):
        spec = _make_spec(
            expertise=[
                ExpertiseSelection(id=e)
                for e in ("python", "node", "react", "typescript")
            ]
        )
        output = tmp_path / "output"
        output.mkdir()

        write_mcp_config(spec, LIBRARY_ROOT, output)

        config = json.loads((output / ".mcp.json").read_text())
        for server_id, entry in config["mcpServers"].items():
            for arg in entry.get("args", []):
                assert "@anthropic/" not in arg, (
                    f"server '{server_id}' still references a fictional "
                    f"@anthropic/* package: {arg}"
                )


class TestRegistryValidation:
    """The writer fails loudly when the registry is missing or malformed."""

    def test_missing_registry_raises(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()
        empty_library = tmp_path / "empty-library"
        empty_library.mkdir()

        with pytest.raises(FileNotFoundError):
            write_mcp_config(spec, empty_library, output)

    def test_malformed_registry_raises(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()
        bad_library = tmp_path / "bad-library"
        (bad_library / "workflows").mkdir(parents=True)
        (bad_library / "workflows" / "mcp-registry.yaml").write_text(
            "- just\n- a\n- list\n"
        )

        with pytest.raises(ValueError, match="must be a mapping"):
            write_mcp_config(spec, bad_library, output)

    def test_server_missing_required_field_raises(self, tmp_path: Path):
        spec = _make_spec()
        output = tmp_path / "output"
        output.mkdir()
        bad_library = tmp_path / "bad-library"
        (bad_library / "workflows").mkdir(parents=True)
        (bad_library / "workflows" / "mcp-registry.yaml").write_text(
            "servers:\n"
            "  broken:\n"
            "    type: stdio\n"
            "    command: npx\n"
            "baseline: [broken]\n"
        )

        with pytest.raises(ValueError, match="missing required field 'args'"):
            write_mcp_config(spec, bad_library, output)
