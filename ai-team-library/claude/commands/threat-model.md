---
name: threat-model
description: "Performs a STRIDE threat analysis on a system architecture. Identifies threats by analyzing trust boundaries, data flows, and entry points; produces a threat model with risk ratings, mitigations, and a testable security checklist."
---

# /threat-model Command

Performs a STRIDE threat analysis on a system architecture. Identifies threats by analyzing trust boundaries, data flows, and entry points; produces a threat model with risk ratings, mitigations, and a testable security checklist.

## Usage

```
/threat-model <architecture-doc> [--scope <component>] [--update <path>] [--output <dir>] [--risk-threshold <level>]
```

- `architecture-doc` -- Path to the architecture spec or design document to analyze.
- `--scope <component>` -- Limit analysis to a specific component or subsystem.
- `--update <path>` -- Update an existing threat model incrementally.
- `--output <dir>` -- Override the output directory (default: `ai/outputs/security-engineer/`).
- `--risk-threshold <level>` -- Only include threats at or above this level in the checklist. Default `medium`.

## See Also

- Skill: `claude/skills/threat-model/SKILL.md` — canonical execution spec.
