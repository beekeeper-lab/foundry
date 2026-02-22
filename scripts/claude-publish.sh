#!/usr/bin/env bash
# claude-publish.sh — Safe two-step push: submodule first, then the main repo.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KIT_DIR="$REPO_ROOT/.claude/kit"

# --- Step 1: Push .claude/kit submodule if it has unpushed commits ---
if [ -e "$KIT_DIR/.git" ] || [ -f "$KIT_DIR/.git" ]; then
    cd "$KIT_DIR"
    if [ -n "$(git status --porcelain)" ] || \
       [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u} 2>/dev/null || echo '')" ]; then
        echo "[claude-kit] Pushing submodule .claude/kit..."
        if git push; then
            echo "[claude-kit] Submodule push succeeded."
        else
            echo "[claude-kit] ERROR: Submodule push failed. Aborting."
            echo "[claude-kit] Fix the issue in .claude/kit/ and retry."
            exit 1
        fi
    else
        echo "[claude-kit] Submodule .claude/kit is up to date."
    fi
    cd "$REPO_ROOT"
else
    echo "[claude-kit] WARNING: No .claude/kit submodule found. Skipping submodule push."
fi

# --- Step 2: Push the main repo ---
echo "[claude-kit] Pushing main repository..."
if git push; then
    echo "[claude-kit] Main repository push succeeded."
else
    echo "[claude-kit] ERROR: Main repository push failed."
    exit 1
fi

echo "[claude-kit] Publish complete."
