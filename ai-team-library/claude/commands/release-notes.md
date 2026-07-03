---
name: release-notes
description: "Generates release notes and a changelog entry from completed work. Collects completed tasks, merged changes, and known issues from a release cycle; produces both user-facing notes and a Keep a Changelog entry."
---

# /release-notes Command

Generates release notes and a changelog entry from completed work. Collects completed tasks, merged changes, and known issues from a release cycle; produces both user-facing notes and a Keep a Changelog entry.

## Usage

```
/release-notes <version> [--previous <version>] [--audience <internal|external|both>] [--tasks <dir>] [--changelog <path>] [--output <dir>] [--dry-run]
```

- `version` -- Version identifier for this release (required).
- `--previous <version>` -- Previous version (auto-detected if omitted).
- `--audience <level>` -- `internal`, `external`, or `both` (default).
- `--tasks <dir>` -- Tasks directory (default: `ai/tasks/`).
- `--changelog <path>` -- Path to the changelog file (default: `CHANGELOG.md`).
- `--output <dir>` -- Override the output directory (default: `ai/outputs/devops-release/`).
- `--dry-run` -- Preview without writing files or appending changelog.

## See Also

- Skill: `claude/skills/release-notes/SKILL.md` — canonical execution spec.
