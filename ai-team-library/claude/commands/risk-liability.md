---
name: risk-liability
description: "Performs a risk assessment and liability analysis across six legal domains: contractual liability, indemnification, limitation of liability, insurance, incident response obligations, and breach notification duties."
---

# /risk-liability Command

Performs a risk assessment and liability analysis across six legal domains: contractual liability, indemnification, limitation of liability, insurance, incident response obligations, and breach notification duties.

## Usage

```
/risk-liability <project-context> [--contracts <paths>] [--architecture <path>] [--regulations <list>] [--insurance <paths>] [--update <path>] [--output <dir>] [--severity <level>]
```

- `project-context` -- Path to the project context or brief (business domain, data types, jurisdictions).
- `--contracts <paths>` -- Comma-separated contract paths.
- `--architecture <path>` -- Path to architecture doc for data flow context.
- `--regulations <list>` -- Comma-separated regulatory identifiers (e.g., `GDPR,CCPA,HIPAA`).
- `--insurance <paths>` -- Comma-separated insurance policy summary paths.
- `--update <path>` -- Update an existing assessment incrementally.
- `--output <dir>` -- Override output directory (default: `ai/outputs/legal-counsel/`).
- `--severity <level>` -- Minimum severity for priority actions. Default `medium`.

## See Also

- Skill: `claude/skills/risk-liability/SKILL.md` — canonical execution spec.
