#!/usr/bin/env bash
# claude-sync.sh — Install git hooks and sync .claude/ content.
# Supports both git-submodule (.claude/kit/) and git-subtree (.claude/) patterns.
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

# --- Sync .claude/ content ---
# Check .claude/kit/.git (initialized) OR .gitmodules reference (uninitialized).
if [ -e "$REPO_ROOT/.claude/kit/.git" ] || grep -q '\[submodule.*claude/kit' "$REPO_ROOT/.gitmodules" 2>/dev/null; then
    # Submodule mode
    echo "[claude-kit] Syncing submodule .claude/kit..."
    git submodule sync --recursive
    git submodule update --init --recursive
    echo "[claude-kit] Submodule sync complete."
elif [ -d "$REPO_ROOT/.claude" ]; then
    # Subtree mode
    if git remote get-url claude-kit >/dev/null 2>&1; then
        echo "[claude-kit] Pulling subtree .claude/ from claude-kit remote..."
        if git subtree pull --prefix=.claude claude-kit main --squash -m "Sync .claude/ from claude-kit"; then
            echo "[claude-kit] Subtree sync complete."
        else
            echo "[claude-kit] ERROR: Subtree pull failed (possible merge conflict)."
            echo "[claude-kit] Resolve conflicts manually, then commit."
            exit 1
        fi
    else
        echo "[claude-kit] WARNING: No 'claude-kit' remote found. Skipping subtree sync."
        echo "[claude-kit] Add it with: git remote add claude-kit <url>"
    fi
else
    echo "[claude-kit] WARNING: No .claude/ directory found. Nothing to sync."
fi
