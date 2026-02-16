"""Safety writer service — generates .claude/settings.json with native Claude Code hooks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from foundry_app.core.models import (
    CompositionSpec,
    HookMode,
    HookPackSelection,
    Posture,
    StageResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hook definitions — each pack maps to PreToolUse / PostToolUse entries
# ---------------------------------------------------------------------------

def _hook_entry(matcher: str, command: str) -> dict[str, Any]:
    """Build a single hook entry in Claude Code native format."""
    return {
        "matcher": matcher,
        "hooks": [{"type": "command", "command": command}],
    }


# Registry: pack id → (pre_tool_use entries, post_tool_use entries)
# Each value is a tuple of (list[dict], list[dict]).
_HOOK_PACK_REGISTRY: dict[str, tuple[list[dict[str, Any]], list[dict[str, Any]]]] = {
    "git-commit-branch": (
        [_hook_entry(
            "Edit|Write|NotebookEdit",
            (
                'branch=$(git branch --show-current 2>/dev/null); '
                'if [ "$branch" = "main" ] || [ "$branch" = "master" ] '
                '|| [ "$branch" = "test" ] || [ "$branch" = "prod" ]; then '
                "echo 'BLOCKED: Cannot edit files on a protected branch "
                "($branch). Create a feature branch first.'; exit 1; fi"
            ),
        )],
        [],
    ),
    "git-push-feature": (
        [_hook_entry(
            "Edit|Write|NotebookEdit",
            (
                'branch=$(git branch --show-current 2>/dev/null); '
                'if [ -n "$branch" ] && ! echo "$branch" '
                "| grep -qE '^(feature|fix|bean|hotfix|chore)/[a-z0-9-]+$'; then "
                "echo \"WARNING: Branch '$branch' does not follow naming convention "
                "(feature|fix|bean|hotfix|chore)/<name>.\"; fi"
            ),
        )],
        [],
    ),
    "pre-commit-lint": (
        [],
        [_hook_entry(
            "Edit|Write",
            "ruff check --quiet . 2>/dev/null || echo 'WARNING: Lint issues detected. "
            "Run ruff check --fix before committing.'",
        )],
    ),
    "security-scan": (
        [],
        [_hook_entry(
            "Edit|Write",
            (
                "git diff --name-only 2>/dev/null "
                "| xargs grep -lE "
                "'(?i)(api[_-]?key|secret[_-]?key|password\\s*=|token\\s*=|"
                "BEGIN (RSA |EC )?PRIVATE KEY)' 2>/dev/null "
                "&& echo 'WARNING: Potential secrets detected in changed files.' "
                "|| true"
            ),
        )],
    ),
    "post-task-qa": (
        [],
        [_hook_entry(
            "Edit|Write",
            "echo 'QA: Verify acceptance criteria and required outputs before "
            "marking task done.'",
        )],
    ),
    "compliance-gate": (
        [],
        [_hook_entry(
            "Edit|Write",
            "echo 'Compliance: Ensure evidence artifacts are collected and "
            "audit trail is maintained.'",
        )],
    ),
    "az-read-only": (
        [_hook_entry(
            "Bash",
            (
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE '^az\\s|;\\s*az\\s|&&\\s*az\\s'; then "
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE 'az\\s+\\S+\\s+(create|delete|update|start|stop|restart|purge|set)'; "
                "then echo 'BLOCKED: Only read-only Azure CLI operations "
                "(show, list, get) are allowed.'; exit 1; fi; fi"
            ),
        )],
        [],
    ),
    "az-limited-ops": (
        [_hook_entry(
            "Bash",
            (
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE '^az\\s|;\\s*az\\s|&&\\s*az\\s'; then "
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE 'az\\s+(group|vm|storage.account|sql.server|sql.db|"
                "keyvault|network.vnet|aks)\\s+delete|az\\s+\\S+\\s+purge'; "
                "then echo 'BLOCKED: Destructive Azure operations are not allowed. "
                "Deployment operations are permitted.'; exit 1; fi; fi"
            ),
        )],
        [],
    ),
    # Workflow packs — no native hooks (managed by workflow, not tool guards)
    "git-generate-pr": ([], []),
    "git-merge-to-test": ([], []),
    "git-merge-to-prod": ([], []),
}


# ---------------------------------------------------------------------------
# Posture → default pack IDs
# ---------------------------------------------------------------------------

_POSTURE_DEFAULTS: dict[Posture, list[str]] = {
    Posture.BASELINE: ["git-commit-branch", "pre-commit-lint"],
    Posture.HARDENED: [
        "git-commit-branch", "pre-commit-lint",
        "git-push-feature", "security-scan",
    ],
    Posture.REGULATED: [
        "git-commit-branch", "pre-commit-lint",
        "git-push-feature", "security-scan",
        "compliance-gate", "post-task-qa",
    ],
}


# ---------------------------------------------------------------------------
# Build hooks from spec
# ---------------------------------------------------------------------------

def _resolve_packs(spec: CompositionSpec) -> list[HookPackSelection]:
    """Resolve which hook packs are active.

    If the spec has explicit pack selections, use those.
    Otherwise, fall back to posture-based defaults.
    """
    if spec.hooks.packs:
        return [p for p in spec.hooks.packs if p.enabled and p.mode != HookMode.DISABLED]

    default_ids = _POSTURE_DEFAULTS.get(spec.hooks.posture, [])
    return [HookPackSelection(id=pid) for pid in default_ids]


def _build_hooks(spec: CompositionSpec) -> dict[str, Any]:
    """Build the native Claude Code hooks structure from the composition spec."""
    pre_tool_use: list[dict[str, Any]] = []
    post_tool_use: list[dict[str, Any]] = []

    packs = _resolve_packs(spec)

    for pack in packs:
        registry_entry = _HOOK_PACK_REGISTRY.get(pack.id)
        if registry_entry is None:
            logger.warning("Unknown hook pack '%s' — skipping", pack.id)
            continue

        pre_entries, post_entries = registry_entry
        pre_tool_use.extend(pre_entries)
        post_tool_use.extend(post_entries)

    return {
        "hooks": {
            "PreToolUse": pre_tool_use,
            "PostToolUse": post_tool_use,
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def write_safety(spec: CompositionSpec, output_dir: str | Path) -> StageResult:
    """Generate ``.claude/settings.json`` with native Claude Code hooks.

    Maps the spec's hook pack selections (or posture-based defaults) to
    concrete ``PreToolUse`` / ``PostToolUse`` hook definitions in the
    Claude Code native format.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.

    Returns:
        A StageResult listing files written and any warnings.
    """
    root = Path(output_dir)
    wrote: list[str] = []
    warnings: list[str] = []

    settings_dir = root / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)

    settings = _build_hooks(spec)

    settings_path = settings_dir / "settings.json"
    settings_path.write_text(
        json.dumps(settings, indent=2) + "\n",
        encoding="utf-8",
    )

    rel_path = str(settings_path.relative_to(root))
    wrote.append(rel_path)

    pack_count = len(settings["hooks"]["PreToolUse"]) + len(settings["hooks"]["PostToolUse"])
    logger.info(
        "Hooks written: posture=%s, hook_entries=%d, path=%s",
        spec.hooks.posture.value,
        pack_count,
        rel_path,
    )

    return StageResult(wrote=wrote, warnings=warnings)
