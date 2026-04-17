# Hook Pack: AWS Limited Ops

## Category
aws

## Purpose

Blocks destructive AWS operations (`delete`, `terminate`, destructive `rm`
sub-commands) while permitting standard deployment operations.

## Hooks

| Hook Name | Trigger | Check | Pass Criteria | Fail Action |
|-----------|---------|-------|---------------|-------------|
| `aws-limited-ops-gate` | `PreToolUse:Bash` | Inspect `aws` commands for destructive verbs | No `delete-*`, `terminate-*`, or `s3 rm --recursive` | Block execution; print offending verb |

## Configuration

- **Default mode:** enforcing
- **Applies to:** every Bash tool call containing an `aws` invocation
- **Customization:** switch to `aws-read-only` for stricter posture.

## Posture Compatibility

| Posture | Included | Default Mode |
|---------|----------|--------------|
| `baseline` | No | — |
| `hardened` | Yes | enforcing |
| `regulated` | Yes | enforcing |

## Stack Signals

Added only when `architecture.cloud_providers` includes `aws`. The Azure
equivalent is `az-limited-ops`.
