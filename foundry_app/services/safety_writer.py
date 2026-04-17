"""Safety writer service — generates .claude/settings.json with native Claude Code hooks.

Posture taxonomy (`baseline` / `hardened` / `regulated`) is documented in
`ai/context/hook-posture.md`. Stack-aware layering on top is documented in
`ai/context/hook-selection.md`. The decision to keep the posture names and
lock the mapping behind `posture_base_packs` is recorded in ADR-006.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from foundry_app.core.models import (
    CloudProvider,
    CompositionSpec,
    HookMode,
    HookPackSelection,
    LibraryIndex,
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
    "pre-commit-lint-js": (
        [],
        [_hook_entry(
            "Edit|Write",
            (
                "npx --no-install prettier --check . 2>/dev/null "
                "|| echo 'WARNING: Prettier formatting issues detected. "
                "Run prettier --write before committing.'; "
                "npx --no-install eslint . 2>/dev/null "
                "|| echo 'WARNING: ESLint issues detected. "
                "Run eslint --fix before committing.'; "
                "npx --no-install tsc --noEmit 2>/dev/null "
                "|| echo 'WARNING: TypeScript errors detected. "
                "Run tsc --noEmit to investigate.'"
            ),
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
    "aws-read-only": (
        [_hook_entry(
            "Bash",
            (
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE '^aws\\s|;\\s*aws\\s|&&\\s*aws\\s'; then "
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE 'aws\\s+\\S+\\s+(create|delete|update|put|run|start|stop|"
                "terminate|modify|attach|detach|associate|disassociate)'; "
                "then echo 'BLOCKED: Only read-only AWS CLI operations "
                "(describe, list, get) are allowed.'; exit 1; fi; fi"
            ),
        )],
        [],
    ),
    "aws-limited-ops": (
        [_hook_entry(
            "Bash",
            (
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE '^aws\\s|;\\s*aws\\s|&&\\s*aws\\s'; then "
                "if echo \"$CLAUDE_TOOL_INPUT\" "
                "| grep -qE 'aws\\s+\\S+\\s+(delete-|terminate-)|"
                "aws\\s+s3\\s+rm\\s+.*--recursive'; "
                "then echo 'BLOCKED: Destructive AWS operations are not allowed. "
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
# Posture taxonomy — see ai/context/hook-posture.md (intent) and
# ai/context/hook-selection.md (stack-aware layering).
# ---------------------------------------------------------------------------

# Posture → always-on packs (stack-independent: git / secrets / compliance).
# If you change this mapping, update ai/context/hook-posture.md and the
# TestPostureTaxonomy lock-in test together.
_POSTURE_BASE: dict[Posture, list[str]] = {
    Posture.BASELINE: ["git-commit-branch"],
    Posture.HARDENED: [
        "git-commit-branch", "git-push-feature", "security-scan",
    ],
    Posture.REGULATED: [
        "git-commit-branch", "git-push-feature", "security-scan",
        "compliance-gate", "post-task-qa",
    ],
}


def posture_base_packs(posture: Posture) -> list[str]:
    """Return the base (stack-independent) pack ids for a posture.

    The returned list is a fresh copy — callers may mutate it. Stack-aware
    layering (expertise lint, cloud guardrails) is applied on top of this
    base in `_stack_aware_default_packs`.

    Canonical reference for what each posture enables:
    `ai/context/hook-posture.md`.
    """
    return list(_POSTURE_BASE.get(posture, []))

# Expertise id → lint/type-check pack id. Multiple expertises that map to the
# same pack only add the pack once. See ai/context/hook-selection.md.
_EXPERTISE_LINT_MAP: dict[str, str] = {
    "python": "pre-commit-lint",
    "python-qt-pyside6": "pre-commit-lint",
    "react": "pre-commit-lint-js",
    "typescript": "pre-commit-lint-js",
    "node": "pre-commit-lint-js",
    "react-native": "pre-commit-lint-js",
    "frontend-build-tooling": "pre-commit-lint-js",
}

# Cloud provider → pack id added at hardened/regulated postures. Baseline
# adds no cloud hook; self-hosted never adds one.
_CLOUD_HOOK_MAP: dict[CloudProvider, str] = {
    CloudProvider.AZURE: "az-limited-ops",
    CloudProvider.AWS: "aws-limited-ops",
}

# Packs that should only appear on a stack that selected them — used to warn
# on explicit user selections that look mismatched.
_STACK_GUARDED_PACKS: dict[str, str] = {
    "pre-commit-lint": "python",
    "pre-commit-lint-js": "js",
    "az-read-only": "azure",
    "az-limited-ops": "azure",
    "aws-read-only": "aws",
    "aws-limited-ops": "aws",
}


# ---------------------------------------------------------------------------
# Build hooks from spec
# ---------------------------------------------------------------------------

def _stack_tags(spec: CompositionSpec) -> set[str]:
    """Return the set of stack tags a composition satisfies.

    Tags correspond to the values in ``_STACK_GUARDED_PACKS`` — ``'python'``,
    ``'js'``, ``'azure'``, ``'aws'``. Used to detect mismatches between an
    explicit pack selection and the declared stack.
    """
    tags: set[str] = set()
    for exp in spec.expertise:
        pack = _EXPERTISE_LINT_MAP.get(exp.id)
        if pack == "pre-commit-lint":
            tags.add("python")
        elif pack == "pre-commit-lint-js":
            tags.add("js")
    for cp in spec.architecture.cloud_providers:
        if cp == CloudProvider.AZURE:
            tags.add("azure")
        elif cp == CloudProvider.AWS:
            tags.add("aws")
    return tags


def _stack_aware_default_packs(spec: CompositionSpec) -> list[str]:
    """Build the default pack id list for a spec without explicit packs.

    Order: posture base, then one lint pack per distinct mapped expertise,
    then one cloud pack per non-baseline cloud provider. Duplicates are
    preserved in insertion order.
    """
    pack_ids: list[str] = posture_base_packs(spec.hooks.posture)

    seen: set[str] = set(pack_ids)
    for exp in spec.expertise:
        lint_id = _EXPERTISE_LINT_MAP.get(exp.id)
        if lint_id and lint_id not in seen:
            pack_ids.append(lint_id)
            seen.add(lint_id)

    if spec.hooks.posture is not Posture.BASELINE:
        for cp in spec.architecture.cloud_providers:
            cloud_id = _CLOUD_HOOK_MAP.get(cp)
            if cloud_id and cloud_id not in seen:
                pack_ids.append(cloud_id)
                seen.add(cloud_id)

    return pack_ids


def _filter_posture_incompatible(
    spec: CompositionSpec,
    packs: list[HookPackSelection],
    library: LibraryIndex | None,
) -> tuple[list[HookPackSelection], list[str]]:
    """Drop packs whose library metadata declares the posture incompatible.

    A defensive filter complementing :func:`validator.run_pre_generation_validation`
    — when a caller bypasses validation (e.g. programmatic use of
    ``write_safety``), this keeps the emitted ``settings.json`` consistent
    with each pack's declared compatibility contract.
    """
    if library is None:
        return packs, []

    posture_key = spec.hooks.posture.value.lower()
    kept: list[HookPackSelection] = []
    warnings: list[str] = []
    for pack in packs:
        info = library.hook_pack_by_id(pack.id)
        row = info.posture_compatibility.get(posture_key) if info else None
        if row and row.get("included", "").strip().lower() == "no":
            warnings.append(
                f"Hook pack '{pack.id}' is incompatible with posture "
                f"'{posture_key}' (pack declares Included: No). Skipped."
            )
            continue
        kept.append(pack)
    return kept, warnings


def _resolve_packs(
    spec: CompositionSpec,
    library: LibraryIndex | None = None,
) -> tuple[list[HookPackSelection], list[str]]:
    """Resolve active hook packs and collect any mismatch warnings.

    If the spec has explicit pack selections, use those (minus disabled) and
    emit a warning for every pack that doesn't match the declared stack.
    Otherwise, build a stack-aware default set from posture + expertise +
    cloud providers.

    When ``library`` is provided, packs whose declared posture compatibility
    excludes the composition's posture are filtered out with a warning.
    """
    if spec.hooks.packs:
        active = [
            p for p in spec.hooks.packs
            if p.enabled and p.mode != HookMode.DISABLED
        ]
        warnings = _mismatch_warnings(spec, active)
    else:
        default_ids = _stack_aware_default_packs(spec)
        active = [HookPackSelection(id=pid) for pid in default_ids]
        warnings = []

    active, posture_warnings = _filter_posture_incompatible(spec, active, library)
    warnings.extend(posture_warnings)
    return active, warnings


def _mismatch_warnings(
    spec: CompositionSpec, packs: list[HookPackSelection],
) -> list[str]:
    """Return a warning for each explicit pack that doesn't match the stack."""
    tags = _stack_tags(spec)
    warnings: list[str] = []
    for pack in packs:
        required = _STACK_GUARDED_PACKS.get(pack.id)
        if required and required not in tags:
            warnings.append(
                f"Hook pack '{pack.id}' requires '{required}' in the stack "
                f"(expertise or cloud providers) but none was selected. "
                f"Keeping the pack for backward compatibility."
            )
    return warnings


def _build_hooks(
    spec: CompositionSpec,
    library: LibraryIndex | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Build the native Claude Code hooks structure from the composition spec."""
    pre_tool_use: list[dict[str, Any]] = []
    post_tool_use: list[dict[str, Any]] = []

    packs, warnings = _resolve_packs(spec, library)

    for pack in packs:
        registry_entry = _HOOK_PACK_REGISTRY.get(pack.id)
        if registry_entry is None:
            logger.warning("Unknown hook pack '%s' — skipping", pack.id)
            continue

        pre_entries, post_entries = registry_entry
        pre_tool_use.extend(pre_entries)
        post_tool_use.extend(post_entries)

    settings = {
        "hooks": {
            "PreToolUse": pre_tool_use,
            "PostToolUse": post_tool_use,
        },
    }
    return settings, warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def write_safety(
    spec: CompositionSpec,
    output_dir: str | Path,
    library: LibraryIndex | None = None,
) -> StageResult:
    """Generate ``.claude/settings.json`` with native Claude Code hooks.

    Maps the spec's hook pack selections (or stack-aware defaults derived
    from posture, expertise, and cloud providers) to concrete ``PreToolUse``
    / ``PostToolUse`` hook definitions in the Claude Code native format.

    Args:
        spec: The composition spec describing the project.
        output_dir: Root directory of the generated project.
        library: Optional indexed library. When provided, packs whose
            declared posture compatibility excludes the composition's
            posture are filtered out with a warning — a defensive
            complement to pre-generation validation.

    Returns:
        A StageResult listing files written and any warnings (e.g., explicit
        pack selections that don't match the declared stack, or packs
        filtered for posture incompatibility).
    """
    root = Path(output_dir)
    wrote: list[str] = []

    settings_dir = root / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)

    settings, warnings = _build_hooks(spec, library)

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
    for w in warnings:
        logger.warning(w)

    return StageResult(wrote=wrote, warnings=warnings)
