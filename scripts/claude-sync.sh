#!/usr/bin/env bash
# claude-sync.sh — Install git hooks and sync .claude/ content via submodule.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$REPO_ROOT/scripts/githooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"

# --- Install versioned hooks ---
if [ -d "$HOOKS_SRC" ]; then
    for hook in "$HOOKS_SRC"/*; do
        [ -f "$hook" ] || continue
        name="$(basename "$hook")"
        cp "$hook" "$HOOKS_DST/$name"
        chmod +x "$HOOKS_DST/$name"
        echo "[claude-kit] Installed hook: $name"
    done
fi

# --- Sync .claude/kit submodule ---
if [ -e "$REPO_ROOT/.claude/kit/.git" ] || grep -q '\[submodule.*claude/kit' "$REPO_ROOT/.gitmodules" 2>/dev/null; then
    echo "[claude-kit] Syncing submodule .claude/kit..."
    git submodule sync --recursive
    git submodule update --init --recursive
    echo "[claude-kit] Submodule sync complete."
else
    echo "[claude-kit] WARNING: No .claude/kit submodule found."
    echo "[claude-kit] Add it with: git submodule add <url> .claude/kit"
    exit 1
fi

# --- Rebuild assembly symlinks ---
LINK_SCRIPT="$REPO_ROOT/scripts/claude-link.sh"
if [ -x "$LINK_SCRIPT" ]; then
    "$LINK_SCRIPT"
else
    echo "[claude-kit] WARNING: scripts/claude-link.sh not found or not executable."
    echo "[claude-kit] Symlinks may be stale."
fi
