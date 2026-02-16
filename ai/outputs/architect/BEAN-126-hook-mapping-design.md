# BEAN-126: Hook Pack → Native Claude Code Hook Mapping Design

## Overview

Each hook pack maps to one or more entries in the `PreToolUse` or `PostToolUse` arrays of `.claude/settings.json`. The format is:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "<tool-name-regex>",
        "hooks": [
          {
            "type": "command",
            "command": "<shell-command>"
          }
        ]
      }
    ],
    "PostToolUse": [...]
  }
}
```

## Design Decisions

1. **Disabled packs** (`mode: disabled`) are excluded entirely — no hook entries generated.
2. **Permissive packs** generate hooks that warn but exit 0 (don't block).
3. **Enforcing packs** generate hooks that exit 1 on failure (block the action).
4. **Posture** determines default packs when none explicitly selected:
   - `baseline`: git-commit-branch, pre-commit-lint
   - `hardened`: baseline + git-push-feature, security-scan
   - `regulated`: hardened + compliance-gate, post-task-qa
5. When packs are explicitly selected, posture defaults are ignored — explicit wins.
6. Multiple hooks for the same matcher are merged into a single entry.

## Hook Pack Mappings

### git-commit-branch (category: git)
**PreToolUse** on `Edit|Write|NotebookEdit`:
```bash
branch=$(git branch --show-current 2>/dev/null)
if [ "$branch" = "main" ] || [ "$branch" = "master" ] || [ "$branch" = "test" ] || [ "$branch" = "prod" ]; then
  echo 'BLOCKED: Cannot edit files on a protected branch. Create a feature branch first.'
  exit 1
fi
```

### git-push-feature (category: git)
**PreToolUse** on `Bash`:
```bash
if echo "$TOOL_INPUT" | grep -q 'git push'; then
  branch=$(git branch --show-current 2>/dev/null)
  if ! echo "$branch" | grep -qE '^(feature|fix|bean|hotfix|chore)/[a-z0-9-]+$'; then
    echo "BLOCKED: Branch '$branch' does not follow naming convention (feature|fix|bean|hotfix|chore)/<name>."
    exit 1
  fi
fi
```

### pre-commit-lint (category: code-quality)
**PreToolUse** on `Bash`:
```bash
if echo "$TOOL_INPUT" | grep -q 'git commit'; then
  ruff check --quiet . 2>/dev/null
  if [ $? -ne 0 ]; then
    echo 'BLOCKED: Lint errors found. Run ruff check --fix to resolve.'
    exit 1
  fi
fi
```

### security-scan (category: code-quality)
**PreToolUse** on `Bash`:
```bash
if echo "$TOOL_INPUT" | grep -q 'git commit'; then
  if git diff --cached --name-only 2>/dev/null | xargs grep -lE '(?i)(api[_-]?key|secret[_-]?key|password\s*=|token\s*=|BEGIN (RSA |EC )?PRIVATE KEY)' 2>/dev/null; then
    echo 'BLOCKED: Potential secrets detected in staged files. Remove credentials before committing.'
    exit 1
  fi
fi
```

### post-task-qa (category: code-quality)
**PostToolUse** on `Edit|Write`:
```bash
echo 'QA reminder: Verify acceptance criteria and required outputs before marking task done.'
```
Note: This is advisory — always exits 0.

### compliance-gate (category: code-quality)
**PostToolUse** on `Edit|Write`:
```bash
echo 'Compliance: Ensure evidence artifacts are collected and audit trail is maintained.'
```
Note: Compliance hooks are advisory reminders at the Claude Code level; actual enforcement happens in the workflow.

### az-read-only (category: az)
**PreToolUse** on `Bash`:
```bash
if echo "$TOOL_INPUT" | grep -qE '^az\s|;\s*az\s|&&\s*az\s|\|\s*az\s'; then
  if echo "$TOOL_INPUT" | grep -qE 'az\s+\S+\s+(create|delete|update|start|stop|restart|purge|set)'; then
    echo 'BLOCKED: Only read-only Azure CLI operations (show, list, get) are allowed.'
    exit 1
  fi
fi
```

### az-limited-ops (category: az)
**PreToolUse** on `Bash`:
```bash
if echo "$TOOL_INPUT" | grep -qE '^az\s|;\s*az\s|&&\s*az\s|\|\s*az\s'; then
  if echo "$TOOL_INPUT" | grep -qE 'az\s+(group|vm|storage account|sql server|sql db|keyvault|network vnet|aks)\s+delete|az\s+\S+\s+purge'; then
    echo 'BLOCKED: Destructive Azure operations are not allowed. Deployment operations are permitted.'
    exit 1
  fi
fi
```

### git-generate-pr (category: git)
No native hook — this is a workflow action, not a guard. The gh CLI is invoked directly by the agent.

### git-merge-to-test (category: git)
No native hook — merge operations are workflow actions managed by the merge captain.

### git-merge-to-prod (category: git)
No native hook — production merges are workflow actions with their own approval process.

## Posture Defaults

When `spec.hooks.packs` is empty, use posture to determine defaults:

| Posture | Default Packs |
|---------|--------------|
| baseline | git-commit-branch, pre-commit-lint |
| hardened | git-commit-branch, pre-commit-lint, git-push-feature, security-scan |
| regulated | git-commit-branch, pre-commit-lint, git-push-feature, security-scan, compliance-gate, post-task-qa |

## Merger Rules

- Multiple hooks sharing the same matcher are combined into a single entry.
- PreToolUse entries are sorted: git hooks first, then code-quality, then az.
- PostToolUse entries follow the same ordering.

## Implementation Notes

- The `TOOL_INPUT` environment variable is not available in Claude Code hooks. Instead, hooks receive the tool input on stdin as JSON. The command should read stdin if it needs to inspect the tool arguments.
- Actually, based on Foundry's own hooks (`.claude/settings.json`), the commands are simple shell scripts that don't inspect tool input — they just check system state (current branch, etc.).
- For Bash-tool hooks that need to inspect the command being run: Claude Code passes the tool input as JSON on stdin. The hook can parse it with `jq` or similar.
- Keep commands concise — single-line where possible for settings.json readability.
