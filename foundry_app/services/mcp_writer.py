"""MCP config writer — generates .claude/mcp.json for generated projects."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml

from foundry_app.core.models import CompositionSpec, StageResult

logger = logging.getLogger(__name__)

REGISTRY_RELPATH = Path("workflows") / "mcp-registry.yaml"

_EMITTED_FIELDS = ("type", "command", "args")


def _load_registry(library_root: Path) -> dict[str, Any]:
    """Load and minimally validate the vetted MCP registry YAML."""
    registry_path = library_root / REGISTRY_RELPATH
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"MCP registry must be a mapping: {registry_path}")

    servers = data.get("servers") or {}
    baseline = data.get("baseline") or []
    by_expertise = data.get("by_expertise") or {}

    if not isinstance(servers, dict):
        raise ValueError(f"MCP registry 'servers' must be a mapping: {registry_path}")
    if not isinstance(baseline, list):
        raise ValueError(f"MCP registry 'baseline' must be a list: {registry_path}")
    if not isinstance(by_expertise, dict):
        raise ValueError(
            f"MCP registry 'by_expertise' must be a mapping: {registry_path}"
        )

    for sid, entry in servers.items():
        if not isinstance(entry, dict):
            raise ValueError(f"MCP registry server '{sid}' must be a mapping")
        for field in ("type", "command", "args"):
            if field not in entry:
                raise ValueError(
                    f"MCP registry server '{sid}' missing required field '{field}'"
                )

    return {"servers": servers, "baseline": baseline, "by_expertise": by_expertise}


def _select_server_ids(
    registry: dict[str, Any], expertise_ids: list[str]
) -> list[str]:
    """Return the ordered, de-duplicated list of server IDs to emit."""
    selected: list[str] = []
    seen: set[str] = set()

    for sid in registry["baseline"]:
        if sid not in seen:
            selected.append(sid)
            seen.add(sid)

    for exp_id in expertise_ids:
        for sid in registry["by_expertise"].get(exp_id, []):
            if sid not in seen:
                selected.append(sid)
                seen.add(sid)

    return selected


def write_mcp_config(
    spec: CompositionSpec,
    library_root: str | Path,
    output_dir: str | Path,
) -> StageResult:
    """Generate .claude/mcp.json for the project from the vetted registry.

    The registry at ``<library_root>/workflows/mcp-registry.yaml`` is the
    single source of truth for MCP server references. Baseline servers are
    always emitted; expertise-specific servers are added when the matching
    expertise is selected in the spec.

    Args:
        spec: The composition spec describing the project.
        library_root: Root of the ai-team-library directory.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    lib_root = Path(library_root)
    out_root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    registry = _load_registry(lib_root)
    expertise_ids = [sel.id for sel in spec.expertise]

    server_ids = _select_server_ids(registry, expertise_ids)
    missing = [sid for sid in server_ids if sid not in registry["servers"]]
    if missing:
        raise ValueError(
            f"MCP registry references undefined server(s): {', '.join(missing)}"
        )

    servers: dict[str, dict] = {}
    for sid in server_ids:
        entry = registry["servers"][sid]
        servers[sid] = {field: entry[field] for field in _EMITTED_FIELDS}

    mcp_config = {"mcpServers": servers}

    mcp_path = out_root / ".claude" / "mcp.json"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    mcp_path.write_text(
        json.dumps(mcp_config, indent=2) + "\n",
        encoding="utf-8",
    )

    rel_path = str(mcp_path.relative_to(out_root))
    wrote.append(rel_path)
    logger.info("Wrote MCP config: %s (%d servers)", rel_path, len(servers))

    return StageResult(wrote=wrote, warnings=warnings)
