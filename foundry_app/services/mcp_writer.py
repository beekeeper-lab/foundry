"""MCP config writer — generates .claude/mcp.json for generated projects."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from foundry_app.core.models import CompositionSpec, StageResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stack-to-MCP-server mappings
# ---------------------------------------------------------------------------

# Baseline server included in every generated project.
_BASELINE_SERVERS: dict[str, dict] = {
    "filesystem": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@anthropic/mcp-filesystem"],
    },
}

# Stack-specific MCP servers suggested per stack ID.
_STACK_SERVERS: dict[str, dict[str, dict]] = {
    "python": {
        "python-docs": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-python-docs"],
        },
    },
    "node": {
        "node-docs": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-node-docs"],
        },
    },
    "react": {
        "react-docs": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-react-docs"],
        },
    },
    "typescript": {
        "typescript-docs": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@anthropic/mcp-typescript-docs"],
        },
    },
}


def write_mcp_config(
    spec: CompositionSpec,
    output_dir: str | Path,
) -> StageResult:
    """Generate .claude/mcp.json for the project.

    Produces a baseline filesystem MCP server for every project,
    plus stack-specific servers for recognized stacks.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    out_root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    # Start with baseline servers
    servers: dict[str, dict] = dict(_BASELINE_SERVERS)

    # Add stack-specific servers
    for stack_sel in spec.stacks:
        stack_servers = _STACK_SERVERS.get(stack_sel.id)
        if stack_servers:
            servers.update(stack_servers)
            logger.debug("Added MCP servers for stack '%s'", stack_sel.id)

    mcp_config = {"mcpServers": servers}

    # Write the file
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
