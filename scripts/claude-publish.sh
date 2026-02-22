#!/usr/bin/env bash
# claude-publish.sh — Safe two-step push: .claude/ changes first, then the main repo.
# Supports both git-submodule (.claude/kit/) and git-subtree (.claude/) patterns.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

# --- Step 1: Push .claude/ changes ---
# Check .claude/kit/.git (initialized) OR .gitmodules reference (uninitialized).
if [ -e "$REPO_ROOT/.claude/kit/.git" ] || grep -q '\[submodule.*claude/kit' "$REPO_ROOT/.gitmodules" 2>/dev/null; then
    # Submodule mode: push from inside .claude/kit
    echo "[claude-kit] Pushing submodule .claude/kit..."
    if (cd "$REPO_ROOT/.claude/kit" && git push); then
        echo "[claude-kit] Submodule push succeeded."
    else
        echo "[claude-kit] ERROR: Submodule push failed. Aborting."
        echo "[claude-kit] Fix the issue in .claude/kit/ and retry."
        exit 1
    fi
elif [ -d "$REPO_ROOT/.claude" ]; then
    # Subtree mode: push via git subtree push
    if git remote get-url claude-kit >/dev/null 2>&1; then
        echo "[claude-kit] Pushing subtree .claude/ to claude-kit remote..."
        if git subtree push --prefix=.claude claude-kit main; then
            echo "[claude-kit] Subtree push succeeded."
        else
            echo "[claude-kit] ERROR: Subtree push failed. Aborting."
            echo "[claude-kit] Check for upstream conflicts and retry."
            exit 1
        fi
    else
        echo "[claude-kit] No 'claude-kit' remote found. Skipping .claude/ push."
    fi
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
