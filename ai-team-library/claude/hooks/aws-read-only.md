# Hook Pack: AWS Read-Only

## Category
aws

## Purpose

Restricts the `aws` CLI to read-only verbs (`describe`, `list`, `get`). Any
command containing a mutating verb is blocked before it runs.

## Hooks

| Hook Name | Trigger | Check | Pass Criteria | Fail Action |
|-----------|---------|-------|---------------|-------------|
| `aws-read-only-gate` | `PreToolUse:Bash` | Inspect the command for `aws` invocations | Only `describe` / `list` / `get` verbs used | Block execution; print offending verb |

## Configuration

- **Default mode:** enforcing
- **Applies to:** every Bash tool call that contains an `aws` invocation
- **Customization:** switch to `aws-limited-ops` to permit non-destructive
  deployment verbs.

## Posture Compatibility

| Posture | Included | Default Mode |
|---------|----------|--------------|
| `baseline` | No | — |
| `hardened` | Optional | enforcing |
| `regulated` | Yes (when explicitly stricter than `aws-limited-ops`) | enforcing |

## Stack Signals

Added only when `architecture.cloud_providers` includes `aws`. Never added to
projects without an AWS footprint.

## Conflicts With

- `aws-limited-ops` — the read-only guard blocks every mutating verb that `aws-limited-ops` is supposed to allow; enabling both neutralizes deployment operations.
