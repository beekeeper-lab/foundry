#!/usr/bin/env bash
# claude-publish.sh — Safe two-step push: submodule first, then the main repo.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
KIT_DIR="$REPO_ROOT/.claude/shared"

# --- Step 1: Push .claude/shared submodule if it has unpushed commits ---
if [ -e "$KIT_DIR/.git" ] || [ -f "$KIT_DIR/.git" ]; then
    cd "$KIT_DIR"

    # Submodules check out detached by default; a blind `git push` from a
    # detached HEAD fails (or worse, pushes nothing while looking green).
    # Refuse with instructions instead (ADR-016 / SPEC-026).
    KIT_BRANCH="$(git branch --show-current)"
    if [ -z "$KIT_BRANCH" ]; then
        echo "[claude-kit] ERROR: .claude/shared is on a detached HEAD."
        echo "[claude-kit] Create a branch first, e.g.:"
        echo "[claude-kit]   git -C .claude/shared checkout -b fix/my-change"
        echo "[claude-kit] then commit and re-run. Downstream contributors"
        echo "[claude-kit] without push rights: use scripts/kit-contribute.sh."
        exit 1
    fi
    if [ -z "$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null)" ]; then
        echo "[claude-kit] Branch '$KIT_BRANCH' has no upstream — pushing with -u origin."
        PUSH_ARGS=(-u origin "$KIT_BRANCH")
    else
        PUSH_ARGS=()
    fi

    if [ -n "$(git status --porcelain)" ] || \
       [ "$(git rev-parse HEAD)" != "$(git rev-parse '@{u}' 2>/dev/null || echo '')" ]; then
        echo "[claude-kit] Pushing submodule .claude/shared..."
        if git push "${PUSH_ARGS[@]}"; then
            echo "[claude-kit] Submodule push succeeded."
        else
            echo "[claude-kit] ERROR: Submodule push failed. Aborting."
            echo "[claude-kit] Fix the issue in .claude/shared/ and retry."
            exit 1
        fi
    else
        echo "[claude-kit] Submodule .claude/shared is up to date."
    fi
    cd "$REPO_ROOT"
else
    echo "[claude-kit] WARNING: No .claude/shared submodule found. Skipping submodule push."
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
