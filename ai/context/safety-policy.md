# Safety Policy: Foundry

> Preset: **baseline**

This document describes the safety guardrails configured for this project.
These rules are enforced via `.claude/settings.local.json` and should be
followed by all agents working in this project.

## Summary

This project uses a **baseline** safety posture. Dangerous operations are blocked.

## Policies

- **Git:** push=yes, force-push=no, branch-delete=no
- **Shell:** sudo=no, install=yes
- **Filesystem:** outside-project=no
- **Network:** network=yes, external-apis=yes
- **Secrets:** block-env=yes, block-credentials=yes
- **Destructive:** rm-rf=no, reset-hard=no, clean=no

See `git-policy.md` and `shell-policy.md` for detailed rules.
